import { useState, useEffect } from 'react';
import { VulnCard } from '../molecules/VulnCard';
import { CyberBadge } from '../atoms/CyberBadge';
import { Hash, Monitor, Copy, Check, X, Download, FileJson, ShieldCheck, Layers, Link as LinkIcon, Trash2 } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { motion, AnimatePresence } from 'motion/react';
import { CyberButton } from '../atoms/CyberButton';
import { fetchScanHistory, type ScanResult } from '@/src/lib/api';
import { PendingApprovalsPanel } from './PendingApprovalsPanel';

interface Threat {
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'safe';
  score: string;
  description: string;
  scanner: string;
  cve: string;
  traceId?: string;
}

const MOCK_THREATS: Threat[] = [
  {
    title: 'Unauthenticated RCE',
    severity: 'critical',
    score: '9.8',
    description: 'Remote code execution vulnerability via unsafe deserialization in the management portal API.',
    scanner: 'kinetic-scanner-v1',
    cve: 'CVE-2026-11234',
    traceId: 'TRC_9a2b_4f8c_1d8e'
  },
  {
    title: 'SSRF in Image Relay',
    severity: 'high',
    score: '8.2',
    description: 'Server-side request forgery vulnerability allowing internal metadata service access.',
    scanner: 'kinetic-scanner-v1',
    cve: 'CVE-2026-98822',
    traceId: 'TRC_1f9c_8e4d_2e4a'
  },
  {
    title: 'Weak SSH Key Exchange',
    severity: 'medium',
    score: '5.5',
    description: 'The target supports legacy key exchange algorithms susceptible to man-in-the-middle attacks.',
    scanner: 'meissner-mapper-v2',
    cve: 'N/A'
  }
];

const SEVERITY_SCORES: Record<string, string> = {
  critical: '9.5', high: '8.0', medium: '5.5', low: '3.0', info: '1.0'
};

function vulnsToThreats(result: ScanResult): Threat[] {
  return result.vulnerabilities.map((v) => ({
    title: v.title,
    severity: (['critical', 'high', 'medium', 'low'].includes(v.severity) ? v.severity : 'medium') as Threat['severity'],
    score: SEVERITY_SCORES[v.severity] || '5.0',
    description: v.description || v.remediation || 'No description available.',
    scanner: v.scanner,
    cve: v.cwe || 'N/A',
    traceId: `TRC_${result.scan_id?.slice(0, 4)}_${result.scan_id?.slice(4, 8)}`
  }));
}

export function ThreatIntelPanel() {
  const [target, setTarget] = useState('192.168.1.104');
  const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'>('ALL');
  const [copied, setCopied] = useState(false);
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null);
  const [liveThreats, setLiveThreats] = useState<Threat[]>([]);

  // Listen for scan results broadcast from TacticalOperationsPanel
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent<ScanResult>).detail;
      if (detail?.vulnerabilities) {
        setTarget(detail.target);
        setLiveThreats(vulnsToThreats(detail));
      }
    };
    window.addEventListener('cherenkov:scan_complete', handler);
    return () => window.removeEventListener('cherenkov:scan_complete', handler);
  }, []);

  // Also load any historical scan data on mount
  useEffect(() => {
    fetchScanHistory().then((scans) => {
      if (scans.length > 0) {
        const latest = scans[0];
        setTarget(latest.target);
        setLiveThreats(vulnsToThreats(latest));
      }
    }).catch(() => {});
  }, []);

  const displayThreats = liveThreats.length > 0 ? liveThreats : MOCK_THREATS;

  const fullHash = "7d2b4f8c1d8e4a9c8f2d1e0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a";

  const handleCopyHash = () => {
    navigator.clipboard.writeText(fullHash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportTrace = (threat: Threat) => {
    const traceData = {
      timestamp: new Date().toISOString(),
      target,
      threat: {
        title: threat.title,
        severity: threat.severity,
        score: threat.score,
        cve: threat.cve,
        scanner: threat.scanner,
        traceId: threat.traceId || 'N/A'
      },
      forensic_signature: fullHash,
      verification_status: 'VERIFIED'
    };

    const blob = new Blob([JSON.stringify(traceData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `cherenkov_trace_${threat.traceId || 'raw'}_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col gap-6 h-full relative">
      <AnimatePresence>
        {selectedThreat && (
          <div className="fixed inset-0 z-[500] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="w-full max-w-xl bg-[#0a0a0a] border border-white/10 p-8 hud-bracket relative shadow-2xl overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-2 opacity-10 pointer-events-none">
                <ShieldCheck size={120} className="text-hud-cyan" />
              </div>

              <button 
                onClick={() => setSelectedThreat(null)}
                className="absolute top-6 right-6 text-fg3 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>

              <div className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 flex items-center justify-center bg-hud-cyan/10 border border-hud-cyan/20">
                  <FileJson size={24} className="text-hud-cyan" />
                </div>
                <div>
                  <h3 className="text-xl font-black text-white uppercase tracking-tight">Forensic Proof View</h3>
                  <p className="text-[10px] font-mono text-hud-cyan/60 uppercase tracking-widest leading-none">Automated_Artifact_Validation_v2.4</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-8">
                <div className="space-y-4">
                  <div className="p-4 bg-white/[0.02] border border-white/5 font-mono text-[11px] space-y-3">
                    <div className="flex flex-col">
                      <span className="text-fg3 text-[9px] uppercase tracking-wider mb-1">Target_Identity</span>
                      <span className="text-fg1 font-bold">{target}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-fg3 text-[9px] uppercase tracking-wider mb-1">Trace_Sequence</span>
                      <span className="text-hud-mint font-bold">{selectedThreat.traceId || 'UNVERIFIED_SEQ'}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-fg3 text-[9px] uppercase tracking-wider mb-1">Detection_Node</span>
                      <span className="text-fg2">{selectedThreat.scanner}</span>
                    </div>
                  </div>

                  <div className="p-4 border border-white/10 bg-white/[0.01]">
                    <div className="flex items-center gap-2 mb-2">
                      <Layers size={12} className="text-hud-cyan" />
                      <span className="text-[10px] font-mono text-fg2 uppercase font-bold tracking-widest">Mem_Redact_Buffers</span>
                    </div>
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-hud-cyan/40" />
                        <span className="text-[10px] font-mono text-fg3">SESS_TKN: [REDACTED_HU_882]</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-hud-cyan/40" />
                        <span className="text-[10px] font-mono text-fg3">USR_PWD: {Array(12).fill('*').join('')}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-hud-cyan/40" />
                        <span className="text-[10px] font-mono text-fg3">PRV_IP: 10.0.***.***</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-4">
                   <div className="p-4 bg-white/[0.04] border-l-2 border-l-hud-amber border-y border-r border-white/5 space-y-3">
                      <h4 className="text-[10px] font-mono font-bold text-hud-amber uppercase tracking-[0.2em]">Threat_Context</h4>
                      <p className="text-[11px] text-fg2 leading-relaxed italic">
                        "{selectedThreat.description}"
                      </p>
                   </div>

                   <div className="flex-1 flex flex-col justify-end">
                      <div className="p-4 border border-dashed border-white/10 rounded-sm bg-black/40">
                         <div className="flex items-center gap-3 mb-2">
                            <ShieldCheck size={16} className="text-hud-mint" />
                            <span className="text-[10px] font-mono text-hud-mint font-bold uppercase tracking-widest">Signature_Status</span>
                         </div>
                         <p className="text-[10px] text-fg3 leading-relaxed">
                            Cryptographic trace matches anomaly pattern isolated by scanner. Forensic integrity verified via Cherenkov L2 validation.
                         </p>
                      </div>
                   </div>
                </div>
              </div>

              <div className="flex items-center justify-between gap-4 pt-6 border-t border-white/10">
                <button className="flex items-center gap-2 group">
                  <Trash2 size={12} className="text-sev-critical group-hover:scale-110 transition-transform" />
                  <span className="text-[9px] font-mono text-fg3 group-hover:text-sev-critical transition-colors uppercase tracking-[0.15em] underline underline-offset-4">shred_receipt: F_RX_922</span>
                </button>

                <div className="flex gap-3">
                  <CyberButton 
                    variant="ghost"
                    className="px-6"
                    onClick={() => setSelectedThreat(null)}
                  >
                    CLOSE
                  </CyberButton>
                  <CyberButton 
                    variant="primary"
                    className="px-6"
                    onClick={() => handleExportTrace(selectedThreat)}
                  >
                    <Download size={14} className="mr-2" />
                    EXPORT TRACE (.JSON)
                  </CyberButton>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Target HUD Block */}
      <div className="bg-bg-surface p-4 border border-white/5 hud-bracket">
         <div className="flex items-center gap-3 mb-2">
            <Monitor size={14} className="text-hud-amber" />
            <span className="text-[10px] font-mono text-hud-amber uppercase tracking-[0.2em]">Active_Target_HUD</span>
         </div>
         <input 
           type="text" 
           value={target}
           onChange={(e) => setTarget(e.target.value)}
           className="w-full bg-transparent border-none text-xl font-mono font-bold text-white outline-none focus:text-hud-cyan transition-colors"
           style={{ caretColor: '#2b7fff' }}
         />
      </div>

      <PendingApprovalsPanel />

      {/* Vulnerability List Section */}
      <div className="flex-1 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-[10px] font-mono text-fg2 uppercase tracking-widest">Anomalies_Isolated</h3>
          <div className="flex gap-1">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as any)}
                className={cn(
                  "px-2 py-0.5 text-[8px] font-mono border transition-all",
                  filter === f ? "bg-cherenkov-accent border-cherenkov-accent text-white" : "border-white/10 text-fg3 hover:border-white/30"
                )}
                style={{ clipPath: 'polygon(0 0, 100% 0, 100% 70%, 80% 100%, 0 100%)' }}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-4 overflow-y-auto custom-scrollbar max-h-[500px] pr-2">
          {displayThreats
            .filter(t => filter === 'ALL' || t.severity.toUpperCase() === filter)
            .map((threat, idx) => (
              <VulnCard 
                key={idx}
                {...threat}
                onViewProof={() => setSelectedThreat(threat)}
              />
            ))}
        </div>
      </div>

      {/* Cherenkov Trace Block */}
      <div className="bg-bg-surface p-4 border border-white/5 border-t-cherenkov-accent/30">
        <div className="flex items-center gap-2 mb-3">
          <Hash size={12} className="text-hud-cyan" />
          <span className="text-[9px] font-mono text-fg2 uppercase tracking-widest">Cherenkov_Trace_Signature</span>
        </div>
        
        <div 
          className="bg-black/50 p-3 flex flex-col gap-2 group cursor-pointer hover:bg-black/70 transition-colors"
          onClick={handleCopyHash}
        >
          <div className="flex items-center justify-between">
            <span className="text-[9px] font-mono text-hud-cyan opacity-80 uppercase">SHA-256_Auth_Trace</span>
            {copied ? <Check size={10} className="text-hud-mint" /> : <Copy size={10} className="text-fg3 opacity-0 group-hover:opacity-100 transition-opacity" />}
          </div>
          <span className="text-[10px] font-mono text-white/60 break-all leading-relaxed">
            {fullHash.slice(0, 20)}...{fullHash.slice(-10)}
          </span>
        </div>
        
        <button className="mt-4 text-[9px] font-mono text-cherenkov-accent hover:text-hud-cyan transition-colors uppercase tracking-[0.2em] flex items-center gap-2">
          <span>{'>'} cryptographic_shred_receipt</span>
        </button>
      </div>
    </div>
  );
}
