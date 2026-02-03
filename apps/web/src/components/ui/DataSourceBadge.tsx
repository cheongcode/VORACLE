'use client';

import { motion } from 'framer-motion';
import { Database, Cloud, Server, Wifi, HardDrive } from 'lucide-react';
import { tokens } from '@/styles/tokens';

type DataSource = 'grid' | 'vlr' | 'live' | 'mock' | 'cache';

interface DataSourceBadgeProps {
  source: DataSource;
  showIcon?: boolean;
  showLabel?: boolean;
  size?: 'xs' | 'sm' | 'md';
  animated?: boolean;
}

const sourceConfig: Record<DataSource, {
  label: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  description: string;
}> = {
  grid: {
    label: 'GRID',
    icon: Server,
    color: tokens.colors.accent.primary,
    bgColor: tokens.colors.accent.muted,
    description: 'Official esports data from GRID API',
  },
  vlr: {
    label: 'VLR',
    icon: Cloud,
    color: '#FF4655',
    bgColor: 'rgba(255, 70, 85, 0.15)',
    description: 'Live data from vlr.gg',
  },
  live: {
    label: 'LIVE',
    icon: Wifi,
    color: tokens.colors.status.success,
    bgColor: 'rgba(34, 197, 94, 0.15)',
    description: 'Real-time data from GRID + VLR APIs',
  },
  mock: {
    label: 'MOCK',
    icon: HardDrive,
    color: tokens.colors.text.muted,
    bgColor: 'rgba(107, 114, 128, 0.15)',
    description: 'Sample data for demonstration',
  },
  cache: {
    label: 'CACHE',
    icon: Database,
    color: tokens.colors.status.warning,
    bgColor: 'rgba(245, 158, 11, 0.15)',
    description: 'Cached data from previous request',
  },
};

export function DataSourceBadge({ 
  source, 
  showIcon = true, 
  showLabel = true,
  size = 'sm',
  animated = true,
}: DataSourceBadgeProps) {
  const config = sourceConfig[source];
  const Icon = config.icon;

  const sizeClasses = {
    xs: 'px-1.5 py-0.5 text-[10px] gap-1',
    sm: 'px-2 py-1 text-xs gap-1.5',
    md: 'px-3 py-1.5 text-sm gap-2',
  };

  const iconSizes = {
    xs: 'h-2.5 w-2.5',
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
  };

  const Component = animated ? motion.div : 'div';
  const animationProps = animated ? {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    whileHover: { scale: 1.05 },
    transition: { duration: 0.2 },
  } : {};

  return (
    <Component
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses[size]}`}
      style={{
        backgroundColor: config.bgColor,
        color: config.color,
        border: `1px solid ${config.color}40`,
      }}
      title={config.description}
      {...animationProps}
    >
      {showIcon && <Icon className={iconSizes[size]} />}
      {showLabel && <span>{config.label}</span>}
      {source === 'live' && (
        <span 
          className="h-1.5 w-1.5 rounded-full animate-pulse"
          style={{ backgroundColor: config.color }}
        />
      )}
    </Component>
  );
}

// Combined data source indicator showing multiple sources
interface MultiSourceBadgeProps {
  sources: DataSource[];
  size?: 'xs' | 'sm' | 'md';
}

export function MultiSourceBadge({ sources, size = 'sm' }: MultiSourceBadgeProps) {
  if (sources.length === 0) return null;

  // If only one source, show single badge
  if (sources.length === 1) {
    return <DataSourceBadge source={sources[0]} size={size} />;
  }

  return (
    <div className="inline-flex items-center gap-1">
      {sources.map((source, index) => (
        <DataSourceBadge 
          key={source} 
          source={source} 
          size={size}
          showLabel={index === 0}
          animated={false}
        />
      ))}
    </div>
  );
}

// Data source indicator for sections/cards
interface SectionSourceProps {
  source: DataSource;
  label?: string;
}

export function SectionSource({ source, label }: SectionSourceProps) {
  const config = sourceConfig[source];

  return (
    <div className="flex items-center gap-2 text-xs text-text-muted">
      {label && <span>{label}</span>}
      <DataSourceBadge source={source} size="xs" />
    </div>
  );
}

// Full source info panel
interface SourceInfoPanelProps {
  primarySource: DataSource;
  secondarySources?: DataSource[];
  lastUpdated?: Date;
}

export function SourceInfoPanel({ 
  primarySource, 
  secondarySources = [],
  lastUpdated 
}: SourceInfoPanelProps) {
  const primaryConfig = sourceConfig[primarySource];

  return (
    <motion.div
      className="rounded-lg border border-border-subtle bg-bg-secondary p-4"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <DataSourceBadge source={primarySource} size="md" />
            {secondarySources.map(source => (
              <DataSourceBadge 
                key={source} 
                source={source} 
                size="sm"
                showLabel={false}
              />
            ))}
          </div>
          <p className="mt-2 text-sm text-text-secondary">
            {primaryConfig.description}
          </p>
        </div>
        {lastUpdated && (
          <div className="text-right text-xs text-text-muted">
            <p>Last updated</p>
            <p className="font-medium">{lastUpdated.toLocaleTimeString()}</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
