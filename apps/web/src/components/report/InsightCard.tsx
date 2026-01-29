'use client';

import { Insight } from '@/types/report';
import { cn, getImpactColor, getConfidenceColor } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  ChevronDown,
  Lightbulb,
  Target,
} from 'lucide-react';
import { useState } from 'react';

interface InsightCardProps {
  insight: Insight;
  index: number;
}

export function InsightCard({ insight, index }: InsightCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getIcon = () => {
    switch (insight.impact) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5" />;
      case 'high':
        return <AlertCircle className="h-5 w-5" />;
      case 'medium':
        return <Info className="h-5 w-5" />;
      default:
        return <CheckCircle className="h-5 w-5" />;
    }
  };

  const getIconColor = () => {
    switch (insight.impact) {
      case 'critical':
        return 'text-valorant-red';
      case 'high':
        return 'text-status-warning';
      case 'medium':
        return 'text-c9-cyan';
      default:
        return 'text-status-success';
    }
  };

  const getCategoryIcon = () => {
    switch (insight.category) {
      case 'economy':
        return '💰';
      case 'maps':
        return '🗺️';
      case 'agents':
        return '🎭';
      case 'players':
        return '👤';
      case 'sides':
        return '⚔️';
      default:
        return '📊';
    }
  };

  return (
    <motion.div
      className={cn(
        'group rounded-xl border bg-valorant-card/80 backdrop-blur-sm transition-all duration-300',
        insight.impact === 'critical'
          ? 'border-valorant-red/50'
          : 'border-valorant-border hover:border-c9-cyan/50'
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      {/* Main Content */}
      <div
        className="cursor-pointer p-5"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div
            className={cn(
              'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg',
              insight.impact === 'critical'
                ? 'bg-valorant-red/20'
                : insight.impact === 'high'
                ? 'bg-status-warning/20'
                : 'bg-c9-cyan/20'
            )}
          >
            <span className={getIconColor()}>{getIcon()}</span>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold text-white">{insight.title}</h3>
              <Badge
                variant={
                  insight.impact === 'critical'
                    ? 'danger'
                    : insight.impact === 'high'
                    ? 'warning'
                    : 'cyan'
                }
                size="sm"
              >
                {insight.impact.toUpperCase()}
              </Badge>
              <span className="text-sm">{getCategoryIcon()}</span>
            </div>

            <p className="mt-1 text-sm text-c9-cyan font-mono">
              {insight.data_point}
            </p>

            <p className="mt-2 text-sm text-text-secondary line-clamp-2">
              {insight.interpretation}
            </p>
          </div>

          {/* Expand Button */}
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="h-5 w-5 text-text-secondary" />
          </motion.div>
        </div>
      </div>

      {/* Expanded Content */}
      <motion.div
        initial={false}
        animate={{
          height: isExpanded ? 'auto' : 0,
          opacity: isExpanded ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        <div className="border-t border-valorant-border px-5 py-4">
          <div className="flex items-start gap-3">
            <Lightbulb className="h-5 w-5 text-status-success flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-text-secondary mb-1">
                Recommendation
              </p>
              <p className="text-sm text-white">{insight.recommendation}</p>
            </div>
          </div>

          <div className="mt-4 flex items-center gap-4 text-xs text-text-secondary">
            <span className={cn('flex items-center gap-1', getConfidenceColor(insight.confidence))}>
              <Target className="h-3 w-3" />
              {insight.confidence.toUpperCase()} confidence
            </span>
            <span>Category: {insight.category}</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

interface InsightsListProps {
  insights: Insight[];
}

export function InsightsList({ insights }: InsightsListProps) {
  if (insights.length === 0) {
    return (
      <div className="rounded-xl border border-valorant-border bg-valorant-card p-8 text-center">
        <Info className="mx-auto h-12 w-12 text-text-secondary" />
        <p className="mt-4 text-text-secondary">
          No significant insights detected. Need more match data for analysis.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-6">
        <AlertCircle className="h-5 w-5 text-c9-cyan" />
        <h2 className="text-sm font-semibold uppercase tracking-widest text-text-secondary">
          Key Insights
        </h2>
        <Badge variant="outline" size="sm">
          {insights.length} found
        </Badge>
      </div>

      {insights.map((insight, index) => (
        <InsightCard key={index} insight={insight} index={index} />
      ))}
    </div>
  );
}
