'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Header } from '@/components/layout/Header';
import { TeamHeader } from '@/components/report/TeamHeader';
import { MapPerformance } from '@/components/report/MapPerformance';
import { PlayerStats } from '@/components/report/PlayerStats';
import { InsightsListNew } from '@/components/report/InsightCardNew';
import { CapabilitiesChart } from '@/components/report/RadarChart';
import { SidePerformance } from '@/components/report/SidePerformance';
import { MapVetoGrid, MapVetoSummary } from '@/components/report/MapVetoCard';
import { TrendAlertsList } from '@/components/ui/TrendAlertStrip';
import { ChecklistBlock } from '@/components/ui/ChecklistBlock';
import { SkeletonReport, FadeIn, Stagger, StaggerItem } from '@/components/ui/Skeleton';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { TrendChart, generateTrendData } from '@/components/charts/TrendChart';
import { MapBarChart } from '@/components/charts/MapBarChart';
import { PlayerComparison, PlayerImpactChart } from '@/components/charts/PlayerComparison';
import { fetchReport, checkHealth } from '@/lib/api';
import type { ScoutingReport } from '@/types/report';
import {
  Download,
  RefreshCw,
  AlertCircle,
  Clock,
  FileText,
  Activity,
  TrendingUp,
  Map,
  Target,
  XCircle,
  Wifi,
  WifiOff,
  Database,
} from 'lucide-react';

export default function ReportPage() {
  const params = useParams();
  const teamName = decodeURIComponent(params.team as string);

  const [report, setReport] = useState<ScoutingReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [useLiveData, setUseLiveData] = useState(true);

  useEffect(() => {
    loadReport(useLiveData);
    checkApiStatus();
  }, [teamName]);

  const loadReport = async (useLiveData: boolean = false) => {
    setLoading(true);
    setError(null);

    try {
      // Try live data first, fall back to mock if it fails
      const data = await fetchReport(teamName, 10, !useLiveData);
      setReport(data);
    } catch (err) {
      // If live data fails, try mock data
      if (useLiveData) {
        try {
          const mockData = await fetchReport(teamName, 10, true);
          setReport(mockData);
          return;
        } catch {
          // Both failed
        }
      }
      setError(err instanceof Error ? err.message : 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const checkApiStatus = async () => {
    const health = await checkHealth();
    setApiStatus(health.status === 'healthy' ? 'connected' : 'disconnected');
  };

  const handleExportPDF = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-valorant-dark print:bg-white">
      <Header />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 print:max-w-none print:px-8">
        <AnimatePresence mode="wait">
          {/* Loading State */}
          {loading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <SkeletonReport />
            </motion.div>
          )}

        {/* Error State */}
        {error && (
          <motion.div
            className="rounded-xl border border-valorant-red/50 bg-valorant-red/10 p-8 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <AlertCircle className="mx-auto h-12 w-12 text-valorant-red" />
            <h2 className="mt-4 text-xl font-semibold text-white">
              Error Loading Report
            </h2>
            <p className="mt-2 text-text-secondary">{error}</p>
            <button
              onClick={() => loadReport()}
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-c9-cyan px-6 py-2 font-semibold text-valorant-dark hover:bg-c9-cyanLight"
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </button>
          </motion.div>
        )}

          {/* Report Content */}
          {report && !loading && (
            <motion.div 
              key="report"
              className="space-y-8 print:space-y-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
            {/* Action Bar */}
            <motion.div
              className="flex flex-wrap items-center justify-between gap-4 print:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="flex flex-wrap items-center gap-4">
                <Badge variant="cyan" size="lg">
                  <FileText className="mr-2 h-4 w-4" />
                  Scouting Report
                </Badge>
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Clock className="h-4 w-4" />
                  Generated {new Date(report.generated_at).toLocaleString()}
                </div>
                {/* Data Source Badge */}
                <div className="flex items-center gap-2 rounded-full border border-border-default bg-bg-secondary px-3 py-1 text-xs">
                  <Database className="h-3 w-3" />
                  <span className="text-text-secondary">Source:</span>
                  <span className={report.meta.data_source === 'live' ? 'text-status-success font-medium' : 'text-text-muted'}>
                    {report.meta.data_source === 'live' ? 'GRID + VLR' : 'Mock Data'}
                  </span>
                </div>
                {/* API Status */}
                <div className="flex items-center gap-2 text-sm">
                  {apiStatus === 'connected' ? (
                    <Wifi className="h-4 w-4 text-status-success" />
                  ) : (
                    <WifiOff className="h-4 w-4 text-status-danger" />
                  )}
                  <span className={apiStatus === 'connected' ? 'text-status-success' : 'text-status-danger'}>
                    {apiStatus === 'connected' ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {/* Data source toggle */}
                <div className="flex items-center rounded-lg border border-border-default overflow-hidden">
                  <button
                    onClick={() => { setUseLiveData(true); loadReport(true); }}
                    className={`px-3 py-2 text-xs font-medium transition-colors ${
                      useLiveData 
                        ? 'bg-c9-cyan text-valorant-dark' 
                        : 'text-text-secondary hover:text-white'
                    }`}
                  >
                    <Wifi className="h-3 w-3 inline mr-1" />
                    Live
                  </button>
                  <button
                    onClick={() => { setUseLiveData(false); loadReport(false); }}
                    className={`px-3 py-2 text-xs font-medium transition-colors ${
                      !useLiveData 
                        ? 'bg-text-muted text-white' 
                        : 'text-text-secondary hover:text-white'
                    }`}
                  >
                    <Database className="h-3 w-3 inline mr-1" />
                    Mock
                  </button>
                </div>
                <button
                  onClick={() => loadReport(useLiveData)}
                  className="flex items-center gap-2 rounded-lg border border-valorant-border px-4 py-2 text-sm font-medium text-text-secondary hover:border-c9-cyan hover:text-c9-cyan transition-colors"
                >
                  <RefreshCw className="h-4 w-4" />
                  Refresh
                </button>
                <button
                  onClick={handleExportPDF}
                  className="flex items-center gap-2 rounded-lg bg-c9-cyan px-4 py-2 text-sm font-semibold text-valorant-dark hover:bg-c9-cyanLight transition-colors"
                >
                  <Download className="h-4 w-4" />
                  Export PDF
                </button>
              </div>
            </motion.div>

            {/* Data Quality Warning */}
            {report.meta.data_quality && report.meta.data_quality !== 'good' && (
              <motion.div
                className="rounded-xl border border-yellow-500/50 bg-yellow-500/10 p-4 print:hidden"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-yellow-500">
                      {report.meta.data_quality === 'rankings_only' 
                        ? 'Limited Data Available'
                        : report.meta.data_quality === 'partial'
                        ? 'Partial Data Available'
                        : 'Data Quality Notice'}
                    </h3>
                    <p className="mt-1 text-sm text-text-secondary">
                      {report.meta.data_quality === 'rankings_only' 
                        ? 'Only team rankings data is available from VLR. Win rate is from the overall W-L record. Individual match details and round-level statistics may be estimated.'
                        : report.meta.data_quality === 'partial'
                        ? 'Some data is missing. Player statistics or match details may be incomplete.'
                        : report.meta.data_quality === 'mock_fallback'
                        ? 'Live data was unavailable. Showing simulated data for demonstration.'
                        : 'Some statistics may be limited due to data availability.'}
                    </p>
                    {report.meta.team_info?.record && (
                      <p className="mt-2 text-sm">
                        <span className="text-text-muted">VLR Record: </span>
                        <span className="text-c9-cyan font-medium">{report.meta.team_info.record}</span>
                        {report.meta.team_info.rank && (
                          <>
                            <span className="text-text-muted"> | Rank: </span>
                            <span className="text-c9-cyan font-medium">#{report.meta.team_info.rank}</span>
                          </>
                        )}
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Section 1: Team Header */}
            <TeamHeader team={{
              name: report.team_summary.name,
              matches_analyzed: report.team_summary.matches_analyzed,
              overall_win_rate: report.team_summary.overall_win_rate,
              date_range: report.team_summary.date_range,
            }} />

            {/* Section 2: Win Rate Trend Chart + Trend Alerts */}
            <div className="grid gap-6 lg:grid-cols-2">
              <TrendChart 
                data={generateTrendData(
                  report.team_summary.matches_analyzed,
                  report.team_summary.overall_win_rate
                )}
                title="Win Rate Trend"
              />
              {report.trend_alerts.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-c9-cyan" />
                      Trend Alerts (Last 3 vs Last 10)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <TrendAlertsList
                      alerts={report.trend_alerts.map(a => ({
                        metric: a.metric,
                        last3: a.last_3,
                        last10: a.last_10,
                        changePct: a.change_pct,
                        direction: a.direction,
                        significance: a.significance,
                      }))}
                    />
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Section 3: Map Analysis */}
            <div className="grid gap-6 lg:grid-cols-2">
              <MapBarChart 
                mapVeto={report.map_veto}
                mapStats={report.map_performance}
                showVetoRecommendation={true}
              />
              {report.map_veto.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Map className="h-4 w-4 text-c9-cyan" />
                      Map Veto Recommendations
                    </CardTitle>
                    <MapVetoSummary vetos={report.map_veto} />
                  </CardHeader>
                  <CardContent>
                    <MapVetoGrid vetos={report.map_veto} />
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Section 4: Performance Grid */}
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-1">
                <MapPerformance maps={report.map_performance} />
              </div>
              <div className="lg:col-span-2">
                <SidePerformance
                  sides={report.side_performance}
                  economy={report.economy_stats}
                />
              </div>
            </div>

            {/* Section 5: Team Capabilities + Player Comparison */}
            <div className="grid gap-6 lg:grid-cols-2">
              <CapabilitiesChart capabilities={report.capabilities} />
              <PlayerComparison players={report.player_stats} />
            </div>

            {/* Section 6: Player Impact Chart */}
            {report.player_stats.length > 0 && (
              <PlayerImpactChart players={report.player_stats} />
            )}

            {/* Section 7: Player Stats Details */}
            <PlayerStats players={report.player_stats.map(p => ({
              name: p.name,
              games: p.games,
              most_played_agent: p.most_played_agent,
              agent_pool: p.agent_pool,
              avg_acs: p.avg_acs,
              avg_kills: p.avg_kills,
              avg_deaths: p.avg_deaths,
              avg_assists: p.avg_assists,
              kd_ratio: p.kd_ratio,
              first_blood_rate: p.first_blood_rate,
              first_death_rate: p.first_death_rate || 0,
            }))} />

            {/* Section 8: Key Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-c9-cyan" />
                  Key Insights
                </CardTitle>
                <Badge variant="outline" size="sm">
                  {report.key_insights.length} detected
                </Badge>
              </CardHeader>
              <CardContent>
                <InsightsListNew insights={report.key_insights} />
              </CardContent>
            </Card>

            {/* Section 9: Actionable Recommendations */}
            <div className="grid gap-6 lg:grid-cols-2">
              {report.how_to_beat.length > 0 && (
                <ChecklistBlock
                  title="How to Beat Them"
                  items={report.how_to_beat}
                  variant="action"
                  icon={<Target className="h-5 w-5 text-c9-cyan" />}
                />
              )}
              {report.what_not_to_do.length > 0 && (
                <ChecklistBlock
                  title="What NOT to Do"
                  items={report.what_not_to_do}
                  variant="warning"
                  icon={<XCircle className="h-5 w-5 text-valorant-red" />}
                />
              )}
            </div>

            {/* Footer Meta */}
            <motion.div
              className="rounded-xl border border-valorant-border bg-valorant-card p-6 print:border-gray-300"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              <div className="grid gap-4 sm:grid-cols-4 text-center">
                <div>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Data Source</p>
                  <p className="mt-1 font-medium text-white">
                    {report.meta.data_source === 'live' ? 'GRID + VLR APIs' : 'Mock Data'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Matches Analyzed</p>
                  <p className="mt-1 font-medium text-c9-cyan">
                    {report.meta.matches_found || report.team_summary.matches_analyzed}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Insights Generated</p>
                  <p className="mt-1 font-medium text-c9-cyan">
                    {report.meta.insight_summary?.total || report.key_insights.length}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Team Rank</p>
                  <p className="mt-1 font-medium text-white">
                    {report.meta.team_info?.rank ? `#${report.meta.team_info.rank}` : 'N/A'}
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
