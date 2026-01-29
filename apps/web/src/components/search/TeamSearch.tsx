'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Search, Loader2, Zap, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TeamSearchProps {
  availableTeams?: string[];
}

export function TeamSearch({ availableTeams = ['Cloud9', 'Sentinels', 'LOUD'] }: TeamSearchProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const filteredTeams = availableTeams.filter((team) =>
    team.toLowerCase().includes(query.toLowerCase())
  );

  const handleSearch = (teamName: string) => {
    setIsLoading(true);
    router.push(`/report/${encodeURIComponent(teamName)}`);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      handleSearch(query.trim());
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Search Form */}
      <form onSubmit={handleSubmit}>
        <motion.div
          className={cn(
            'relative flex items-center rounded-xl border-2 bg-valorant-card transition-all duration-300',
            isFocused
              ? 'border-c9-cyan shadow-glow-md'
              : 'border-valorant-border hover:border-c9-cyan/50'
          )}
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center pl-4">
            {isLoading ? (
              <Loader2 className="h-5 w-5 text-c9-cyan animate-spin" />
            ) : (
              <Search className="h-5 w-5 text-text-secondary" />
            )}
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setTimeout(() => setIsFocused(false), 200)}
            placeholder="Enter team name..."
            className="flex-1 bg-transparent px-4 py-4 text-lg text-white placeholder-text-secondary outline-none"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className={cn(
              'mr-2 flex items-center gap-2 rounded-lg px-6 py-2 font-semibold transition-all duration-300',
              query.trim() && !isLoading
                ? 'bg-c9-cyan text-valorant-dark hover:bg-c9-cyanLight'
                : 'bg-valorant-border text-text-secondary cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                Scout
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </motion.div>
      </form>

      {/* Autocomplete Dropdown */}
      {isFocused && query && filteredTeams.length > 0 && (
        <motion.div
          className="absolute z-50 mt-2 w-full max-w-2xl rounded-xl border border-valorant-border bg-valorant-card shadow-lg"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {filteredTeams.map((team) => (
            <button
              key={team}
              onClick={() => handleSearch(team)}
              className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-c9-cyan/10 transition-colors first:rounded-t-xl last:rounded-b-xl"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded bg-valorant-dark text-sm font-bold text-c9-cyan">
                {team.charAt(0)}
              </div>
              <span className="text-white">{team}</span>
            </button>
          ))}
        </motion.div>
      )}

      {/* Quick Select */}
      <motion.div
        className="mt-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <p className="mb-3 text-center text-sm text-text-secondary">
          Quick Select (Demo Teams)
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          {availableTeams.map((team, index) => (
            <motion.button
              key={team}
              onClick={() => handleSearch(team)}
              className="flex items-center gap-2 rounded-lg border border-valorant-border bg-valorant-card px-4 py-2 text-sm font-medium text-white transition-all hover:border-c9-cyan hover:shadow-glow-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
              disabled={isLoading}
            >
              <Zap className="h-4 w-4 text-c9-cyan" />
              {team}
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
