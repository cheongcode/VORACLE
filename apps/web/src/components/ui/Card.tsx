'use client';

import { cn } from '@/lib/utils';
import { motion, HTMLMotionProps } from 'framer-motion';
import { ReactNode } from 'react';

interface CardProps extends HTMLMotionProps<'div'> {
  children: ReactNode;
  variant?: 'default' | 'glass' | 'glow';
  hover?: boolean;
}

export function Card({
  children,
  className,
  variant = 'default',
  hover = false,
  ...props
}: CardProps) {
  const variants = {
    default: 'bg-valorant-card border-valorant-border',
    glass: 'bg-valorant-card/60 backdrop-blur-md border-valorant-border/50',
    glow: 'bg-valorant-card border-c9-cyan shadow-glow-sm',
  };

  return (
    <motion.div
      className={cn(
        'rounded-xl border p-6',
        variants[variant],
        hover && 'transition-all duration-300 hover:border-c9-cyan/50 hover:shadow-glow-sm',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function CardHeader({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('mb-4 flex items-center justify-between', className)}>
      {children}
    </div>
  );
}

export function CardTitle({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <h3
      className={cn(
        'text-sm font-semibold uppercase tracking-widest text-text-secondary',
        className
      )}
    >
      {children}
    </h3>
  );
}

export function CardContent({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={cn('', className)}>{children}</div>;
}
