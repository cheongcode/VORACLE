'use client';

import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Users, Crosshair, Shield, Zap } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { PlayerStats } from '@/types/report';
import { tokens } from '@/styles/tokens';

interface PlayerComparisonProps {
  players: PlayerStats[];
  metric?: 'acs' | 'kd' | 'all';
}

export function PlayerComparison({ players, metric = 'all' }: PlayerComparisonProps) {
  // Prepare data for the chart
  const chartData = players.slice(0, 5).map(player => ({
    name: player.name.length > 10 ? player.name.substring(0, 10) + '...' : player.name,
    fullName: player.name,
    ACS: Math.round(player.avg_acs),
    'K/D': Math.round(player.kd_ratio * 100) / 100,
    'FB Rate': Math.round(player.first_blood_rate * 100),
    'FD Rate': Math.round(player.first_death_rate * 100),
    agent: player.most_played_agent,
    games: player.games,
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const playerData = payload[0]?.payload;
      return (
        <div className="rounded-lg border border-border-default bg-bg-elevated px-4 py-3 shadow-lg">
          <p className="font-semibold text-white">{playerData?.fullName}</p>
          <p className="text-xs text-text-muted">{playerData?.agent} Main</p>
          <div className="mt-2 space-y-1">
            {payload.map((entry: any, index: number) => (
              <p key={index} className="text-sm">
                <span className="text-text-secondary">{entry.name}: </span>
                <span style={{ color: entry.color }}>{entry.value}</span>
              </p>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  if (players.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-4 w-4 text-c9-cyan" />
            Player Comparison
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center text-text-secondary">
            No player data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-4 w-4 text-c9-cyan" />
          Player Comparison
        </CardTitle>
      </CardHeader>
      <CardContent>
        <motion.div
          className="h-72 w-full"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: -10, bottom: 5 }}
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={tokens.colors.border.subtle}
                vertical={false}
              />
              <XAxis 
                dataKey="name"
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={{ stroke: tokens.colors.border.default }}
                tickLine={false}
              />
              <YAxis 
                yAxisId="left"
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                domain={[0, 3]}
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
              <Legend 
                wrapperStyle={{ paddingTop: 10 }}
                formatter={(value) => <span className="text-xs text-text-secondary">{value}</span>}
              />
              {(metric === 'all' || metric === 'acs') && (
                <Bar 
                  yAxisId="left"
                  dataKey="ACS" 
                  fill={tokens.colors.accent.primary}
                  radius={[4, 4, 0, 0]}
                  maxBarSize={30}
                />
              )}
              {(metric === 'all' || metric === 'kd') && (
                <Bar 
                  yAxisId="right"
                  dataKey="K/D" 
                  fill={tokens.colors.status.success}
                  radius={[4, 4, 0, 0]}
                  maxBarSize={30}
                />
              )}
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Player Cards */}
        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          {players.slice(0, 5).map((player, index) => (
            <motion.div
              key={player.name}
              className="rounded-lg border border-border-subtle bg-valorant-dark/50 p-3"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <p className="truncate text-xs font-medium text-white">{player.name}</p>
              <p className="text-xs text-text-muted">{player.most_played_agent}</p>
              <div className="mt-2 flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <Crosshair className="h-3 w-3 text-c9-cyan" />
                  <span className="text-xs text-c9-cyan">{Math.round(player.avg_acs)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Zap className="h-3 w-3 text-yellow-500" />
                  <span className="text-xs text-yellow-500">{player.kd_ratio.toFixed(2)}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// First Blood / First Death comparison chart
export function PlayerImpactChart({ players }: { players: PlayerStats[] }) {
  const chartData = players.slice(0, 5).map(player => ({
    name: player.name.length > 8 ? player.name.substring(0, 8) + '...' : player.name,
    fullName: player.name,
    'First Bloods': Math.round(player.first_blood_rate * 100),
    'First Deaths': Math.round(player.first_death_rate * 100),
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const playerData = payload[0]?.payload;
      return (
        <div className="rounded-lg border border-border-default bg-bg-elevated px-4 py-3 shadow-lg">
          <p className="font-semibold text-white">{playerData?.fullName}</p>
          <div className="mt-2 space-y-1">
            <p className="text-sm">
              <span className="text-text-secondary">First Bloods: </span>
              <span className="text-green-500">{payload[0]?.value}%</span>
            </p>
            <p className="text-sm">
              <span className="text-text-secondary">First Deaths: </span>
              <span className="text-red-500">{payload[1]?.value}%</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  if (players.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-c9-cyan" />
          Opening Duels
        </CardTitle>
      </CardHeader>
      <CardContent>
        <motion.div
          className="h-64 w-full"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: -10, bottom: 5 }}
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={tokens.colors.border.subtle}
                vertical={false}
              />
              <XAxis 
                dataKey="name"
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={{ stroke: tokens.colors.border.default }}
                tickLine={false}
              />
              <YAxis 
                tickFormatter={(value) => `${value}%`}
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
              <Legend 
                wrapperStyle={{ paddingTop: 10 }}
                formatter={(value) => <span className="text-xs text-text-secondary">{value}</span>}
              />
              <Bar 
                dataKey="First Bloods" 
                fill={tokens.colors.status.success}
                radius={[4, 4, 0, 0]}
                maxBarSize={25}
              />
              <Bar 
                dataKey="First Deaths" 
                fill={tokens.colors.red.primary}
                radius={[4, 4, 0, 0]}
                maxBarSize={25}
              />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </CardContent>
    </Card>
  );
}
