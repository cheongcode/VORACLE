"""
Insight Generation Engine

Runs all rules, deduplicates, ranks by impact, and generates actionable checklists.
"""
from __future__ import annotations

import logging
from typing import Optional

from ..metrics.valorant import AllMetrics
from ..normalize.valorant import NormalizedData
from .rules import ALL_RULES, InsightResult

logger = logging.getLogger(__name__)

# Configuration
MIN_INSIGHTS = 6
MAX_INSIGHTS = 12


def generate_insights(
    metrics: AllMetrics,
    data: NormalizedData,
    min_insights: int = MIN_INSIGHTS,
    max_insights: int = MAX_INSIGHTS,
) -> list[InsightResult]:
    """
    Generate insights by running all rules against team metrics.
    
    This function:
    1. Runs all rule functions
    2. Filters out None results
    3. Deduplicates by similarity
    4. Ranks by impact score
    5. Returns between min_insights and max_insights insights
    
    Args:
        metrics: Computed metrics for the team.
        data: Normalized match data.
        min_insights: Minimum number of insights to return.
        max_insights: Maximum number of insights to return.
        
    Returns:
        List of InsightResult objects, ranked by importance.
    """
    insights: list[InsightResult] = []
    
    # Run all rules
    for rule in ALL_RULES:
        try:
            result = rule(metrics, data)
            if result is not None:
                insights.append(result)
                logger.debug(f"Rule {rule.__name__} generated insight: {result.title}")
        except Exception as e:
            logger.warning(f"Rule {rule.__name__} failed: {e}")
            continue
    
    logger.info(f"Generated {len(insights)} raw insights")
    
    # Deduplicate
    insights = deduplicate_insights(insights)
    logger.info(f"After deduplication: {len(insights)} insights")
    
    # Rank by impact
    insights = rank_insights(insights)
    
    # Ensure we have at least min_insights (pad with lower priority if needed)
    # and at most max_insights
    insights = insights[:max_insights]
    
    logger.info(f"Final insight count: {len(insights)}")
    return insights


def deduplicate_insights(insights: list[InsightResult]) -> list[InsightResult]:
    """
    Remove similar insights based on title similarity and category overlap.
    
    Keeps the insight with higher impact score when duplicates are found.
    """
    if not insights:
        return insights
    
    # Group by category first
    seen_titles = set()
    seen_categories = {}
    unique = []
    
    # Sort by impact score descending to keep best version
    sorted_insights = sorted(insights, key=lambda x: x.impact_score, reverse=True)
    
    for insight in sorted_insights:
        # Check title similarity
        title_key = _normalize_title(insight.title)
        
        if title_key in seen_titles:
            continue
        
        # Check category limits (max 3 per category)
        category = insight.category
        if category in seen_categories and seen_categories[category] >= 3:
            continue
        
        seen_titles.add(title_key)
        seen_categories[category] = seen_categories.get(category, 0) + 1
        unique.append(insight)
    
    return unique


def _normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    # Remove player/map names and lowercase
    words = title.lower().split()
    # Keep key action words
    key_words = [w for w in words if w in (
        "weak", "strong", "force", "ban", "target", "collapse",
        "declining", "improving", "reliance", "below", "above",
        "pistol", "eco", "attack", "defense", "trend", "map"
    )]
    return " ".join(key_words) if key_words else title.lower()


def rank_insights(insights: list[InsightResult]) -> list[InsightResult]:
    """
    Sort insights by impact score with severity as tiebreaker.
    """
    severity_order = {"HIGH": 3, "MED": 2, "LOW": 1}
    
    return sorted(
        insights,
        key=lambda x: (
            x.impact_score,
            severity_order.get(x.severity, 0),
        ),
        reverse=True,
    )


def generate_how_to_beat(
    insights: list[InsightResult],
    max_items: int = 6,
) -> list[str]:
    """
    Generate "How to Beat Them" checklist from top insights.
    
    Extracts the most actionable recommendations from high-impact insights.
    """
    recommendations: list[str] = []
    seen = set()
    
    # Prioritize HIGH severity
    high_severity = [i for i in insights if i.severity == "HIGH"]
    med_severity = [i for i in insights if i.severity == "MED"]
    
    for insight in high_severity + med_severity:
        if len(recommendations) >= max_items:
            break
        
        rec = insight.recommendation
        if rec and rec not in seen:
            # Clean up recommendation
            rec = rec.strip()
            if not rec.endswith("."):
                rec += "."
            
            recommendations.append(rec)
            seen.add(rec)
    
    return recommendations


def generate_what_not_to_do(
    insights: list[InsightResult],
    max_items: int = 4,
) -> list[str]:
    """
    Extract warnings from insights with what_not_to_do field.
    """
    warnings: list[str] = []
    seen = set()
    
    for insight in insights:
        if len(warnings) >= max_items:
            break
        
        if insight.what_not_to_do:
            warning = insight.what_not_to_do.strip()
            if not warning.endswith("."):
                warning += "."
            
            if warning not in seen:
                warnings.append(warning)
                seen.add(warning)
    
    return warnings


def categorize_insights(
    insights: list[InsightResult],
) -> dict[str, list[InsightResult]]:
    """
    Group insights by category.
    """
    categories: dict[str, list[InsightResult]] = {}
    
    for insight in insights:
        category = insight.category or "general"
        if category not in categories:
            categories[category] = []
        categories[category].append(insight)
    
    return categories


def get_trend_alerts(
    insights: list[InsightResult],
) -> list[InsightResult]:
    """
    Extract trend-related insights for the trend alerts section.
    """
    return [i for i in insights if i.category == "trend"]


def get_map_veto_insights(
    insights: list[InsightResult],
) -> list[InsightResult]:
    """
    Extract map veto insights for the map recommendations section.
    """
    return [i for i in insights if i.category == "map_veto"]


def generate_map_veto_recommendations(
    metrics: AllMetrics,
    insights: list[InsightResult],
) -> list[dict]:
    """
    Generate structured map veto recommendations.
    
    Returns list of {map_name, recommendation, win_rate, games, confidence}.
    """
    recommendations = []
    
    for map_name, map_metric in metrics.map_win_rates.items():
        rec = {
            "map_name": map_name,
            "win_rate": map_metric.value,
            "games": map_metric.denominator,
            "wins": map_metric.numerator,
            "confidence": map_metric.confidence,
            "recommendation": map_metric.meta.get("suggestion", "NEUTRAL"),
        }
        recommendations.append(rec)
    
    # Sort by recommendation priority (BAN/PICK first) then by impact
    priority = {"BAN": 3, "PICK": 2, "NEUTRAL": 1, "LOW_SAMPLE": 0}
    recommendations.sort(
        key=lambda x: (priority.get(x["recommendation"], 0), abs(x["win_rate"] - 0.5)),
        reverse=True,
    )
    
    return recommendations


def compute_insight_summary(
    insights: list[InsightResult],
) -> dict:
    """
    Compute summary statistics about generated insights.
    """
    if not insights:
        return {
            "total": 0,
            "by_severity": {},
            "by_category": {},
            "avg_impact": 0,
        }
    
    by_severity = {}
    by_category = {}
    
    for insight in insights:
        by_severity[insight.severity] = by_severity.get(insight.severity, 0) + 1
        by_category[insight.category] = by_category.get(insight.category, 0) + 1
    
    avg_impact = sum(i.impact_score for i in insights) / len(insights)
    
    return {
        "total": len(insights),
        "by_severity": by_severity,
        "by_category": by_category,
        "avg_impact": round(avg_impact, 3),
    }
