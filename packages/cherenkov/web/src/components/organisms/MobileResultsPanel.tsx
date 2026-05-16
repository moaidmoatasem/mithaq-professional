import React from 'react';
import { AlertTriangle, ShieldCheck, ChevronRight, Binary } from 'lucide-react';
import { cn } from '@/src/lib/utils';

interface MobileResultsPanelProps {
  result: any;
}

export function MobileResultsPanel({ result }: MobileResultsPanelProps) {
  const findings = result.vulnerabilities || [];
  
  return (
    <div className="bg-bg-surface border border-white/5 h-full flex flex-col overflow-hidden">
      <div className="h-10 px-4 border-b border-white/5 bg-white/[0.02] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Binary size={14} className="text-cherenkov-accent" />
          <span className="text-[10px] font-mono text-fg3 uppercase tracking-widest">Analysis_Payload_Result</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-[9px] font-mono text-fg3 opacity-40">TRC_ID: {result.scan_id?.slice(0, 8).toUpperCase()}</span>
          <span className="text-[9px] font-mono text-hud-mint px-1.5 py-0.5 bg-hud-mint/10 border border-hud-mint/20">VERIFIED</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        <div className="flex flex-col gap-3">
          {findings.length > 0 ? (
            findings.map((finding: any, idx: number) => (
              <div 
                key={idx}
                className={cn(
                  "p-4 border group hover:bg-white/[0.02] transition-colors relative",
                  finding.severity === 'CRITICAL' ? "border-sev-critical/20 bg-sev-critical/5" :
                  finding.severity === 'HIGH' ? "border-sev-high/20 bg-sev-high/5" :
                  "border-white/5"
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "text-[9px] font-mono px-1.5 py-0.5 border",
                      finding.severity === 'CRITICAL' ? "text-sev-critical border-sev-critical/40 bg-sev-critical/10" :
                      finding.severity === 'HIGH' ? "text-sev-high border-sev-high/40 bg-sev-high/10" :
                      "text-fg3 border-white/10"
                    )}>
                      {finding.severity}
                    </span>
                    <span className="text-xs font-bold text-white tracking-tight">{finding.title}</span>
                  </div>
                  <ChevronRight size={14} className="text-fg3 opacity-20 group-hover:opacity-100 transition-opacity" />
                </div>
                
                <p className="text-[11px] text-fg2 leading-relaxed mb-3">{finding.description}</p>
                
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
                  <span className="text-[9px] font-mono text-fg3 uppercase opacity-60">Scanner: {finding.scanner}</span>
                  <div className="flex gap-2">
                     {finding.cwe && (
                       <span className="text-[9px] font-mono text-cherenkov-accent">CWE-{finding.cwe}</span>
                     )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center py-12 opacity-40">
              <ShieldCheck size={32} className="text-hud-mint mb-2" />
              <span className="text-[10px] font-mono uppercase tracking-widest">No_Vulnerabilities_Detected</span>
            </div>
          )}
        </div>
      </div>

      <div className="p-4 border-t border-white/5 bg-white/[0.01]">
         <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
               <span className="text-[8px] font-mono text-fg3 uppercase">Binary_Entropy</span>
               <div className="h-1 bg-white/5 overflow-hidden">
                  <div className="h-full bg-cherenkov-accent w-[65%]" />
               </div>
            </div>
            <div className="flex flex-col gap-1">
               <span className="text-[8px] font-mono text-fg3 uppercase">Audit_Signed</span>
               <span className="text-[9px] font-mono text-hud-mint">0x74...F92A</span>
            </div>
         </div>
      </div>
    </div>
  );
}
