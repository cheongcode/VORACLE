#!/usr/bin/env python3
"""
Explore GRID API to understand the data structure.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.grid.client import GRIDClient


async def explore():
    async with GRIDClient() as client:
        # 1. Search for VALORANT teams
        print("=" * 60)
        print("1. SEARCHING FOR VALORANT TEAMS")
        print("=" * 60)
        
        teams_query = """
        query SearchTeams($name: String!, $first: Int!) {
            teams(filter: { name: { contains: $name } }, first: $first) {
                edges {
                    node {
                        id
                        name
                        nameShortened
                        title {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        result = await client.query("search_teams", teams_query, {"name": "Cloud9", "first": 10})
        print(json.dumps(result, indent=2))
        
        # Get team ID for VALORANT team
        team_id = None
        for edge in result.get("teams", {}).get("edges", []):
            node = edge.get("node", {})
            title = node.get("title", {}).get("name", "")
            if "VALORANT" in title.upper():
                team_id = node.get("id")
                print(f"\nFound VALORANT team: {node.get('name')} (ID: {team_id})")
                break
        
        if not team_id:
            # Just use first team
            edges = result.get("teams", {}).get("edges", [])
            if edges:
                team_id = edges[0].get("node", {}).get("id")
                print(f"\nUsing first team: {edges[0].get('node', {}).get('name')} (ID: {team_id})")
        
        if not team_id:
            print("No team found!")
            return
        
        # 2. Get series for this team
        print("\n" + "=" * 60)
        print("2. GETTING RECENT SERIES FOR TEAM")
        print("=" * 60)
        
        series_query = """
        query GetTeamSeries($teamId: ID!, $first: Int!) {
            allSeries(
                filter: { teamId: $teamId }
                first: $first
                orderBy: START_TIME_SCHEDULED
                orderDirection: DESC
            ) {
                edges {
                    node {
                        id
                        startTimeScheduled
                        type
                        format {
                            name
                        }
                        tournament {
                            name
                        }
                        teams {
                            edges {
                                node {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        series_result = await client.query("get_series", series_query, {"teamId": team_id, "first": 5})
        print(json.dumps(series_result, indent=2))
        
        # Get first series ID
        series_edges = series_result.get("allSeries", {}).get("edges", [])
        if not series_edges:
            print("No series found!")
            return
        
        series_id = series_edges[0].get("node", {}).get("id")
        print(f"\nFirst series ID: {series_id}")
        
        # 3. Get series details with matches
        print("\n" + "=" * 60)
        print("3. GETTING SERIES DETAILS")
        print("=" * 60)
        
        series_detail_query = """
        query GetSeriesDetail($seriesId: ID!) {
            series(id: $seriesId) {
                id
                startTimeScheduled
                type
                format {
                    name
                }
                tournament {
                    name
                }
                teams {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
                players {
                    edges {
                        node {
                            id
                            nickname
                        }
                    }
                }
            }
        }
        """
        
        series_detail = await client.query("series_detail", series_detail_query, {"seriesId": series_id})
        print(json.dumps(series_detail, indent=2))


if __name__ == "__main__":
    asyncio.run(explore())
