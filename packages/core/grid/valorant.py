"""
VALORANT-specific GRID API Client

Provides high-level methods for fetching VALORANT esports data.
Uses both GraphQL Central Data API and File Download API for complete data.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import httpx

from .client import GRIDClient, GRIDClientError

logger = logging.getLogger(__name__)

# VALORANT title ID in GRID (IMPORTANT: 6 not 29!)
VALORANT_TITLE_ID = 6

# File download endpoint for match data
FILE_DOWNLOAD_URL = "https://api.grid.gg/file-download/end-state/grid/series"


@dataclass
class GridTeam:
    """Team data from GRID."""
    id: str
    name: str
    name_short: Optional[str] = None
    logo_url: Optional[str] = None


@dataclass
class GridPlayer:
    """Player data from GRID."""
    id: str
    nickname: str
    team_id: Optional[str] = None


@dataclass
class GridSeries:
    """Series (match) data from GRID."""
    id: str
    start_time: datetime
    tournament_name: str
    tournament_id: str
    format_name: str
    series_type: str
    teams: list[GridTeam] = field(default_factory=list)
    players: list[GridPlayer] = field(default_factory=list)


@dataclass
class GridMapResult:
    """Individual map result from a series."""
    map_name: str
    team1_name: str
    team1_score: int
    team2_name: str
    team2_score: int
    winner: str


@dataclass 
class GridPlayerStats:
    """Player statistics from a map."""
    player_name: str
    team_name: str
    agent: str
    kills: int
    deaths: int
    assists: int
    headshots: int
    first_kills: int
    damage: int


@dataclass
class GridMapVeto:
    """Map veto action."""
    action_type: str  # "ban" or "pick"
    map_name: str
    team_name: str
    team_id: str


@dataclass
class GridSeriesDetail:
    """Full series detail including maps, scores, and player stats."""
    series_id: str
    team1: GridTeam
    team2: GridTeam
    maps: list[GridMapResult] = field(default_factory=list)
    player_stats: dict[str, list[GridPlayerStats]] = field(default_factory=dict)  # map -> players
    map_veto: list[GridMapVeto] = field(default_factory=list)
    winner: Optional[str] = None


class ValorantGridClient:
    """
    High-level client for fetching VALORANT data from GRID.
    
    Uses both:
    - GraphQL Central Data API for series listings and team info
    - File Download API for detailed match data (scores, player stats)
    """
    
    def __init__(self, client: Optional[GRIDClient] = None):
        self._client = client
        self._owns_client = client is None
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        if self._owns_client:
            self._client = GRIDClient()
            await self._client.__aenter__()
        # Create HTTP client for file downloads
        import os
        self._http_client = httpx.AsyncClient(
            timeout=60,
            headers={"x-api-key": os.getenv("GRID_API_KEY", "")}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._http_client:
            await self._http_client.aclose()
        if self._owns_client and self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def search_teams(self, name: str, limit: int = 10) -> list[GridTeam]:
        """
        Search for VALORANT teams by name.
        """
        # Use allSeries to find teams since teams query may have restrictions
        query = f"""
        {{
            allSeries(
                first: 50
                filter: {{ titleId: {VALORANT_TITLE_ID}, types: [ESPORTS] }}
                orderBy: StartTimeScheduled
                orderDirection: DESC
            ) {{
                edges {{
                    node {{
                        teams {{
                            baseInfo {{
                                id
                                name
                                nameShortened
                                logoUrl
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        
        result = await self._client.query(f"search_teams_{name}", query, {})
        
        # Extract unique teams matching the query
        teams_seen = set()
        teams = []
        name_lower = name.lower()
        
        for edge in result.get("allSeries", {}).get("edges", []):
            for team_data in edge.get("node", {}).get("teams", []):
                base_info = team_data.get("baseInfo", {})
                team_id = base_info.get("id", "")
                team_name = base_info.get("name", "")
                
                if team_id and team_id not in teams_seen:
                    # Check if team name matches query
                    if name_lower in team_name.lower() or team_name.lower() in name_lower:
                        teams_seen.add(team_id)
                        teams.append(GridTeam(
                            id=team_id,
                            name=team_name,
                            name_short=base_info.get("nameShortened"),
                            logo_url=base_info.get("logoUrl"),
                        ))
        
        return teams[:limit]
    
    async def get_team_by_name(self, name: str) -> Optional[GridTeam]:
        """
        Get a specific team by exact or close name match.
        """
        teams = await self.search_teams(name, limit=10)
        
        name_lower = name.lower()
        
        # Try exact match first
        for team in teams:
            if team.name.lower() == name_lower:
                return team
        
        # Try partial match (team name contains search term)
        for team in teams:
            if name_lower in team.name.lower():
                return team
        
        # Try short name match
        for team in teams:
            if team.name_short and team.name_short.lower() == name_lower:
                return team
        
        # Return first result only if it contains the search term
        for team in teams:
            if name_lower in team.name.lower() or team.name.lower() in name_lower:
                return team
        
        return None
    
    async def get_series_detail(self, series_id: str) -> Optional[GridSeriesDetail]:
        """
        Fetch detailed match data for a series via file-download endpoint.
        
        This provides:
        - Map scores
        - Player stats (K/D/A, damage, headshots)
        - Map veto sequence
        - Agent picks
        """
        if not self._http_client:
            logger.error("HTTP client not initialized")
            return None
        
        url = f"{FILE_DOWNLOAD_URL}/{series_id}"
        
        try:
            response = await self._http_client.get(url)
            
            if response.status_code != 200:
                logger.warning(f"File download failed for series {series_id}: {response.status_code}")
                return None
            
            data = response.json()
            series_state = data.get("seriesState", {})
            
            # Parse teams
            teams_data = series_state.get("teams", [])
            team_map = {}
            team1 = None
            team2 = None
            
            for i, t in enumerate(teams_data):
                team = GridTeam(
                    id=str(t.get("id", "")),
                    name=t.get("name", "Unknown"),
                )
                team_map[team.id] = team
                if i == 0:
                    team1 = team
                else:
                    team2 = team
            
            if not team1 or not team2:
                logger.warning(f"Could not parse teams for series {series_id}")
                return None
            
            result = GridSeriesDetail(
                series_id=series_id,
                team1=team1,
                team2=team2,
            )
            
            # Parse map veto
            for action in series_state.get("draftActions", []):
                draftable = action.get("draftable", {})
                drafter = action.get("drafter", {})
                
                if draftable.get("type") == "map":
                    team_id = str(drafter.get("id", ""))
                    team_name = team_map.get(team_id, GridTeam(id="", name="Unknown")).name
                    
                    result.map_veto.append(GridMapVeto(
                        action_type=action.get("type", "unknown"),
                        map_name=draftable.get("name", "unknown"),
                        team_name=team_name,
                        team_id=team_id,
                    ))
            
            # Parse games (maps)
            games = series_state.get("games", [])
            team1_wins = 0
            team2_wins = 0
            
            for game in games:
                map_info = game.get("map", {})
                map_name = map_info.get("name", "unknown")
                
                game_teams = game.get("teams", [])
                t1_score = 0
                t2_score = 0
                t1_name = team1.name
                t2_name = team2.name
                t1_won = False
                t2_won = False
                
                for gt in game_teams:
                    name = gt.get("name", "")
                    score = gt.get("score", 0)
                    won = gt.get("won", False)
                    
                    if name == team1.name:
                        t1_score = score
                        t1_won = won
                    elif name == team2.name:
                        t2_score = score
                        t2_won = won
                
                winner = t1_name if t1_won else (t2_name if t2_won else "Draw")
                if t1_won:
                    team1_wins += 1
                elif t2_won:
                    team2_wins += 1
                
                result.maps.append(GridMapResult(
                    map_name=map_name,
                    team1_name=t1_name,
                    team1_score=t1_score,
                    team2_name=t2_name,
                    team2_score=t2_score,
                    winner=winner,
                ))
                
                # Parse player stats for this map
                player_stats = []
                for gt in game_teams:
                    team_name = gt.get("name", "Unknown")
                    for p in gt.get("players", []):
                        char = p.get("character", {})
                        agent = char.get("id", "unknown") if char else "unknown"
                        
                        player_stats.append(GridPlayerStats(
                            player_name=p.get("name", "Unknown"),
                            team_name=team_name,
                            agent=agent,
                            kills=p.get("kills", 0),
                            deaths=p.get("deaths", 0),
                            assists=p.get("killAssistsGiven", 0),
                            headshots=p.get("headshots", 0),
                            first_kills=p.get("firstKill", 0) if isinstance(p.get("firstKill"), int) else 0,
                            damage=p.get("damageDealt", 0),
                        ))
                
                result.player_stats[map_name] = player_stats
            
            # Determine series winner
            result.winner = team1.name if team1_wins > team2_wins else (team2.name if team2_wins > team1_wins else None)
            
            logger.info(f"Series {series_id}: {team1.name} vs {team2.name}, {len(result.maps)} maps, winner: {result.winner}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching series detail {series_id}: {e}")
            return None

    async def get_recent_series(
        self,
        limit: int = 20,
        team_id: Optional[str] = None,
        series_type: str = "ESPORTS",
    ) -> list[GridSeries]:
        """
        Get recent VALORANT series.
        
        Args:
            limit: Maximum number of series to return
            team_id: Filter by team ID (optional)
            series_type: Filter by series type (ESPORTS, SCRIM, COMPETITIVE)
        """
        # Build filter - titleId must be integer 6 for VALORANT
        filter_parts = [f"titleId: {VALORANT_TITLE_ID}"]
        if series_type:
            filter_parts.append(f"types: [{series_type}]")
        if team_id:
            filter_parts.append(f'teamId: "{team_id}"')
        
        filter_str = ", ".join(filter_parts)
        
        query = f"""
        query GetRecentSeries($first: Int!) {{
            allSeries(
                first: $first
                filter: {{ {filter_str} }}
                orderBy: StartTimeScheduled
                orderDirection: DESC
            ) {{
                totalCount
                edges {{
                    node {{
                        id
                        startTimeScheduled
                        format {{
                            name
                        }}
                        type
                        tournament {{
                            id
                            name
                        }}
                        teams {{
                            baseInfo {{
                                id
                                name
                                nameShortened
                                logoUrl
                            }}
                            scoreAdvantage
                        }}
                        players {{
                            id
                            nickname
                        }}
                    }}
                }}
            }}
        }}
        """
        
        result = await self._client.query(
            "recent_series",
            query,
            {"first": limit},
        )
        
        series_list = []
        for edge in result.get("allSeries", {}).get("edges", []):
            node = edge.get("node", {})
            
            # Parse teams
            teams = []
            for team_data in node.get("teams", []):
                base_info = team_data.get("baseInfo", {})
                teams.append(GridTeam(
                    id=base_info.get("id", ""),
                    name=base_info.get("name", ""),
                    name_short=base_info.get("nameShortened"),
                    logo_url=base_info.get("logoUrl"),
                ))
            
            # Parse players
            players = []
            for player_data in node.get("players", []):
                players.append(GridPlayer(
                    id=player_data.get("id", ""),
                    nickname=player_data.get("nickname", ""),
                ))
            
            # Parse datetime
            start_time_str = node.get("startTimeScheduled", "")
            try:
                start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            except:
                start_time = datetime.now()
            
            series_list.append(GridSeries(
                id=node.get("id", ""),
                start_time=start_time,
                tournament_name=node.get("tournament", {}).get("name", "Unknown"),
                tournament_id=node.get("tournament", {}).get("id", ""),
                format_name=node.get("format", {}).get("name", ""),
                series_type=node.get("type", ""),
                teams=teams,
                players=players,
            ))
        
        return series_list
    
    async def get_team_series(
        self,
        team_name: str,
        limit: int = 20,
    ) -> tuple[Optional[GridTeam], list[GridSeries]]:
        """
        Get series for a specific team by name.
        
        Returns:
            Tuple of (team, series_list)
        """
        # First find the team
        team = await self.get_team_by_name(team_name)
        
        if not team:
            logger.warning(f"Team not found: {team_name}")
            return None, []
        
        logger.info(f"Found team: {team.name} (ID: {team.id})")
        
        # Get series for this team
        series = await self.get_recent_series(limit=limit, team_id=team.id)
        
        return team, series

    async def get_team_series_with_details(
        self,
        team_name: str,
        limit: int = 10,
    ) -> tuple[Optional[GridTeam], list[GridSeriesDetail]]:
        """
        Get series for a team WITH full match details.
        
        This fetches both the series list and detailed data for each series
        including map scores, player stats, and map veto.
        
        Returns:
            Tuple of (team, detailed_series_list)
        """
        team, series_list = await self.get_team_series(team_name, limit=limit)
        
        if not team or not series_list:
            return team, []
        
        # Fetch details for each series (in parallel, limit to avoid rate limits)
        details = []
        batch_size = 5
        
        for i in range(0, len(series_list), batch_size):
            batch = series_list[i:i + batch_size]
            tasks = [self.get_series_detail(s.id) for s in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, GridSeriesDetail):
                    details.append(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Failed to fetch series detail: {result}")
        
        logger.info(f"Fetched {len(details)} detailed series for {team.name}")
        return team, details


async def fetch_valorant_data(team_name: str, n_series: int = 10) -> dict[str, Any]:
    """
    Fetch VALORANT data for a team from GRID.
    
    This is the main entry point for getting real GRID data.
    """
    logger.info(f"Fetching VALORANT data for {team_name} from GRID")
    
    async with ValorantGridClient() as client:
        team, series = await client.get_team_series(team_name, limit=n_series)
        
        if not team:
            raise ValueError(f"Team not found: {team_name}")
        
        return {
            "team": {
                "id": team.id,
                "name": team.name,
                "name_short": team.name_short,
                "logo_url": team.logo_url,
            },
            "series": [
                {
                    "id": s.id,
                    "start_time": s.start_time.isoformat(),
                    "tournament": s.tournament_name,
                    "format": s.format_name,
                    "type": s.series_type,
                    "teams": [{"id": t.id, "name": t.name} for t in s.teams],
                    "players": [{"id": p.id, "nickname": p.nickname} for p in s.players],
                }
                for s in series
            ],
            "source": "grid",
        }
