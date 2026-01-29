'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

interface TrendAlertStripProps {
  metric: string;
  last3: number;
  last10: number;
  changePct: number;
  direction: 'improving' | 'declining';
  significance: 'HIGH' | 'MED' | 'LOW';
  className?: string;
}

export function TrendAlertStrip({
  metric,
  last3,
  last10,
  changePct,
  direction,
  significance,
  className,
}: TrendAlertStripProps) {
  const isImproving = direction === 'improving';
  
  const bgColor = isImproving
    ? 'bg-status-success/10 border-status-success/30'
    : 'bg-valorant-red/10 border-valorant-red/30';
  
  const textColor = isImproving ? 'text-status-success' : 'text-valorant-red';
  const Icon = isImproving ? TrendingUp : TrendingDown;

  const formatMetric = (name: string) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <motion.div
      className={cn(
        'flex items-center justify-between rounded-lg border px-4 py-3',
        bgColor,
        className
      )}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center gap-3">
        <div className={cn('p-1.5 rounded-lg', isImproving ? 'bg-status-success/20' : 'bg-valorant-red/20')}>
          <Icon className={cn('h-4 w-4', textColor)} />
        </div>
        
        <div>
          <p className="text-sm font-medium text-white">
            {formatMetric(metric)} {isImproving ? 'Improving' : 'Declining'}
          </p>
          <p className="text-xs text-text-secondary">
            Last 3: {(last3 * 100).toFixed(0)}% → Last 10: {(last10 * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className={cn('text-lg font-bold tabular-nums', textColor)}>
          {changePct > 0 ? '+' : ''}{changePct.toFixed(0)}%
        </span>
        
        {significance === 'HIGH' && (
          <div className="flex items-center gap-1 px-2 py-1 rounded bg-valorant-red/20 text-valorant-red text-xs font-medium">
            <AlertTriangle className="h-3 w-3" />
            ALERT
          </div>
        )}
      </div>
    </motion.div>
  );
}

interface TrendAlertsListProps {
  alerts: TrendAlertStripProps[];
  className?: string;
}

export function TrendAlertsList({ alerts, className }: TrendAlertsListProps) {
  if (alerts.length === 0) {
    return (
      <div className={cn('text-center py-4 text-text-secondary text-sm', className)}>
        No significant trends detected
      </div>
    );
  }

  return (
    <div className={cn('space-y-2', className)}>
      {alerts.map((alert, index) => (
        <TrendAlertStrip key={`${alert.metric}-${index}`} {...alert} />
      ))}
    </div>
  );
}
