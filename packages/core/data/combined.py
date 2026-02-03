"""
Combined Data Layer

Fetches and combines data from GRID and VLR APIs for comprehensive coverage.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import pandas as pd
import numpy as np

from ..grid.valorant import (
    ValorantGridClient, GridSeries, GridTeam, GridSeriesDetail,
    GridMapResult, GridPlayerStats, GridMapVeto
)
from ..vlr.client import VlrClient, VlrMatch, VlrPlayerStats, VlrTeamRanking

logger = logging.getLogger(__name__)


# Team name aliases for matching across different data sources
# VLR uses abbreviations like "C9" while we search for "Cloud9"
TEAM_ALIASES = {
    "cloud9": ["c9", "cloud 9", "cloud nine"],
    "100 thieves": ["100t", "100thieves"],
    "evil geniuses": ["eg"],
    "g2 esports": ["g2", "g2esports"],
    "sentinels": ["sen"],
    "nrg": ["nrg esports"],
    "faze": ["faze clan"],
    "fnatic": ["fnc"],
    "team liquid": ["tl", "liquid"],
    "team vitality": ["vit", "vitality"],
    "karmine corp": ["kc", "karmine"],
    "loud": [],
    "leviatán": ["lev", "leviatan"],
    "kru": ["kru esports"],
    "drx": ["drx esports"],
    "t1": ["t1 esports"],
    "gen.g": ["geng", "gen g"],
    "paper rex": ["prx"],
    "rrq": ["rex regum qeon"],
}


def _matches_team_name(query: str, candidate: str) -> bool:
    """
    Check if a candidate string matches a team query with alias support.
    
    Args:
        query: The team name we're searching for (e.g., "Cloud9")
        candidate: The candidate name to check (e.g., "C9" from VLR)
        
    Returns:
        True if the candidate matches the query or any of its aliases.
    """
    if not query or not candidate:
        return False
        
    query_lower = query.lower().strip()
    candidate_lower = candidate.lower().strip()
    
    # Direct match (either contains the other)
    if query_lower in candidate_lower or candidate_lower in query_lower:
        return True
    
    # Check aliases for the query team
    for team_name, aliases in TEAM_ALIASES.items():
        # Check if query matches this team
        if query_lower in team_name or team_name in query_lower:
            # Check if candidate is an alias
            if candidate_lower in aliases:
                return True
            for alias in aliases:
                if alias in candidate_lower or candidate_lower in alias:
                    return True
        
        # Also check reverse - if candidate is the team name and query is an alias
        if candidate_lower in team_name or team_name in candidate_lower:
            if query_lower in aliases:
                return True
            for alias in aliases:
                if alias in query_lower or query_lower in alias:
                    return True
    
    return False


def _parse_record(record: str) -> tuple[int, int]:
    """
    Parse a W-L record string like "28-28" or "40–20" into wins and losses.
    
    Returns:
        Tuple of (wins, losses). Returns (0, 0) if parsing fails.
    """
    if not record:
        return (0, 0)
    
    # Handle different dash characters
    for sep in ["-", "–", "—", "−"]:
        if sep in record:
            parts = record.split(sep)
            if len(parts) == 2:
                try:
                    wins = int(parts[0].strip())
                    losses = int(parts[1].strip())
                    return (wins, losses)
                except ValueError:
                    pass
    
    return (0, 0)


@dataclass
class CombinedMatchData:
    """Combined match data from GRID and VLR."""
    match_id: str
    date: datetime
    map_name: str
    team_name: str
    opponent: str
    result: str  # "win" or "loss"
    score_us: int
    score_them: int
    event_name: str
    source: str  # "grid" or "vlr"


@dataclass
class CombinedPlayerData:
    """Combined player data."""
    player_name: str
    team: str
    agent: str
    acs: float
    kills: int
    deaths: int
    assists: int
    kd: float
    rating: float
    first_bloods: int
    first_deaths: int


@dataclass
class CombinedMapVeto:
    """Map veto action."""
    action: str  # "ban" or "pick"
    map_name: str
    team_name: str
    is_our_team: bool


@dataclass
class CombinedTeamData:
    """Combined team data from all sources."""
    team_id: str
    team_name: str
    team_short: Optional[str]
    logo_url: Optional[str]
    rank: Optional[str]
    record: Optional[str]
    earnings: Optional[str]
    matches: list[CombinedMatchData] = field(default_factory=list)
    players: list[CombinedPlayerData] = field(default_factory=list)
    map_veto: list[CombinedMapVeto] = field(default_factory=list)
    region: str = "na"
    # Win rate from VLR rankings W-L record
    wins_from_record: int = 0
    losses_from_record: int = 0
    win_rate_from_record: Optional[float] = None
    data_quality: str = "unknown"  # "good", "partial", "rankings_only", "mock"


def _parse_score(score_str: str) -> int:
    """Parse score string to int."""
    try:
        return int(score_str)
    except (ValueError, TypeError):
        return 0


def _determine_region(team_name: str) -> str:
    """Determine region based on team name heuristics."""
    team_lower = team_name.lower()
    
    # NA teams
    na_teams = ["cloud9", "sentinels", "100 thieves", "nrg", "g2", "evil geniuses", "faze"]
    for t in na_teams:
        if t in team_lower:
            return "na"
    
    # EU teams  
    eu_teams = ["fnatic", "team liquid", "vitality", "karmine", "gentle mates"]
    for t in eu_teams:
        if t in team_lower:
            return "eu"
    
    # APAC teams
    ap_teams = ["drx", "t1", "gen.g", "paper rex", "rrq"]
    for t in ap_teams:
        if t in team_lower:
            return "ap"
    
    # LATAM teams
    la_teams = ["loud", "leviatán", "kru", "mibr"]
    for t in la_teams:
        if t in team_lower:
            return "la"
    
    return "na"  # Default


async def fetch_combined_data(
    team_name: str,
    n_matches: int = 20,
) -> CombinedTeamData:
    """
    Fetch combined data from GRID and VLR APIs.
    
    This provides the most comprehensive dataset by combining:
    - GRID: Official tournament data, team/player IDs
    - VLR: Live match results, player stats, rankings
    """
    logger.info(f"Fetching combined data for {team_name}")
    
    region = _determine_region(team_name)
    
    # Initialize result
    result = CombinedTeamData(
        team_id="",
        team_name=team_name,
        team_short=None,
        logo_url=None,
        rank=None,
        record=None,
        earnings=None,
        region=region,
    )
    
    # Fetch from both sources in parallel
    grid_task = _fetch_grid_data(team_name, n_matches)
    vlr_task = _fetch_vlr_data(team_name, region)
    
    grid_data, vlr_data = await asyncio.gather(
        grid_task, vlr_task,
        return_exceptions=True
    )
    
    # Process GRID data
    if isinstance(grid_data, Exception):
        logger.warning(f"GRID fetch failed: {grid_data}")
        grid_data = None
    
    if grid_data:
        result.team_id = grid_data.get("team_id", "")
        result.team_name = grid_data.get("team_name", team_name)
        result.team_short = grid_data.get("team_short")
        result.logo_url = grid_data.get("logo_url")
        
        for match in grid_data.get("matches", []):
            result.matches.append(CombinedMatchData(
                match_id=match["match_id"],
                date=match["date"],
                map_name=match.get("map", "Unknown"),
                team_name=result.team_name,
                opponent=match["opponent"],
                result=match["result"],
                score_us=match["score_us"],
                score_them=match["score_them"],
                event_name=match.get("event", ""),
                source=match.get("source", "grid"),
            ))
        
        # Add GRID player stats (from detailed data)
        for player in grid_data.get("players", []):
            result.players.append(CombinedPlayerData(
                player_name=player["player_name"],
                team=player.get("team", result.team_name),
                agent=", ".join(player.get("agents", [])) or "Various",
                acs=player.get("acs", 0),
                kills=player.get("kills", 0),
                deaths=player.get("deaths", 0),
                assists=player.get("assists", 0),
                kd=player.get("kd", 0),
                rating=0,  # GRID doesn't provide rating
                first_bloods=player.get("first_kills", 0),
                first_deaths=0,
            ))
        
        # Add map veto data
        for veto in grid_data.get("map_veto", []):
            result.map_veto.append(CombinedMapVeto(
                action=veto["action"],
                map_name=veto["map"],
                team_name=veto["team"],
                is_our_team=veto["is_our_team"],
            ))
    
    # Process VLR data
    if isinstance(vlr_data, Exception):
        logger.warning(f"VLR fetch failed: {vlr_data}")
        vlr_data = None
    
    if vlr_data:
        # Update ranking info from VLR
        if vlr_data.get("rank"):
            result.rank = vlr_data["rank"]
            result.record = vlr_data.get("record")
            result.earnings = vlr_data.get("earnings")
            # Store parsed W-L record
            result.wins_from_record = vlr_data.get("wins", 0)
            result.losses_from_record = vlr_data.get("losses", 0)
            result.win_rate_from_record = vlr_data.get("win_rate_from_record")
        
        # Add VLR matches
        for match in vlr_data.get("matches", []):
            # Check if this match is already from GRID (avoid duplicates)
            is_duplicate = any(
                m.opponent.lower() == match["opponent"].lower() and
                m.score_us == match["score_us"] and
                m.score_them == match["score_them"]
                for m in result.matches
            )
            
            if not is_duplicate:
                result.matches.append(CombinedMatchData(
                    match_id=f"vlr_{len(result.matches)}",
                    date=match["date"],
                    map_name="Unknown",  # VLR doesn't provide map per match in results
                    team_name=result.team_name,
                    opponent=match["opponent"],
                    result=match["result"],
                    score_us=match["score_us"],
                    score_them=match["score_them"],
                    event_name=match.get("event", ""),
                    source="vlr",
                ))
        
        # Add player stats from VLR (only if we don't have GRID data for them)
        existing_players = {p.player_name.lower() for p in result.players}
        for player in vlr_data.get("players", []):
            player_name = player.get("player", "")
            if player_name.lower() not in existing_players:
                result.players.append(CombinedPlayerData(
                    player_name=player_name,
                    team=player.get("org", result.team_name),
                    agent="Various",  # VLR stats are aggregated
                    acs=player.get("acs", 0),
                    kills=0,
                    deaths=0,
                    assists=0,
                    kd=player.get("kd", 0),
                    rating=player.get("rating", 0),
                    first_bloods=0,
                    first_deaths=0,
                ))
            else:
                # Update existing player with VLR rating
                for p in result.players:
                    if p.player_name.lower() == player_name.lower():
                        p.rating = player.get("rating", p.rating)
                        if p.acs == 0:
                            p.acs = player.get("acs", 0)
                        if p.kd == 0:
                            p.kd = player.get("kd", 0)
                        break
    
    # Sort matches by date (most recent first)
    # Handle timezone-aware and naive datetimes
    def get_sort_key(m):
        try:
            dt = m.date
            if dt is None:
                return datetime.min
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt
        except Exception:
            return datetime.min
    
    try:
        result.matches.sort(key=get_sort_key, reverse=True)
    except Exception as e:
        logger.warning(f"Failed to sort matches by date: {e}")
    
    # Assess data quality
    result.data_quality = _assess_data_quality(result)
    
    logger.info(f"Combined data: {len(result.matches)} matches, {len(result.players)} players, quality: {result.data_quality}")
    return result


def _assess_data_quality(data: CombinedTeamData) -> str:
    """
    Assess the quality of the combined data.
    
    Returns:
        - "good": Has GRID detailed match data with player stats
        - "partial": Has some real data but missing key components
        - "rankings_only": Only have W-L record from rankings, limited match details
        - "no_data": No usable data at all
    """
    has_matches = len(data.matches) > 0
    has_players = len(data.players) > 0
    has_rankings = data.rank is not None and data.record is not None
    has_map_veto = len(data.map_veto) > 0
    
    # Count matches with actual results vs unknown
    known_results = sum(1 for m in data.matches if m.result in ["win", "loss", "draw"])
    grid_detailed = sum(1 for m in data.matches if m.source == "grid_detail")
    total_matches = len(data.matches)
    
    # Check if we have GRID detailed data (from file-download)
    has_grid_detail = grid_detailed >= 3
    
    # Check if players have actual stats (not just VLR aggregates)
    players_with_stats = sum(1 for p in data.players if p.kills > 0 or p.deaths > 0)
    
    # "good" quality: Has GRID detailed match data
    if has_grid_detail and players_with_stats >= 3:
        return "good"
    
    # "good" if we have enough known results with player data
    if known_results >= 5 and has_players:
        return "good"
    
    # "partial" if we have some data
    if known_results >= 3 or (has_players and has_rankings):
        return "partial"
    
    # "rankings_only" if we only have rankings
    if has_rankings:
        return "rankings_only"
    
    # No usable data
    if has_matches or has_players:
        return "partial"
    
    return "no_data"


async def _fetch_grid_data(team_name: str, n_matches: int) -> dict[str, Any]:
    """
    Fetch data from GRID API with FULL MATCH DETAILS.
    
    Uses the file-download endpoint to get:
    - Map scores (actual round counts)
    - Player stats (K/D/A, damage, headshots, first kills)
    - Map veto sequence
    - Agent picks
    """
    try:
        async with ValorantGridClient() as client:
            # Get series with full details
            team, series_details = await client.get_team_series_with_details(team_name, limit=n_matches)
            
            if not team:
                logger.warning(f"Team not found in GRID: {team_name}")
                return {}
            
            matches = []
            players_map = {}  # player_name -> aggregated stats
            map_veto_data = []
            
            for detail in series_details:
                # Determine which team is ours
                is_team1 = _matches_team_name(team_name, detail.team1.name)
                our_team = detail.team1 if is_team1 else detail.team2
                opp_team = detail.team2 if is_team1 else detail.team1
                
                # Process each map in the series
                for map_result in detail.maps:
                    # Determine scores relative to our team
                    if is_team1:
                        score_us = map_result.team1_score
                        score_them = map_result.team2_score
                    else:
                        score_us = map_result.team2_score
                        score_them = map_result.team1_score
                    
                    # Determine result
                    if score_us > score_them:
                        result = "win"
                    elif score_us < score_them:
                        result = "loss"
                    else:
                        result = "draw"
                    
                    matches.append({
                        "match_id": f"{detail.series_id}_{map_result.map_name}",
                        "series_id": detail.series_id,
                        "date": datetime.now(),  # Series list has date, but details don't
                        "map": map_result.map_name,
                        "opponent": opp_team.name,
                        "result": result,
                        "score_us": score_us,
                        "score_them": score_them,
                        "event": "",  # From series metadata
                        "source": "grid_detail",
                    })
                    
                    # Process player stats for this map
                    if map_result.map_name in detail.player_stats:
                        for ps in detail.player_stats[map_result.map_name]:
                            # Only track our team's players
                            if _matches_team_name(team_name, ps.team_name):
                                if ps.player_name not in players_map:
                                    players_map[ps.player_name] = {
                                        "player_name": ps.player_name,
                                        "team": ps.team_name,
                                        "kills": 0,
                                        "deaths": 0,
                                        "assists": 0,
                                        "headshots": 0,
                                        "first_kills": 0,
                                        "damage": 0,
                                        "maps_played": 0,
                                        "agents": [],
                                    }
                                
                                p = players_map[ps.player_name]
                                p["kills"] += ps.kills
                                p["deaths"] += ps.deaths
                                p["assists"] += ps.assists
                                p["headshots"] += ps.headshots
                                p["first_kills"] += ps.first_kills
                                p["damage"] += ps.damage
                                p["maps_played"] += 1
                                if ps.agent and ps.agent not in p["agents"]:
                                    p["agents"].append(ps.agent)
                
                # Collect map veto
                for veto in detail.map_veto:
                    map_veto_data.append({
                        "action": veto.action_type,
                        "map": veto.map_name,
                        "team": veto.team_name,
                        "is_our_team": _matches_team_name(team_name, veto.team_name),
                    })
            
            # Convert players map to list with calculated stats
            players = []
            for name, stats in players_map.items():
                maps_played = max(1, stats["maps_played"])
                kd = stats["kills"] / max(1, stats["deaths"])
                acs = stats["damage"] / (maps_played * 13)  # Rough ACS approximation
                
                players.append({
                    "player_name": name,
                    "team": stats["team"],
                    "kills": stats["kills"],
                    "deaths": stats["deaths"],
                    "assists": stats["assists"],
                    "kd": round(kd, 2),
                    "acs": round(acs, 1),
                    "first_kills": stats["first_kills"],
                    "headshots": stats["headshots"],
                    "damage": stats["damage"],
                    "maps_played": maps_played,
                    "agents": stats["agents"],
                })
            
            logger.info(f"GRID detailed data: {len(matches)} maps, {len(players)} players for {team.name}")
            
            return {
                "team_id": team.id,
                "team_name": team.name,
                "team_short": team.name_short,
                "logo_url": team.logo_url,
                "matches": matches,
                "players": players,
                "map_veto": map_veto_data,
            }
    except Exception as e:
        logger.error(f"GRID fetch error: {e}")
        raise


async def _fetch_vlr_data(team_name: str, region: str) -> dict[str, Any]:
    """
    Fetch data from VLR API.
    
    VLR provides:
    - Team rankings with W-L records
    - Recent match results with scores
    - Player statistics (ACS, K/D, KAST, etc.)
    
    This is our primary source for actual match results.
    """
    try:
        async with VlrClient() as client:
            # Parallel fetch from VLR endpoints
            rankings_task = client.get_rankings(region)
            matches_task = client.get_team_matches(team_name, limit=30)
            stats_task = client.get_player_stats(region, "60")
            
            rankings, matches, stats = await asyncio.gather(
                rankings_task, matches_task, stats_task,
                return_exceptions=True
            )
            
            result = {"matches": [], "players": []}
            
            # Process rankings - find team's rank using alias matching
            if not isinstance(rankings, Exception):
                for r in rankings:
                    if _matches_team_name(team_name, r.team):
                        result["rank"] = r.rank
                        result["record"] = r.record
                        result["earnings"] = r.earnings
                        result["team_name_vlr"] = r.team
                        # Parse W-L record for win rate calculation
                        wins, losses = _parse_record(r.record)
                        result["wins"] = wins
                        result["losses"] = losses
                        if wins + losses > 0:
                            result["win_rate_from_record"] = wins / (wins + losses)
                        logger.info(f"VLR ranking for {team_name}: #{r.rank}, {r.record} ({wins}W-{losses}L)")
                        break
            else:
                logger.warning(f"VLR rankings fetch failed: {rankings}")
            
            # Process matches - these have actual scores
            if not isinstance(matches, Exception):
                for m in matches:
                    # Determine which team is ours using alias matching
                    is_team1 = _matches_team_name(team_name, m.team1)
                    is_team2 = _matches_team_name(team_name, m.team2)
                    
                    if not (is_team1 or is_team2):
                        continue
                    
                    if is_team1:
                        score_us = _parse_score(m.score1)
                        score_them = _parse_score(m.score2)
                        opponent = m.team2
                    else:
                        score_us = _parse_score(m.score2)
                        score_them = _parse_score(m.score1)
                        opponent = m.team1
                    
                    # Determine result
                    if score_us > score_them:
                        result_str = "win"
                    elif score_us < score_them:
                        result_str = "loss"
                    else:
                        result_str = "draw"
                    
                    result["matches"].append({
                        "opponent": opponent,
                        "result": result_str,
                        "score_us": score_us,
                        "score_them": score_them,
                        "event": m.event,
                        "date": datetime.now(),  # VLR results don't include exact timestamps
                        "match_page": m.match_page,
                    })
                
                logger.info(f"VLR matches for {team_name}: {len(result['matches'])} found")
            else:
                logger.warning(f"VLR matches fetch failed: {matches}")
            
            # Process player stats - use alias matching
            if not isinstance(stats, Exception):
                for s in stats:
                    org = s.org if s.org else ""
                    # Use alias-aware matching
                    if _matches_team_name(team_name, org):
                        try:
                            result["players"].append({
                                "player": s.player,
                                "org": s.org,
                                "rating": float(s.rating) if s.rating else 0,
                                "acs": float(s.acs) if s.acs else 0,
                                "kd": float(s.kd) if s.kd else 0,
                                "kast": s.kast,
                                "adr": float(s.adr) if s.adr else 0,
                                "kpr": float(s.kpr) if s.kpr else 0,
                                "fkpr": float(s.fkpr) if s.fkpr else 0,
                                "fdpr": float(s.fdpr) if s.fdpr else 0,
                                "hs_pct": s.hs_pct,
                            })
                        except (ValueError, TypeError):
                            pass
                
                logger.info(f"VLR player stats for {team_name}: {len(result['players'])} players")
            else:
                logger.warning(f"VLR stats fetch failed: {stats}")
            
            return result
            
    except Exception as e:
        logger.error(f"VLR fetch error: {e}")
        raise


def combined_to_dataframes(data: CombinedTeamData) -> dict[str, pd.DataFrame]:
    """
    Convert CombinedTeamData to pandas DataFrames for analysis.
    """
    # Matches DataFrame
    matches_data = []
    for m in data.matches:
        matches_data.append({
            "match_id": m.match_id,
            "date": m.date,
            "map": m.map_name,
            "team_name": m.team_name,
            "opponent": m.opponent,
            "result": m.result,
            "score_us": m.score_us,
            "score_them": m.score_them,
            "event_name": m.event_name,
            "source": m.source,
        })
    
    if matches_data:
        matches_df = pd.DataFrame(matches_data)
    else:
        # Create empty DataFrame with required columns
        matches_df = pd.DataFrame(columns=[
            "match_id", "date", "map", "team_name", "opponent",
            "result", "score_us", "score_them", "event_name", "source"
        ])
    
    # Players DataFrame
    players_data = []
    for p in data.players:
        players_data.append({
            "player_name": p.player_name,
            "team": p.team,
            "agent": p.agent,
            "acs": p.acs,
            "kills": p.kills,
            "deaths": p.deaths,
            "assists": p.assists,
            "kd": p.kd,
            "rating": p.rating,
            "first_bloods": p.first_bloods,
            "first_deaths": p.first_deaths,
            "is_our_team": True,  # These are team players
        })
    
    if players_data:
        players_df = pd.DataFrame(players_data)
    else:
        # Create empty DataFrame with required columns
        players_df = pd.DataFrame(columns=[
            "player_name", "team", "agent", "acs", "kills", "deaths",
            "assists", "kd", "rating", "first_bloods", "first_deaths", "is_our_team"
        ])
    
    # Rounds DataFrame (synthetic from match scores)
    rounds_data = []
    for i, m in enumerate(data.matches):
        # Create synthetic round data based on match score
        total_rounds = m.score_us + m.score_them
        for round_num in range(1, total_rounds + 1):
            # Distribute wins/losses across rounds
            is_pistol = round_num in [1, 13, 25]
            
            # Simple heuristic: distribute wins proportionally
            win_ratio = m.score_us / max(1, total_rounds)
            winner = "team" if (round_num / total_rounds) <= win_ratio else "opponent"
            
            rounds_data.append({
                "match_id": m.match_id,
                "round_num": round_num,
                "side": "attack" if round_num <= 12 else "defense",
                "winner": winner,
                "pistol_round_bool": is_pistol,
                "eco_round_bool": False,
                "score_us": min(round_num, m.score_us) if winner == "team" else max(0, round_num - (total_rounds - m.score_us)),
                "score_them": min(round_num, m.score_them) if winner == "opponent" else max(0, round_num - (total_rounds - m.score_them)),
            })
    
    if rounds_data:
        rounds_df = pd.DataFrame(rounds_data)
    else:
        # Create empty DataFrame with required columns
        rounds_df = pd.DataFrame(columns=[
            "match_id", "round_num", "side", "winner",
            "pistol_round_bool", "eco_round_bool", "score_us", "score_them"
        ])
    
    return {
        "matches_df": matches_df,
        "players_df": players_df,
        "rounds_df": rounds_df,
    }
