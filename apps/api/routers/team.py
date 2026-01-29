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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/team", tags=["Teams"])


class TeamResult(BaseModel):
    """Team search result."""
    id: str
    name: str


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
