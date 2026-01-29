'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchReport } from '@/lib/api';
import type { ScoutingReport } from '@/types/report';

interface UseReportOptions {
  teamName: string;
  nMatches?: number;
  useMock?: boolean;
  autoFetch?: boolean;
}

interface UseReportReturn {
  report: ScoutingReport | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useReport({
  teamName,
  nMatches = 10,
  useMock = true,
  autoFetch = true,
}: UseReportOptions): UseReportReturn {
  const [report, setReport] = useState<ScoutingReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!teamName) return;

    setLoading(true);
    setError(null);

    try {
      const data = await fetchReport(teamName, nMatches, useMock);
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch report');
      setReport(null);
    } finally {
      setLoading(false);
    }
  }, [teamName, nMatches, useMock]);

  useEffect(() => {
    if (autoFetch && teamName) {
      fetchData();
    }
  }, [autoFetch, teamName, fetchData]);

  return {
    report,
    loading,
    error,
    refetch: fetchData,
  };
}
