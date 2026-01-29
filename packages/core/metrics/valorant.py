"""
VALORANT Metrics Computation

Comprehensive metrics with evidence tracking for scouting reports.
Each metric includes confidence scoring, evidence DataFrames, and denominators.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..normalize.valorant import NormalizedData

logger = logging.getLogger(__name__)


@dataclass
class MetricResult:
    """
    Result container for a computed metric.
    
    Attributes:
        value: The computed metric value (e.g., win rate as decimal).
        numerator: The count of successes.
        denominator: The total sample size.
        confidence: Confidence level based on sample size ("high", "medium", "low").
        evidence_df: DataFrame containing the underlying evidence.
        meta: Additional metadata (e.g., breakdown by category).
    """
    value: float
    numerator: int
    denominator: int
    confidence: str
    evidence_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    meta: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (without evidence_df for JSON serialization)."""
        return {
            "value": self.value,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "confidence": self.confidence,
            "formatted": f"{self.numerator}/{self.denominator}",
            "percent": f"{self.value:.1%}" if self.denominator > 0 else "N/A",
            "meta": self.meta,
        }
    
    def get_evidence_sample(self, n: int = 5) -> list[dict]:
        """Get sample rows from evidence for UI display."""
        if self.evidence_df.empty:
            return []
        return self.evidence_df.head(n).to_dict("records")


@dataclass
class AllMetrics:
    """
    Container for all computed metrics for a team.
    """
    team_name: str
    matches_analyzed: int
    overall_win_rate: MetricResult
    map_win_rates: dict[str, MetricResult]
    attack_win_rate: MetricResult
    defense_win_rate: MetricResult
    pistol_win_rate: MetricResult
    eco_conversion_rate: MetricResult
    player_first_blood_rates: dict[str, MetricResult]
    player_first_death_rates: dict[str, MetricResult]
    player_agent_picks: dict[str, dict[str, MetricResult]]
    player_acs: dict[str, MetricResult]
    loss_patterns: dict[str, MetricResult]
    trend_metrics: dict[str, dict[str, MetricResult]]
    meta_comparison: dict[str, MetricResult]


def _get_confidence(sample_size: int) -> str:
    """Determine confidence level based on sample size."""
    if sample_size >= 10:
        return "high"
    elif sample_size >= 5:
        return "medium"
    else:
        return "low"


def _safe_divide(numerator: int, denominator: int, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


# ============================================================================
# Core Metrics
# ============================================================================

def compute_overall_win_rate(
    matches_df: pd.DataFrame,
    team_name: str,
) -> MetricResult:
    """Compute overall match win rate for a team."""
    if matches_df.empty:
        return MetricResult(0.0, 0, 0, "low")
    
    team_matches = matches_df[matches_df["team_name"].str.lower() == team_name.lower()].copy()
    total = len(team_matches)
    wins = len(team_matches[team_matches["result"] == "win"])
    
    return MetricResult(
        value=_safe_divide(wins, total),
        numerator=wins,
        denominator=total,
        confidence=_get_confidence(total),
        evidence_df=team_matches,
    )


def compute_map_win_rates(
    matches_df: pd.DataFrame,
    team_name: str,
) -> dict[str, MetricResult]:
    """
    Compute win rate per map with pick/ban suggestions.
    
    Returns dictionary mapping map name to MetricResult with meta containing:
    - suggestion: "BAN", "PICK", or "NEUTRAL"
    """
    if matches_df.empty:
        return {}
    
    team_matches = matches_df[matches_df["team_name"].str.lower() == team_name.lower()].copy()
    results = {}
    
    for map_name in team_matches["map"].unique():
        map_matches = team_matches[team_matches["map"] == map_name]
        total = len(map_matches)
        wins = len(map_matches[map_matches["result"] == "win"])
        win_rate = _safe_divide(wins, total)
        
        # Determine suggestion
        if total >= 3:
            if win_rate >= 0.65:
                suggestion = "PICK"
            elif win_rate <= 0.35:
                suggestion = "BAN"
            else:
                suggestion = "NEUTRAL"
        else:
            suggestion = "LOW_SAMPLE"
        
        results[map_name] = MetricResult(
            value=win_rate,
            numerator=wins,
            denominator=total,
            confidence=_get_confidence(total),
            evidence_df=map_matches,
            meta={"suggestion": suggestion},
        )
    
    return results


def compute_side_win_rates(
    rounds_df: pd.DataFrame,
    team_name: str,
) -> tuple[MetricResult, MetricResult]:
    """Compute attack and defense side win rates."""
    if rounds_df.empty:
        empty_result = MetricResult(0.0, 0, 0, "low")
        return empty_result, empty_result
    
    # Attack rounds won by team
    attack_rounds = rounds_df[rounds_df["side"].isin(["attack", "Attack"])].copy()
    attack_wins = len(attack_rounds[attack_rounds["winner"] == "team"])
    attack_total = len(attack_rounds)
    
    # Defense rounds won by team
    defense_rounds = rounds_df[rounds_df["side"].isin(["defense", "Defense"])].copy()
    defense_wins = len(defense_rounds[defense_rounds["winner"] == "team"])
    defense_total = len(defense_rounds)
    
    attack_result = MetricResult(
        value=_safe_divide(attack_wins, attack_total),
        numerator=attack_wins,
        denominator=attack_total,
        confidence=_get_confidence(attack_total),
        evidence_df=attack_rounds[attack_rounds["winner"] == "team"],
    )
    
    defense_result = MetricResult(
        value=_safe_divide(defense_wins, defense_total),
        numerator=defense_wins,
        denominator=defense_total,
        confidence=_get_confidence(defense_total),
        evidence_df=defense_rounds[defense_rounds["winner"] == "team"],
    )
    
    return attack_result, defense_result


def compute_pistol_win_rate(
    rounds_df: pd.DataFrame,
    team_name: str,
) -> MetricResult:
    """Compute pistol round win rate."""
    if rounds_df.empty:
        return MetricResult(0.0, 0, 0, "low")
    
    pistol_rounds = rounds_df[rounds_df["pistol_round_bool"] == True].copy()
    total = len(pistol_rounds)
    wins = len(pistol_rounds[pistol_rounds["winner"] == "team"])
    
    return MetricResult(
        value=_safe_divide(wins, total),
        numerator=wins,
        denominator=total,
        confidence=_get_confidence(total),
        evidence_df=pistol_rounds,
    )


def compute_eco_conversion_rate(
    rounds_df: pd.DataFrame,
    team_name: str,
) -> MetricResult:
    """Compute eco round conversion (win) rate."""
    if rounds_df.empty:
        return MetricResult(0.0, 0, 0, "low")
    
    eco_rounds = rounds_df[rounds_df["eco_round_bool"] == True].copy()
    total = len(eco_rounds)
    wins = len(eco_rounds[eco_rounds["winner"] == "team"])
    
    return MetricResult(
        value=_safe_divide(wins, total),
        numerator=wins,
        denominator=total,
        confidence=_get_confidence(total),
        evidence_df=eco_rounds,
    )


# ============================================================================
# Player Metrics
# ============================================================================

def compute_player_first_blood_rates(
    players_df: pd.DataFrame,
    team_name: str,
) -> dict[str, MetricResult]:
    """Compute first blood rate per player (FB per game)."""
    if players_df.empty:
        return {}
    
    team_players = players_df[players_df["is_our_team"] == True].copy()
    results = {}
    
    for player_name in team_players["player_name"].unique():
        player_data = team_players[team_players["player_name"] == player_name]
        total_matches = len(player_data)
        total_fb = player_data["first_bloods"].sum()
        
        if pd.isna(total_fb):
            total_fb = 0
        
        results[player_name] = MetricResult(
            value=_safe_divide(int(total_fb), total_matches),
            numerator=int(total_fb),
            denominator=total_matches,
            confidence=_get_confidence(total_matches),
            evidence_df=player_data,
        )
    
    return results


def compute_player_first_death_rates(
    players_df: pd.DataFrame,
    team_name: str,
) -> dict[str, MetricResult]:
    """Compute first death rate per player (FD per game)."""
    if players_df.empty:
        return {}
    
    team_players = players_df[players_df["is_our_team"] == True].copy()
    results = {}
    
    for player_name in team_players["player_name"].unique():
        player_data = team_players[team_players["player_name"] == player_name]
        total_matches = len(player_data)
        total_fd = player_data["first_deaths"].sum()
        
        if pd.isna(total_fd):
            total_fd = 0
        
        results[player_name] = MetricResult(
            value=_safe_divide(int(total_fd), total_matches),
            numerator=int(total_fd),
            denominator=total_matches,
            confidence=_get_confidence(total_matches),
            evidence_df=player_data,
        )
    
    return results


def compute_player_agent_picks(
    players_df: pd.DataFrame,
    team_name: str,
) -> dict[str, dict[str, MetricResult]]:
    """Compute agent pick frequency per player."""
    if players_df.empty:
        return {}
    
    team_players = players_df[players_df["is_our_team"] == True].copy()
    results = {}
    
    for player_name in team_players["player_name"].unique():
        player_picks = team_players[team_players["player_name"] == player_name]
        total_games = len(player_picks)
        
        agent_results = {}
        for agent in player_picks["agent"].unique():
            agent_count = len(player_picks[player_picks["agent"] == agent])
            
            agent_results[agent] = MetricResult(
                value=_safe_divide(agent_count, total_games),
                numerator=agent_count,
                denominator=total_games,
                confidence=_get_confidence(total_games),
                evidence_df=player_picks[player_picks["agent"] == agent],
            )
        
        results[player_name] = agent_results
    
    return results


def compute_player_acs(
    players_df: pd.DataFrame,
    team_name: str,
) -> dict[str, MetricResult]:
    """Compute average ACS per player."""
    if players_df.empty:
        return {}
    
    team_players = players_df[players_df["is_our_team"] == True].copy()
    results = {}
    
    for player_name in team_players["player_name"].unique():
        player_data = team_players[team_players["player_name"] == player_name]
        total_matches = len(player_data)
        avg_acs = player_data["acs"].mean()
        
        if pd.isna(avg_acs):
            avg_acs = 0.0
        
        results[player_name] = MetricResult(
            value=avg_acs,
            numerator=int(avg_acs * total_matches),
            denominator=total_matches,
            confidence=_get_confidence(total_matches),
            evidence_df=player_data,
            meta={"avg_kills": player_data["kills"].mean(), "avg_deaths": player_data["deaths"].mean()},
        )
    
    return results


# ============================================================================
# Loss Pattern Analysis
# ============================================================================

def compute_loss_after_pistol(
    rounds_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    team_name: str,
) -> MetricResult:
    """
    Compute loss rate when team loses pistol round.
    
    Returns the percentage of matches lost after losing the first pistol round.
    """
    if rounds_df.empty or matches_df.empty:
        return MetricResult(0.0, 0, 0, "low")
    
    # Get first pistol round per match
    pistol_rounds = rounds_df[rounds_df["pistol_round_bool"] == True].copy()
    first_pistols = pistol_rounds[pistol_rounds["round_num"] == 1]
    
    # Find matches where team lost pistol
    lost_pistol_matches = first_pistols[first_pistols["winner"] == "opponent"]["match_id"].unique()
    
    # Check match outcomes for those matches
    team_matches = matches_df[matches_df["team_name"].str.lower() == team_name.lower()].copy()
    lost_pistol_outcomes = team_matches[team_matches["match_id"].isin(lost_pistol_matches)]
    
    total = len(lost_pistol_outcomes)
    losses = len(lost_pistol_outcomes[lost_pistol_outcomes["result"] == "loss"])
    
    return MetricResult(
        value=_safe_divide(losses, total),
        numerator=losses,
        denominator=total,
        confidence=_get_confidence(total),
        evidence_df=lost_pistol_outcomes,
        meta={"condition": "Lost first pistol round"},
    )


def compute_loss_after_first_blood(
    rounds_df: pd.DataFrame,
    events_df: Optional[pd.DataFrame],
    team_name: str,
) -> MetricResult:
    """
    Compute round loss rate when opponent gets first blood.
    """
    if rounds_df.empty:
        return MetricResult(0.0, 0, 0, "low")
    
    # For now, we'll use a proxy - this would need events_df with FB info
    # We'll count rounds where team lost as "lost first blood" proxy
    total_rounds = len(rounds_df)
    lost_rounds = len(rounds_df[rounds_df["winner"] == "opponent"])
    
    return MetricResult(
        value=_safe_divide(lost_rounds, total_rounds),
        numerator=lost_rounds,
        denominator=total_rounds,
        confidence=_get_confidence(total_rounds),
        evidence_df=rounds_df[rounds_df["winner"] == "opponent"],
        meta={"condition": "Lost first blood (proxy)"},
    )


def compute_loss_when_down_early(
    rounds_df: pd.DataFrame,
    team_name: str,
) -> MetricResult:
    """
    Compute loss rate when down 0-2 early in the half.
    """
    if rounds_df.empty:
        return MetricResult(0.0, 0, 0, "low")
    
    # Check if score columns exist
    if "score_us" not in rounds_df.columns or "score_them" not in rounds_df.columns:
        return MetricResult(0.0, 0, 0, "low", meta={"condition": "Score data not available"})
    
    # Find instances where team was 0-2 down at round 3
    round_3 = rounds_df[rounds_df["round_num"] == 3].copy()
    
    if round_3.empty:
        return MetricResult(0.0, 0, 0, "low")
    
    down_0_2 = round_3[
        (round_3["score_us"] == 0) & (round_3["score_them"] >= 2)
    ]
    
    if down_0_2.empty:
        return MetricResult(0.0, 0, 0, "low", meta={"condition": "No 0-2 down situations found"})
    
    # For these matches, check if team lost more rounds than won
    down_match_ids = down_0_2["match_id"].unique()
    subsequent_rounds = rounds_df[
        (rounds_df["match_id"].isin(down_match_ids)) &
        (rounds_df["round_num"] > 3) &
        (rounds_df["round_num"] <= 12)
    ]
    
    total = len(subsequent_rounds)
    losses = len(subsequent_rounds[subsequent_rounds["winner"] == "opponent"])
    
    return MetricResult(
        value=_safe_divide(losses, total),
        numerator=losses,
        denominator=total,
        confidence=_get_confidence(total),
        evidence_df=subsequent_rounds,
        meta={"condition": "Down 0-2 at round 3"},
    )


def compute_loss_patterns(
    rounds_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    events_df: Optional[pd.DataFrame],
    team_name: str,
) -> dict[str, MetricResult]:
    """Compute all loss pattern metrics."""
    return {
        "after_pistol_loss": compute_loss_after_pistol(rounds_df, matches_df, team_name),
        "after_first_blood_loss": compute_loss_after_first_blood(rounds_df, events_df, team_name),
        "when_down_early": compute_loss_when_down_early(rounds_df, team_name),
    }


# ============================================================================
# Trend Analysis
# ============================================================================

def compute_trend_metrics(
    matches_df: pd.DataFrame,
    rounds_df: pd.DataFrame,
    players_df: pd.DataFrame,
    team_name: str,
) -> dict[str, dict[str, MetricResult]]:
    """
    Compute metrics for last_3 and last_10 matches to detect trends.
    
    Returns nested dict: {metric_name: {period: MetricResult}}
    """
    if matches_df.empty:
        return {}
    
    # Sort by date and get last N matches
    team_matches = matches_df[matches_df["team_name"].str.lower() == team_name.lower()].copy()
    
    if "date" in team_matches.columns:
        team_matches = team_matches.sort_values("date", ascending=False)
    
    results = {}
    
    for period, n in [("last_3", 3), ("last_10", 10)]:
        period_matches = team_matches.head(n)
        period_match_ids = period_matches["match_id"].unique()
        
        # Filter rounds and players to this period
        period_rounds = rounds_df[rounds_df["match_id"].isin(period_match_ids)].copy()
        period_players = players_df[players_df["match_id"].isin(period_match_ids)].copy()
        
        # Compute metrics for this period
        win_rate = compute_overall_win_rate(period_matches, team_name)
        pistol = compute_pistol_win_rate(period_rounds, team_name)
        attack, defense = compute_side_win_rates(period_rounds, team_name)
        
        if "win_rate" not in results:
            results["win_rate"] = {}
        if "pistol" not in results:
            results["pistol"] = {}
        if "attack" not in results:
            results["attack"] = {}
        if "defense" not in results:
            results["defense"] = {}
        
        results["win_rate"][period] = win_rate
        results["pistol"][period] = pistol
        results["attack"][period] = attack
        results["defense"][period] = defense
    
    return results


def compute_trend_shift(
    trend_metrics: dict[str, dict[str, MetricResult]],
    min_change: float = 0.15,
) -> dict[str, dict[str, Any]]:
    """
    Compute trend shifts between last_3 and last_10.
    
    Returns dict of significant shifts with direction and magnitude.
    """
    shifts = {}
    
    for metric_name, periods in trend_metrics.items():
        if "last_3" not in periods or "last_10" not in periods:
            continue
        
        last_3 = periods["last_3"]
        last_10 = periods["last_10"]
        
        # Need sufficient sample size
        if last_3.denominator < 3 or last_10.denominator < 5:
            continue
        
        change = last_3.value - last_10.value
        
        if abs(change) >= min_change:
            shifts[metric_name] = {
                "last_3": last_3.value,
                "last_10": last_10.value,
                "change": change,
                "change_pct": change * 100,
                "direction": "improving" if change > 0 else "declining",
                "significance": "high" if abs(change) >= 0.25 else "medium",
            }
    
    return shifts


# ============================================================================
# Meta Comparison
# ============================================================================

def compute_meta_baseline(
    all_matches_df: pd.DataFrame,
    all_rounds_df: pd.DataFrame,
) -> dict[str, float]:
    """
    Compute tournament-wide baseline metrics.
    
    This would typically use data from all teams in the tournament.
    """
    if all_matches_df.empty:
        return {}
    
    # Basic baseline metrics
    total_matches = len(all_matches_df)
    
    baseline = {
        "win_rate": 0.5,  # By definition
        "pistol_win_rate": 0.5,
        "attack_win_rate": 0.5,
        "defense_win_rate": 0.5,
    }
    
    if not all_rounds_df.empty:
        pistol_rounds = all_rounds_df[all_rounds_df["pistol_round_bool"] == True]
        if len(pistol_rounds) > 0:
            baseline["pistol_win_rate"] = 0.5
        
        attack_rounds = all_rounds_df[all_rounds_df["side"].isin(["attack", "Attack"])]
        if len(attack_rounds) > 0:
            baseline["attack_win_rate"] = len(attack_rounds[attack_rounds["winner"] == "team"]) / len(attack_rounds)
    
    return baseline


def compare_to_meta(
    team_metrics: AllMetrics,
    meta_baseline: dict[str, float],
) -> dict[str, MetricResult]:
    """
    Compare team metrics to meta baseline.
    
    Returns metrics with meta containing comparison info.
    """
    comparisons = {}
    
    # Win rate comparison
    if "win_rate" in meta_baseline:
        diff = team_metrics.overall_win_rate.value - meta_baseline["win_rate"]
        comparisons["win_rate"] = MetricResult(
            value=diff,
            numerator=int(diff * 100),
            denominator=100,
            confidence=team_metrics.overall_win_rate.confidence,
            meta={
                "team": team_metrics.overall_win_rate.value,
                "baseline": meta_baseline["win_rate"],
                "relative": "above" if diff > 0 else "below",
            },
        )
    
    # Pistol comparison
    if "pistol_win_rate" in meta_baseline:
        diff = team_metrics.pistol_win_rate.value - meta_baseline["pistol_win_rate"]
        comparisons["pistol"] = MetricResult(
            value=diff,
            numerator=int(diff * 100),
            denominator=100,
            confidence=team_metrics.pistol_win_rate.confidence,
            meta={
                "team": team_metrics.pistol_win_rate.value,
                "baseline": meta_baseline["pistol_win_rate"],
                "relative": "above" if diff > 0 else "below",
            },
        )
    
    return comparisons


# ============================================================================
# Main Entry Point
# ============================================================================

def compute_all_metrics(
    data: NormalizedData,
    team_name: str,
) -> AllMetrics:
    """
    Compute all metrics for a team.
    
    This is the main entry point for metrics computation.
    """
    matches_df = data.matches_df
    players_df = data.players_df
    rounds_df = data.rounds_df
    events_df = data.events_df
    
    # Filter to team's data
    if not matches_df.empty:
        team_matches = matches_df[matches_df["team_name"].str.lower() == team_name.lower()].copy()
        match_ids = team_matches["match_id"].unique()
        team_rounds = rounds_df[rounds_df["match_id"].isin(match_ids)].copy() if not rounds_df.empty else pd.DataFrame()
        team_players = players_df[players_df["is_our_team"] == True].copy() if not players_df.empty else pd.DataFrame()
    else:
        team_matches = pd.DataFrame()
        team_rounds = pd.DataFrame()
        team_players = pd.DataFrame()
    
    # Compute all metrics
    overall_win_rate = compute_overall_win_rate(team_matches, team_name)
    map_win_rates = compute_map_win_rates(team_matches, team_name)
    attack_win_rate, defense_win_rate = compute_side_win_rates(team_rounds, team_name)
    pistol_win_rate = compute_pistol_win_rate(team_rounds, team_name)
    eco_conversion_rate = compute_eco_conversion_rate(team_rounds, team_name)
    
    player_first_blood_rates = compute_player_first_blood_rates(team_players, team_name)
    player_first_death_rates = compute_player_first_death_rates(team_players, team_name)
    player_agent_picks = compute_player_agent_picks(team_players, team_name)
    player_acs = compute_player_acs(team_players, team_name)
    
    loss_patterns = compute_loss_patterns(team_rounds, team_matches, events_df, team_name)
    trend_metrics = compute_trend_metrics(team_matches, team_rounds, team_players, team_name)
    
    # Meta comparison (using default baseline for now)
    meta_baseline = {"win_rate": 0.5, "pistol_win_rate": 0.5}
    
    return AllMetrics(
        team_name=team_name,
        matches_analyzed=len(team_matches),
        overall_win_rate=overall_win_rate,
        map_win_rates=map_win_rates,
        attack_win_rate=attack_win_rate,
        defense_win_rate=defense_win_rate,
        pistol_win_rate=pistol_win_rate,
        eco_conversion_rate=eco_conversion_rate,
        player_first_blood_rates=player_first_blood_rates,
        player_first_death_rates=player_first_death_rates,
        player_agent_picks=player_agent_picks,
        player_acs=player_acs,
        loss_patterns=loss_patterns,
        trend_metrics=trend_metrics,
        meta_comparison={},
    )
