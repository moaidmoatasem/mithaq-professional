import React from 'react';
import { cn } from '@/src/lib/utils';
import { Activity } from 'lucide-react';
import { useQueueDepth } from '@/src/hooks/useMetrics';

export function QueueDepthSparkline() {
  const { history, current } = useQueueDepth(5000);
  
  // ensure we have something to draw even if array is small
  const paddingLength = Math.max(0, 20 - history.length);
  const paddedHistory = [...Array(paddingLength).fill(0), ...history];
  const max = Math.max(...paddedHistory, 5);
  
  return (
    <div className="bg-bg-surface p-4 border border-white/5 flex flex-col justify-between h-full min-h-[90px]">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Activity size={12} className="text-hud-cyan" />
          <span className="text-[10px] font-mono text-fg2 uppercase tracking-widest font-bold">Redis_Queue</span>
        </div>
        <span className="text-[9px] font-mono text-fg3 uppercase tracking-widest">Jobs: <span className="text-white font-bold">{current} pending</span></span>
      </div>

      <div className="flex-1 flex items-end gap-[2px] w-full pt-2">
        {paddedHistory.map((val, idx) => {
          const heightPct = (val / max) * 100;
          return (
            <div 
              key={idx}
              className={cn(
                "flex-1 rounded-t-sm transition-all duration-300",
                idx === paddedHistory.length - 1 ? "bg-hud-cyan" : "bg-white/10 hover:bg-white/20 cursor-pointer"
              )}
              style={{ height: `${Math.max(10, heightPct)}%` }}
            />
          );
        })}
      </div>
    </div>
  );
}
