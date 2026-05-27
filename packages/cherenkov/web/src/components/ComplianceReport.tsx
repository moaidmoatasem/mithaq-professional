import { FileJson, Shield, AlertTriangle, CheckCircle, HelpCircle } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { CyberBadge } from './atoms/CyberBadge';

export interface MappedFinding {
  finding_title: string;
  cwe: string;
  severity: string;
  controls: string[];
  domain: string;
  remediation: string;
  compliant: boolean;
  arabic_text?: string;
}

export interface ComplianceReportData {
  scan_id: string;
  framework_id: string;
  framework_name: string;
  framework_version: string;
  regulator: string;
  controls_total: number;
  controls_tested: number;
  coverage_pct: number;
  findings_mapped: number;
  findings_unmapped: number;
  compliance_score: number;
  mapped_findings: MappedFinding[];
  summary: string;
  arabic_summary?: string;
}

interface ComplianceReportProps {
  report: ComplianceReportData | null;
  className?: string;
}

export function ComplianceReport({ report, className }: ComplianceReportProps) {
  if (!report) {
    return (
      <div className={cn("bg-bg-surface p-6 border border-white/5 border-dashed rounded flex flex-col items-center justify-center text-center text-fg3 min-h-[220px]", className)}>
        <Shield size={36} className="text-white/10 mb-3 animate-pulse" />
        <h4 className="text-xs font-mono uppercase tracking-widest font-bold mb-1">Awaiting Scan Compliance Mapping</h4>
        <p className="text-[10px] font-mono text-fg3/50 max-w-sm uppercase">
          Configure a scan with a regulatory framework selected (e.g. EGY-FIN CSF, SAMA CSF) to generate an automated compliance report.
        </p>
      </div>
    );
  }

  // Color logic for score: red <50, yellow 50-80, green >80
  const score = report.compliance_score;
  const scoreColor = score >= 80 ? 'text-hud-mint' : score >= 50 ? 'text-hud-amber' : 'text-sev-critical';
  const scoreBg = score >= 80 ? 'bg-hud-mint/10 border-hud-mint/20 text-hud-mint' : score >= 50 ? 'bg-hud-amber/10 border-hud-amber/20 text-hud-amber' : 'bg-sev-critical/10 border-sev-critical/20 text-sev-critical';

  return (
    <div className={cn("bg-bg-surface border border-white/5 p-6 hud-bracket flex flex-col gap-6", className)}>
      {/* Header Info */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 flex items-center justify-center bg-hud-cyan/10 border border-hud-cyan/20 shrink-0">
            <FileJson size={20} className="text-hud-cyan" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-md font-bold text-white uppercase tracking-tight">{report.framework_name}</h3>
              <CyberBadge text={`v${report.framework_version}`} type="info" />
            </div>
            <p className="text-[9px] font-mono text-fg3 uppercase tracking-widest mt-1">
              REGULATOR: <span className="text-hud-cyan">{report.regulator}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          {/* Tested Controls Count */}
          <div className="text-right font-mono">
            <span className="text-[8px] text-fg3 uppercase tracking-widest block mb-0.5">Controls_Assessed</span>
            <span className="text-sm font-bold text-white">{report.controls_tested} / {report.controls_total}</span>
          </div>

          {/* Score Badge */}
          <div className={cn("px-4 py-2 border font-mono flex flex-col items-center min-w-[100px]", scoreBg)}>
            <span className="text-[8px] uppercase tracking-widest">Score</span>
            <span className="text-2xl font-black tracking-tight leading-none mt-1">{score}%</span>
          </div>
        </div>
      </div>

      {/* Progress Bars & Aggregations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <div className="flex justify-between items-end text-[10px] font-mono">
            <span className="text-fg2 uppercase tracking-widest">Assessment Coverage</span>
            <span className="text-hud-cyan font-bold">{report.coverage_pct}%</span>
          </div>
          <div className="h-2 bg-white/5 relative overflow-hidden">
            <div 
              className="h-full bg-hud-cyan transition-all duration-500" 
              style={{ width: `${report.coverage_pct}%` }} 
            />
          </div>
        </div>

        <div className="p-3 bg-black/40 border border-white/5 font-mono text-[10px] space-y-1.5 flex flex-col justify-center">
          <div className="flex justify-between">
            <span className="text-fg3 uppercase">Findings Mapped:</span>
            <span className="text-white font-bold">{report.findings_mapped}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-fg3 uppercase">Unmapped Findings:</span>
            <span className="text-white font-bold">{report.findings_unmapped}</span>
          </div>
        </div>
      </div>

      {/* Arabic and English Summaries */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white/[0.01] p-4 border border-white/5">
        <div className="space-y-1">
          <span className="text-[8px] font-mono text-fg3 uppercase tracking-widest block">Executive Summary</span>
          <p className="text-xs text-soft leading-relaxed italic">"{report.summary}"</p>
        </div>
        {report.arabic_summary && (
          <div className="space-y-1 text-right" dir="rtl">
            <span className="text-[8px] font-mono text-fg3 uppercase tracking-widest block font-sans">ملخص تنفيذي</span>
            <p className="text-xs text-soft leading-relaxed font-sans italic">"{report.arabic_summary}"</p>
          </div>
        )}
      </div>

      {/* Compliance Mapping Table */}
      <div className="space-y-2">
        <span className="text-[10px] font-mono text-fg2 uppercase tracking-widest font-bold">Regulatory Controls Audit Trace</span>
        
        <div className="overflow-x-auto border border-white/5 bg-black/20">
          <table className="w-full text-left font-mono text-[10px] border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-white/[0.02] text-fg3">
                <th className="p-3 font-bold uppercase tracking-wider">Control ID</th>
                <th className="p-3 font-bold uppercase tracking-wider">Domain</th>
                <th className="p-3 font-bold uppercase tracking-wider">Assessed Anomaly</th>
                <th className="p-3 font-bold uppercase tracking-wider">Severity</th>
                <th className="p-3 font-bold uppercase tracking-wider text-right">Audit Status</th>
              </tr>
            </thead>
            <tbody>
              {report.mapped_findings.map((finding, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.01] transition-colors">
                  <td className="p-3 font-bold text-hud-cyan">{finding.controls.join(', ')}</td>
                  <td className="p-3 text-fg2">{finding.domain}</td>
                  <td className="p-3 text-white max-w-[200px] truncate" title={finding.finding_title}>
                    {finding.finding_title}
                  </td>
                  <td className="p-3">
                    <CyberBadge 
                      text={finding.severity} 
                      type={finding.severity === 'critical' || finding.severity === 'high' ? 'critical' : finding.severity === 'medium' ? 'medium' : 'low'} 
                    />
                  </td>
                  <td className="p-3 text-right">
                    {finding.compliant ? (
                      <span className="text-hud-mint font-bold flex items-center justify-end gap-1.5">
                        <CheckCircle size={12} /> COMPLIANT
                      </span>
                    ) : (
                      <span className="text-sev-critical font-bold flex items-center justify-end gap-1.5">
                        <AlertTriangle size={12} /> NON-COMPLIANT
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {report.mapped_findings.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-fg3 italic uppercase">
                    No mapped compliance audit entries.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
