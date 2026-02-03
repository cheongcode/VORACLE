"""
API Routers
"""

from apps.api.routers.report import router as report_router
from apps.api.routers.team import router as team_router

__all__ = ["report_router", "team_router"]
