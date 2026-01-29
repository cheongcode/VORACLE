'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface StatPillProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'cyan';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  animate?: boolean;
}

export function StatPill({
  label,
  value,
  icon,
  trend,
  trendValue,
  variant = 'default',
  size = 'md',
  className,
  animate = true,
}: StatPillProps) {
  const variants = {
    default: 'bg-valorant-card border-valorant-border',
    success: 'bg-status-success/10 border-status-success/30',
    warning: 'bg-status-warning/10 border-status-warning/30',
    danger: 'bg-valorant-red/10 border-valorant-red/30',
    cyan: 'bg-c9-cyan/10 border-c9-cyan/30',
  };

  const sizes = {
    sm: 'px-3 py-2',
    md: 'px-4 py-3',
    lg: 'px-6 py-4',
  };

  const textSizes = {
    sm: { label: 'text-xs', value: 'text-lg' },
    md: { label: 'text-xs', value: 'text-xl' },
    lg: { label: 'text-sm', value: 'text-2xl' },
  };

  const trendColors = {
    up: 'text-status-success',
    down: 'text-status-danger',
    neutral: 'text-text-secondary',
  };

  const content = (
    <div
      className={cn(
        'flex items-center gap-3 rounded-xl border',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {icon && (
        <div className="flex-shrink-0 text-c9-cyan">
          {icon}
        </div>
      )}
      
      <div className="flex-1 min-w-0">
        <p className={cn(
          'font-medium uppercase tracking-wider text-text-secondary',
          textSizes[size].label
        )}>
          {label}
        </p>
        <div className="flex items-baseline gap-2">
          <span className={cn(
            'font-bold text-white tabular-nums',
            textSizes[size].value
          )}>
            {value}
          </span>
          {trend && trendValue && (
            <span className={cn('text-sm', trendColors[trend])}>
              {trend === 'up' && '↑'}
              {trend === 'down' && '↓'}
              {trendValue}
            </span>
          )}
        </div>
      </div>
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}

// Grid of stat pills
interface StatPillGridProps {
  children: ReactNode;
  columns?: 2 | 3 | 4;
  className?: string;
}

export function StatPillGrid({
  children,
  columns = 3,
  className,
}: StatPillGridProps) {
  const gridCols = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={cn('grid gap-4', gridCols[columns], className)}>
      {children}
    </div>
  );
}
