'use client';

import { TeamOverview } from '@/types/report';
import { formatPercent } from '@/lib/utils';
import { CircularProgress } from '@/components/ui/Progress';
import { Badge } from '@/components/ui/Badge';
import { motion } from 'framer-motion';
import { Calendar, Trophy, TrendingUp } from 'lucide-react';

interface TeamHeaderProps {
  team: TeamOverview;
}

export function TeamHeader({ team }: TeamHeaderProps) {
  const winRatePercent = team.overall_win_rate * 100;

  return (
    <motion.div
      className="rounded-xl border border-valorant-border bg-gradient-to-br from-valorant-card to-valorant-dark p-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        {/* Team Info */}
        <div className="flex items-center gap-6">
          {/* Team Logo Placeholder */}
          <motion.div
            className="relative flex h-20 w-20 items-center justify-center rounded-xl bg-valorant-dark border border-c9-cyan/30"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2, type: 'spring' }}
          >
            <span className="text-3xl font-bold text-c9-cyan">
              {team.name.charAt(0)}
            </span>
            <div className="absolute inset-0 rounded-xl bg-c9-cyan/10 blur-lg" />
          </motion.div>

          <div>
            <motion.h1
              className="text-3xl font-bold tracking-tight text-white"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              {team.name}
            </motion.h1>
            <motion.div
              className="mt-2 flex flex-wrap items-center gap-3"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <Badge variant="cyan" size="sm">
                <Trophy className="mr-1 h-3 w-3" />
                Scouting Report
              </Badge>
              <div className="flex items-center gap-1 text-sm text-text-secondary">
                <Calendar className="h-4 w-4" />
                <span>{team.date_range}</span>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Win Rate Circle */}
        <motion.div
          className="flex items-center gap-6"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="text-right hidden md:block">
            <p className="text-sm font-medium uppercase tracking-wider text-text-secondary">
              Overall Win Rate
            </p>
            <p className="text-sm text-text-muted">
              {team.matches_analyzed} matches analyzed
            </p>
          </div>

          <CircularProgress value={winRatePercent} size={100} strokeWidth={8}>
            <div className="text-center">
              <motion.span
                className="text-2xl font-bold text-white"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 1 }}
              >
                {formatPercent(team.overall_win_rate)}
              </motion.span>
              <p className="text-xs text-text-secondary">Win Rate</p>
            </div>
          </CircularProgress>
        </motion.div>
      </div>

      {/* Quick Stats */}
      <motion.div
        className="mt-6 grid grid-cols-2 gap-4 border-t border-valorant-border pt-6 md:grid-cols-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <QuickStat
          icon={<TrendingUp className="h-4 w-4" />}
          label="Matches"
          value={team.matches_analyzed.toString()}
        />
        <QuickStat
          icon={<Trophy className="h-4 w-4" />}
          label="Wins"
          value={Math.round(team.matches_analyzed * team.overall_win_rate).toString()}
        />
        <QuickStat
          label="Losses"
          value={Math.round(team.matches_analyzed * (1 - team.overall_win_rate)).toString()}
        />
        <QuickStat
          label="Period"
          value={team.date_range.split(' to ')[0] || 'Recent'}
        />
      </motion.div>
    </motion.div>
  );
}

function QuickStat({
  icon,
  label,
  value,
}: {
  icon?: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-3">
      {icon && (
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-c9-cyan/10 text-c9-cyan">
          {icon}
        </div>
      )}
      <div>
        <p className="text-xs font-medium uppercase tracking-wider text-text-secondary">
          {label}
        </p>
        <p className="text-lg font-semibold text-white">{value}</p>
      </div>
    </div>
  );
}
