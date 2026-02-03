'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Search, Loader2, Zap, ArrowRight, Globe, Trophy } from 'lucide-react';
import { cn } from '@/lib/utils';
import { fetchPopularTeams, type PopularTeam } from '@/lib/api';

interface TeamSearchProps {
  availableTeams?: string[];
}

const REGIONS = [
  { code: 'na', name: 'Americas', flag: '🇺🇸' },
  { code: 'eu', name: 'EMEA', flag: '🇪🇺' },
  { code: 'ap', name: 'Pacific', flag: '🌏' },
  { code: 'la', name: 'LATAM', flag: '🌎' },
];

export function TeamSearch({ availableTeams = [] }: TeamSearchProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [popularTeams, setPopularTeams] = useState<PopularTeam[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [isLoadingTeams, setIsLoadingTeams] = useState(true);
  const [dataSource, setDataSource] = useState<string>('');

  useEffect(() => {
    loadPopularTeams();
  }, []);

  const loadPopularTeams = async () => {
    setIsLoadingTeams(true);
    try {
      const response = await fetchPopularTeams('na,eu,ap,la', 5);
      setPopularTeams(response.teams);
      setDataSource(response.source);
    } catch (error) {
      console.error('Failed to load teams:', error);
    } finally {
      setIsLoadingTeams(false);
    }
  };

  const displayedTeams = selectedRegion === 'all' 
    ? popularTeams 
    : popularTeams.filter(t => t.region.toLowerCase() === selectedRegion);

  const filteredTeams = query 
    ? popularTeams.filter(t => t.name.toLowerCase().includes(query.toLowerCase()))
    : [];

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
    <div className="w-full max-w-4xl mx-auto">
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
              key={team.name}
              onClick={() => handleSearch(team.name)}
              className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-c9-cyan/10 transition-colors first:rounded-t-xl last:rounded-b-xl"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded bg-valorant-dark text-sm font-bold text-c9-cyan">
                  #{team.rank}
                </div>
                <div>
                  <span className="text-white font-medium">{team.name}</span>
                  <span className="ml-2 text-xs text-text-muted">{team.region}</span>
                </div>
              </div>
              <span className="text-xs text-text-secondary">{team.record}</span>
            </button>
          ))}
        </motion.div>
      )}

      {/* Region Filter */}
      <motion.div
        className="mt-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="flex items-center justify-center gap-2 mb-4">
          <Globe className="h-4 w-4 text-text-secondary" />
          <p className="text-sm text-text-secondary">Select Region</p>
          {dataSource && (
            <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-c9-cyan/20 text-c9-cyan">
              {dataSource === 'vlr' ? 'Live Data' : 'Cached'}
            </span>
          )}
        </div>
        <div className="flex flex-wrap justify-center gap-2 mb-6">
          <button
            onClick={() => setSelectedRegion('all')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-all',
              selectedRegion === 'all'
                ? 'bg-c9-cyan text-valorant-dark'
                : 'border border-valorant-border text-text-secondary hover:border-c9-cyan hover:text-white'
            )}
          >
            All Regions
          </button>
          {REGIONS.map((region) => (
            <button
              key={region.code}
              onClick={() => setSelectedRegion(region.code)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                selectedRegion === region.code
                  ? 'bg-c9-cyan text-valorant-dark'
                  : 'border border-valorant-border text-text-secondary hover:border-c9-cyan hover:text-white'
              )}
            >
              {region.flag} {region.name}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Teams Grid */}
      <motion.div
        className="mt-2"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        {isLoadingTeams ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 text-c9-cyan animate-spin" />
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {displayedTeams.map((team, index) => (
              <motion.button
                key={`${team.name}-${team.region}`}
                onClick={() => handleSearch(team.name)}
                className="group flex items-center gap-4 rounded-xl border border-valorant-border bg-valorant-card/50 p-4 text-left transition-all hover:border-c9-cyan hover:shadow-glow-sm min-w-[200px]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
                disabled={isLoading}
              >
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-c9-cyan/10 text-c9-cyan font-bold group-hover:bg-c9-cyan/20">
                  <Trophy className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-white text-base">{team.name}</span>
                    <span className="text-xs px-1.5 py-0.5 rounded bg-valorant-dark text-text-muted flex-shrink-0">
                      {team.region}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-sm text-c9-cyan font-medium">#{team.rank}</span>
                    <span className="text-sm text-text-muted">{team.record}</span>
                  </div>
                </div>
                <ArrowRight className="h-5 w-5 flex-shrink-0 text-text-muted group-hover:text-c9-cyan transition-colors" />
              </motion.button>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
