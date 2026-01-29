'use client';

import { cn } from '@/lib/utils';
import { SeverityBadge, ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  Lightbulb,
  XCircle,
  Database,
  AlertTriangle,
  TrendingUp,
  Map,
  Users,
  Target,
  BarChart,
} from 'lucide-react';
import { useState } from 'react';

interface EvidenceRef {
  table: string;
  filters: Record<string, any>;
  sample_rows: Record<string, any>[];
}

interface InsightData {
  title: string;
  severity: string;
  confidence: string;
  data_point: string;
  interpretation: string;
  recommendation: string;
  what_not_to_do?: string | null;
  evidence_refs: EvidenceRef[];
  impact_score: number;
  category: string;
}

interface InsightCardNewProps {
  insight: InsightData;
  index: number;
}

const categoryIcons: Record<string, React.ReactNode> = {
  trend: <TrendingUp className="h-5 w-5" />,
  loss_pattern: <AlertTriangle className="h-5 w-5" />,
  agent: <Users className="h-5 w-5" />,
  map_veto: <Map className="h-5 w-5" />,
  playbook: <Target className="h-5 w-5" />,
  meta: <BarChart className="h-5 w-5" />,
  general: <Lightbulb className="h-5 w-5" />,
};

export function InsightCardNew({ insight, index }: InsightCardNewProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const severityColors = {
    HIGH: 'border-valorant-red/50 bg-valorant-red/5',
    MED: 'border-status-warning/50 bg-status-warning/5',
    LOW: 'border-status-success/50 bg-status-success/5',
  };

  const iconBgColors = {
    HIGH: 'bg-valorant-red/20 text-valorant-red',
    MED: 'bg-status-warning/20 text-status-warning',
    LOW: 'bg-c9-cyan/20 text-c9-cyan',
  };

  const borderColor = severityColors[insight.severity as keyof typeof severityColors] || severityColors.LOW;
  const iconBg = iconBgColors[insight.severity as keyof typeof iconBgColors] || iconBgColors.LOW;

  return (
    <motion.div
      className={cn(
        'rounded-xl border overflow-hidden transition-all duration-300',
        borderColor,
        'bg-valorant-card/80 backdrop-blur-sm'
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
    >
      {/* Main Header - Clickable */}
      <div
        className="cursor-pointer p-5"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start gap-4">
          {/* Category Icon */}
          <div className={cn('flex-shrink-0 p-2.5 rounded-lg', iconBg)}>
            {categoryIcons[insight.category] || categoryIcons.general}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Title Row */}
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <h3 className="font-semibold text-white">{insight.title}</h3>
              <SeverityBadge level={insight.severity} size="sm" />
              <ConfidenceBadge level={insight.confidence} size="sm" />
            </div>

            {/* Data Point */}
            <p className="text-sm text-c9-cyan font-mono mb-2">
              {insight.data_point}
            </p>

            {/* Interpretation */}
            <p className="text-sm text-text-secondary line-clamp-2">
              {insight.interpretation}
            </p>
          </div>

          {/* Expand Icon */}
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
            className="flex-shrink-0"
          >
            <ChevronDown className="h-5 w-5 text-text-secondary" />
          </motion.div>
        </div>
      </div>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="border-t border-valorant-border px-5 py-4 space-y-4">
              {/* Recommendation */}
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-status-success/20">
                  <Lightbulb className="h-4 w-4 text-status-success" />
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-text-secondary mb-1">
                    Recommendation
                  </p>
                  <p className="text-sm text-white">{insight.recommendation}</p>
                </div>
              </div>

              {/* What NOT to do */}
              {insight.what_not_to_do && (
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-valorant-red/20">
                    <XCircle className="h-4 w-4 text-valorant-red" />
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-text-secondary mb-1">
                      What NOT to Do
                    </p>
                    <p className="text-sm text-white">{insight.what_not_to_do}</p>
                  </div>
                </div>
              )}

              {/* Evidence Drawer */}
              {insight.evidence_refs.length > 0 && (
                <EvidenceDrawer evidenceRefs={insight.evidence_refs} />
              )}

              {/* Footer */}
              <div className="flex items-center gap-4 pt-2 text-xs text-text-muted">
                <span>Category: {insight.category}</span>
                <span>Impact Score: {insight.impact_score.toFixed(2)}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function EvidenceDrawer({ evidenceRefs }: { evidenceRefs: EvidenceRef[] }) {
  const [showEvidence, setShowEvidence] = useState(false);

  return (
    <div className="pt-2">
      <button
        onClick={(e) => {
          e.stopPropagation();
          setShowEvidence(!showEvidence);
        }}
        className="flex items-center gap-2 text-xs font-medium text-text-secondary hover:text-c9-cyan transition-colors"
      >
        <Database className="h-3.5 w-3.5" />
        {showEvidence ? 'Hide' : 'Show'} Evidence ({evidenceRefs.length} sources)
        <ChevronDown
          className={cn(
            'h-3.5 w-3.5 transition-transform',
            showEvidence && 'rotate-180'
          )}
        />
      </button>

      <AnimatePresence>
        {showEvidence && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mt-3 space-y-3"
          >
            {evidenceRefs.map((ref, i) => (
              <div
                key={i}
                className="rounded-lg bg-valorant-dark/50 p-3 text-xs"
              >
                <p className="font-medium text-c9-cyan mb-2">
                  Source: {ref.table}
                </p>
                
                {Object.keys(ref.filters).length > 0 && (
                  <p className="text-text-secondary mb-2">
                    Filters: {JSON.stringify(ref.filters)}
                  </p>
                )}

                {ref.sample_rows.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-valorant-border">
                          {Object.keys(ref.sample_rows[0]).slice(0, 5).map((key) => (
                            <th key={key} className="pb-2 pr-4 text-text-secondary">
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {ref.sample_rows.slice(0, 3).map((row, ri) => (
                          <tr key={ri} className="border-b border-valorant-border/50">
                            {Object.entries(row).slice(0, 5).map(([key, value]) => (
                              <td key={key} className="py-2 pr-4 text-white">
                                {String(value).substring(0, 20)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface InsightsListNewProps {
  insights: InsightData[];
}

export function InsightsListNew({ insights }: InsightsListNewProps) {
  if (insights.length === 0) {
    return (
      <div className="rounded-xl border border-valorant-border bg-valorant-card p-8 text-center">
        <Lightbulb className="mx-auto h-12 w-12 text-text-secondary" />
        <p className="mt-4 text-text-secondary">
          No significant insights detected. Need more match data for analysis.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {insights.map((insight, index) => (
        <InsightCardNew key={index} insight={insight} index={index} />
      ))}
    </div>
  );
}
