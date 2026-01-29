"""
Insight Detection Rules

Comprehensive rule-based engine for detecting actionable scouting insights.
Organized into 6 rule groups with evidence tracking and impact scoring.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from ..metrics.valorant import AllMetrics, MetricResult
from ..normalize.valorant import NormalizedData

logger = logging.getLogger(__name__)


@dataclass
class EvidenceRef:
    """Reference to evidence supporting an insight."""
    table: str
    filters: dict[str, Any]
    sample_rows: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "table": self.table,
            "filters": self.filters,
            "sample_rows": self.sample_rows[:5],
        }


@dataclass
class InsightResult:
    """
    Complete insight with evidence and impact scoring.
    """
    title: str
    severity: str  # HIGH, MED, LOW
    confidence: str  # HIGH, MED, LOW
    data_point: str
    interpretation: str
    recommendation: str
    what_not_to_do: Optional[str] = None
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    impact_score: float = 0.0
    category: str = "general"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity,
            "confidence": self.confidence,
            "data_point": self.data_point,
            "interpretation": self.interpretation,
            "recommendation": self.recommendation,
            "what_not_to_do": self.what_not_to_do,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "impact_score": self.impact_score,
            "category": self.category,
        }


# Type alias for rule functions
RuleFunction = Callable[[AllMetrics, NormalizedData], Optional[InsightResult]]


def _calculate_impact_score(
    confidence: str,
    effect_size: float,
    sample_size: int,
) -> float:
    """
    Calculate impact score for ranking insights.
    
    impact = confidence_weight * effect_size * log(sample_size + 1)
    """
    import math
    
    conf_weights = {"high": 1.0, "medium": 0.7, "low": 0.4}
    conf_weight = conf_weights.get(confidence.lower(), 0.5)
    
    freq_factor = math.log(sample_size + 1) / math.log(20)  # Normalize around 20 samples
    freq_factor = min(1.0, max(0.3, freq_factor))
    
    return conf_weight * abs(effect_size) * freq_factor


def _make_evidence_ref(
    metric: MetricResult,
    table_name: str,
    filters: Optional[dict] = None,
) -> EvidenceRef:
    """Create an evidence reference from a MetricResult."""
    sample_rows = []
    if not metric.evidence_df.empty:
        sample_rows = metric.evidence_df.head(5).to_dict("records")
    
    return EvidenceRef(
        table=table_name,
        filters=filters or {},
        sample_rows=sample_rows,
    )


# ============================================================================
# GROUP 1: Trend Alert Rules
# ============================================================================

def rule_trend_win_rate_shift(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect significant win rate change between last 3 and last 10 matches."""
    trend = metrics.trend_metrics.get("win_rate", {})
    
    if "last_3" not in trend or "last_10" not in trend:
        return None
    
    last_3 = trend["last_3"]
    last_10 = trend["last_10"]
    
    if last_3.denominator < 3 or last_10.denominator < 5:
        return None
    
    change = last_3.value - last_10.value
    
    if abs(change) < 0.15:  # Require 15% change
        return None
    
    direction = "improving" if change > 0 else "declining"
    severity = "HIGH" if abs(change) >= 0.25 else "MED"
    
    return InsightResult(
        title=f"Win Rate {direction.capitalize()}",
        severity=severity,
        confidence=last_3.confidence,
        data_point=f"Win rate shifted from {last_10.value:.0%} to {last_3.value:.0%} ({change:+.0%})",
        interpretation=f"Team is {direction} significantly in recent matches. This trend may indicate roster changes, meta adaptation, or form fluctuation.",
        recommendation=f"{'Capitalize on momentum and force uncomfortable maps' if direction == 'declining' else 'Be cautious - they may be adapting. Review their recent VODs.'}",
        what_not_to_do="Don't assume past performance predicts future results without checking recent form." if direction == "improving" else None,
        evidence_refs=[_make_evidence_ref(last_3, "matches_df", {"period": "last_3"})],
        impact_score=_calculate_impact_score(last_3.confidence, change, last_3.denominator),
        category="trend",
    )


def rule_trend_pistol_shift(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect significant pistol round performance change."""
    trend = metrics.trend_metrics.get("pistol", {})
    
    if "last_3" not in trend or "last_10" not in trend:
        return None
    
    last_3 = trend["last_3"]
    last_10 = trend["last_10"]
    
    if last_3.denominator < 4 or last_10.denominator < 8:
        return None
    
    change = last_3.value - last_10.value
    
    if abs(change) < 0.20:
        return None
    
    direction = "improving" if change > 0 else "declining"
    
    return InsightResult(
        title=f"Pistol Performance {direction.capitalize()}",
        severity="MED",
        confidence=last_3.confidence,
        data_point=f"Pistol win rate: {last_10.value:.0%} → {last_3.value:.0%} ({change:+.0%})",
        interpretation=f"Pistol round performance is {direction}. May indicate changes in pistol strategy or coordination.",
        recommendation=f"{'Their pistol rounds are vulnerable - prepare strong pistol strats' if direction == 'declining' else 'Expect improved pistol execution - vary your approach'}",
        evidence_refs=[_make_evidence_ref(last_3, "rounds_df", {"pistol_round_bool": True})],
        impact_score=_calculate_impact_score(last_3.confidence, change, last_3.denominator),
        category="trend",
    )


def rule_trend_side_shift(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect significant attack/defense balance change."""
    attack_trend = metrics.trend_metrics.get("attack", {})
    defense_trend = metrics.trend_metrics.get("defense", {})
    
    if not attack_trend or not defense_trend:
        return None
    
    # Check for attack-defense gap change
    if "last_3" in attack_trend and "last_3" in defense_trend:
        attack_3 = attack_trend["last_3"].value
        defense_3 = defense_trend["last_3"].value
        gap = attack_3 - defense_3
        
        if abs(gap) >= 0.15:
            stronger_side = "attack" if gap > 0 else "defense"
            weaker_side = "defense" if gap > 0 else "attack"
            
            return InsightResult(
                title=f"Side Imbalance: {stronger_side.capitalize()} Heavy",
                severity="MED",
                confidence="medium",
                data_point=f"Attack: {attack_3:.0%}, Defense: {defense_3:.0%} (gap: {abs(gap):.0%})",
                interpretation=f"Team currently favors {stronger_side} side significantly. May have predictable patterns on {weaker_side}.",
                recommendation=f"Focus on exploiting their {weaker_side} side. Force them into uncomfortable situations.",
                evidence_refs=[
                    _make_evidence_ref(attack_trend["last_3"], "rounds_df", {"side": "attack"}),
                ],
                impact_score=_calculate_impact_score("medium", gap, 10),
                category="trend",
            )
    
    return None


# ============================================================================
# GROUP 2: Loss Pattern Rules
# ============================================================================

def rule_loss_after_pistol(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect high loss rate after losing pistol."""
    pattern = metrics.loss_patterns.get("after_pistol_loss")
    
    if not pattern or pattern.denominator < 3:
        return None
    
    if pattern.value < 0.65:  # Need high loss rate
        return None
    
    return InsightResult(
        title="Pistol Loss Collapse",
        severity="HIGH",
        confidence=pattern.confidence,
        data_point=f"Lose {pattern.value:.0%} of matches after losing first pistol (n={pattern.denominator})",
        interpretation="Team struggles to recover from pistol losses. Economy management or mental reset may be weak.",
        recommendation="Prioritize winning pistol rounds. Their economy cascade is vulnerable.",
        what_not_to_do="Don't force after winning pistol - let them tilt from the loss.",
        evidence_refs=[_make_evidence_ref(pattern, "matches_df", {"lost_pistol": True})],
        impact_score=_calculate_impact_score(pattern.confidence, pattern.value - 0.5, pattern.denominator),
        category="loss_pattern",
    )


def rule_loss_when_down_early(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect collapse when behind early."""
    pattern = metrics.loss_patterns.get("when_down_early")
    
    if not pattern or pattern.denominator < 10:
        return None
    
    if pattern.value < 0.70:
        return None
    
    return InsightResult(
        title="Early Deficit Collapse",
        severity="HIGH",
        confidence=pattern.confidence,
        data_point=f"Lose {pattern.value:.0%} of remaining rounds when down 0-2 (n={pattern.denominator})",
        interpretation="Team tilts when falling behind early. Mental fortitude or adaptation mid-game is weak.",
        recommendation="Establish early round advantage aggressively. Their confidence breaks when behind.",
        what_not_to_do="Don't let up if you're ahead - keep pressure on.",
        evidence_refs=[_make_evidence_ref(pattern, "rounds_df", {"down_early": True})],
        impact_score=_calculate_impact_score(pattern.confidence, pattern.value - 0.5, pattern.denominator),
        category="loss_pattern",
    )


def rule_eco_vulnerability(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect poor eco round conversion or giving up too many eco rounds."""
    eco = metrics.eco_conversion_rate
    
    if eco.denominator < 5:
        return None
    
    # Check if they're TOO good at eco (meaning opponents give up rounds)
    if eco.value > 0.35:
        return InsightResult(
            title="Strong Eco Round Conversion",
            severity="MED",
            confidence=eco.confidence,
            data_point=f"Win {eco.value:.0%} of eco rounds (n={eco.denominator})",
            interpretation="Team converts eco rounds at high rate. May have practiced eco strats.",
            recommendation="Don't underestimate their ecos. Play disciplined and trade carefully.",
            evidence_refs=[_make_evidence_ref(eco, "rounds_df", {"eco_round_bool": True})],
            impact_score=_calculate_impact_score(eco.confidence, eco.value - 0.15, eco.denominator),
            category="loss_pattern",
        )
    elif eco.value < 0.10:
        return InsightResult(
            title="Weak Eco Rounds",
            severity="LOW",
            confidence=eco.confidence,
            data_point=f"Win only {eco.value:.0%} of eco rounds (n={eco.denominator})",
            interpretation="Team rarely converts eco rounds. May not have practiced eco strats.",
            recommendation="Force them into eco situations. They won't punish overconfidence.",
            evidence_refs=[_make_evidence_ref(eco, "rounds_df", {"eco_round_bool": True})],
            impact_score=_calculate_impact_score(eco.confidence, 0.15 - eco.value, eco.denominator),
            category="loss_pattern",
        )
    
    return None


# ============================================================================
# GROUP 3: Agent Neutralization Rules
# ============================================================================

def rule_agent_dependency(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect player overly dependent on one agent."""
    for player, agents in metrics.player_agent_picks.items():
        for agent, pick in agents.items():
            if pick.denominator >= 5 and pick.value >= 0.85:
                return InsightResult(
                    title=f"{player} One-Tricks {agent}",
                    severity="HIGH",
                    confidence=pick.confidence,
                    data_point=f"{player} plays {agent} in {pick.value:.0%} of games ({pick.numerator}/{pick.denominator})",
                    interpretation=f"Player is heavily dependent on {agent}. May struggle with agent bans or counter-comps.",
                    recommendation=f"Counter-pick against {agent}. Watch for {player}'s common positions and utility usage.",
                    what_not_to_do=f"Don't ignore {player} - their comfort pick makes them dangerous.",
                    evidence_refs=[_make_evidence_ref(pick, "players_df", {"player_name": player, "agent": agent})],
                    impact_score=_calculate_impact_score(pick.confidence, pick.value - 0.5, pick.denominator),
                    category="agent",
                )
    return None


def rule_agent_target(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Identify specific player/agent combo to target based on FB rates."""
    for player, fb_rate in metrics.player_first_blood_rates.items():
        fd_rate = metrics.player_first_death_rates.get(player)
        
        if fb_rate.denominator < 5:
            continue
        
        if fd_rate and fd_rate.value > fb_rate.value and fd_rate.value >= 2.0:
            return InsightResult(
                title=f"Target: {player}",
                severity="MED",
                confidence=fb_rate.confidence,
                data_point=f"{player}: {fb_rate.value:.1f} FB/game but {fd_rate.value:.1f} FD/game",
                interpretation=f"{player} dies first more often than getting first blood. Aggressive but punishable.",
                recommendation=f"Set up crossfires for {player}'s entry. They overextend.",
                evidence_refs=[_make_evidence_ref(fb_rate, "players_df", {"player_name": player})],
                impact_score=_calculate_impact_score(fb_rate.confidence, fd_rate.value - fb_rate.value, fb_rate.denominator),
                category="agent",
            )
    
    return None


def rule_first_blood_reliance(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect if team relies heavily on one player for first bloods."""
    fb_rates = metrics.player_first_blood_rates
    
    if len(fb_rates) < 3:
        return None
    
    rates = [(name, m.value) for name, m in fb_rates.items() if m.denominator >= 3]
    if not rates:
        return None
    
    sorted_rates = sorted(rates, key=lambda x: x[1], reverse=True)
    top_player, top_rate = sorted_rates[0]
    avg_rate = sum(r for _, r in rates) / len(rates)
    
    if avg_rate > 0 and top_rate >= avg_rate * 2 and top_rate >= 2.0:
        metric = fb_rates[top_player]
        return InsightResult(
            title=f"Entry Reliance on {top_player}",
            severity="HIGH",
            confidence=metric.confidence,
            data_point=f"{top_player}: {top_rate:.1f} FB/game (team avg: {avg_rate:.1f})",
            interpretation=f"Team's entry depends heavily on {top_player}. Shutting them down disrupts tempo.",
            recommendation=f"Focus {top_player} early. Set up specific counters for their entry paths.",
            what_not_to_do="Don't let them get first blood - it swings rounds heavily.",
            evidence_refs=[_make_evidence_ref(metric, "players_df", {"player_name": top_player})],
            impact_score=_calculate_impact_score(metric.confidence, top_rate / avg_rate - 1, metric.denominator),
            category="agent",
        )
    
    return None


# ============================================================================
# GROUP 4: Map Veto Rules
# ============================================================================

def rule_map_weakness(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect maps to force (opponent weak on)."""
    for map_name, map_metric in metrics.map_win_rates.items():
        if map_metric.denominator >= 3 and map_metric.value <= 0.35:
            return InsightResult(
                title=f"Force: {map_name}",
                severity="HIGH",
                confidence=map_metric.confidence,
                data_point=f"{map_metric.value:.0%} win rate on {map_name} ({map_metric.numerator}/{map_metric.denominator})",
                interpretation=f"Team consistently struggles on {map_name}. Likely unpracticed or fundamentally weak.",
                recommendation=f"Force {map_name} in map veto. Prepare your best strats for this map.",
                evidence_refs=[_make_evidence_ref(map_metric, "matches_df", {"map": map_name})],
                impact_score=_calculate_impact_score(map_metric.confidence, 0.5 - map_metric.value, map_metric.denominator),
                category="map_veto",
            )
    return None


def rule_map_strength(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect maps to ban (opponent strong on)."""
    for map_name, map_metric in metrics.map_win_rates.items():
        if map_metric.denominator >= 3 and map_metric.value >= 0.70:
            return InsightResult(
                title=f"Ban: {map_name}",
                severity="HIGH",
                confidence=map_metric.confidence,
                data_point=f"{map_metric.value:.0%} win rate on {map_name} ({map_metric.numerator}/{map_metric.denominator})",
                interpretation=f"Team dominates on {map_name}. Well-practiced with refined strats.",
                recommendation=f"Ban {map_name} if possible. If forced to play, prepare specific counter-strats.",
                what_not_to_do=f"Don't play default on {map_name} - they will out-execute you.",
                evidence_refs=[_make_evidence_ref(map_metric, "matches_df", {"map": map_name})],
                impact_score=_calculate_impact_score(map_metric.confidence, map_metric.value - 0.5, map_metric.denominator),
                category="map_veto",
            )
    return None


def rule_map_sample_size(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Flag maps with low sample size - risky picks."""
    low_sample_maps = []
    for map_name, map_metric in metrics.map_win_rates.items():
        if map_metric.denominator < 3 and map_metric.denominator > 0:
            low_sample_maps.append(f"{map_name} ({map_metric.denominator})")
    
    if low_sample_maps:
        return InsightResult(
            title="Low Data Maps",
            severity="LOW",
            confidence="low",
            data_point=f"Limited data on: {', '.join(low_sample_maps)}",
            interpretation="Some maps have insufficient sample size for reliable analysis.",
            recommendation="These maps are wildcards. Extra VOD review recommended before picking.",
            evidence_refs=[],
            impact_score=0.3,
            category="map_veto",
        )
    return None


# ============================================================================
# GROUP 5: Playbook Predictor Rules
# ============================================================================

def rule_pistol_tendencies(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect predictable pistol setups."""
    pistol = metrics.pistol_win_rate
    
    if pistol.denominator < 6:
        return None
    
    # High or low pistol rate indicates predictable patterns
    if pistol.value >= 0.65:
        return InsightResult(
            title="Strong Pistol Execution",
            severity="MED",
            confidence=pistol.confidence,
            data_point=f"{pistol.value:.0%} pistol win rate ({pistol.numerator}/{pistol.denominator})",
            interpretation="Team has refined pistol strats. Likely use utility-heavy or coordinated setups.",
            recommendation="Scout their pistol setups. Counter with anti-pistol utility or aggressive pushes.",
            evidence_refs=[_make_evidence_ref(pistol, "rounds_df", {"pistol_round_bool": True})],
            impact_score=_calculate_impact_score(pistol.confidence, pistol.value - 0.5, pistol.denominator),
            category="playbook",
        )
    elif pistol.value <= 0.35:
        return InsightResult(
            title="Weak Pistol Rounds",
            severity="MED",
            confidence=pistol.confidence,
            data_point=f"{pistol.value:.0%} pistol win rate ({pistol.numerator}/{pistol.denominator})",
            interpretation="Team struggles in pistol rounds. May rely on aim duels or have poor coordination.",
            recommendation="Play aggressive pistols. They're vulnerable to early pressure.",
            evidence_refs=[_make_evidence_ref(pistol, "rounds_df", {"pistol_round_bool": True})],
            impact_score=_calculate_impact_score(pistol.confidence, 0.5 - pistol.value, pistol.denominator),
            category="playbook",
        )
    
    return None


def rule_side_preference(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect strong side preference indicating default patterns."""
    attack = metrics.attack_win_rate
    defense = metrics.defense_win_rate
    
    if attack.denominator < 20 or defense.denominator < 20:
        return None
    
    gap = abs(attack.value - defense.value)
    
    if gap >= 0.15:
        stronger = "attack" if attack.value > defense.value else "defense"
        weaker = "defense" if stronger == "attack" else "attack"
        
        return InsightResult(
            title=f"{stronger.capitalize()}-Sided Team",
            severity="MED",
            confidence="high" if gap >= 0.20 else "medium",
            data_point=f"Attack: {attack.value:.0%}, Defense: {defense.value:.0%} (gap: {gap:.0%})",
            interpretation=f"Team favors {stronger} significantly. Likely have more refined {stronger} playbook.",
            recommendation=f"Force them to play {weaker}. Their defaults on {weaker} are exploitable.",
            evidence_refs=[
                _make_evidence_ref(attack, "rounds_df", {"side": "attack"}),
                _make_evidence_ref(defense, "rounds_df", {"side": "defense"}),
            ],
            impact_score=_calculate_impact_score("high" if gap >= 0.20 else "medium", gap, attack.denominator),
            category="playbook",
        )
    
    return None


# ============================================================================
# GROUP 6: Meta Comparison Rules
# ============================================================================

def rule_below_meta_baseline(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect significantly below-average performance areas."""
    # Compare to 50% baseline for now
    areas_below = []
    
    if metrics.pistol_win_rate.value < 0.40 and metrics.pistol_win_rate.denominator >= 6:
        areas_below.append(("pistol", metrics.pistol_win_rate))
    
    if metrics.attack_win_rate.value < 0.40 and metrics.attack_win_rate.denominator >= 20:
        areas_below.append(("attack", metrics.attack_win_rate))
    
    if metrics.defense_win_rate.value < 0.40 and metrics.defense_win_rate.denominator >= 20:
        areas_below.append(("defense", metrics.defense_win_rate))
    
    if areas_below:
        worst = min(areas_below, key=lambda x: x[1].value)
        area, metric = worst
        
        return InsightResult(
            title=f"Below Average: {area.capitalize()}",
            severity="HIGH",
            confidence=metric.confidence,
            data_point=f"{area.capitalize()} performance: {metric.value:.0%} vs ~50% baseline",
            interpretation=f"Team is significantly below average in {area}. Fundamental weakness.",
            recommendation=f"Exploit their {area} weakness with focused preparation.",
            evidence_refs=[_make_evidence_ref(metric, "rounds_df", {"category": area})],
            impact_score=_calculate_impact_score(metric.confidence, 0.5 - metric.value, metric.denominator),
            category="meta",
        )
    
    return None


def rule_above_meta_baseline(
    metrics: AllMetrics,
    data: NormalizedData,
) -> Optional[InsightResult]:
    """Detect significantly above-average performance areas."""
    areas_above = []
    
    if metrics.pistol_win_rate.value > 0.60 and metrics.pistol_win_rate.denominator >= 6:
        areas_above.append(("pistol", metrics.pistol_win_rate))
    
    if metrics.attack_win_rate.value > 0.60 and metrics.attack_win_rate.denominator >= 20:
        areas_above.append(("attack", metrics.attack_win_rate))
    
    if metrics.defense_win_rate.value > 0.60 and metrics.defense_win_rate.denominator >= 20:
        areas_above.append(("defense", metrics.defense_win_rate))
    
    if areas_above:
        best = max(areas_above, key=lambda x: x[1].value)
        area, metric = best
        
        return InsightResult(
            title=f"Strong: {area.capitalize()}",
            severity="MED",
            confidence=metric.confidence,
            data_point=f"{area.capitalize()} performance: {metric.value:.0%} vs ~50% baseline",
            interpretation=f"Team excels in {area}. Well-practiced and coordinated.",
            recommendation=f"Prepare specific counters for their {area}. Don't play into their strength.",
            what_not_to_do=f"Don't underestimate their {area} - respect it and adapt.",
            evidence_refs=[_make_evidence_ref(metric, "rounds_df", {"category": area})],
            impact_score=_calculate_impact_score(metric.confidence, metric.value - 0.5, metric.denominator),
            category="meta",
        )
    
    return None


# ============================================================================
# All Rules Registry
# ============================================================================

ALL_RULES: list[RuleFunction] = [
    # Trend Alert Rules
    rule_trend_win_rate_shift,
    rule_trend_pistol_shift,
    rule_trend_side_shift,
    
    # Loss Pattern Rules
    rule_loss_after_pistol,
    rule_loss_when_down_early,
    rule_eco_vulnerability,
    
    # Agent Neutralization Rules
    rule_agent_dependency,
    rule_agent_target,
    rule_first_blood_reliance,
    
    # Map Veto Rules
    rule_map_weakness,
    rule_map_strength,
    rule_map_sample_size,
    
    # Playbook Predictor Rules
    rule_pistol_tendencies,
    rule_side_preference,
    
    # Meta Comparison Rules
    rule_below_meta_baseline,
    rule_above_meta_baseline,
]
