"""
GRID GraphQL API Client

Production-ready async client for fetching VALORANT match data from the GRID API.
Includes retry logic, timeout handling, disk-based caching, and structured logging.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

import httpx
from diskcache import Cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)


class GRIDClientError(Exception):
    """Custom exception for GRID API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class GRIDClient:
    """
    Async GraphQL client for the GRID API.
    
    Features:
    - Automatic retries with exponential backoff
    - Request timeout handling
    - Disk-based response caching
    - Structured logging
    - Schema introspection support
    - Environment-based configuration
    
    Usage:
        async with GRIDClient() as client:
            result = await client.query("match_list", query_string, {"team": "Cloud9"})
    """
    
    # GRID GraphQL endpoint
    DEFAULT_API_URL = "https://api.grid.gg/central-data/graphql"
    
    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1.0  # seconds
    MAX_BACKOFF = 10.0  # seconds
    
    # Timeout configuration
    DEFAULT_TIMEOUT = 30.0  # seconds
    
    # Introspection query
    INTROSPECTION_QUERY = """
    query IntrospectionQuery {
        __schema {
            queryType { name }
            mutationType { name }
            types {
                kind
                name
                description
                fields(includeDeprecated: true) {
                    name
                    description
                    args {
                        name
                        description
                        type {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                }
                            }
                        }
                        defaultValue
                    }
                    type {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                            }
                        }
                    }
                    isDeprecated
                    deprecationReason
                }
                inputFields {
                    name
                    description
                    type {
                        kind
                        name
                        ofType {
                            kind
                            name
                        }
                    }
                    defaultValue
                }
                interfaces {
                    kind
                    name
                }
                enumValues(includeDeprecated: true) {
                    name
                    description
                    isDeprecated
                    deprecationReason
                }
                possibleTypes {
                    kind
                    name
                }
            }
            directives {
                name
                description
                locations
                args {
                    name
                    description
                    type {
                        kind
                        name
                        ofType {
                            kind
                            name
                        }
                    }
                    defaultValue
                }
            }
        }
    }
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize the GRID client.
        
        Args:
            api_key: GRID API key. Falls back to GRID_API_KEY env var.
            api_url: GRID API URL. Falls back to GRID_API_URL env var.
            cache_dir: Directory for disk cache. Falls back to CACHE_DIR env var.
            cache_ttl: Cache time-to-live in seconds. Falls back to CACHE_TTL env var.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or os.getenv("GRID_API_KEY")
        if not self.api_key:
            raise GRIDClientError(
                "GRID API key not provided. Set GRID_API_KEY environment variable."
            )
        
        self.api_url = api_url or os.getenv("GRID_API_URL", self.DEFAULT_API_URL)
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        
        # Initialize cache
        cache_path = cache_dir or os.getenv("CACHE_DIR", ".cache")
        self.cache_ttl = cache_ttl or int(os.getenv("CACHE_TTL", "3600"))
        self.cache = Cache(cache_path)
        
        # HTTP client (initialized in __aenter__)
        self._client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"GRIDClient initialized with API URL: {self.api_url}")
    
    async def __aenter__(self) -> "GRIDClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
            },
        )
        logger.debug("HTTP client initialized")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.debug("HTTP client closed")
    
    def _cache_key(self, query: str, variables: dict[str, Any]) -> str:
        """
        Generate a cache key from query and variables.
        
        Args:
            query: GraphQL query string.
            variables: Query variables.
            
        Returns:
            SHA256 hash of query + variables as cache key.
        """
        content = json.dumps({"query": query, "variables": variables}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def query(
        self,
        name: str,
        gql: str,
        variables: Optional[dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Execute a GraphQL query against the GRID API.
        
        Args:
            name: Human-readable name for the query (for logging).
            gql: GraphQL query string.
            variables: Query variables dictionary.
            use_cache: Whether to use cached responses.
            
        Returns:
            Parsed JSON response data.
            
        Raises:
            GRIDClientError: If the request fails after all retries.
        """
        if self._client is None:
            raise GRIDClientError(
                "Client not initialized. Use 'async with GRIDClient() as client:'"
            )
        
        variables = variables or {}
        
        # Check cache first
        cache_key = self._cache_key(gql, variables)
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for query '{name}'")
                return cached
        
        logger.info(f"Executing query '{name}' with variables: {list(variables.keys())}")
        
        # Execute query with retries
        last_error: Optional[Exception] = None
        backoff = self.INITIAL_BACKOFF
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.debug(f"Query '{name}' attempt {attempt}/{self.MAX_RETRIES}")
                
                response = await self._client.post(
                    self.api_url,
                    json={"query": gql, "variables": variables},
                )
                
                # Log response details
                logger.debug(f"Response status: {response.status_code}")
                
                response.raise_for_status()
                
                result = response.json()
                
                # Check for GraphQL errors
                if "errors" in result:
                    error_messages = [e.get("message", "Unknown error") for e in result["errors"]]
                    error_str = "; ".join(error_messages)
                    logger.error(f"GraphQL errors for query '{name}': {error_str}")
                    raise GRIDClientError(
                        f"GraphQL errors: {error_str}",
                        status_code=response.status_code,
                        response_body=response.text[:500],
                    )
                
                data = result.get("data", {})
                
                # Cache successful response
                if use_cache:
                    self.cache.set(cache_key, data, expire=self.cache_ttl)
                    logger.debug(f"Cached response for query '{name}'")
                
                logger.info(f"Query '{name}' completed successfully")
                return data
                
            except httpx.TimeoutException as e:
                last_error = GRIDClientError(
                    f"Request timeout for query '{name}': {e}",
                    status_code=None,
                )
                logger.warning(f"Timeout on attempt {attempt} for query '{name}'")
                
            except httpx.HTTPStatusError as e:
                last_error = GRIDClientError(
                    f"HTTP error {e.response.status_code} for query '{name}'",
                    status_code=e.response.status_code,
                    response_body=e.response.text[:500],
                )
                logger.warning(f"HTTP {e.response.status_code} on attempt {attempt} for query '{name}'")
                
            except httpx.RequestError as e:
                last_error = GRIDClientError(f"Request failed for query '{name}': {e}")
                logger.warning(f"Request error on attempt {attempt} for query '{name}': {e}")
                
            except json.JSONDecodeError as e:
                last_error = GRIDClientError(f"Invalid JSON response for query '{name}': {e}")
                logger.error(f"JSON decode error for query '{name}'")
            
            # Wait before retry (with exponential backoff)
            if attempt < self.MAX_RETRIES:
                logger.debug(f"Waiting {backoff:.1f}s before retry")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self.MAX_BACKOFF)
        
        # All retries exhausted
        logger.error(f"Query '{name}' failed after {self.MAX_RETRIES} attempts")
        raise last_error or GRIDClientError(f"Query '{name}' failed after {self.MAX_RETRIES} attempts")
    
    async def introspect(self) -> dict[str, Any]:
        """
        Fetch GraphQL schema via introspection query.
        
        Returns:
            Full schema introspection result.
        """
        logger.info("Fetching GraphQL schema via introspection")
        return await self.query(
            "introspection",
            self.INTROSPECTION_QUERY,
            {},
            use_cache=False,  # Always fetch fresh schema
        )
    
    async def search_teams(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search for teams by name.
        
        Args:
            query: Search query string.
            limit: Maximum number of results.
            
        Returns:
            List of team objects with id and name.
        """
        gql = """
        query SearchTeams($query: String!, $first: Int!) {
            teams(filter: { name: { contains: $query } }, first: $first) {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
        """
        
        result = await self.query(
            "search_teams",
            gql,
            {"query": query, "first": limit},
        )
        
        teams = []
        edges = result.get("teams", {}).get("edges", [])
        for edge in edges:
            node = edge.get("node", {})
            if node.get("id") and node.get("name"):
                teams.append({
                    "id": node["id"],
                    "name": node["name"],
                })
        
        logger.info(f"Found {len(teams)} teams matching '{query}'")
        return teams
    
    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cache_stats(self) -> dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache size and volume information.
        """
        return {
            "size": len(self.cache),
            "volume": self.cache.volume(),
        }


# Singleton-style helper for simple usage
_default_client: Optional[GRIDClient] = None


async def get_client() -> GRIDClient:
    """Get or create the default GRID client."""
    global _default_client
    if _default_client is None:
        _default_client = GRIDClient()
    return _default_client
