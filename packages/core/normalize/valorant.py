"""
VALORANT Data Normalization

Robust conversion of raw GRID API responses into clean pandas DataFrames.
Includes defensive parsing, missing field handling, and structured logging.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class NormalizedData:
    """
    Container for all normalized VALORANT match data.
    
    Attributes:
        matches_df: Match-level data (one row per match).
        players_df: Player performance data (one row per player per match).
        rounds_df: Round-by-round data (one row per round per match).
        events_df: Kill/death events (optional, may be None).
        economy_df: Economy data per round (optional, may be None).
        picks_df: Agent pick data (one row per player per match).
    """
    matches_df: pd.DataFrame
    players_df: pd.DataFrame
    rounds_df: pd.DataFrame
    events_df: Optional[pd.DataFrame] = None
    economy_df: Optional[pd.DataFrame] = None
    picks_df: Optional[pd.DataFrame] = None


def _safe_get(data: Any, *keys: str, default: Any = None) -> Any:
    """
    Safely navigate nested dictionaries.
    
    Args:
        data: Root dictionary or None.
        keys: Sequence of keys to navigate.
        default: Default value if path not found.
        
    Returns:
        Value at path or default.
    """
    result = data
    for key in keys:
        if result is None or not isinstance(result, dict):
            logger.debug(f"Missing key path: {'.'.join(keys)}")
            return default
        result = result.get(key, default)
    return result


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse datetime from various formats."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            # Try ISO format
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
        try:
            # Try common formats
            for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                return datetime.strptime(value, fmt)
        except ValueError:
            pass
    logger.warning(f"Could not parse datetime: {value}")
    return None


def normalize_match_list(
    raw: dict[str, Any],
    team_name: str,
) -> pd.DataFrame:
    """
    Normalize match list data into a DataFrame.
    
    Args:
        raw: Raw API response from match list query.
        team_name: Name of the team being analyzed.
        
    Returns:
        DataFrame with columns:
        - match_id: Unique match identifier
        - date: Match date
        - map: Map name
        - opponent: Opponent team name
        - result: "win" or "loss"
        - team_name: Analyzed team name
        - event_name: Tournament/event name
        - score_us: Team's score
        - score_them: Opponent's score
    """
    rows = []
    
    # Navigate to team data
    teams = _safe_get(raw, "teams", "edges", default=[])
    
    for team_edge in teams:
        team_node = _safe_get(team_edge, "node", default={})
        actual_team_name = _safe_get(team_node, "name", default=team_name)
        
        # Get series participations
        participations = _safe_get(team_node, "seriesParticipations", "edges", default=[])
        
        for part_edge in participations:
            series = _safe_get(part_edge, "node", "series", default={})
            event_name = _safe_get(series, "tournament", "name", default="Unknown Event")
            series_date = _parse_datetime(_safe_get(series, "startTimeScheduled"))
            
            # Get opponent from series
            series_teams = _safe_get(series, "teams", default=[])
            opponent_name = "Unknown"
            for st in series_teams:
                st_name = _safe_get(st, "name") or _safe_get(st, "baseInfo", "name")
                if st_name and st_name.lower() != actual_team_name.lower():
                    opponent_name = st_name
                    break
            
            # Get matches
            matches = _safe_get(series, "matches", "edges", default=[])
            
            for match_edge in matches:
                match_node = _safe_get(match_edge, "node", default={})
                match_id = _safe_get(match_node, "id")
                
                if not match_id:
                    continue
                
                map_name = _safe_get(match_node, "map", "name", default="Unknown")
                
                # Determine result
                match_teams = _safe_get(match_node, "teams", default=[])
                score_us = 0
                score_them = 0
                result = "unknown"
                
                for mt in match_teams:
                    mt_name = _safe_get(mt, "baseInfo", "name") or _safe_get(mt, "name")
                    mt_score = _safe_get(mt, "score", default=0)
                    mt_won = _safe_get(mt, "won", default=False)
                    
                    if mt_name and mt_name.lower() == actual_team_name.lower():
                        score_us = mt_score
                        result = "win" if mt_won else "loss"
                    else:
                        score_them = mt_score
                        if opponent_name == "Unknown" and mt_name:
                            opponent_name = mt_name
                
                rows.append({
                    "match_id": match_id,
                    "date": series_date,
                    "map": map_name,
                    "opponent": opponent_name,
                    "result": result,
                    "team_name": actual_team_name,
                    "event_name": event_name,
                    "score_us": score_us,
                    "score_them": score_them,
                })
    
    df = pd.DataFrame(rows)
    
    # Ensure required columns exist
    required_cols = ["match_id", "date", "map", "opponent", "result", "team_name"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan
    
    logger.info(f"Normalized {len(df)} matches for {team_name}")
    return df


def normalize_match_detail(
    raw: dict[str, Any],
    team_name: str,
    match_id: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Normalize match detail data into DataFrames.
    
    Args:
        raw: Raw API response from match detail query.
        team_name: Name of the team being analyzed.
        match_id: Match ID (if not in raw data).
        
    Returns:
        Tuple of (players_df, rounds_df, events_df, economy_df).
        events_df and economy_df may be None if data not available.
    """
    match = _safe_get(raw, "match", default={}) or raw
    actual_match_id = _safe_get(match, "id") or match_id or "unknown"
    map_name = _safe_get(match, "map", "name", default="Unknown")
    
    # Process players
    player_rows = []
    match_teams = _safe_get(match, "teams", default=[])
    
    for team in match_teams:
        team_base_name = _safe_get(team, "baseInfo", "name") or _safe_get(team, "name", default="")
        is_our_team = team_base_name.lower() == team_name.lower()
        
        players = _safe_get(team, "players", default=[])
        for player in players:
            player_id = _safe_get(player, "baseInfo", "id", default="")
            player_name = _safe_get(player, "baseInfo", "nickname", default="Unknown")
            agent = _safe_get(player, "agent", "name", default="Unknown")
            
            stats = _safe_get(player, "stats", default={})
            kills = _safe_get(stats, "kills", default=np.nan)
            deaths = _safe_get(stats, "deaths", default=np.nan)
            assists = _safe_get(stats, "assists", default=np.nan)
            damage = _safe_get(stats, "damageDealt", default=np.nan)
            
            # ACS calculation (if we have damage and round count)
            acs = np.nan
            
            player_rows.append({
                "match_id": actual_match_id,
                "player_id": player_id,
                "player_name": player_name,
                "team": team_base_name,
                "is_our_team": is_our_team,
                "agent": agent,
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "damage": damage,
                "acs": acs,
                "first_bloods": np.nan,  # Will be filled from rounds
                "first_deaths": np.nan,
            })
    
    players_df = pd.DataFrame(player_rows)
    
    # Process rounds
    round_rows = []
    event_rows = []
    economy_rows = []
    
    rounds = _safe_get(match, "rounds", default=[])
    
    # Track first bloods/deaths per player
    player_fb_counts = {}
    player_fd_counts = {}
    
    total_rounds = len(rounds)
    score_us = 0
    score_them = 0
    
    for round_data in rounds:
        round_num = _safe_get(round_data, "number", default=0)
        
        # Determine winner
        winning_team = _safe_get(round_data, "winningTeam", "baseInfo", "name", default="")
        winner = "team" if winning_team.lower() == team_name.lower() else "opponent"
        
        if winner == "team":
            score_us += 1
        else:
            score_them += 1
        
        # Determine side (first 12 rounds: team_a attacks, then swap)
        # This is a simplification - actual side depends on team order
        side = "attack" if round_num <= 12 else "defense"
        if round_num > 24:
            side = "overtime"
        
        # Pistol and eco detection
        is_pistol = round_num in [1, 13, 25]
        is_eco = False  # Will be determined from economy if available
        
        # Win condition
        win_condition = _safe_get(round_data, "winCondition", default="")
        
        # Spike info
        spike_planted = _safe_get(round_data, "spike", "planted", default=False)
        spike_defused = _safe_get(round_data, "spike", "defused", default=False)
        
        round_rows.append({
            "match_id": actual_match_id,
            "round_num": round_num,
            "side": side,
            "winner": winner,
            "winning_team_name": winning_team,
            "pistol_round_bool": is_pistol,
            "eco_round_bool": is_eco,
            "score_us": score_us,
            "score_them": score_them,
            "win_condition": win_condition,
            "spike_planted": spike_planted,
            "spike_defused": spike_defused,
        })
        
        # Process player stats per round
        player_stats = _safe_get(round_data, "playerStats", default=[])
        
        for ps in player_stats:
            player_nick = _safe_get(ps, "player", "baseInfo", "nickname", default="")
            was_fb = _safe_get(ps, "wasFirstBlood", default=False)
            was_fd = _safe_get(ps, "wasFirstDeath", default=False)
            loadout = _safe_get(ps, "loadoutValue", default=np.nan)
            round_kills = _safe_get(ps, "kills", default=0)
            round_deaths = _safe_get(ps, "deaths", default=0)
            round_damage = _safe_get(ps, "damageDealt", default=0)
            
            # Track FB/FD
            if was_fb:
                player_fb_counts[player_nick] = player_fb_counts.get(player_nick, 0) + 1
            if was_fd:
                player_fd_counts[player_nick] = player_fd_counts.get(player_nick, 0) + 1
            
            # Add to events
            if round_kills > 0 or round_deaths > 0:
                event_rows.append({
                    "match_id": actual_match_id,
                    "round_num": round_num,
                    "player_name": player_nick,
                    "kills": round_kills,
                    "deaths": round_deaths,
                    "damage": round_damage,
                    "was_first_blood": was_fb,
                    "was_first_death": was_fd,
                    "loadout_value": loadout,
                })
            
            # Add economy data
            if not np.isnan(loadout) if isinstance(loadout, float) else loadout is not None:
                economy_rows.append({
                    "match_id": actual_match_id,
                    "round_num": round_num,
                    "player_name": player_nick,
                    "loadout_value": loadout,
                })
    
    rounds_df = pd.DataFrame(round_rows)
    
    # Update players_df with FB/FD counts
    if not players_df.empty:
        players_df["first_bloods"] = players_df["player_name"].map(
            lambda x: player_fb_counts.get(x, 0)
        )
        players_df["first_deaths"] = players_df["player_name"].map(
            lambda x: player_fd_counts.get(x, 0)
        )
        
        # Calculate ACS if we have damage and rounds
        if total_rounds > 0:
            players_df["acs"] = players_df["damage"].apply(
                lambda d: round(d / total_rounds, 1) if pd.notna(d) else np.nan
            )
    
    # Create events_df if we have data
    events_df = pd.DataFrame(event_rows) if event_rows else None
    
    # Create economy_df if we have data
    economy_df = pd.DataFrame(economy_rows) if economy_rows else None
    
    logger.info(f"Normalized match {actual_match_id}: {len(players_df)} players, {len(rounds_df)} rounds")
    
    return players_df, rounds_df, events_df, economy_df


def normalize_all(
    match_list_raw: dict[str, Any],
    match_details: list[dict[str, Any]],
    team_name: str,
) -> NormalizedData:
    """
    Normalize all match data into structured DataFrames.
    
    Args:
        match_list_raw: Raw response from match list query.
        match_details: List of raw responses from match detail queries.
        team_name: Name of the team being analyzed.
        
    Returns:
        NormalizedData containing all DataFrames.
    """
    # Normalize match list
    matches_df = normalize_match_list(match_list_raw, team_name)
    
    # Normalize match details
    all_players = []
    all_rounds = []
    all_events = []
    all_economy = []
    
    for detail in match_details:
        match_id = _safe_get(detail, "match", "id")
        players_df, rounds_df, events_df, economy_df = normalize_match_detail(
            detail, team_name, match_id
        )
        
        all_players.append(players_df)
        all_rounds.append(rounds_df)
        
        if events_df is not None:
            all_events.append(events_df)
        if economy_df is not None:
            all_economy.append(economy_df)
    
    # Combine DataFrames
    players_df = pd.concat(all_players, ignore_index=True) if all_players else pd.DataFrame()
    rounds_df = pd.concat(all_rounds, ignore_index=True) if all_rounds else pd.DataFrame()
    events_df = pd.concat(all_events, ignore_index=True) if all_events else None
    economy_df = pd.concat(all_economy, ignore_index=True) if all_economy else None
    
    # Create picks_df from players_df
    picks_df = None
    if not players_df.empty:
        picks_df = players_df[["match_id", "team", "player_name", "agent"]].copy()
    
    logger.info(f"Normalized all data: {len(matches_df)} matches, {len(players_df)} player records, {len(rounds_df)} rounds")
    
    return NormalizedData(
        matches_df=matches_df,
        players_df=players_df,
        rounds_df=rounds_df,
        events_df=events_df,
        economy_df=economy_df,
        picks_df=picks_df,
    )


def normalize_mock_data(
    raw_matches: list[dict[str, Any]],
    team_name: str,
) -> NormalizedData:
    """
    Normalize mock data format into DataFrames.
    
    This handles the mock data format from grid/mock_data.py.
    
    Args:
        raw_matches: List of mock match data.
        team_name: Name of the team.
        
    Returns:
        NormalizedData containing all DataFrames.
    """
    match_rows = []
    player_rows = []
    round_rows = []
    pick_rows = []
    
    for match in raw_matches:
        match_id = match.get("id", "")
        date = _parse_datetime(match.get("date"))
        map_name = match.get("map", "Unknown")
        
        teams = match.get("teams", [])
        if len(teams) >= 2:
            team_a = teams[0]
            team_b = teams[1]
            
            # Determine which is our team
            if team_a.get("name", "").lower() == team_name.lower():
                score_us = team_a.get("score", 0)
                score_them = team_b.get("score", 0)
                opponent = team_b.get("name", "Unknown")
                result = "win" if team_a.get("isWinner", False) else "loss"
            else:
                score_us = team_b.get("score", 0)
                score_them = team_a.get("score", 0)
                opponent = team_a.get("name", "Unknown")
                result = "win" if team_b.get("isWinner", False) else "loss"
        else:
            score_us = 0
            score_them = 0
            opponent = "Unknown"
            result = "unknown"
        
        match_rows.append({
            "match_id": match_id,
            "date": date,
            "map": map_name,
            "opponent": opponent,
            "result": result,
            "team_name": team_name,
            "score_us": score_us,
            "score_them": score_them,
        })
        
        # Process players
        for player in match.get("players", []):
            is_our_team = player.get("teamName", "").lower() == team_name.lower()
            
            player_rows.append({
                "match_id": match_id,
                "player_id": player.get("playerId", ""),
                "player_name": player.get("playerName", "Unknown"),
                "team": player.get("teamName", ""),
                "is_our_team": is_our_team,
                "agent": player.get("agent", "Unknown"),
                "kills": player.get("kills", np.nan),
                "deaths": player.get("deaths", np.nan),
                "assists": player.get("assists", np.nan),
                "acs": player.get("acs", np.nan),
                "first_bloods": player.get("firstBloods", np.nan),
                "first_deaths": np.nan,
                "damage": player.get("damagePerRound", np.nan),
            })
            
            pick_rows.append({
                "match_id": match_id,
                "team": player.get("teamName", ""),
                "player_name": player.get("playerName", "Unknown"),
                "agent": player.get("agent", "Unknown"),
            })
        
        # Process rounds with score tracking
        score_us = 0
        score_them = 0
        for round_data in match.get("rounds", []):
            round_num = round_data.get("roundNumber", 0)
            winner = "team" if round_data.get("winner", "").lower() == team_name.lower() else "opponent"
            
            # Update scores
            if winner == "team":
                score_us += 1
            else:
                score_them += 1
            
            round_rows.append({
                "match_id": match_id,
                "round_num": round_num,
                "side": round_data.get("winnerSide", ""),
                "winner": winner,
                "winning_team_name": round_data.get("winner", ""),
                "pistol_round_bool": round_data.get("isPistol", False),
                "eco_round_bool": round_data.get("economyType") == "eco",
                "economy_type": round_data.get("economyType", ""),
                "spike_planted": round_data.get("spikePlanted", False),
                "spike_defused": round_data.get("spikeDefused", False),
                "score_us": score_us,
                "score_them": score_them,
            })
    
    matches_df = pd.DataFrame(match_rows)
    players_df = pd.DataFrame(player_rows)
    rounds_df = pd.DataFrame(round_rows)
    picks_df = pd.DataFrame(pick_rows)
    
    logger.info(f"Normalized mock data: {len(matches_df)} matches")
    
    return NormalizedData(
        matches_df=matches_df,
        players_df=players_df,
        rounds_df=rounds_df,
        picks_df=picks_df,
    )


# Convenience functions for filtering
def get_team_matches(data: NormalizedData, team_name: str) -> pd.DataFrame:
    """Filter matches to only include those involving a specific team."""
    df = data.matches_df
    if df.empty:
        return df
    return df[df["team_name"].str.lower() == team_name.lower()].copy()


def get_team_players(data: NormalizedData, team_name: str) -> pd.DataFrame:
    """Filter player data to only include a specific team."""
    df = data.players_df
    if df.empty:
        return df
    return df[df["is_our_team"] == True].copy()


def get_team_rounds(data: NormalizedData, team_name: str) -> pd.DataFrame:
    """Get rounds from team's matches."""
    matches_df = get_team_matches(data, team_name)
    if matches_df.empty or data.rounds_df.empty:
        return data.rounds_df
    match_ids = matches_df["match_id"].unique()
    return data.rounds_df[data.rounds_df["match_id"].isin(match_ids)].copy()
