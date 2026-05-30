import { ExternalLink, ShieldCheck, AlertTriangle, Shield } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { CyberBadge } from './atoms/CyberBadge';
import type { Vulnerability } from '@/src/lib/api';

interface FindingsTableProps {
  findings: Vulnerability[];
  traceHash?: string;
  complianceMap?: Record<string, string[]>; // Maps CWE to control IDs from Compliance Report
  className?: string;
}

export function FindingsTable({ findings, traceHash, complianceMap, className }: FindingsTableProps) {

  const getCweLink = (cweStr: string) => {
    if (!cweStr || cweStr === 'N/A') return null;
    const match = cweStr.match(/\d+/);
    if (!match) return null;
    return `https://cwe.mitre.org/data/definitions/${match[0]}.html`;
  };

  const getVerifiedBadge = (confirmed?: boolean) => {
    if (confirmed === true) {
      return (
        <span className="text-hud-mint font-bold flex items-center gap-1.5" title="TOKAMAK Sandbox Confirmed PoC">
          <ShieldCheck size={12} /> ✓ Verified
        </span>
      );
    }
    if (confirmed === false) {
      return (
        <span className="text-sev-critical font-bold flex items-center gap-1.5" title="Unconfirmed / Pending Validation">
          <AlertTriangle size={12} /> ⚠ Unconfirmed
        </span>
      );
    }
    return <span className="text-fg3 font-mono">—</span>;
  };

  if (!findings || findings.length === 0) {
    return (
      <div className={cn("bg-bg-surface p-6 border border-white/5 rounded flex flex-col items-center justify-center text-center text-fg3 min-h-[160px] hud-bracket", className)}>
        <Shield size={28} className="text-white/10 mb-2" />
        <span className="text-[10px] font-mono uppercase tracking-widest">No isolated findings to display</span>
      </div>
    );
  }

  const shortTraceHash = traceHash ? traceHash.slice(0, 8).toUpperCase() : 'RAW_SCAN';

  return (
    <div className={cn("bg-bg-surface border border-white/5 p-4 hud-bracket flex flex-col gap-4", className)}>
      <div className="flex items-center justify-between border-b border-white/5 pb-2">
        <span className="text-[10px] font-mono text-fg2 uppercase tracking-widest font-bold">Isolated Vulnerabilities Register</span>
        <span className="text-[9px] font-mono text-fg3 uppercase">Trace_ID: <span className="text-hud-cyan font-bold">{shortTraceHash}</span></span>
      </div>

      <div className="overflow-x-auto bg-black/20 border border-white/5">
        <table className="w-full text-left font-mono text-[10px] border-collapse">
          <thead>
            <tr className="border-b border-white/10 bg-white/[0.02] text-fg3">
              <th className="p-3 font-bold uppercase tracking-wider">Verified</th>
              <th className="p-3 font-bold uppercase tracking-wider">Vulnerability Finding</th>
              <th className="p-3 font-bold uppercase tracking-wider">Severity</th>
              <th className="p-3 font-bold uppercase tracking-wider">CWE Reference</th>
              <th className="p-3 font-bold uppercase tracking-wider">CSF Control</th>
              <th className="p-3 font-bold uppercase tracking-wider">Detection Node</th>
              <th className="p-3 font-bold uppercase tracking-wider text-right">Forensic Hash</th>
            </tr>
          </thead>
          <tbody>
            {findings.map((finding, idx) => {
              const cweUrl = getCweLink(finding.cwe);
              const mappedControls = complianceMap && finding.cwe ? complianceMap[finding.cwe] : null;

              return (
                <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.01] transition-colors">
                  <td className="p-3">{getVerifiedBadge(finding.confirmed)}</td>
                  <td className="p-3 text-white font-bold max-w-[180px] truncate" title={finding.title}>
                    {finding.title}
                  </td>
                  <td className="p-3">
                    <CyberBadge
                      text={finding.severity}
                      type={finding.severity === 'critical' || finding.severity === 'high' ? 'critical' : finding.severity === 'medium' ? 'medium' : 'low'}
                    />
                  </td>
                  <td className="p-3">
                    {cweUrl ? (
                      <a
                        href={cweUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-hud-cyan hover:underline inline-flex items-center gap-1 group"
                      >
                        {finding.cwe}
                        <ExternalLink size={10} className="opacity-45 group-hover:opacity-100 transition-opacity" />
                      </a>
                    ) : (
                      <span className="text-fg3">{finding.cwe || 'N/A'}</span>
                    )}
                  </td>
                  <td className="p-3 text-hud-amber font-bold">
                    {mappedControls && mappedControls.length > 0 ? mappedControls.join(', ') : 'UNMAPPED'}
                  </td>
                  <td className="p-3 text-fg2">{finding.scanner}</td>
                  <td className="p-3 text-right text-fg3 font-mono select-all">
                    {traceHash ? traceHash.slice(0, 8).toLowerCase() : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
