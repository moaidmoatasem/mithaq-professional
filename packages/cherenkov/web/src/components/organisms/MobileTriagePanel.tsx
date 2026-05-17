import { motion } from 'motion/react';
import { Smartphone, ShieldCheck, AlertCircle, FileSearch } from 'lucide-react';
import { cn } from '@/src/lib/utils';

interface MobileFinding {
  title: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  cwe: string;
}

interface MobileTriagePanelProps {
  findings: MobileFinding[];
  platform: 'android' | 'ios' | 'unknown';
  className?: string;
}

export function MobileTriagePanel({ findings, platform, className }: MobileTriagePanelProps) {
  return (
    <div className={cn("bg-bg-surface border border-white/5 p-4 flex flex-col h-full", className)}>
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Smartphone size={16} className="text-cherenkov-accent" />
          <h3 className="text-sm font-bold text-white uppercase tracking-tight">Mobile Triage</h3>
        </div>
        <div className="flex items-center gap-2">
           <span className="text-[10px] font-mono text-fg3 uppercase tracking-widest">Platform:</span>
           <span className="text-[10px] font-mono text-cherenkov-accent uppercase font-bold">{platform}</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-2">
        {findings.length > 0 ? (
          findings.map((finding, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-white/[0.02] border border-white/5 p-3 rounded-sm group hover:border-cherenkov-accent/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-2">
                  <div className={cn(
                    "w-1.5 h-1.5 rounded-full",
                    finding.severity === 'HIGH' ? "bg-sev-critical shadow-[0_0_8px_rgba(255,68,68,0.5)]" :
                    finding.severity === 'MEDIUM' ? "bg-sev-high shadow-[0_0_8px_rgba(255,187,0,0.5)]" :
                    "bg-hud-mint shadow-[0_0_8px_rgba(0,255,136,0.5)]"
                  )} />
                  <span className="text-[11px] font-bold text-white leading-none">{finding.title}</span>
                </div>
                <span className="text-[9px] font-mono text-fg3 uppercase">{finding.cwe}</span>
              </div>
              <div className="flex items-center gap-4 mt-3 pt-3 border-t border-white/[0.02]">
                <div className="flex items-center gap-1.5">
                  <ShieldCheck size={10} className="text-hud-mint" />
                  <span className="text-[9px] font-mono text-hud-mint/80 uppercase">Static_Verified</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <AlertCircle size={10} className="text-fg3" />
                  <span className="text-[9px] font-mono text-fg3 uppercase">Policy_Violated</span>
                </div>
              </div>
            </motion.div>
          ))
        ) : (
          <div className="h-full flex flex-col items-center justify-center opacity-20 py-12">
            <FileSearch size={48} className="mb-4" />
            <span className="text-[10px] font-mono uppercase tracking-[0.3em]">No Mobile Findings</span>
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-white/5">
        <div className="flex items-center justify-between text-[9px] font-mono text-fg3 uppercase tracking-tighter">
          <span>Triage_Engine: v2.1.0</span>
          <span>Status: Standby</span>
        </div>
      </div>
    </div>
  );
}
