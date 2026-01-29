"""
Report Router

API endpoints for generating scouting reports.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from packages.core.report.build import build_report, build_debug_report
from packages.core.report.models import ScoutingReport, DebugReport

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Reports"])


@router.get("/report", response_model=ScoutingReport)
async def get_report(
    team: str = Query(..., description="Team name to generate report for"),
    n: int = Query(10, ge=1, le=50, description="Number of matches to analyze"),
    mock: bool = Query(True, description="Use mock data instead of GRID API"),
) -> ScoutingReport:
    """
    Generate a scouting report for a VALORANT team.
    
    This endpoint fetches recent match data, computes metrics,
    generates insights, and returns a complete scouting report.
    
    Args:
        team: Name of the team to analyze.
        n: Number of recent matches to include (1-50).
        mock: If true, use mock data for testing.
        
    Returns:
        Complete scouting report with insights and recommendations.
    """
    logger.info(f"Generating report for team: {team} (n={n}, mock={mock})")
    
    try:
        report = await build_report(
            team_name=team,
            n_matches=n,
            use_mock=mock,
        )
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report for {team}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/report/debug", response_model=DebugReport)
async def get_debug_report(
    team: str = Query(..., description="Team name"),
    n: int = Query(10, ge=1, le=50, description="Number of matches"),
    mock: bool = Query(True, description="Use mock data"),
) -> DebugReport:
    """
    Generate a debug report with raw DataFrame info.
    
    This endpoint is useful for debugging data parsing and
    understanding the underlying data structure.
    
    Args:
        team: Name of the team.
        n: Number of matches to analyze.
        mock: Use mock data.
        
    Returns:
        Debug report with DataFrame shapes, columns, and sample rows.
    """
    logger.info(f"Generating debug report for team: {team}")
    
    try:
        debug = await build_debug_report(
            team_name=team,
            n_matches=n,
            use_mock=mock,
        )
        return debug
        
    except Exception as e:
        logger.error(f"Failed to generate debug report for {team}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate debug report: {str(e)}",
        )


@router.get("/report/teams")
async def list_available_teams():
    """
    List available teams for testing with mock data.
    
    Returns:
        List of team names that have mock data available.
    """
    from packages.core.grid.mock_data import MOCK_TEAMS
    
    return {
        "teams": list(MOCK_TEAMS.keys()),
        "note": "These teams are available for testing with mock=true",
    }
