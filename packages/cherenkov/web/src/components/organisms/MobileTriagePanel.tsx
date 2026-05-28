import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Smartphone, ShieldCheck, AlertCircle, FileSearch } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import type { ScanResult } from '@/src/lib/api';

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

const MOBILE_CWES = new Set([
  'CWE-276', 'CWE-798', 'CWE-295', 'CWE-312', 'CWE-311',
  'CWE-326', 'CWE-327', 'CWE-522', 'CWE-89', 'CWE-287',
  'CWE-200', 'CWE-919', 'CWE-940', 'CWE-921',
]);

function detectPlatform(target?: string): 'android' | 'ios' | 'unknown' {
  if (!target) return 'unknown';
  const lower = target.toLowerCase();
  if (lower.includes('android') || lower.includes('play.google')) return 'android';
  if (lower.includes('ios') || lower.includes('apple') || lower.includes('itunes.apple')) return 'ios';
  return 'unknown';
}

function filterMobileFindings(scan: ScanResult): MobileFinding[] {
  return scan.vulnerabilities
    .filter(v => MOBILE_CWES.has(v.cwe) || v.title.toLowerCase().includes('mobile'))
    .map(v => ({
      title: v.title,
      severity: (v.severity.toUpperCase() === 'CRITICAL' ? 'HIGH' : v.severity.toUpperCase()) as MobileFinding['severity'],
      cwe: v.cwe,
    }));
}

export function MobileTriagePanel({ findings: propFindings, platform: propPlatform, className }: MobileTriagePanelProps) {
  const [liveFindings, setLiveFindings] = useState<MobileFinding[]>([]);
  const [livePlatform, setLivePlatform] = useState<'android' | 'ios' | 'unknown'>(propPlatform);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent<ScanResult>).detail;
      if (detail?.vulnerabilities) {
        const mobile = filterMobileFindings(detail);
        if (mobile.length > 0) {
          setLiveFindings(mobile);
          setLivePlatform(detectPlatform(detail.target));
        }
      }
    };
    window.addEventListener('cherenkov:scan_complete', handler);
    return () => window.removeEventListener('cherenkov:scan_complete', handler);
  }, []);

  const findings = liveFindings.length > 0 ? liveFindings : propFindings;
  const platform = livePlatform !== 'unknown' ? livePlatform : propPlatform;

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
