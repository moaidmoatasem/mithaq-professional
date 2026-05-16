import { useState, useEffect } from 'react';
import { CherenkovLogo } from '../atoms/Logo';
import { PulseDot } from '../atoms/PulseDot';
import { CyberBadge } from '../atoms/CyberBadge';
import { cn } from '@/src/lib/utils';
import { AlertTriangle, LogOut } from 'lucide-react';
import { useHealth, useAblationStats, usePendingApprovals } from '@/src/hooks/useMetrics';
import { useLiveEvents } from '@/src/hooks/useLiveEvents';
import { logout } from '@/src/lib/api';

type MeissnerStatus = 'LOCKED' | 'PERMEABLE' | 'BREACH';
type AblationStatus = 'SYNCED' | 'ACTIVE' | 'FAILED';

export function ForensicHeader() {
  const [time, setTime] = useState('00:00:00');
  const { data: healthData } = useHealth(5000);
  const { data: ablationData } = useAblationStats(10000);
  const { lastEvent } = useLiveEvents();
  const { data: pendingApprovals } = usePendingApprovals(5000);
  const [pendingCount, setPendingCount] = useState(0);

  const [wsMeissner, setWsMeissner] = useState<string | null>(null);

  useEffect(() => {
    if (pendingApprovals) {
      setPendingCount(pendingApprovals.length);
    }
  }, [pendingApprovals]);

  useEffect(() => {
    if (lastEvent?.event === 'circuit_breaker') {
      setWsMeissner(lastEvent.state);
    } else if (lastEvent?.event === 'finding_discovered') {
      setPendingCount(prev => prev + 1);
    }
  }, [lastEvent]);

  useEffect(() => {
    const start = Date.now();
    const timer = setInterval(() => {
      const elapsed = Date.now() - start;
      const h = Math.floor(elapsed / 3600000).toString().padStart(2, '0');
      const m = Math.floor((elapsed % 3600000) / 60000).toString().padStart(2, '0');
      const s = Math.floor((elapsed % 60000) / 1000).toString().padStart(2, '0');
      setTime(`${h}:${m}:${s}`);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const currentMeissnerState = wsMeissner || healthData?.meissner?.state || 'CLOSED';
  const currentAblationState = lastEvent?.event === 'ablation_alert' ? true : (ablationData?.session_stats?.alert_active || false);

  let meissnerStatus: MeissnerStatus = 'LOCKED';
  if (currentMeissnerState === 'OPEN') meissnerStatus = 'BREACH';
  else if (currentMeissnerState === 'HALF_OPEN') meissnerStatus = 'PERMEABLE';

  let ablationStatus: AblationStatus = currentAblationState ? 'ACTIVE' : 'SYNCED';

  return (
    <header className="h-16 px-6 border-b border-white/10 bg-bg-canvas flex items-center justify-between sticky top-0 z-[100] backdrop-blur-md">
      {/* Brand Mark */}
      <div className="flex items-center gap-4 group">
        <CherenkovLogo size={32} />
        <div className="flex flex-col">
          <h1 
            className="text-lg font-bold tracking-tighter text-hud-cyan fx-glitch transition-all group-hover:neon" 
            data-text="CHERENKOV"
          >
            CHERENKOV
          </h1>
          <span className="text-[8px] font-mono text-fg2 tracking-[0.4em] uppercase opacity-50">The Forensic Reveal</span>
        </div>
      </div>

      {/* Center Intelligence */}
      <div className="hidden md:flex items-center gap-8">
        <div className="flex items-center gap-3 px-4 py-1.5 border border-white/5 bg-white/[0.02] chamfered">
           <span className="text-[8px] font-mono text-fg3 uppercase tracking-widest">Mission_Timer</span>
           <span className="text-sm font-mono text-white tabular-nums tracking-widest">{time}</span>
        </div>
      </div>

      {/* System Status Indicators */}
      <div className="flex items-center gap-6">
        {/* HITL Approvals Status */}
        <div className="flex items-center gap-3">
          {pendingCount > 0 && (
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-sev-critical/20 border border-sev-critical animate-pulse text-[10px] font-bold text-sev-critical">
              {pendingCount}
            </div>
          )}
          <div className="flex flex-col">
             <span className="text-[8px] font-mono text-fg3 uppercase">HITL_Gate</span>
             <span className={cn(
               "text-[9px] font-bold font-mono tracking-widest uppercase",
               pendingCount > 0 ? "text-sev-critical" : "text-hud-mint"
             )}>
               {pendingCount > 0 ? 'PENDING' : 'CLEAR'}
             </span>
          </div>
        </div>

        <div className="w-px h-6 bg-white/10" />

        {/* MEISSNER Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {meissnerStatus === 'BREACH' && (
              <AlertTriangle size={14} className="text-sev-critical animate-pulse" />
            )}
            <PulseDot color={meissnerStatus === 'LOCKED' ? 'green' : meissnerStatus === 'PERMEABLE' ? 'amber' : 'red'} />
          </div>
          <div className="flex flex-col">
             <span className="text-[8px] font-mono text-fg3 uppercase">Meissner_Shield</span>
             <span className={cn(
               "text-[9px] font-bold font-mono tracking-widest uppercase",
               meissnerStatus === 'LOCKED' ? "text-hud-mint" : meissnerStatus === 'PERMEABLE' ? "text-hud-amber" : "text-sev-critical",
               meissnerStatus === 'BREACH' && "animate-pulse"
             )}>
               {meissnerStatus}
             </span>
          </div>
        </div>

        <div className="w-px h-6 bg-white/10" />

        {/* ABLATION Status */}
        <div className="flex items-center gap-4">
           {ablationStatus === 'ACTIVE' && (
             <AlertTriangle size={14} className="text-hud-amber animate-pulse" />
           )}
           <div className="flex flex-col items-end">
              <span className="text-[8px] font-mono text-fg3 uppercase">Ablation_Sync</span>
              <CyberBadge 
                text={ablationStatus} 
                type={ablationStatus === 'SYNCED' ? 'safe' : ablationStatus === 'ACTIVE' ? 'medium' : 'critical'} 
                className={ablationStatus === 'ACTIVE' ? 'animate-pulse' : ''}
              />
           </div>
        </div>
      </div>

      <div className="flex items-center gap-2 ml-4 pl-4 border-l border-white/10">
        <button 
          onClick={logout}
          className="p-2 rounded-md text-fg3 hover:text-sev-critical hover:bg-sev-critical/10 transition-all group"
          title="Terminate Session"
        >
          <LogOut size={16} className="group-hover:scale-110 transition-transform" />
        </button>
      </div>
    </header>
  );
}
