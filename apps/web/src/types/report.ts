/**
 * TypeScript types for VORACLE scouting reports.
 * These match the Pydantic models from the backend.
 */

// Evidence
export interface EvidenceRef {
  table: string;
  filters: Record<string, any>;
  sample_rows: Record<string, any>[];
}

// Insights
export interface KeyInsight {
  title: string;
  severity: 'HIGH' | 'MED' | 'LOW';
  confidence: 'high' | 'medium' | 'low';
  data_point: string;
  interpretation: string;
  recommendation: string;
  what_not_to_do: string | null;
  evidence_refs: EvidenceRef[];
  impact_score: number;
  category: string;
}

export interface TrendAlert {
  metric: string;
  last_3: number;
  last_10: number;
  change_pct: number;
  direction: 'improving' | 'declining';
  significance: 'HIGH' | 'MED' | 'LOW';
}

// Team
export interface TeamSummary {
  name: string;
  matches_analyzed: number;
  overall_win_rate: number;
  date_range: string;
}

// Agent
export interface AgentStats {
  agent_name: string;
  games: number;
  pick_rate: number;
}

// Player
export interface PlayerStats {
  name: string;
  games: number;
  most_played_agent: string;
  agent_pool: AgentStats[];
  avg_acs: number;
  avg_kills: number;
  avg_deaths: number;
  avg_assists: number;
  kd_ratio: number;
  first_blood_rate: number;
  first_death_rate: number;
}

// Map
export interface MapVeto {
  map_name: string;
  recommendation: 'BAN' | 'PICK' | 'NEUTRAL' | 'LOW_SAMPLE';
  win_rate: number;
  games: number;
  wins: number;
  confidence: string;
}

export interface MapStats {
  map_name: string;
  games: number;
  wins: number;
  losses: number;
  win_rate: number;
  avg_rounds_won: number;
  avg_rounds_lost: number;
}

// Side
export interface SideStats {
  side: 'attack' | 'defense';
  rounds_played: number;
  rounds_won: number;
  win_rate: number;
}

// Economy
export interface EconomyStats {
  pistol_rounds: number;
  pistol_wins: number;
  pistol_win_rate: number;
  eco_rounds: number;
  eco_wins: number;
  eco_conversion_rate: number;
}

// Capabilities
export interface TeamCapabilities {
  pistol: number;
  economy: number;
  first_bloods: number;
  attack: number;
  defense: number;
  consistency: number;
}

// Main Report
export interface ScoutingReport {
  generated_at: string;
  team_summary: TeamSummary;
  trend_alerts: TrendAlert[];
  map_veto: MapVeto[];
  map_performance: MapStats[];
  side_performance: SideStats[];
  economy_stats: EconomyStats | null;
  player_stats: PlayerStats[];
  capabilities: TeamCapabilities;
  key_insights: KeyInsight[];
  how_to_beat: string[];
  what_not_to_do: string[];
  evidence_tables: Record<string, Record<string, any>[]>;
  meta: Record<string, any>;
}

// Debug Report
export interface DataFrameInfo {
  name: string;
  shape: [number, number];
  columns: string[];
  sample_rows: Record<string, any>[];
  dtypes: Record<string, string>;
}

export interface DebugReport {
  team_name: string;
  generated_at: string;
  dataframes: DataFrameInfo[];
  metrics_summary: Record<string, any>;
  insight_summary: Record<string, any>;
  errors: string[];
}

// Legacy types for backward compatibility
export interface Insight {
  title: string;
  data_point: string;
  interpretation: string;
  recommendation: string;
  confidence: string;
  evidence_ref: string;
  category: string;
  impact: string;
}

export interface TeamOverview {
  name: string;
  matches_analyzed: number;
  overall_win_rate: number;
  date_range: string;
}
