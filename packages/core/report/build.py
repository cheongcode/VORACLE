"""
Report Builder

Orchestrates the full scouting report generation pipeline:
GRID API → Normalize → Metrics → Insights → Report
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..grid.client import GRIDClient, GRIDClientError
from ..grid.mock_data import get_mock_matches
from ..insights.generator import (
    generate_insights,
    generate_how_to_beat,
    generate_what_not_to_do,
    generate_map_veto_recommendations,
    get_trend_alerts,
    compute_insight_summary,
)
from ..insights.rules import InsightResult
from ..metrics.valorant import AllMetrics, compute_all_metrics, compute_trend_shift
from ..normalize.valorant import NormalizedData, normalize_mock_data, normalize_all, normalize_match_list, normalize_match_detail
from .models import (
    AgentStats,
    DataFrameInfo,
    DebugReport,
    EconomyStats,
    EvidenceRef,
    KeyInsight,
    MapStats,
    MapVeto,
    PlayerStats,
    ScoutingReport,
    SideStats,
    TeamCapabilities,
    TeamSummary,
    TrendAlert,
)

logger = logging.getLogger(__name__)


def _build_team_summary(metrics: AllMetrics, data: NormalizedData) -> TeamSummary:
    """Build team summary from metrics."""
    matches_df = data.matches_df
    
    # Get date range
    date_range = "N/A"
    if not matches_df.empty and "date" in matches_df.columns:
        dates = matches_df["date"].dropna()
        if len(dates) > 0:
            min_date = dates.min()
            max_date = dates.max()
            if hasattr(min_date, "strftime"):
                date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
    
    return TeamSummary(
        name=metrics.team_name,
        matches_analyzed=metrics.matches_analyzed,
        overall_win_rate=metrics.overall_win_rate.value,
        date_range=date_range,
    )


def _build_trend_alerts(metrics: AllMetrics) -> list[TrendAlert]:
    """Build trend alerts from metrics."""
    alerts = []
    
    # Compute trend shifts
    shifts = compute_trend_shift(metrics.trend_metrics)
    
    for metric_name, shift_data in shifts.items():
        alerts.append(TrendAlert(
            metric=metric_name,
            last_3=shift_data["last_3"],
            last_10=shift_data["last_10"],
            change_pct=shift_data["change_pct"],
            direction=shift_data["direction"],
            significance=shift_data["significance"].upper(),
        ))
    
    return alerts


def _build_map_veto(metrics: AllMetrics, insights: list[InsightResult]) -> list[MapVeto]:
    """Build map veto recommendations."""
    vetos = []
    
    for map_name, map_metric in metrics.map_win_rates.items():
        suggestion = map_metric.meta.get("suggestion", "NEUTRAL")
        
        vetos.append(MapVeto(
            map_name=map_name,
            recommendation=suggestion,
            win_rate=map_metric.value,
            games=map_metric.denominator,
            wins=map_metric.numerator,
            confidence=map_metric.confidence,
        ))
    
    # Sort by recommendation priority
    priority = {"BAN": 3, "PICK": 2, "NEUTRAL": 1, "LOW_SAMPLE": 0}
    vetos.sort(key=lambda x: (priority.get(x.recommendation, 0), abs(x.win_rate - 0.5)), reverse=True)
    
    return vetos


def _build_map_stats(metrics: AllMetrics) -> list[MapStats]:
    """Build map statistics."""
    stats = []
    
    for map_name, map_metric in metrics.map_win_rates.items():
        wins = map_metric.numerator
        total = map_metric.denominator
        losses = total - wins
        
        stats.append(MapStats(
            map_name=map_name,
            games=total,
            wins=wins,
            losses=losses,
            win_rate=map_metric.value,
        ))
    
    stats.sort(key=lambda x: x.games, reverse=True)
    return stats


def _build_side_stats(metrics: AllMetrics) -> list[SideStats]:
    """Build side performance statistics."""
    return [
        SideStats(
            side="attack",
            rounds_played=metrics.attack_win_rate.denominator,
            rounds_won=metrics.attack_win_rate.numerator,
            win_rate=metrics.attack_win_rate.value,
        ),
        SideStats(
            side="defense",
            rounds_played=metrics.defense_win_rate.denominator,
            rounds_won=metrics.defense_win_rate.numerator,
            win_rate=metrics.defense_win_rate.value,
        ),
    ]


def _build_economy_stats(metrics: AllMetrics) -> EconomyStats:
    """Build economy statistics."""
    return EconomyStats(
        pistol_rounds=metrics.pistol_win_rate.denominator,
        pistol_wins=metrics.pistol_win_rate.numerator,
        pistol_win_rate=metrics.pistol_win_rate.value,
        eco_rounds=metrics.eco_conversion_rate.denominator,
        eco_wins=metrics.eco_conversion_rate.numerator,
        eco_conversion_rate=metrics.eco_conversion_rate.value,
    )


def _build_player_stats(metrics: AllMetrics, data: NormalizedData) -> list[PlayerStats]:
    """Build player statistics."""
    players_df = data.players_df
    team_players = players_df[players_df["is_our_team"] == True] if not players_df.empty else players_df
    
    player_stats = []
    
    for player_name in team_players["player_name"].unique() if not team_players.empty else []:
        player_data = team_players[team_players["player_name"] == player_name]
        
        if player_data.empty:
            continue
        
        games = len(player_data)
        
        # Get agent picks
        agent_picks = metrics.player_agent_picks.get(player_name, {})
        if agent_picks:
            most_played = max(agent_picks.items(), key=lambda x: x[1].numerator)
            most_played_agent = most_played[0]
            
            agent_pool = [
                AgentStats(
                    agent_name=agent,
                    games=pick.numerator,
                    pick_rate=pick.value,
                )
                for agent, pick in agent_picks.items()
            ]
            agent_pool.sort(key=lambda x: x.games, reverse=True)
        else:
            most_played_agent = player_data["agent"].mode().iloc[0] if not player_data.empty else "Unknown"
            agent_pool = []
        
        # Calculate averages
        avg_acs = player_data["acs"].mean() if "acs" in player_data.columns else 0.0
        avg_kills = player_data["kills"].mean() if "kills" in player_data.columns else 0.0
        avg_deaths = player_data["deaths"].mean() if "deaths" in player_data.columns else 0.0
        avg_assists = player_data["assists"].mean() if "assists" in player_data.columns else 0.0
        
        # K/D ratio
        total_kills = player_data["kills"].sum() if "kills" in player_data.columns else 0
        total_deaths = player_data["deaths"].sum() if "deaths" in player_data.columns else 0
        kd_ratio = total_kills / max(1, total_deaths)
        
        # First blood rates
        fb_metric = metrics.player_first_blood_rates.get(player_name)
        fb_rate = fb_metric.value if fb_metric else 0.0
        
        fd_metric = metrics.player_first_death_rates.get(player_name)
        fd_rate = fd_metric.value if fd_metric else 0.0
        
        player_stats.append(PlayerStats(
            name=player_name,
            games=games,
            most_played_agent=most_played_agent,
            agent_pool=agent_pool[:3],
            avg_acs=round(float(avg_acs) if avg_acs else 0, 1),
            avg_kills=round(float(avg_kills) if avg_kills else 0, 1),
            avg_deaths=round(float(avg_deaths) if avg_deaths else 0, 1),
            avg_assists=round(float(avg_assists) if avg_assists else 0, 1),
            kd_ratio=round(kd_ratio, 2),
            first_blood_rate=round(fb_rate, 2),
            first_death_rate=round(fd_rate, 2),
        ))
    
    player_stats.sort(key=lambda x: x.avg_acs, reverse=True)
    return player_stats


def _build_capabilities(metrics: AllMetrics) -> TeamCapabilities:
    """Build radar chart capabilities data."""
    import statistics
    
    # Pistol: scaled 0-100
    pistol = min(100, max(0, metrics.pistol_win_rate.value * 100))
    
    # Economy: based on eco conversion
    eco_base = metrics.eco_conversion_rate.value
    economy = min(100, max(0, (eco_base / 0.30) * 100))
    
    # First bloods: based on average team FB rate
    fb_rates = [m.value for m in metrics.player_first_blood_rates.values()]
    avg_fb = sum(fb_rates) / len(fb_rates) if fb_rates else 0
    first_bloods = min(100, max(0, (avg_fb / 3.0) * 100))
    
    # Attack/Defense
    attack = min(100, max(0, metrics.attack_win_rate.value * 100))
    defense = min(100, max(0, metrics.defense_win_rate.value * 100))
    
    # Consistency: based on map win rate variance
    map_rates = [m.value for m in metrics.map_win_rates.values()]
    if len(map_rates) >= 2:
        variance = statistics.variance(map_rates)
        consistency = min(100, max(0, (1 - variance) * 100))
    else:
        consistency = 50
    
    return TeamCapabilities(
        pistol=round(pistol, 1),
        economy=round(economy, 1),
        first_bloods=round(first_bloods, 1),
        attack=round(attack, 1),
        defense=round(defense, 1),
        consistency=round(consistency, 1),
    )


def _build_key_insights(insights: list[InsightResult]) -> list[KeyInsight]:
    """Convert InsightResult to KeyInsight models."""
    return [
        KeyInsight(
            title=i.title,
            severity=i.severity,
            confidence=i.confidence,
            data_point=i.data_point,
            interpretation=i.interpretation,
            recommendation=i.recommendation,
            what_not_to_do=i.what_not_to_do,
            evidence_refs=[
                EvidenceRef(
                    table=e.table,
                    filters=e.filters,
                    sample_rows=e.sample_rows,
                )
                for e in i.evidence_refs
            ],
            impact_score=i.impact_score,
            category=i.category,
        )
        for i in insights
    ]


def _build_evidence_tables(data: NormalizedData, max_rows: int = 10) -> dict[str, list[dict]]:
    """Build evidence tables for UI evidence drawer."""
    tables = {}
    
    if not data.matches_df.empty:
        tables["matches"] = data.matches_df.head(max_rows).to_dict("records")
    
    if not data.players_df.empty:
        tables["players"] = data.players_df.head(max_rows).to_dict("records")
    
    if not data.rounds_df.empty:
        tables["rounds"] = data.rounds_df.head(max_rows).to_dict("records")
    
    return tables


def _load_query(name: str) -> str:
    """Load a GraphQL query from file."""
    query_path = Path(__file__).parent.parent / "grid" / "queries" / "valorant" / f"{name}.graphql"
    if query_path.exists():
        return query_path.read_text()
    raise FileNotFoundError(f"Query file not found: {query_path}")


async def _fetch_grid_data(
    team_name: str,
    n_matches: int,
) -> NormalizedData:
    """
    Fetch data from GRID API and normalize it.
    """
    logger.info(f"Fetching GRID data for {team_name}")
    
    async with GRIDClient() as client:
        # Load queries
        match_list_query = _load_query("match_list")
        match_detail_query = _load_query("match_detail")
        
        # Fetch match list
        match_list_raw = await client.query(
            "match_list",
            match_list_query,
            {"teamName": team_name, "first": n_matches},
        )
        
        # Normalize match list to get match IDs
        matches_df = normalize_match_list(match_list_raw, team_name)
        
        if matches_df.empty:
            logger.warning(f"No matches found for team: {team_name}")
            raise ValueError(f"No matches found for team: {team_name}")
        
        # Fetch match details for each match
        match_ids = matches_df["match_id"].unique()[:n_matches]
        logger.info(f"Fetching details for {len(match_ids)} matches")
        
        match_details = []
        for match_id in match_ids:
            try:
                detail = await client.query(
                    f"match_detail_{match_id}",
                    match_detail_query,
                    {"matchId": match_id},
                )
                match_details.append(detail)
            except GRIDClientError as e:
                logger.warning(f"Failed to fetch match {match_id}: {e}")
                continue
        
        if not match_details:
            logger.warning("No match details fetched, falling back to match list only")
        
        # Normalize all data
        data = normalize_all(match_list_raw, match_details, team_name)
        
        return data


async def build_report(
    team_name: str,
    n_matches: int = 10,
    use_mock: bool = False,
) -> ScoutingReport:
    """
    Build a complete scouting report for a team.
    
    This is the main entry point for report generation.
    """
    logger.info(f"Building report for {team_name} with {n_matches} matches (mock={use_mock})")
    
    # Step 1: Fetch data
    if use_mock:
        raw_matches = get_mock_matches(team_name, n_matches)
        data = normalize_mock_data(raw_matches, team_name)
    else:
        # Fetch from GRID API
        try:
            data = await _fetch_grid_data(team_name, n_matches)
        except (GRIDClientError, ValueError) as e:
            logger.warning(f"GRID API fetch failed: {e}. Falling back to mock data.")
            raw_matches = get_mock_matches(team_name, n_matches)
            data = normalize_mock_data(raw_matches, team_name)
    
    # Step 2: Compute metrics
    metrics = compute_all_metrics(data, team_name)
    
    # Step 3: Generate insights
    insights = generate_insights(metrics, data)
    how_to_beat = generate_how_to_beat(insights)
    what_not_to_do = generate_what_not_to_do(insights)
    
    # Step 4: Build report
    report = ScoutingReport(
        generated_at=datetime.now(),
        team_summary=_build_team_summary(metrics, data),
        trend_alerts=_build_trend_alerts(metrics),
        map_veto=_build_map_veto(metrics, insights),
        map_performance=_build_map_stats(metrics),
        side_performance=_build_side_stats(metrics),
        economy_stats=_build_economy_stats(metrics),
        player_stats=_build_player_stats(metrics, data),
        capabilities=_build_capabilities(metrics),
        key_insights=_build_key_insights(insights),
        how_to_beat=how_to_beat,
        what_not_to_do=what_not_to_do,
        evidence_tables=_build_evidence_tables(data),
        meta={
            "data_source": "mock" if use_mock else "grid",
            "matches_requested": n_matches,
            "matches_found": len(data.matches_df),
            "insight_summary": compute_insight_summary(insights),
        },
    )
    
    logger.info(f"Report built: {len(insights)} insights, {len(how_to_beat)} recommendations")
    return report


async def build_debug_report(
    team_name: str,
    n_matches: int = 10,
    use_mock: bool = True,
) -> DebugReport:
    """
    Build a debug report with raw DataFrame info.
    """
    logger.info(f"Building debug report for {team_name}")
    
    errors = []
    
    try:
        # Fetch and normalize data
        if use_mock:
            raw_matches = get_mock_matches(team_name, n_matches)
            data = normalize_mock_data(raw_matches, team_name)
        else:
            raw_matches = get_mock_matches(team_name, n_matches)
            data = normalize_mock_data(raw_matches, team_name)
        
        # Compute metrics
        metrics = compute_all_metrics(data, team_name)
        
        # Generate insights
        insights = generate_insights(metrics, data)
        
    except Exception as e:
        errors.append(str(e))
        data = NormalizedData(
            matches_df=__import__("pandas").DataFrame(),
            players_df=__import__("pandas").DataFrame(),
            rounds_df=__import__("pandas").DataFrame(),
        )
        metrics = None
        insights = []
    
    # Build DataFrame info
    dataframes = []
    
    for name, df in [
        ("matches_df", data.matches_df),
        ("players_df", data.players_df),
        ("rounds_df", data.rounds_df),
        ("events_df", data.events_df),
        ("economy_df", data.economy_df),
        ("picks_df", data.picks_df),
    ]:
        if df is not None and not df.empty:
            dataframes.append(DataFrameInfo(
                name=name,
                shape=(len(df), len(df.columns)),
                columns=list(df.columns),
                sample_rows=df.head(5).to_dict("records"),
                dtypes={str(k): str(v) for k, v in df.dtypes.items()},
            ))
    
    return DebugReport(
        team_name=team_name,
        generated_at=datetime.now(),
        dataframes=dataframes,
        metrics_summary={
            "matches_analyzed": metrics.matches_analyzed if metrics else 0,
            "win_rate": metrics.overall_win_rate.value if metrics else 0,
        },
        insight_summary=compute_insight_summary(insights),
        errors=errors,
    )
