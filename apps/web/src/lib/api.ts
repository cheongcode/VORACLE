/**
 * API client for VORACLE backend.
 */

import type { ScoutingReport, DebugReport } from '@/types/report';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Fetch a scouting report for a team.
 */
export async function fetchReport(
  teamName: string,
  nMatches: number = 10,
  useMock: boolean = false  // Use live GRID data by default
): Promise<ScoutingReport> {
  const params = new URLSearchParams({
    team: teamName,
    n: nMatches.toString(),
    mock: useMock.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/report?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new APIError(response.status, error.detail || 'Failed to fetch report');
  }

  return response.json();
}

/**
 * Fetch a debug report for a team.
 */
export async function fetchDebugReport(
  teamName: string,
  nMatches: number = 10,
  useMock: boolean = false  // Use live GRID data by default
): Promise<DebugReport> {
  const params = new URLSearchParams({
    team: teamName,
    n: nMatches.toString(),
    mock: useMock.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/report/debug?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new APIError(response.status, error.detail || 'Failed to fetch debug report');
  }

  return response.json();
}

/**
 * Search for teams.
 */
export async function searchTeams(
  query: string,
  limit: number = 10,
  useMock: boolean = false
): Promise<{ teams: { id: string; name: string }[]; total: number; source: string }> {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
    use_mock: useMock.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/team/search?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    // Return mock teams as fallback
    return {
      teams: [
        { id: 'mock_1', name: 'Cloud9' },
        { id: 'mock_2', name: 'Sentinels' },
        { id: 'mock_3', name: 'LOUD' },
      ].filter(t => t.name.toLowerCase().includes(query.toLowerCase())),
      total: 3,
      source: 'fallback',
    };
  }

  return response.json();
}

/**
 * Fetch list of available teams (for mock data).
 */
export async function fetchAvailableTeams(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/report/teams`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    return ['Cloud9', 'Sentinels', 'LOUD']; // Fallback
  }

  const data = await response.json();
  return data.teams || [];
}

/**
 * Check API health.
 */
export async function checkHealth(): Promise<{ status: string; api_key_configured: boolean }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      return { status: 'unhealthy', api_key_configured: false };
    }
    return response.json();
  } catch {
    return { status: 'unreachable', api_key_configured: false };
  }
}

/**
 * Popular team data from VLR rankings.
 */
export interface PopularTeam {
  name: string;
  rank: string;
  region: string;
  record: string;
  logo: string | null;
}

export interface PopularTeamsResponse {
  teams: PopularTeam[];
  source: string;
}

/**
 * Fetch popular VALORANT teams with rankings.
 */
export async function fetchPopularTeams(
  regions: string = 'na,eu,ap,la',
  limit: number = 5
): Promise<PopularTeamsResponse> {
  try {
    const params = new URLSearchParams({
      regions,
      limit: limit.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/team/popular?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch popular teams');
    }

    return response.json();
  } catch (error) {
    console.warn('Failed to fetch popular teams from API:', error);
    
    // Return fallback data
    return {
      teams: [
        { name: 'Sentinels', rank: '1', region: 'NA', record: '52-33', logo: null },
        { name: 'Cloud9', rank: '2', region: 'NA', record: '28-28', logo: null },
        { name: 'NRG', rank: '3', region: 'NA', record: '40-20', logo: null },
        { name: '100 Thieves', rank: '4', region: 'NA', record: '36-26', logo: null },
        { name: 'G2 Esports', rank: '5', region: 'NA', record: '60-29', logo: null },
        { name: 'Fnatic', rank: '1', region: 'EU', record: '56-28', logo: null },
        { name: 'LOUD', rank: '1', region: 'LA', record: '45-22', logo: null },
        { name: 'DRX', rank: '1', region: 'AP', record: '55-20', logo: null },
      ],
      source: 'fallback',
    };
  }
}
