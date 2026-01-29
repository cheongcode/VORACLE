'use client';

import { cn } from '@/lib/utils';
import { CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';

interface ConfidenceBadgeProps {
  level: 'high' | 'medium' | 'low' | string;
  showLabel?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export function ConfidenceBadge({
  level,
  showLabel = true,
  size = 'md',
  className,
}: ConfidenceBadgeProps) {
  const normalizedLevel = level.toLowerCase();
  
  const config = {
    high: {
      icon: CheckCircle,
      color: 'text-status-success',
      bg: 'bg-status-success/10',
      border: 'border-status-success/30',
      label: 'HIGH',
    },
    medium: {
      icon: AlertCircle,
      color: 'text-status-warning',
      bg: 'bg-status-warning/10',
      border: 'border-status-warning/30',
      label: 'MED',
    },
    low: {
      icon: HelpCircle,
      color: 'text-text-secondary',
      bg: 'bg-valorant-border/50',
      border: 'border-valorant-border',
      label: 'LOW',
    },
  };

  const { icon: Icon, color, bg, border, label } = 
    config[normalizedLevel as keyof typeof config] || config.low;

  const sizes = {
    sm: {
      wrapper: 'px-2 py-0.5 gap-1',
      icon: 'h-3 w-3',
      text: 'text-xs',
    },
    md: {
      wrapper: 'px-2.5 py-1 gap-1.5',
      icon: 'h-4 w-4',
      text: 'text-xs',
    },
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border font-medium',
        bg,
        border,
        sizes[size].wrapper,
        className
      )}
    >
      <Icon className={cn(sizes[size].icon, color)} />
      {showLabel && (
        <span className={cn(sizes[size].text, color)}>
          {label}
        </span>
      )}
    </span>
  );
}

interface SeverityBadgeProps {
  level: 'HIGH' | 'MED' | 'LOW' | string;
  showLabel?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export function SeverityBadge({
  level,
  showLabel = true,
  size = 'md',
  className,
}: SeverityBadgeProps) {
  const normalizedLevel = level.toUpperCase();
  
  const config = {
    HIGH: {
      color: 'text-valorant-red',
      bg: 'bg-valorant-red/10',
      border: 'border-valorant-red/30',
    },
    MED: {
      color: 'text-status-warning',
      bg: 'bg-status-warning/10',
      border: 'border-status-warning/30',
    },
    LOW: {
      color: 'text-status-success',
      bg: 'bg-status-success/10',
      border: 'border-status-success/30',
    },
  };

  const { color, bg, border } = 
    config[normalizedLevel as keyof typeof config] || config.LOW;

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border font-bold',
        bg,
        border,
        color,
        sizes[size],
        className
      )}
    >
      {showLabel ? normalizedLevel : '●'}
    </span>
  );
}
