'use client';

import { Header } from '@/components/layout/Header';
import { TeamSearch } from '@/components/search/TeamSearch';
import { motion } from 'framer-motion';
import { Zap, Shield, Target, BarChart3 } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Header />

      {/* Hero Section */}
      <main className="relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-c9-cyan/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-valorant-red/5 rounded-full blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          {/* Title */}
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <motion.div
              className="inline-flex items-center gap-2 rounded-full border border-c9-cyan/30 bg-c9-cyan/10 px-4 py-2 text-sm text-c9-cyan mb-6"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Zap className="h-4 w-4" />
              Cloud9 x JetBrains Hackathon
            </motion.div>

            <h1 className="text-5xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl">
              <span className="text-gradient">VORACLE</span>
            </h1>
            <p className="mt-4 text-xl text-text-secondary sm:text-2xl">
              VALORANT Opponent Scouting Intelligence
            </p>
            <p className="mt-2 text-lg text-text-muted max-w-2xl mx-auto">
              Generate professional scouting reports with AI-powered insights,
              strategic recommendations, and comprehensive opponent analysis.
            </p>
          </motion.div>

          {/* Search */}
          <motion.div
            className="mt-12 relative"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <TeamSearch />
          </motion.div>

          {/* Features */}
          <motion.div
            className="mt-24 grid gap-8 sm:grid-cols-2 lg:grid-cols-4"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <FeatureCard
              icon={<BarChart3 className="h-6 w-6" />}
              title="Deep Analytics"
              description="Comprehensive stats from map win rates to player performance metrics"
              delay={0.6}
            />
            <FeatureCard
              icon={<Target className="h-6 w-6" />}
              title="Actionable Insights"
              description="AI-detected patterns with specific counter-strategy recommendations"
              delay={0.7}
            />
            <FeatureCard
              icon={<Shield className="h-6 w-6" />}
              title="Coach-Ready Reports"
              description="Professional formatting designed for esports coaching staff"
              delay={0.8}
            />
            <FeatureCard
              icon={<Zap className="h-6 w-6" />}
              title="Real-Time Data"
              description="Powered by GRID API with live match data integration"
              delay={0.9}
            />
          </motion.div>
        </div>

        {/* Footer */}
        <footer className="border-t border-valorant-border py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
              <p className="text-sm text-text-secondary">
                Built for the Cloud9 x JetBrains Hackathon
              </p>
              <div className="flex items-center gap-4 text-sm text-text-muted">
                <span>Category 2: Automated Scouting Report Generator</span>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  delay,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  delay: number;
}) {
  return (
    <motion.div
      className="group rounded-xl border border-valorant-border bg-valorant-card/50 p-6 transition-all hover:border-c9-cyan/50 hover:shadow-glow-sm"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-c9-cyan/10 text-c9-cyan transition-colors group-hover:bg-c9-cyan/20">
        {icon}
      </div>
      <h3 className="font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm text-text-secondary">{description}</p>
    </motion.div>
  );
}
