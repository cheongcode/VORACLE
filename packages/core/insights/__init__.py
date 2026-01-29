"""
Insight Generation Module

Rule-based engine for generating actionable scouting insights.
"""

from .generator import (
    generate_insights,
    generate_how_to_beat,
    generate_what_not_to_do,
    generate_map_veto_recommendations,
)
from .rules import InsightResult, EvidenceRef, ALL_RULES

__all__ = [
    "generate_insights",
    "generate_how_to_beat",
    "generate_what_not_to_do",
    "generate_map_veto_recommendations",
    "InsightResult",
    "EvidenceRef",
    "ALL_RULES",
]
