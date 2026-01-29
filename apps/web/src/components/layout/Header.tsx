'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { Activity, Zap } from 'lucide-react';
import Link from 'next/link';

interface HeaderProps {
  className?: string;
}

export function Header({ className }: HeaderProps) {
  return (
    <motion.header
      className={cn(
        'sticky top-0 z-50 border-b border-valorant-border bg-valorant-dark/80 backdrop-blur-md',
        className
      )}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <div className="relative">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-c9-cyan/10 border border-c9-cyan/30">
              <Zap className="h-5 w-5 text-c9-cyan" />
            </div>
            <div className="absolute inset-0 rounded-lg bg-c9-cyan/20 blur-md" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              <span className="text-gradient">VORACLE</span>
            </h1>
            <p className="text-[10px] font-medium uppercase tracking-widest text-text-secondary">
              Scouting Intelligence
            </p>
          </div>
        </Link>

        {/* Nav */}
        <nav className="flex items-center gap-6">
          <Link
            href="/"
            className="text-sm font-medium text-text-secondary transition-colors hover:text-c9-cyan"
          >
            New Report
          </Link>
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Activity className="h-4 w-4 text-status-success" />
            <span>API Connected</span>
          </div>
        </nav>
      </div>
    </motion.header>
  );
}
