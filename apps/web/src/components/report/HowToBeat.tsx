'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { motion } from 'framer-motion';
import { Target, Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface HowToBeatProps {
  recommendations: string[];
  teamName: string;
}

export function HowToBeat({ recommendations, teamName }: HowToBeatProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopy = async (text: string, index: number) => {
    await navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <Card variant="glow" className="relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-c9-cyan/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-c9-cyan" />
          <span className="text-white">How to Beat {teamName}</span>
        </CardTitle>
      </CardHeader>

      <CardContent className="relative">
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <motion.div
              key={index}
              className="group relative flex items-start gap-4 rounded-lg bg-valorant-dark/50 p-4 border border-valorant-border/50 hover:border-c9-cyan/30 transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              {/* Number Badge */}
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-c9-cyan text-sm font-bold text-valorant-dark">
                {index + 1}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white leading-relaxed">{rec}</p>
              </div>

              {/* Copy Button */}
              <button
                onClick={() => handleCopy(rec, index)}
                className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Copy to clipboard"
              >
                {copiedIndex === index ? (
                  <Check className="h-4 w-4 text-status-success" />
                ) : (
                  <Copy className="h-4 w-4 text-text-secondary hover:text-c9-cyan" />
                )}
              </button>
            </motion.div>
          ))}
        </div>

        {/* Call to Action */}
        <motion.div
          className="mt-6 rounded-lg bg-c9-cyan/10 border border-c9-cyan/30 p-4 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: recommendations.length * 0.1 }}
        >
          <p className="text-sm text-c9-cyan">
            Use these strategies to exploit {teamName}&apos;s weaknesses
          </p>
        </motion.div>
      </CardContent>
    </Card>
  );
}
