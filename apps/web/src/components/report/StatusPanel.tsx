'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Wifi, 
  WifiOff, 
  Server, 
  Database, 
  Activity,
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { tokens } from '@/styles/tokens';

interface ServiceStatus {
  name: string;
  status: 'connected' | 'disconnected' | 'checking';
  latency?: number;
  lastChecked?: Date;
}

interface StatusPanelProps {
  apiBaseUrl?: string;
  onStatusChange?: (status: 'healthy' | 'unhealthy') => void;
}

export function StatusPanel({ apiBaseUrl, onStatusChange }: StatusPanelProps) {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'VORACLE API', status: 'checking' },
    { name: 'GRID API', status: 'checking' },
    { name: 'VLR API', status: 'checking' },
  ]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    checkAllServices();
    // Re-check every 60 seconds
    const interval = setInterval(checkAllServices, 60000);
    return () => clearInterval(interval);
  }, []);

  const checkAllServices = async () => {
    setIsChecking(true);
    
    const baseUrl = apiBaseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Check VORACLE API
    const voracleStatus = await checkService(`${baseUrl}/health`, 'VORACLE API');
    
    // GRID and VLR are checked through the backend
    // For now, we'll infer their status from the main API
    const gridStatus: ServiceStatus = {
      name: 'GRID API',
      status: voracleStatus.status === 'connected' ? 'connected' : 'disconnected',
      lastChecked: new Date(),
    };
    
    const vlrStatus: ServiceStatus = {
      name: 'VLR API',
      status: voracleStatus.status === 'connected' ? 'connected' : 'disconnected',
      lastChecked: new Date(),
    };

    setServices([voracleStatus, gridStatus, vlrStatus]);
    setIsChecking(false);
    
    // Notify parent of overall status
    const allHealthy = voracleStatus.status === 'connected';
    onStatusChange?.(allHealthy ? 'healthy' : 'unhealthy');
  };

  const checkService = async (url: string, name: string): Promise<ServiceStatus> => {
    const startTime = Date.now();
    try {
      const response = await fetch(url, { method: 'GET' });
      const latency = Date.now() - startTime;
      
      return {
        name,
        status: response.ok ? 'connected' : 'disconnected',
        latency,
        lastChecked: new Date(),
      };
    } catch {
      return {
        name,
        status: 'disconnected',
        lastChecked: new Date(),
      };
    }
  };

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'connected':
        return <CheckCircle2 className="h-4 w-4 text-status-success" />;
      case 'disconnected':
        return <XCircle className="h-4 w-4 text-status-danger" />;
      case 'checking':
        return <Loader2 className="h-4 w-4 text-text-muted animate-spin" />;
    }
  };

  const getStatusColor = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'connected': return tokens.colors.status.success;
      case 'disconnected': return tokens.colors.status.danger;
      case 'checking': return tokens.colors.text.muted;
    }
  };

  const overallStatus = services.every(s => s.status === 'connected') 
    ? 'connected' 
    : services.some(s => s.status === 'checking')
      ? 'checking'
      : 'disconnected';

  return (
    <div className="relative">
      {/* Compact Status Indicator */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 rounded-lg border border-border-default bg-bg-secondary px-3 py-2 text-sm transition-colors hover:border-border-hover"
      >
        {overallStatus === 'connected' ? (
          <Wifi className="h-4 w-4 text-status-success" />
        ) : overallStatus === 'checking' ? (
          <Loader2 className="h-4 w-4 text-text-muted animate-spin" />
        ) : (
          <WifiOff className="h-4 w-4 text-status-danger" />
        )}
        <span className="text-text-secondary">
          {overallStatus === 'connected' ? 'All Services Online' : 
           overallStatus === 'checking' ? 'Checking...' : 'Service Issues'}
        </span>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-text-muted" />
        ) : (
          <ChevronDown className="h-4 w-4 text-text-muted" />
        )}
      </button>

      {/* Expanded Panel */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 z-50 mt-2 w-72 rounded-xl border border-border-default bg-bg-card p-4 shadow-xl"
          >
            <div className="mb-3 flex items-center justify-between">
              <h4 className="text-sm font-semibold text-white">Service Status</h4>
              <button
                onClick={checkAllServices}
                disabled={isChecking}
                className="text-xs text-c9-cyan hover:text-c9-cyanLight disabled:opacity-50"
              >
                {isChecking ? 'Checking...' : 'Refresh'}
              </button>
            </div>

            <div className="space-y-2">
              {services.map((service, index) => (
                <motion.div
                  key={service.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between rounded-lg bg-bg-secondary p-2"
                >
                  <div className="flex items-center gap-2">
                    {getStatusIcon(service.status)}
                    <span className="text-sm text-white">{service.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {service.latency && (
                      <span className="text-xs text-text-muted">
                        {service.latency}ms
                      </span>
                    )}
                    <div
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: getStatusColor(service.status) }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-3 border-t border-border-subtle pt-3">
              <p className="text-xs text-text-muted">
                Last checked: {services[0]?.lastChecked?.toLocaleTimeString() || 'Never'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Inline status badge for use in other components
export function StatusBadge({ 
  status, 
  label,
  size = 'sm' 
}: { 
  status: 'online' | 'offline' | 'checking'; 
  label?: string;
  size?: 'sm' | 'md';
}) {
  const dotSize = size === 'sm' ? 'h-2 w-2' : 'h-3 w-3';
  const textSize = size === 'sm' ? 'text-xs' : 'text-sm';

  const getColor = () => {
    switch (status) {
      case 'online': return tokens.colors.status.success;
      case 'offline': return tokens.colors.status.danger;
      case 'checking': return tokens.colors.text.muted;
    }
  };

  return (
    <div className="inline-flex items-center gap-1.5">
      <div
        className={`${dotSize} rounded-full ${status === 'online' ? 'animate-pulse' : ''}`}
        style={{ backgroundColor: getColor() }}
      />
      {label && (
        <span className={`${textSize} text-text-secondary`}>{label}</span>
      )}
    </div>
  );
}
