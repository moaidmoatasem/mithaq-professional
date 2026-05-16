import React from 'react';
import { cn } from '@/src/lib/utils';
import { ShieldAlert } from 'lucide-react';
import { useAblationStats } from '@/src/hooks/useMetrics';

interface AblationMeterProps {
  className?: string;
  // Overrides for preview context if needed, but not used by default
}

export function AblationMeter({ className }: AblationMeterProps) {
  const { data, error } = useAblationStats(10000);

  const dropRate = data?.session_stats?.drop_rate != null ? data.session_stats.drop_rate * 100 : 0;
  const drops = data?.session_stats?.drops ?? 0;
  const attempts = data?.session_stats?.attempts ?? 0;
  const alertActive = data?.session_stats?.alert_active === true || error != null;

  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = Math.max(0, Math.min(circumference, circumference - (dropRate / 100) * circumference));

  const getStatusColor = () => {
    if (error) return 'text-sev-critical';
    if (dropRate > 20) return 'text-sev-critical';
    if (dropRate >= 10) return 'text-hud-amber';
    return 'text-status-confirmed';
  };

  return (
    <div className={cn("bg-bg-surface p-4 border border-white/5 flex items-center justify-between relative", className)}>
      {alertActive && !error && (
        <div className="absolute top-0 right-0 left-0 bg-sev-critical/20 text-sev-critical text-[8px] font-mono text-center py-0.5 uppercase tracking-widest border-b border-sev-critical/30 animate-pulse">
           ABLATION ALERT ACTIVE
        </div>
      )}
      {error && (
        <div className="absolute top-0 right-0 left-0 bg-sev-critical/20 text-sev-critical text-[8px] font-mono text-center py-0.5 uppercase tracking-widest border-b border-sev-critical/30">
           BACKEND OFFLINE
        </div>
      )}

      <div className="flex flex-col gap-2 relative group cursor-help mt-2">
        <div className="flex items-center gap-2">
          <ShieldAlert size={14} className={getStatusColor()} />
          <span className="text-[10px] font-mono text-fg2 uppercase tracking-widest font-bold">Ablation_Meter</span>
        </div>
        <div className="flex items-end gap-2">
          <span className={cn("text-xl font-bold font-mono tracking-tighter", getStatusColor())}>
            {dropRate.toFixed(1)}%
          </span>
          <span className="text-[9px] font-mono text-fg3 uppercase tracking-widest mb-1">Drop_Rate</span>
        </div>

        {/* Tooltip */}
        <div className="absolute top-10 left-0 w-48 bg-black/90 border border-white/10 p-3 opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50">
          <div className="flex flex-col gap-2">
            <span className="text-[10px] font-mono text-white opacity-80 border-b border-white/10 pb-1 uppercase tracking-widest">Ablation_Stats</span>
            <div className="flex justify-between">
              <span className="text-[9px] font-mono text-fg3 uppercase">Total Drops</span>
              <span className="text-[9px] font-mono text-white font-bold">{drops}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[9px] font-mono text-fg3 uppercase">Total Attempts</span>
              <span className="text-[9px] font-mono text-white font-bold">{attempts}</span>
            </div>
            {data?.drop_reasons && (
              <div className="mt-1 pt-1 border-t border-white/10 flex flex-col gap-1">
                 <span className="text-[8px] font-mono text-fg3 uppercase">Reasons Breakdown</span>
                 {Object.entries(data.drop_reasons).map(([reason, count]) => (
                   <span key={reason} className="text-[8px] font-mono text-fg2 capitalize">- {reason.replace(/_/g, ' ')} ({count as React.ReactNode})</span>
                 ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="relative w-[70px] h-[70px] flex items-center justify-center mt-2">
        {/* Background Circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="35"
            cy="35"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="4"
            className="text-white/5"
          />
          {/* Progress Circle */}
          <circle
            cx="35"
            cy="35"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="4"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className={cn("transition-all duration-1000 ease-out", getStatusColor())}
          />
        </svg>
        <span className={cn("absolute text-[10px] font-mono font-bold text-center leading-none", getStatusColor())}>
          {dropRate.toFixed(0)}<br/>
          <span className="text-[7px]">DRP</span>
        </span>
      </div>
    </div>
  );
}
