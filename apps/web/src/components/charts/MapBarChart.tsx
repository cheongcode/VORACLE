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
  Cell,
  ReferenceLine,
} from 'recharts';
import { Map, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { MapVeto, MapStats } from '@/types/report';
import { tokens } from '@/styles/tokens';

interface MapBarChartProps {
  mapVeto?: MapVeto[];
  mapStats?: MapStats[];
  showVetoRecommendation?: boolean;
}

export function MapBarChart({ 
  mapVeto = [], 
  mapStats = [],
  showVetoRecommendation = true 
}: MapBarChartProps) {
  // Combine veto and stats data
  const data = mapVeto.length > 0 
    ? mapVeto.map(v => ({
        name: v.map_name,
        winRate: v.win_rate,
        games: v.games,
        wins: v.wins,
        recommendation: v.recommendation,
      }))
    : mapStats.map(s => ({
        name: s.map_name,
        winRate: s.win_rate,
        games: s.games,
        wins: s.wins,
        recommendation: s.win_rate >= 0.55 ? 'PICK' : s.win_rate <= 0.45 ? 'BAN' : 'NEUTRAL',
      }));

  // Sort by win rate descending
  data.sort((a, b) => b.winRate - a.winRate);

  // Get bar color based on recommendation
  const getBarColor = (recommendation: string) => {
    switch (recommendation) {
      case 'PICK': return tokens.colors.veto.pick;
      case 'BAN': return tokens.colors.veto.ban;
      default: return tokens.colors.veto.neutral;
    }
  };

  // Get recommendation icon
  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case 'PICK': return <ThumbsUp className="h-3 w-3" />;
      case 'BAN': return <ThumbsDown className="h-3 w-3" />;
      default: return <Minus className="h-3 w-3" />;
    }
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="rounded-lg border border-border-default bg-bg-elevated px-4 py-3 shadow-lg">
          <p className="font-semibold text-white">{item.name}</p>
          <p className="text-sm text-text-secondary">
            Win Rate: <span className="text-c9-cyan">{(item.winRate * 100).toFixed(0)}%</span>
          </p>
          <p className="text-sm text-text-secondary">
            Record: <span className="text-white">{item.wins}W - {item.games - item.wins}L</span>
          </p>
          {showVetoRecommendation && (
            <p className="mt-1 text-xs" style={{ color: getBarColor(item.recommendation) }}>
              Recommendation: {item.recommendation}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Map className="h-4 w-4 text-c9-cyan" />
            Map Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center text-text-secondary">
            No map data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Map className="h-4 w-4 text-c9-cyan" />
          Map Win Rates
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
              data={data}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 60, bottom: 5 }}
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={tokens.colors.border.subtle}
                horizontal={false}
              />
              <XAxis 
                type="number"
                domain={[0, 1]}
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={{ stroke: tokens.colors.border.default }}
              />
              <YAxis 
                type="category"
                dataKey="name"
                tick={{ fill: tokens.colors.text.primary, fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={55}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
              <ReferenceLine 
                x={0.5} 
                stroke={tokens.colors.text.muted}
                strokeDasharray="5 5"
              />
              <Bar 
                dataKey="winRate" 
                radius={[0, 4, 4, 0]}
                maxBarSize={24}
              >
                {data.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={getBarColor(entry.recommendation)}
                    style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Legend */}
        {showVetoRecommendation && (
          <div className="mt-4 flex justify-center gap-6">
            {[
              { label: 'Pick', color: tokens.colors.veto.pick, icon: <ThumbsUp className="h-3 w-3" /> },
              { label: 'Neutral', color: tokens.colors.veto.neutral, icon: <Minus className="h-3 w-3" /> },
              { label: 'Ban', color: tokens.colors.veto.ban, icon: <ThumbsDown className="h-3 w-3" /> },
            ].map((item) => (
              <motion.div
                key={item.label}
                className="flex items-center gap-2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div 
                  className="flex h-4 w-4 items-center justify-center rounded-sm"
                  style={{ backgroundColor: item.color }}
                >
                  {item.icon}
                </div>
                <span className="text-xs text-text-secondary">{item.label}</span>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
