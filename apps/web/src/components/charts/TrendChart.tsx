'use client';

import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { tokens } from '@/styles/tokens';

interface TrendDataPoint {
  match: number;
  winRate: number;
  label: string;
}

interface TrendChartProps {
  data: TrendDataPoint[];
  title?: string;
  showAverage?: boolean;
}

export function TrendChart({ 
  data, 
  title = 'Win Rate Trend',
  showAverage = true 
}: TrendChartProps) {
  // Calculate trend direction
  const recentAvg = data.slice(-3).reduce((acc, d) => acc + d.winRate, 0) / Math.min(3, data.length);
  const olderAvg = data.slice(0, -3).reduce((acc, d) => acc + d.winRate, 0) / Math.max(1, data.length - 3);
  const isImproving = recentAvg > olderAvg;
  const overallAvg = data.reduce((acc, d) => acc + d.winRate, 0) / data.length;

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border border-border-default bg-bg-elevated px-3 py-2 shadow-lg">
          <p className="text-xs text-text-secondary">{payload[0]?.payload?.label || `Match ${label}`}</p>
          <p className="text-sm font-semibold text-c9-cyan">
            {(payload[0].value * 100).toFixed(0)}% Win Rate
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            {isImproving ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
            {title}
          </span>
          <span className={`text-sm font-normal ${isImproving ? 'text-green-500' : 'text-red-500'}`}>
            {isImproving ? 'Improving' : 'Declining'}
          </span>
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
            <LineChart
              data={data}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={tokens.colors.border.subtle}
                vertical={false}
              />
              <XAxis 
                dataKey="match" 
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={{ stroke: tokens.colors.border.default }}
                tickLine={false}
              />
              <YAxis 
                domain={[0, 1]}
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                tick={{ fill: tokens.colors.text.secondary, fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              {showAverage && (
                <ReferenceLine 
                  y={overallAvg} 
                  stroke={tokens.colors.text.muted}
                  strokeDasharray="5 5"
                  label={{
                    value: `Avg: ${(overallAvg * 100).toFixed(0)}%`,
                    position: 'insideTopRight',
                    fill: tokens.colors.text.muted,
                    fontSize: 10,
                  }}
                />
              )}
              <Line
                type="monotone"
                dataKey="winRate"
                stroke={tokens.colors.accent.primary}
                strokeWidth={3}
                dot={{ 
                  fill: tokens.colors.accent.primary, 
                  strokeWidth: 0,
                  r: 4,
                }}
                activeDot={{ 
                  r: 6, 
                  fill: tokens.colors.accent.light,
                  stroke: tokens.colors.accent.primary,
                  strokeWidth: 2,
                }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Stats summary */}
        <div className="mt-4 flex justify-between gap-4">
          <motion.div
            className="flex-1 rounded-lg bg-valorant-dark/50 p-3 text-center"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <p className="text-xs text-text-secondary">Last 3 Matches</p>
            <p className="text-xl font-bold text-c9-cyan">{(recentAvg * 100).toFixed(0)}%</p>
          </motion.div>
          <motion.div
            className="flex-1 rounded-lg bg-valorant-dark/50 p-3 text-center"
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <p className="text-xs text-text-secondary">Overall Average</p>
            <p className="text-xl font-bold text-white">{(overallAvg * 100).toFixed(0)}%</p>
          </motion.div>
        </div>
      </CardContent>
    </Card>
  );
}

// Helper function to generate trend data from report
export function generateTrendData(matchCount: number, overallWinRate: number): TrendDataPoint[] {
  const data: TrendDataPoint[] = [];
  
  // Generate simulated match-by-match data around the overall win rate
  for (let i = 1; i <= matchCount; i++) {
    // Add some variance but trend towards overall win rate
    const variance = (Math.random() - 0.5) * 0.4;
    const winRate = Math.max(0, Math.min(1, overallWinRate + variance));
    
    data.push({
      match: i,
      winRate,
      label: `Match ${i}`,
    });
  }
  
  return data;
}
