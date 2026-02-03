/**
 * Utility functions for VORACLE frontend.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with proper precedence.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a decimal as a percentage string.
 */
export function formatPercent(value: number, decimals: number = 0): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a number with commas.
 */
export function formatNumber(value: number, decimals: number = 0): string {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Get color class based on win rate.
 */
export function getWinRateColor(winRate: number): string {
  if (winRate >= 0.6) return 'text-status-success';
  if (winRate >= 0.4) return 'text-status-warning';
  return 'text-status-danger';
}

/**
 * Get background color class based on win rate.
 */
export function getWinRateBgColor(winRate: number): string {
  if (winRate >= 0.6) return 'bg-status-success';
  if (winRate >= 0.4) return 'bg-status-warning';
  return 'bg-status-danger';
}

/**
 * Get impact badge color.
 */
export function getImpactColor(impact: string): string {
  switch (impact) {
    case 'critical':
      return 'bg-valorant-red text-white';
    case 'high':
      return 'bg-status-warning text-black';
    case 'medium':
      return 'bg-c9-cyan text-black';
    default:
      return 'bg-valorant-border text-white';
  }
}

/**
 * Get confidence badge color.
 */
export function getConfidenceColor(confidence: string): string {
  switch (confidence) {
    case 'high':
      return 'text-status-success';
    case 'medium':
      return 'text-status-warning';
    default:
      return 'text-text-secondary';
  }
}

/**
 * Truncate text with ellipsis.
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

/**
 * Agent role mapping for icons.
 */
export const AGENT_ROLES: Record<string, string> = {
  Jett: 'duelist',
  Raze: 'duelist',
  Reyna: 'duelist',
  Phoenix: 'duelist',
  Yoru: 'duelist',
  Neon: 'duelist',
  Iso: 'duelist',
  Sova: 'initiator',
  Breach: 'initiator',
  Skye: 'initiator',
  'KAY/O': 'initiator',
  Fade: 'initiator',
  Gekko: 'initiator',
  Brimstone: 'controller',
  Omen: 'controller',
  Viper: 'controller',
  Astra: 'controller',
  Harbor: 'controller',
  Clove: 'controller',
  Sage: 'sentinel',
  Cypher: 'sentinel',
  Killjoy: 'sentinel',
  Chamber: 'sentinel',
  Deadlock: 'sentinel',
};

/**
 * Get agent role.
 */
export function getAgentRole(agentName: string): string {
  return AGENT_ROLES[agentName] || 'flex';
}
