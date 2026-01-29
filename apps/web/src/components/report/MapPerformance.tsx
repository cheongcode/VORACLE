'use client';

import { MapStats } from '@/types/report';
import { formatPercent, getWinRateColor, cn } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { motion } from 'framer-motion';
import { Map, TrendingUp, TrendingDown } from 'lucide-react';

interface MapPerformanceProps {
  maps: MapStats[];
}

export function MapPerformance({ maps }: MapPerformanceProps) {
  // Sort by games played
  const sortedMaps = [...maps].sort((a, b) => b.games - a.games);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Map className="h-4 w-4 text-c9-cyan" />
          Map Performance
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedMaps.map((map, index) => (
            <MapRow key={map.map_name} map={map} index={index} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function MapRow({ map, index }: { map: MapStats; index: number }) {
  const isStrong = map.win_rate >= 0.6;
  const isWeak = map.win_rate < 0.4;

  return (
    <motion.div
      className="group relative"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      <div className="flex items-center gap-4">
        {/* Map Name */}
        <div className="w-24 flex-shrink-0">
          <p className="font-medium text-white">{map.map_name}</p>
          <p className="text-xs text-text-secondary">
            {map.wins}W - {map.losses}L
          </p>
        </div>

        {/* Progress Bar */}
        <div className="flex-1">
          <Progress
            value={map.win_rate * 100}
            colorByValue
            animate
            delay={index * 0.1}
          />
        </div>

        {/* Win Rate */}
        <div className="w-20 text-right">
          <span
            className={cn(
              'text-lg font-bold tabular-nums',
              getWinRateColor(map.win_rate)
            )}
          >
            {formatPercent(map.win_rate)}
          </span>
        </div>

        {/* Trend Indicator */}
        <div className="w-8">
          {isStrong && (
            <TrendingUp className="h-5 w-5 text-status-success" />
          )}
          {isWeak && (
            <TrendingDown className="h-5 w-5 text-status-danger" />
          )}
        </div>
      </div>

      {/* Hover Detail */}
      <div className="absolute inset-0 -z-10 rounded-lg bg-c9-cyan/5 opacity-0 transition-opacity group-hover:opacity-100" />
    </motion.div>
  );
}

// Compact version for smaller displays
export function MapPerformanceCompact({ maps }: MapPerformanceProps) {
  const sortedMaps = [...maps].sort((a, b) => b.win_rate - a.win_rate);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Map className="h-4 w-4 text-c9-cyan" />
          Maps
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {sortedMaps.slice(0, 6).map((map, index) => (
            <motion.div
              key={map.map_name}
              className="flex items-center justify-between rounded-lg bg-valorant-dark/50 px-3 py-2"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <span className="text-sm text-text-secondary">{map.map_name}</span>
              <span
                className={cn(
                  'text-sm font-semibold tabular-nums',
                  getWinRateColor(map.win_rate)
                )}
              >
                {formatPercent(map.win_rate)}
              </span>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
