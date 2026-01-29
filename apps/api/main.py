"""
VORACLE FastAPI Application

Main entry point for the VORACLE scouting report API.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import report_router, team_router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("VORACLE API starting up...")
    yield
    # Shutdown
    print("VORACLE API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="VORACLE",
    description="VALORANT Opponent Scouting Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(report_router, tags=["Reports"])
app.include_router(team_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "VORACLE",
        "description": "VALORANT Opponent Scouting Intelligence System",
        "version": "1.0.0",
        "endpoints": {
            "report": "/report?team=TeamName&n=10",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("GRID_API_KEY")),
    }
