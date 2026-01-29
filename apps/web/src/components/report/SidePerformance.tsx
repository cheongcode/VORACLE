'use client';

import { SideStats, EconomyStats } from '@/types/report';
import { formatPercent, cn, getWinRateColor } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { motion } from 'framer-motion';
import { Swords, Shield, Coins, CircleDollarSign } from 'lucide-react';

interface SidePerformanceProps {
  sides: SideStats[];
  economy: EconomyStats | null;
}

export function SidePerformance({ sides, economy }: SidePerformanceProps) {
  const attack = sides.find((s) => s.side === 'attack');
  const defense = sides.find((s) => s.side === 'defense');

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Attack/Defense Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Swords className="h-4 w-4 text-c9-cyan" />
            Side Performance
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {attack && (
            <SideRow
              icon={<Swords className="h-4 w-4" />}
              label="Attack"
              side={attack}
              color="text-valorant-red"
              bgColor="bg-valorant-red"
              index={0}
            />
          )}
          {defense && (
            <SideRow
              icon={<Shield className="h-4 w-4" />}
              label="Defense"
              side={defense}
              color="text-c9-cyan"
              bgColor="bg-c9-cyan"
              index={1}
            />
          )}
        </CardContent>
      </Card>

      {/* Economy Card */}
      {economy && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Coins className="h-4 w-4 text-c9-cyan" />
              Economy Stats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <EconomyRow
              icon={<CircleDollarSign className="h-4 w-4" />}
              label="Pistol Rounds"
              wins={economy.pistol_wins}
              total={economy.pistol_rounds}
              winRate={economy.pistol_win_rate}
              index={0}
            />
            <EconomyRow
              icon={<Coins className="h-4 w-4" />}
              label="Eco Conversion"
              wins={economy.eco_wins}
              total={economy.eco_rounds}
              winRate={economy.eco_conversion_rate}
              index={1}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function SideRow({
  icon,
  label,
  side,
  color,
  bgColor,
  index,
}: {
  icon: React.ReactNode;
  label: string;
  side: SideStats;
  color: string;
  bgColor: string;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={color}>{icon}</span>
          <span className="text-sm font-medium text-white">{label}</span>
        </div>
        <span className={cn('text-lg font-bold tabular-nums', getWinRateColor(side.win_rate))}>
          {formatPercent(side.win_rate)}
        </span>
      </div>
      <Progress
        value={side.win_rate * 100}
        colorByValue
        animate
        delay={index * 0.1}
      />
      <p className="mt-1 text-xs text-text-secondary">
        {side.rounds_won} / {side.rounds_played} rounds won
      </p>
    </motion.div>
  );
}

function EconomyRow({
  icon,
  label,
  wins,
  total,
  winRate,
  index,
}: {
  icon: React.ReactNode;
  label: string;
  wins: number;
  total: number;
  winRate: number;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-status-warning">{icon}</span>
          <span className="text-sm font-medium text-white">{label}</span>
        </div>
        <span className={cn('text-lg font-bold tabular-nums', getWinRateColor(winRate))}>
          {formatPercent(winRate)}
        </span>
      </div>
      <Progress
        value={winRate * 100}
        colorByValue
        animate
        delay={index * 0.1}
      />
      <p className="mt-1 text-xs text-text-secondary">
        {wins} / {total} rounds won
      </p>
    </motion.div>
  );
}
