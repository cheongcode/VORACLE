'use client';

import { cn, formatPercent } from '@/lib/utils';
import { motion } from 'framer-motion';
import { Ban, Check, Minus, HelpCircle } from 'lucide-react';

interface MapVetoData {
  map_name: string;
  recommendation: string;
  win_rate: number;
  games: number;
  wins: number;
  confidence: string;
}

interface MapVetoCardProps {
  veto: MapVetoData;
  index: number;
}

export function MapVetoCard({ veto, index }: MapVetoCardProps) {
  const recommendations = {
    BAN: {
      icon: Ban,
      color: 'text-valorant-red',
      bg: 'bg-valorant-red/10',
      border: 'border-valorant-red/30',
      label: 'BAN',
    },
    PICK: {
      icon: Check,
      color: 'text-status-success',
      bg: 'bg-status-success/10',
      border: 'border-status-success/30',
      label: 'PICK',
    },
    NEUTRAL: {
      icon: Minus,
      color: 'text-text-secondary',
      bg: 'bg-valorant-border/50',
      border: 'border-valorant-border',
      label: 'NEUTRAL',
    },
    LOW_SAMPLE: {
      icon: HelpCircle,
      color: 'text-status-warning',
      bg: 'bg-status-warning/10',
      border: 'border-status-warning/30',
      label: 'LOW DATA',
    },
  };

  const config = recommendations[veto.recommendation as keyof typeof recommendations] || recommendations.NEUTRAL;
  const Icon = config.icon;

  return (
    <motion.div
      className={cn(
        'rounded-xl border p-4',
        config.border,
        config.bg
      )}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-white">{veto.map_name}</h3>
        <div className={cn(
          'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold',
          config.bg,
          config.color
        )}>
          <Icon className="h-3.5 w-3.5" />
          {config.label}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs text-text-secondary uppercase tracking-wider">Win Rate</p>
          <p className={cn(
            'text-2xl font-bold tabular-nums',
            veto.win_rate >= 0.5 ? 'text-status-success' : 'text-valorant-red'
          )}>
            {formatPercent(veto.win_rate)}
          </p>
        </div>
        <div>
          <p className="text-xs text-text-secondary uppercase tracking-wider">Record</p>
          <p className="text-2xl font-bold tabular-nums text-white">
            {veto.wins}-{veto.games - veto.wins}
          </p>
        </div>
      </div>

      {/* Sample Size */}
      <div className="mt-3 pt-3 border-t border-valorant-border/50">
        <p className="text-xs text-text-muted">
          {veto.games} games played • {veto.confidence} confidence
        </p>
      </div>
    </motion.div>
  );
}

interface MapVetoGridProps {
  vetos: MapVetoData[];
}

export function MapVetoGrid({ vetos }: MapVetoGridProps) {
  // Sort by recommendation priority
  const priority = { BAN: 3, PICK: 2, NEUTRAL: 1, LOW_SAMPLE: 0 };
  const sortedVetos = [...vetos].sort((a, b) => {
    const pa = priority[a.recommendation as keyof typeof priority] || 0;
    const pb = priority[b.recommendation as keyof typeof priority] || 0;
    if (pa !== pb) return pb - pa;
    return Math.abs(b.win_rate - 0.5) - Math.abs(a.win_rate - 0.5);
  });

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {sortedVetos.map((veto, index) => (
        <MapVetoCard key={veto.map_name} veto={veto} index={index} />
      ))}
    </div>
  );
}

// Compact summary for header
export function MapVetoSummary({ vetos }: MapVetoGridProps) {
  const bans = vetos.filter(v => v.recommendation === 'BAN');
  const picks = vetos.filter(v => v.recommendation === 'PICK');

  return (
    <div className="flex items-center gap-4 text-sm">
      {bans.length > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-valorant-red font-medium">BAN:</span>
          <span className="text-white">{bans.map(b => b.map_name).join(', ')}</span>
        </div>
      )}
      {picks.length > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-status-success font-medium">PICK:</span>
          <span className="text-white">{picks.map(p => p.map_name).join(', ')}</span>
        </div>
      )}
    </div>
  );
}
