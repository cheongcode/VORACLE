'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export function Skeleton({ className, animate = true }: SkeletonProps) {
  return (
    <div
      className={cn(
        'rounded-md bg-valorant-border/50',
        animate && 'animate-pulse',
        className
      )}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-valorant-border bg-valorant-card p-6">
      <Skeleton className="mb-4 h-4 w-24" />
      <Skeleton className="mb-2 h-8 w-32" />
      <Skeleton className="h-4 w-48" />
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="rounded-xl border border-valorant-border bg-valorant-card p-6">
      <Skeleton className="mb-4 h-4 w-32" />
      <div className="h-64 flex items-end gap-2">
        {[40, 70, 55, 85, 60, 75, 45].map((h, i) => (
          <Skeleton 
            key={i} 
            className="flex-1 rounded-t-md" 
            style={{ height: `${h}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export function SkeletonRadar() {
  return (
    <div className="rounded-xl border border-valorant-border bg-valorant-card p-6">
      <Skeleton className="mb-4 h-4 w-40" />
      <div className="flex justify-center">
        <Skeleton className="h-64 w-64 rounded-full" />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <Skeleton key={i} className="h-10" />
        ))}
      </div>
    </div>
  );
}

export function SkeletonPlayerCard() {
  return (
    <div className="rounded-lg border border-valorant-border bg-valorant-card/50 p-4">
      <div className="flex items-center gap-3">
        <Skeleton className="h-12 w-12 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-16" />
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2">
        <Skeleton className="h-8" />
        <Skeleton className="h-8" />
        <Skeleton className="h-8" />
      </div>
    </div>
  );
}

export function SkeletonInsight() {
  return (
    <div className="rounded-lg border border-valorant-border bg-valorant-card p-4">
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
      <Skeleton className="mt-3 h-16 w-full" />
    </div>
  );
}

export function SkeletonReport() {
  return (
    <motion.div 
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Skeleton className="h-8 w-32 rounded-lg" />
          <Skeleton className="h-6 w-48" />
        </div>
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-24 rounded-lg" />
          <Skeleton className="h-10 w-32 rounded-lg" />
        </div>
      </div>

      {/* Header Skeleton */}
      <div className="rounded-xl border border-valorant-border bg-valorant-card p-8">
        <div className="flex items-center gap-6">
          <Skeleton className="h-20 w-20 rounded-full" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="flex items-center gap-4">
            <Skeleton className="h-24 w-24 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-8 w-20" />
              <Skeleton className="h-4 w-16" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SkeletonChart />
        <SkeletonCard />
      </div>

      {/* Map Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SkeletonChart />
        <SkeletonCard />
      </div>

      {/* Performance Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        <SkeletonCard />
        <div className="lg:col-span-2">
          <SkeletonCard />
        </div>
      </div>

      {/* Capabilities + Players */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SkeletonRadar />
        <SkeletonChart />
      </div>

      {/* Player Cards */}
      <div className="rounded-xl border border-valorant-border bg-valorant-card p-6">
        <Skeleton className="mb-4 h-4 w-32" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <SkeletonPlayerCard />
          <SkeletonPlayerCard />
          <SkeletonPlayerCard />
        </div>
      </div>

      {/* Insights */}
      <div className="rounded-xl border border-valorant-border bg-valorant-card p-6">
        <Skeleton className="mb-4 h-4 w-24" />
        <div className="space-y-3">
          <SkeletonInsight />
          <SkeletonInsight />
          <SkeletonInsight />
        </div>
      </div>

      {/* Checklists */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-valorant-border bg-valorant-card p-6">
          <Skeleton className="mb-4 h-4 w-40" />
          <div className="space-y-2">
            {[1, 2, 3, 4].map(i => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        </div>
        <div className="rounded-xl border border-valorant-border bg-valorant-card p-6">
          <Skeleton className="mb-4 h-4 w-32" />
          <div className="space-y-2">
            {[1, 2, 3, 4].map(i => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <Skeleton className="h-20 w-full rounded-xl" />
    </motion.div>
  );
}

// Fade-in wrapper for smooth transitions
interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
}

export function FadeIn({ children, delay = 0, duration = 0.5, className }: FadeInProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// Stagger children animation wrapper
interface StaggerProps {
  children: React.ReactNode;
  staggerDelay?: number;
  className?: string;
}

export function Stagger({ children, staggerDelay = 0.1, className }: StaggerProps) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: staggerDelay,
          },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
