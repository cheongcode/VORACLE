'use client';

import { PlayerStats as PlayerStatsType } from '@/types/report';
import { cn, formatNumber, getAgentRole } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { motion } from 'framer-motion';
import { Users, Crosshair, Skull, Target, Flame } from 'lucide-react';

interface PlayerStatsProps {
  players: PlayerStatsType[];
}

export function PlayerStats({ players }: PlayerStatsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-4 w-4 text-c9-cyan" />
          Player Statistics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-valorant-border">
                <th className="pb-3 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">
                  Player
                </th>
                <th className="pb-3 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">
                  Agent
                </th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">
                  ACS
                </th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">
                  K/D
                </th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">
                  FB/Game
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-valorant-border/50">
              {players.map((player, index) => (
                <PlayerRow key={player.name} player={player} index={index} />
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function PlayerRow({
  player,
  index,
}: {
  player: PlayerStatsType;
  index: number;
}) {
  const role = getAgentRole(player.most_played_agent);
  const isTopACS = index === 0;
  const hasHighFB = player.first_blood_rate >= 2.0;

  return (
    <motion.tr
      className="group"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      {/* Player Name */}
      <td className="py-4">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-lg text-sm font-bold',
              isTopACS
                ? 'bg-c9-cyan/20 text-c9-cyan border border-c9-cyan/30'
                : 'bg-valorant-dark text-text-secondary'
            )}
          >
            {player.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-white">{player.name}</p>
            <p className="text-xs text-text-secondary">
              {player.games} games
            </p>
          </div>
        </div>
      </td>

      {/* Agent */}
      <td className="py-4">
        <div className="flex items-center gap-2">
          <Badge
            variant={role === 'duelist' ? 'danger' : role === 'controller' ? 'cyan' : 'outline'}
            size="sm"
          >
            {player.most_played_agent}
          </Badge>
        </div>
      </td>

      {/* ACS */}
      <td className="py-4 text-right">
        <span
          className={cn(
            'text-lg font-bold tabular-nums',
            isTopACS ? 'text-c9-cyan' : 'text-white'
          )}
        >
          {formatNumber(player.avg_acs, 1)}
        </span>
      </td>

      {/* K/D */}
      <td className="py-4 text-right">
        <span
          className={cn(
            'font-semibold tabular-nums',
            player.kd_ratio >= 1.2
              ? 'text-status-success'
              : player.kd_ratio < 0.9
              ? 'text-status-danger'
              : 'text-white'
          )}
        >
          {formatNumber(player.kd_ratio, 2)}
        </span>
      </td>

      {/* First Bloods */}
      <td className="py-4 text-right">
        <div className="flex items-center justify-end gap-2">
          {hasHighFB && <Flame className="h-4 w-4 text-valorant-red" />}
          <span
            className={cn(
              'font-semibold tabular-nums',
              hasHighFB ? 'text-valorant-red' : 'text-white'
            )}
          >
            {formatNumber(player.first_blood_rate, 1)}
          </span>
        </div>
      </td>
    </motion.tr>
  );
}

// Card version for mobile
export function PlayerStatsCards({ players }: PlayerStatsProps) {
  return (
    <div className="space-y-3">
      {players.map((player, index) => (
        <motion.div
          key={player.name}
          className="rounded-lg border border-valorant-border bg-valorant-card p-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: index * 0.1 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-valorant-dark text-lg font-bold text-c9-cyan">
                {player.name.charAt(0)}
              </div>
              <div>
                <p className="font-semibold text-white">{player.name}</p>
                <Badge variant="outline" size="sm">
                  {player.most_played_agent}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-c9-cyan">
                {formatNumber(player.avg_acs, 0)}
              </p>
              <p className="text-xs text-text-secondary">ACS</p>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-4 border-t border-valorant-border pt-4">
            <StatMini icon={<Crosshair />} label="K/D" value={formatNumber(player.kd_ratio, 2)} />
            <StatMini icon={<Flame />} label="FB" value={formatNumber(player.first_blood_rate, 1)} />
            <StatMini icon={<Target />} label="Games" value={player.games.toString()} />
          </div>
        </motion.div>
      ))}
    </div>
  );
}

function StatMini({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <div className="text-text-secondary">{icon}</div>
      <div>
        <p className="text-xs text-text-secondary">{label}</p>
        <p className="font-semibold text-white">{value}</p>
      </div>
    </div>
  );
}
