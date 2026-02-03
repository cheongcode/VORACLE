"""
VLR.gg API Client

Unofficial API for vlr.gg VALORANT esports data.
Based on: https://github.com/axsddlr/vlrggapi
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

# VLR API base URL
VLR_API_URL = "https://vlrggapi.vercel.app"


@dataclass
class VlrTeamRanking:
    """Team ranking data from VLR."""
    rank: str
    team: str
    country: str
    last_played: str
    record: str
    earnings: str
    logo: str


@dataclass
class VlrPlayerStats:
    """Player statistics from VLR."""
    player: str
    org: str
    rating: str
    acs: str  # Average Combat Score
    kd: str  # Kill/Death ratio
    kast: str  # Kill, Assist, Survive, Trade %
    adr: str  # Average Damage per Round
    kpr: str  # Kills per Round
    apr: str  # Assists per Round
    fkpr: str  # First Kills per Round
    fdpr: str  # First Deaths per Round
    hs_pct: str  # Headshot %
    clutch_pct: str  # Clutch Success %


@dataclass
class VlrMatch:
    """Match data from VLR."""
    team1: str
    team2: str
    score1: str
    score2: str
    event: str
    series: str
    match_page: str
    timestamp: str
    status: str  # "upcoming", "live", "completed"


class VlrClient:
    """
    Client for the unofficial VLR.gg API.
    
    Provides access to:
    - Team rankings by region
    - Player statistics
    - Match results and upcoming matches
    - News and events
    """
    
    def __init__(self, timeout: float = 30.0):
        self.base_url = VLR_API_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    async def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request to the VLR API."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"VLR API error: {e}")
            raise
    
    async def get_rankings(self, region: str = "na") -> list[VlrTeamRanking]:
        """
        Get team rankings for a region.
        
        Regions: na, eu, ap, la, la-n, la-s, oce, kr, mn, gc, br, cn
        """
        data = await self._get("rankings", {"region": region})
        
        rankings = []
        for item in data.get("data", []):
            rankings.append(VlrTeamRanking(
                rank=item.get("rank", ""),
                team=item.get("team", ""),
                country=item.get("country", ""),
                last_played=item.get("last_played", ""),
                record=item.get("record", ""),
                earnings=item.get("earnings", ""),
                logo=item.get("logo", ""),
            ))
        
        return rankings
    
    async def get_player_stats(
        self,
        region: str = "na",
        timespan: str = "60",
    ) -> list[VlrPlayerStats]:
        """
        Get player statistics for a region.
        
        Args:
            region: Region code (na, eu, ap, etc.)
            timespan: Days to look back (30, 60, 90, or "all")
        """
        data = await self._get("stats", {"region": region, "timespan": timespan})
        
        stats = []
        for item in data.get("data", {}).get("segments", []):
            stats.append(VlrPlayerStats(
                player=item.get("player", ""),
                org=item.get("org", ""),
                rating=item.get("rating", "0"),
                acs=item.get("average_combat_score", "0"),
                kd=item.get("kill_deaths", "0"),
                kast=item.get("kill_assists_survived_traded", "0%"),
                adr=item.get("average_damage_per_round", "0"),
                kpr=item.get("kills_per_round", "0"),
                apr=item.get("assists_per_round", "0"),
                fkpr=item.get("first_kills_per_round", "0"),
                fdpr=item.get("first_deaths_per_round", "0"),
                hs_pct=item.get("headshot_percentage", "0%"),
                clutch_pct=item.get("clutch_success_percentage", "0%"),
            ))
        
        return stats
    
    async def get_matches(self, query: str = "results") -> list[VlrMatch]:
        """
        Get matches by type.
        
        Args:
            query: "upcoming", "live_score", or "results"
        """
        data = await self._get("match", {"q": query})
        
        matches = []
        segments = data.get("data", {}).get("segments", [])
        
        for item in segments:
            matches.append(VlrMatch(
                team1=item.get("team1", ""),
                team2=item.get("team2", ""),
                score1=item.get("score1", "0"),
                score2=item.get("score2", "0"),
                event=item.get("match_event", item.get("tournament_name", "")),
                series=item.get("match_series", item.get("round_info", "")),
                match_page=item.get("match_page", ""),
                timestamp=item.get("unix_timestamp", item.get("time_completed", "")),
                status=query,
            ))
        
        return matches
    
    async def get_team_matches(self, team_name: str, limit: int = 20) -> list[VlrMatch]:
        """
        Get recent matches for a specific team.
        """
        results = await self.get_matches("results")
        
        # Filter matches involving the team
        team_lower = team_name.lower()
        team_matches = []
        
        for match in results:
            if team_lower in match.team1.lower() or team_lower in match.team2.lower():
                team_matches.append(match)
                if len(team_matches) >= limit:
                    break
        
        return team_matches
    
    async def get_news(self) -> list[dict]:
        """Get latest VALORANT esports news."""
        data = await self._get("news")
        return data.get("data", {}).get("segments", [])
    
    async def get_events(self, query: str = "") -> list[dict]:
        """
        Get VALORANT events.
        
        Args:
            query: "upcoming", "completed", or "" for all
        """
        params = {"q": query} if query else {}
        data = await self._get("events", params)
        return data.get("data", {}).get("segments", [])


async def fetch_vlr_data(team_name: str, region: str = "na") -> dict[str, Any]:
    """
    Fetch live VALORANT data from VLR.gg.
    
    Returns comprehensive data including:
    - Team matches
    - Player stats
    - Rankings
    """
    logger.info(f"Fetching VLR data for {team_name}")
    
    async with VlrClient() as client:
        # Get various data in parallel
        import asyncio
        
        matches_task = client.get_team_matches(team_name, limit=20)
        rankings_task = client.get_rankings(region)
        stats_task = client.get_player_stats(region, "60")
        
        matches, rankings, stats = await asyncio.gather(
            matches_task, rankings_task, stats_task,
            return_exceptions=True
        )
        
        # Handle any exceptions
        if isinstance(matches, Exception):
            logger.warning(f"Failed to fetch matches: {matches}")
            matches = []
        if isinstance(rankings, Exception):
            logger.warning(f"Failed to fetch rankings: {rankings}")
            rankings = []
        if isinstance(stats, Exception):
            logger.warning(f"Failed to fetch stats: {stats}")
            stats = []
        
        return {
            "matches": [
                {
                    "team1": m.team1,
                    "team2": m.team2,
                    "score1": m.score1,
                    "score2": m.score2,
                    "event": m.event,
                    "match_page": m.match_page,
                }
                for m in matches
            ],
            "rankings": [
                {
                    "rank": r.rank,
                    "team": r.team,
                    "record": r.record,
                    "earnings": r.earnings,
                }
                for r in rankings[:20]
            ],
            "player_stats": [
                {
                    "player": s.player,
                    "org": s.org,
                    "rating": s.rating,
                    "acs": s.acs,
                    "kd": s.kd,
                    "kast": s.kast,
                }
                for s in stats[:30]
            ],
            "source": "vlr",
        }
