#!/usr/bin/env python3
"""
Test GRID API access with different queries to find what's available.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.grid.client import GRIDClient, GRIDClientError


async def test_queries():
    async with GRIDClient() as client:
        queries_to_test = [
            # Try titles (game types)
            ("titles", """
                query GetTitles {
                    titles(first: 10) {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
            """, {}),
            
            # Try tournaments
            ("tournaments", """
                query GetTournaments($first: Int!) {
                    tournaments(first: $first) {
                        edges {
                            node {
                                id
                                name
                                startDate
                                endDate
                            }
                        }
                    }
                }
            """, {"first": 5}),
            
            # Try organizations
            ("organizations", """
                query GetOrganizations($first: Int!) {
                    organizations(first: $first) {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
            """, {"first": 5}),
            
            # Try players
            ("players", """
                query GetPlayers($first: Int!) {
                    players(first: $first) {
                        edges {
                            node {
                                id
                                nickname
                            }
                        }
                    }
                }
            """, {"first": 5}),
            
            # Try series without filter
            ("allSeries", """
                query GetAllSeries($first: Int!) {
                    allSeries(
                        first: $first
                        orderBy: START_TIME_SCHEDULED
                        orderDirection: DESC
                    ) {
                        edges {
                            node {
                                id
                                startTimeScheduled
                                type
                            }
                        }
                    }
                }
            """, {"first": 3}),
        ]
        
        for name, query, variables in queries_to_test:
            print(f"\n{'=' * 60}")
            print(f"Testing: {name}")
            print("=" * 60)
            
            try:
                result = await client.query(name, query, variables, use_cache=False)
                print(f"SUCCESS!")
                print(json.dumps(result, indent=2)[:500])
                if len(json.dumps(result)) > 500:
                    print("... (truncated)")
            except GRIDClientError as e:
                print(f"FAILED: {e}")


if __name__ == "__main__":
    asyncio.run(test_queries())
