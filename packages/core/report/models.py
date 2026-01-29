"""
Pydantic Models for VORACLE Scouting Reports

Complete report structure with evidence refs and all sections.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Evidence Models
# ============================================================================

class EvidenceRef(BaseModel):
    """Reference to evidence supporting an insight."""
    table: str
    filters: dict[str, Any] = Field(default_factory=dict)
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# Insight Models
# ============================================================================

class KeyInsight(BaseModel):
    """A single scouting insight with evidence."""
    title: str
    severity: str  # HIGH, MED, LOW
    confidence: str  # high, medium, low
    data_point: str
    interpretation: str
    recommendation: str
    what_not_to_do: Optional[str] = None
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    impact_score: float = 0.0
    category: str = "general"


class TrendAlert(BaseModel):
    """Alert for significant trend changes."""
    metric: str
    last_3: float
    last_10: float
    change_pct: float
    direction: str  # "improving" | "declining"
    significance: str  # HIGH, MED, LOW


# ============================================================================
# Team & Player Models
# ============================================================================

class TeamSummary(BaseModel):
    """High-level team information."""
    name: str
    matches_analyzed: int
    overall_win_rate: float
    date_range: str


class AgentStats(BaseModel):
    """Statistics for an agent pick."""
    agent_name: str
    games: int
    pick_rate: float


class PlayerStats(BaseModel):
    """Performance statistics for a single player."""
    name: str
    games: int
    most_played_agent: str
    agent_pool: list[AgentStats] = Field(default_factory=list)
    avg_acs: float
    avg_kills: float = 0.0
    avg_deaths: float = 0.0
    avg_assists: float = 0.0
    kd_ratio: float = 0.0
    first_blood_rate: float = 0.0
    first_death_rate: float = 0.0


# ============================================================================
# Map & Side Models
# ============================================================================

class MapVeto(BaseModel):
    """Map veto recommendation."""
    map_name: str
    recommendation: str  # BAN, PICK, NEUTRAL, LOW_SAMPLE
    win_rate: float
    games: int
    wins: int
    confidence: str


class MapStats(BaseModel):
    """Performance statistics for a single map."""
    map_name: str
    games: int
    wins: int
    losses: int = 0
    win_rate: float
    avg_rounds_won: float = 0.0
    avg_rounds_lost: float = 0.0


class SideStats(BaseModel):
    """Performance statistics for a side."""
    side: str  # attack, defense
    rounds_played: int
    rounds_won: int
    win_rate: float


# ============================================================================
# Economy Models
# ============================================================================

class EconomyStats(BaseModel):
    """Economy-related statistics."""
    pistol_rounds: int
    pistol_wins: int
    pistol_win_rate: float
    eco_rounds: int
    eco_wins: int
    eco_conversion_rate: float


# ============================================================================
# Capability Models
# ============================================================================

class TeamCapabilities(BaseModel):
    """Radar chart data for team capabilities."""
    pistol: float = 50.0
    economy: float = 50.0
    first_bloods: float = 50.0
    attack: float = 50.0
    defense: float = 50.0
    consistency: float = 50.0


# ============================================================================
# Main Report Model
# ============================================================================

class ScoutingReport(BaseModel):
    """
    Complete scouting report for a team.
    
    This is the main output model containing all analysis results.
    """
    generated_at: datetime = Field(default_factory=datetime.now)
    
    # Team Summary
    team_summary: TeamSummary
    
    # Trend Alerts
    trend_alerts: list[TrendAlert] = Field(default_factory=list)
    
    # Map Analysis
    map_veto: list[MapVeto] = Field(default_factory=list)
    map_performance: list[MapStats] = Field(default_factory=list)
    
    # Side & Economy
    side_performance: list[SideStats] = Field(default_factory=list)
    economy_stats: Optional[EconomyStats] = None
    
    # Player Stats
    player_stats: list[PlayerStats] = Field(default_factory=list)
    
    # Capabilities (for radar chart)
    capabilities: TeamCapabilities = Field(default_factory=TeamCapabilities)
    
    # Insights
    key_insights: list[KeyInsight] = Field(default_factory=list)
    
    # Actionable Checklists
    how_to_beat: list[str] = Field(default_factory=list)
    what_not_to_do: list[str] = Field(default_factory=list)
    
    # Evidence Tables (for UI evidence drawer)
    evidence_tables: dict[str, list[dict]] = Field(default_factory=dict)
    
    # Metadata
    meta: dict = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


# ============================================================================
# Debug Models
# ============================================================================

class DataFrameInfo(BaseModel):
    """Debug info for a DataFrame."""
    name: str
    shape: tuple[int, int]
    columns: list[str]
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)
    dtypes: dict[str, str] = Field(default_factory=dict)


class DebugReport(BaseModel):
    """Debug report with raw DataFrame info."""
    team_name: str
    generated_at: datetime = Field(default_factory=datetime.now)
    dataframes: list[DataFrameInfo] = Field(default_factory=list)
    metrics_summary: dict[str, Any] = Field(default_factory=dict)
    insight_summary: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


# ============================================================================
# Legacy Compatibility
# ============================================================================

# For backward compatibility with existing code
class Insight(BaseModel):
    """Legacy insight model (deprecated, use KeyInsight)."""
    title: str
    data_point: str
    interpretation: str
    recommendation: str
    confidence: str = "medium"
    evidence_ref: str = ""
    category: str = "general"
    impact: str = "medium"


class TeamOverview(BaseModel):
    """Legacy team overview (deprecated, use TeamSummary)."""
    name: str
    matches_analyzed: int
    overall_win_rate: float
    date_range: str
