'use client';

import { TeamCapabilities } from '@/types/report';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { motion } from 'framer-motion';
import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from 'recharts';
import { Activity } from 'lucide-react';

interface CapabilitiesChartProps {
  capabilities: TeamCapabilities;
}

export function CapabilitiesChart({ capabilities }: CapabilitiesChartProps) {
  const data = [
    { subject: 'Pistol', value: capabilities.pistol, fullMark: 100 },
    { subject: 'Economy', value: capabilities.economy, fullMark: 100 },
    { subject: 'First Bloods', value: capabilities.first_bloods, fullMark: 100 },
    { subject: 'Attack', value: capabilities.attack, fullMark: 100 },
    { subject: 'Defense', value: capabilities.defense, fullMark: 100 },
    { subject: 'Consistency', value: capabilities.consistency, fullMark: 100 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-c9-cyan" />
          Team Capabilities
        </CardTitle>
      </CardHeader>
      <CardContent>
        <motion.div
          className="h-64 w-full"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <RechartsRadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
              <PolarGrid stroke="#2A3A4D" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: '#8B9EB7', fontSize: 11 }}
              />
              <Radar
                name="Capabilities"
                dataKey="value"
                stroke="#00AEEF"
                fill="#00AEEF"
                fillOpacity={0.3}
                strokeWidth={2}
              />
            </RechartsRadarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Legend */}
        <div className="mt-4 grid grid-cols-2 gap-2">
          {data.map((item, index) => (
            <motion.div
              key={item.subject}
              className="flex items-center justify-between rounded bg-valorant-dark/50 px-3 py-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <span className="text-xs text-text-secondary">{item.subject}</span>
              <span className="text-sm font-semibold text-c9-cyan">
                {item.value.toFixed(0)}
              </span>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
