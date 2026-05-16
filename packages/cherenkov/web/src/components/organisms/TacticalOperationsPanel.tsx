import { useState, useRef, useEffect } from 'react';
import { cn, generateTrace } from '@/src/lib/utils';
import { submitScan } from '@/src/lib/api';
import { motion, AnimatePresence } from 'motion/react';
import { CyberButton } from '../atoms/CyberButton';
import { StatGrid } from '../molecules/StatGrid';
import { TridentVisualizer, ContainmentState } from '../molecules/TridentVisualizer';
import { NodeStatusRow } from './NodeStatusRow';
import { Check, AlertTriangle, Cpu, Terminal } from 'lucide-react';
import { AblationMeter } from './AblationMeter';
import { QueueDepthSparkline } from './QueueDepthSparkline';
import { NewScanForm } from './NewScanForm';
import { MobileTriagePanel } from './MobileTriagePanel';
import { useLiveEvents } from '@/src/hooks/useLiveEvents';

interface LogEntry {
  type: 'info' | 'alert' | 'verified';
  message: string;
  timestamp: string;
}

const STEPS = [
  'MONITORING',
  'MEISSNER LOCKDOWN',
  'ABLATION SWEEP',
  'KINETIC ENGAGEMENT',
  'TOKAMAK CONTAINMENT',
  'TRACE SIGNED'
];

export function TacticalOperationsPanel() {
  const [activeStep, setActiveStep] = useState(0);
  const [isExecuting, setIsExecuting] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [traceId, setTraceId] = useState('');
  const [containmentState, setContainmentState] = useState<ContainmentState>('MONITORING');
  const scrollRef = useRef<HTMLDivElement>(null);
  
  const [showNewScan, setShowNewScan] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [totalScanners, setTotalScanners] = useState(0);
  const [completedScanners, setCompletedScanners] = useState(0);

  const { lastEvent, connected } = useLiveEvents();

  const addLog = (message: string, type: 'info' | 'alert' | 'verified' = 'info') => {
    const timestamp = new Date().toISOString().split('T')[1].slice(0, 8);
    setLogs(prev => [...prev.slice(-499), { message, type, timestamp }]);
  };

  useEffect(() => {
    if (!lastEvent) return;
    
    switch (lastEvent.event) {
      case 'scan_started':
        setTotalScanners(lastEvent.total_scanners);
        setCompletedScanners(0);
        setScanProgress(0);
        addLog(`Scan started: ${lastEvent.total_scanners} scanners engaged.`, 'info');
        setIsExecuting(true);
        setActiveStep(1);
        setContainmentState('MEISSNER_LOCKED');
        break;
      case 'scan_progress':
        setCompletedScanners(prev => {
          const next = prev + 1;
          const progress = totalScanners > 0 ? (next / totalScanners) * 100 : 0;
          setScanProgress(progress);
          
          if (progress >= 30 && progress < 60) {
            setActiveStep(2);
            setContainmentState('ABLATION_ACTIVE');
          } else if (progress >= 60 && progress < 90) {
            setActiveStep(3);
            setContainmentState('THREAT_DETECTED');
          } else if (progress >= 90 && progress < 100) {
            setActiveStep(4);
            setContainmentState('TOKAMAK_EXECUTING');
          }
          
          return next;
        });
        addLog(`[${lastEvent.scanner}] Completed. Findings: ${lastEvent.findings_count}`, 'info');
        break;
      case 'scan_complete':
        setIsExecuting(false);
        setActiveStep(5);
        setContainmentState('TRACE_SIGNED');
        setScanProgress(100);
        addLog(`Operation Complete. ${lastEvent.count} vulnerabilities confirmed.`, 'verified');
        break;
      case 'circuit_breaker':
        addLog(`Meissner Circuit: ${lastEvent.state} - ${lastEvent.reason}`, 'alert');
        if (lastEvent.state === 'OPEN') {
          setActiveStep(1);
          setContainmentState('MEISSNER_LOCKED');
        }
        break;
      case 'ablation_alert':
        addLog(`ABLATION ALERT: Drop rate ${lastEvent.drop_rate}`, 'alert');
        setActiveStep(2);
        setContainmentState('ABLATION_ACTIVE');
        break;
      case 'finding_discovered':
      case 'burhan_verdict':
        addLog(`Finding update: ${lastEvent.finding?.title || lastEvent.finding_id}`, 'verified');
        setActiveStep(4);
        setContainmentState('TOKAMAK_EXECUTING');
        break;
      case 'health_pulse':
        // Optional pulse tracking
        break;
    }
  }, [lastEvent]);

  const initiateScan = async (data: any) => {
    // Audit log and API call will trigger WS events
    const result = await submitScan({ url: data.target });
    
    setTraceId(result.scan_id?.slice(0, 8).toUpperCase() || generateTrace().slice(0, 8).toUpperCase());
    setIsExecuting(true);
    if (data.profile === 'mobile') {
      setContainmentState('MOBILE_TRIAGE');
      setActiveStep(3); // Start further ahead for mobile
    } else {
      setContainmentState('MEISSNER_LOCKED');
      setActiveStep(1);
    }
    setLogs([]);
    setScanProgress(0);
    addLog(`Initiating ${data.profile} scan on ${data.target}...`);

    // Simulate progress since the scan already completed synchronously.
    // In a full streaming implementation this would come via WebSocket events.
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20 + 10;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setIsExecuting(false);
        setActiveStep(5);
        setContainmentState('TRACE_SIGNED');
        setScanProgress(100);
        addLog(`Scan complete. ${result.count} vulnerabilities found.`, 'verified');
        // Emit custom event so ThreatIntelPanel picks up results
        window.dispatchEvent(new CustomEvent('cherenkov:scan_complete', { detail: result }));
      } else {
        setScanProgress(progress);
        addLog(`Scanning... ${progress.toFixed(0)}%`, 'info');
      }

      if (progress >= 30 && progress < 60) {
        setActiveStep(2);
        setContainmentState('ABLATION_ACTIVE');
      } else if (progress >= 60 && progress < 90) {
        setActiveStep(3);
        setContainmentState('THREAT_DETECTED');
      } else if (progress >= 90 && progress < 100) {
        setActiveStep(4);
        setContainmentState('TOKAMAK_EXECUTING');
      }
    }, 600);
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="flex flex-col gap-6 h-full relative">
      <NewScanForm 
        isOpen={showNewScan} 
        onClose={() => setShowNewScan(false)} 
        onSubmit={initiateScan} 
      />

      {/* Panel Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-6 bg-cherenkov-accent" />
          <h2 className="text-xl font-bold tracking-tight text-white uppercase">C2 Hub Dashboard</h2>
          {!connected && (
             <span className="text-[10px] font-mono text-sev-critical uppercase tracking-widest px-2 py-1 bg-sev-critical/20 border border-sev-critical/50">
               WS_DISCONNECTED
             </span>
          )}
        </div>
        <div className="flex gap-4">
          <CyberButton 
            text="REBOOT_TOPOLOGY" 
            variant="ghost" 
            onClick={() => {
              setActiveStep(0);
              setContainmentState('MONITORING');
              setTraceId('');
              setLogs([]);
              setScanProgress(0);
              setIsExecuting(false);
            }}
            disabled={isExecuting}
          />
          <CyberButton 
            text={isExecuting ? 'SCAN ACTIVE...' : '▶ INITIATE NEW SCAN'} 
            onClick={() => setShowNewScan(true)}
            disabled={isExecuting}
            className="min-w-[180px]"
          />
        </div>
      </div>

      {/* Node Status Row */}
      <NodeStatusRow />

      {/* StatGrid */}
      <StatGrid 
        stats={[
          { id: 'nodes', label: 'Nodes_Mapped', value: '142', accent: '#00e5ff' },
          { id: 'payloads', label: 'Payloads_Delivered', value: '47', accent: '#2b7fff' },
          { id: 'anomalies', label: 'Anomalies_Isolated', value: activeStep >= 4 ? '12' : '0', accent: '#ff4444' },
          { id: 'traces', label: 'Traces_Signed', value: !isExecuting && activeStep === 5 ? '8' : '0', accent: '#00ff88' },
        ]}
      />

      {/* State Machine Visualizer */}
      <div className="bg-bg-surface p-6 border border-white/5 hud-bracket fx-sweep overflow-hidden">
        <div className="flex items-center justify-between relative">
          {STEPS.map((step, idx) => (
            <div key={step} className="flex flex-col items-center gap-3 z-10 basis-1 flex-1 relative">
              {/* Connector Line */}
              {idx < STEPS.length - 1 && (
                <div className="absolute top-3 left-[50%] w-full h-px border-t border-dashed border-white/10 overflow-hidden">
                  <div className={cn(
                    "absolute inset-0 fx-march border-t border-hud-cyan/40",
                    idx < activeStep ? "opacity-100" : "opacity-0"
                  )} />
                </div>
              )}

              <div className={cn(
                "w-6 h-6 rounded-sm flex items-center justify-center transition-all duration-500",
                idx === activeStep ? "bg-cherenkov-accent/20 border-cherenkov-accent neon shadow-[0_0_15px_rgba(43,127,255,0.4)]" :
                idx < activeStep ? "bg-hud-mint/10 border-hud-mint text-hud-mint" : "bg-white/5 border border-white/10"
              )}>
                {idx < activeStep ? <Check size={12} /> : idx === activeStep ? <div className="w-2 h-2 bg-cherenkov-accent fx-pulse" /> : null}
              </div>
              <span className={cn(
                "text-[7px] font-mono font-bold text-center tracking-[0.2em] max-w-[60px] leading-tight transition-colors",
                idx === activeStep ? "text-cherenkov-accent" : idx < activeStep ? "text-hud-mint opacity-60" : "text-fg3"
              )}>
                {step}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Grid: Visualizer & Logs */}
      <div className="flex-1 min-h-[360px] grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Trident Topology / Mobile Triage */}
        <div className="bg-bg-surface border border-white/5 relative overflow-hidden flex flex-col items-center justify-center p-4">
          <div className="absolute top-0 left-0 p-3 flex items-center gap-2 z-30">
            <div className="w-1.5 h-1.5 bg-cherenkov-accent" />
            <span className="text-[9px] font-mono text-fg2 uppercase tracking-widest">
              {containmentState === 'MOBILE_TRIAGE' ? 'Mobile_Triage_Analysis' : 'Trident_Topology'}
            </span>
          </div>
          {containmentState === 'MOBILE_TRIAGE' ? (
            <MobileTriagePanel
              findings={[
                { title: 'Insecure Permissions Detected', severity: 'HIGH', cwe: 'CWE-276' },
                { title: 'Hardcoded API Secrets', severity: 'HIGH', cwe: 'CWE-798' },
                { title: 'Insecure SSL Pinning', severity: 'MEDIUM', cwe: 'CWE-295' },
              ]}
              platform="android"
              className="w-full h-full border-none bg-transparent"
            />
          ) : (
            <TridentVisualizer state={containmentState} traceId={traceId} className="w-full h-full" />
          )}
        </div>

        {/* Operation Stream */}
        <div className="bg-bg-surface border border-white/5 relative overflow-hidden flex flex-col">
          <div className="absolute inset-0 pointer-events-none opacity-[0.03] fx-grid" />
          <div className="h-8 px-4 border-b border-white/5 bg-white/[0.02] flex items-center justify-between z-10 shrink-0">
             <div className="flex items-center gap-2">
                <Terminal size={12} className="text-hud-cyan" />
                <span className="text-[9px] font-mono text-fg3 uppercase tracking-widest">Operation_Stream_Log</span>
             </div>
             <span className="text-[8px] font-mono text-fg3 opacity-40">TRC_SIG_BUFFER: ACTIVE</span>
          </div>
          
          <div 
            ref={scrollRef}
            className="flex-1 p-4 overflow-y-auto font-mono text-[11px] leading-relaxed custom-scrollbar z-10"
          >
            {logs.map((log, i) => (
              <div key={i} className={cn(
                "flex gap-3 py-0.5",
                log.type === 'alert' ? "text-sev-critical" : log.type === 'verified' ? "text-hud-mint" : "text-fg2"
              )}>
                <span className="opacity-40 shrink-0">[{log.timestamp}]</span>
                <span className="shrink-0">{log.type === 'info' ? '[+]' : log.type === 'alert' ? '[!]' : '[✓]'}</span>
                <span className="break-all">{log.message}</span>
              </div>
            ))}
            {isExecuting && (
              <div className="flex gap-2 text-fg3 opacity-50 mt-1">
                <span>{'>'}</span>
                <span className="inline-block w-2 h-4 bg-fg3 animate-pulse" />
              </div>
            )}
            {logs.length === 0 && <div className="h-full flex items-center justify-center text-fg3/20 italic uppercase tracking-widest">Awaiting Command...</div>}
          </div>
        </div>
      </div>

      {/* System Capacity Meter and Bottom Dashboards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <AblationMeter className="h-full" />
        
        <QueueDepthSparkline />
        
        <div className="bg-bg-surface p-4 border border-white/5 flex flex-col justify-center">
          <div className="flex justify-between items-end mb-2">
             <span className="text-[10px] font-mono text-fg2 uppercase tracking-widest">Scan Progress</span>
             <span className={cn(
               "text-xs font-mono font-bold",
               scanProgress === 100 ? "text-hud-mint" : "text-hud-amber"
             )}>
               {scanProgress.toFixed(1)}%
             </span>
          </div>
          <div className="h-1.5 bg-white/5 relative overflow-hidden">
             <motion.div 
               className={cn(
                 "h-full transition-colors duration-500",
                 scanProgress === 100 ? "bg-hud-mint" : "bg-hud-amber"
               )}
               initial={{ width: 0 }}
               animate={{ width: `${scanProgress}%` }}
             />
             <div className="absolute inset-0 fx-march border-t border-white/10 opacity-20" />
          </div>
        </div>
      </div>
    </div>
  );
}
