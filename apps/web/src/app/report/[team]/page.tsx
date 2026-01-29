'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
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
import { SkeletonReport } from '@/components/ui/Skeleton';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
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
} from 'lucide-react';

export default function ReportPage() {
  const params = useParams();
  const teamName = decodeURIComponent(params.team as string);

  const [report, setReport] = useState<ScoutingReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  useEffect(() => {
    loadReport();
    checkApiStatus();
  }, [teamName]);

  const loadReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchReport(teamName, 10, true);
      setReport(data);
    } catch (err) {
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
        {/* Loading State */}
        {loading && <SkeletonReport />}

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
              onClick={loadReport}
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-c9-cyan px-6 py-2 font-semibold text-valorant-dark hover:bg-c9-cyanLight"
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </button>
          </motion.div>
        )}

        {/* Report Content */}
        {report && !loading && (
          <div className="space-y-8 print:space-y-6">
            {/* Action Bar */}
            <motion.div
              className="flex items-center justify-between print:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="flex items-center gap-4">
                <Badge variant="cyan" size="lg">
                  <FileText className="mr-2 h-4 w-4" />
                  Scouting Report
                </Badge>
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Clock className="h-4 w-4" />
                  Generated {new Date(report.generated_at).toLocaleString()}
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Activity className={apiStatus === 'connected' ? 'h-4 w-4 text-status-success' : 'h-4 w-4 text-status-danger'} />
                  <span className={apiStatus === 'connected' ? 'text-status-success' : 'text-status-danger'}>
                    API {apiStatus === 'connected' ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={loadReport}
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

            {/* Section 1: Team Header */}
            <TeamHeader team={{
              name: report.team_summary.name,
              matches_analyzed: report.team_summary.matches_analyzed,
              overall_win_rate: report.team_summary.overall_win_rate,
              date_range: report.team_summary.date_range,
            }} />

            {/* Section 2: Trend Alerts */}
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

            {/* Section 3: Map Veto Recommendations */}
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

            {/* Section 5: Capabilities Radar */}
            <CapabilitiesChart capabilities={report.capabilities} />

            {/* Section 6: Player Stats */}
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
              first_blood_pct: 0,
            }))} />

            {/* Section 7: Key Insights */}
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

            {/* Section 8: How to Beat Them */}
            {report.how_to_beat.length > 0 && (
              <ChecklistBlock
                title="How to Beat Them"
                items={report.how_to_beat}
                variant="action"
                icon={<Target className="h-5 w-5 text-c9-cyan" />}
              />
            )}

            {/* Section 9: What NOT to Do */}
            {report.what_not_to_do.length > 0 && (
              <ChecklistBlock
                title="What NOT to Do"
                items={report.what_not_to_do}
                variant="warning"
                icon={<XCircle className="h-5 w-5 text-valorant-red" />}
              />
            )}

            {/* Footer Meta */}
            <motion.div
              className="rounded-xl border border-valorant-border bg-valorant-card p-4 text-center text-sm text-text-secondary print:border-gray-300"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              Data Source: {report.meta.data_source || 'mock'} |{' '}
              Matches: {report.meta.matches_found || report.team_summary.matches_analyzed} |{' '}
              Insights: {report.meta.insight_summary?.total || report.key_insights.length}
            </motion.div>
          </div>
        )}
      </main>
    </div>
  );
}
