"""
Team Router

API endpoints for team search and discovery.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from packages.core.grid.client import GRIDClient, GRIDClientError
from packages.core.grid.mock_data import MOCK_TEAMS
from packages.core.vlr.client import VlrClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/team", tags=["Teams"])


class TeamResult(BaseModel):
    """Team search result."""
    id: str
    name: str


class PopularTeam(BaseModel):
    """Popular team with ranking info."""
    name: str
    rank: str
    region: str
    record: str
    logo: Optional[str] = None


class PopularTeamsResponse(BaseModel):
    """Response for popular teams."""
    teams: list[PopularTeam]
    source: str


class TeamSearchResponse(BaseModel):
    """Response for team search."""
    teams: list[TeamResult]
    total: int
    source: str  # "grid" or "mock"


@router.get("/search", response_model=TeamSearchResponse)
async def search_teams(
    q: str = Query(..., min_length=2, description="Search query (min 2 characters)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return"),
    use_mock: bool = Query(False, description="Use mock data instead of GRID API"),
) -> TeamSearchResponse:
    """
    Search for teams by name.
    
    Args:
        q: Search query string (minimum 2 characters).
        limit: Maximum number of results (1-50).
        use_mock: If true, search mock data only.
        
    Returns:
        List of matching teams with id and name.
    """
    if use_mock:
        # Search mock teams
        results = []
        for team_name, team_data in MOCK_TEAMS.items():
            if q.lower() in team_name.lower():
                results.append(TeamResult(
                    id=team_data["id"],
                    name=team_name,
                ))
        
        return TeamSearchResponse(
            teams=results[:limit],
            total=len(results),
            source="mock",
        )
    
    # Search via GRID API
    try:
        async with GRIDClient() as client:
            teams = await client.search_teams(q, limit)
            
            results = [
                TeamResult(id=t["id"], name=t["name"])
                for t in teams
            ]
            
            return TeamSearchResponse(
                teams=results,
                total=len(results),
                source="grid",
            )
            
    except GRIDClientError as e:
        logger.error(f"GRID API error during team search: {e}")
        
        # Fall back to mock data
        results = []
        for team_name, team_data in MOCK_TEAMS.items():
            if q.lower() in team_name.lower():
                results.append(TeamResult(
                    id=team_data["id"],
                    name=team_name,
                ))
        
        return TeamSearchResponse(
            teams=results[:limit],
            total=len(results),
            source="mock",
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during team search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search teams: {str(e)}",
        )


@router.get("/available")
async def list_available_teams():
    """
    List teams available for testing with mock data.
    
    Returns:
        List of team names that have mock data available.
    """
    return {
        "teams": [
            {"name": name, "id": data["id"]}
            for name, data in MOCK_TEAMS.items()
        ],
        "note": "These teams are available for testing with mock=true",
    }


@router.get("/popular", response_model=PopularTeamsResponse)
async def get_popular_teams(
    regions: str = Query("na,eu,ap,la", description="Comma-separated region codes (na, eu, ap, la, br, kr)"),
    limit: int = Query(5, ge=1, le=20, description="Teams per region"),
) -> PopularTeamsResponse:
    """
    Get popular VALORANT teams with rankings from VLR.
    
    Args:
        regions: Comma-separated list of regions (na, eu, ap, la, br, kr)
        limit: Number of teams to return per region
        
    Returns:
        List of popular teams with their rankings.
    """
    region_list = [r.strip().lower() for r in regions.split(",")]
    all_teams = []
    
    try:
        async with VlrClient() as client:
            for region in region_list:
                try:
                    rankings = await client.get_rankings(region)
                    
                    for team in rankings[:limit]:
                        all_teams.append(PopularTeam(
                            name=team.team,
                            rank=team.rank,
                            region=region.upper(),
                            record=team.record,
                            logo=team.logo if team.logo else None,
                        ))
                except Exception as e:
                    logger.warning(f"Failed to fetch rankings for region {region}: {e}")
                    continue
        
        if all_teams:
            return PopularTeamsResponse(
                teams=all_teams,
                source="vlr",
            )
    except Exception as e:
        logger.error(f"VLR API error: {e}")
    
    # Fallback to hardcoded popular teams
    fallback_teams = [
        PopularTeam(name="Sentinels", rank="1", region="NA", record="52-33", logo=None),
        PopularTeam(name="Cloud9", rank="2", region="NA", record="28-28", logo=None),
        PopularTeam(name="NRG", rank="3", region="NA", record="40-20", logo=None),
        PopularTeam(name="100 Thieves", rank="4", region="NA", record="36-26", logo=None),
        PopularTeam(name="G2 Esports", rank="5", region="NA", record="60-29", logo=None),
        PopularTeam(name="Fnatic", rank="1", region="EU", record="56-28", logo=None),
        PopularTeam(name="Team Vitality", rank="2", region="EU", record="42-30", logo=None),
        PopularTeam(name="Team Liquid", rank="3", region="EU", record="38-25", logo=None),
        PopularTeam(name="LOUD", rank="1", region="LA", record="45-22", logo=None),
        PopularTeam(name="Leviatan", rank="2", region="LA", record="40-28", logo=None),
        PopularTeam(name="DRX", rank="1", region="AP", record="55-20", logo=None),
        PopularTeam(name="Paper Rex", rank="2", region="AP", record="48-25", logo=None),
        PopularTeam(name="T1", rank="3", region="AP", record="42-30", logo=None),
    ]
    
    # Filter by requested regions
    filtered = [t for t in fallback_teams if t.region.lower() in region_list]
    
    return PopularTeamsResponse(
        teams=filtered,
        source="fallback",
    )
