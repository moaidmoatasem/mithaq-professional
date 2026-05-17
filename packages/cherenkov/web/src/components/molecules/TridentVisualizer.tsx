import { motion } from 'motion/react';
import { cn } from '@/src/lib/utils';
import { ShieldCheck } from 'lucide-react';

export type ContainmentState = 'MONITORING' | 'THREAT_DETECTED' | 'MEISSNER_LOCKED' | 'ABLATION_ACTIVE' | 'TOKAMAK_EXECUTING' | 'TRACE_SIGNED' | 'MOBILE_TRIAGE';

interface VisualizerProps {
  state: ContainmentState;
  traceId: string;
  className?: string;
}

export function TridentVisualizer({ state, traceId, className }: VisualizerProps) {
  return (
    <div className={cn("relative w-full h-full flex items-center justify-center bg-bg-canvas overflow-hidden", className)}>
      {/* HUD GRID */}
      <div className="absolute inset-0 bg-[length:32px_32px] bg-[linear-gradient(to_right,#2b7fff10_1px,transparent_1px),linear-gradient(to_bottom,#2b7fff10_1px,transparent_1px)]" />
      
      {/* CONCENTRIC RINGS */}
      <div className="relative flex items-center justify-center scale-75 md:scale-100">
        {/* MEISSNER OUTER RING */}
        <motion.div 
          animate={{ 
            borderColor: ['MEISSNER_LOCKED', 'ABLATION_ACTIVE', 'TOKAMAK_EXECUTING', 'TRACE_SIGNED'].includes(state)
              ? '#2b7fff' 
              : '#ffffff1a',
            scale: state === 'MEISSNER_LOCKED' ? [1, 1.02, 1] : 1,
            borderWidth: state === 'MEISSNER_LOCKED' ? '2px' : '1px'
          }}
          transition={{ duration: 0.3 }}
          className="w-64 h-64 rounded-full border border-white/10 flex items-center justify-center relative"
        >
          {/* ABLATION MIDDLE RING */}
          <motion.div 
            animate={{ 
              borderColor: ['ABLATION_ACTIVE', 'TOKAMAK_EXECUTING', 'TRACE_SIGNED'].includes(state)
                ? '#9D00FF' 
                : '#ffffff0a',
            }}
            className="w-48 h-48 rounded-full border border-white/5 flex items-center justify-center"
          >
            {/* TOKAMAK CORE */}
            <motion.div 
              animate={{ 
                scale: state === 'TOKAMAK_EXECUTING' ? [1, 1.1, 1] : 1,
                backgroundColor: state === 'TOKAMAK_EXECUTING' ? 'rgba(157, 0, 255, 0.1)' : 'rgba(0, 0, 0, 0.4)',
              }}
              transition={{ repeat: state === 'TOKAMAK_EXECUTING' ? Infinity : 0, duration: 1 }}
              className="w-32 h-32 rounded-full border border-white/5 flex items-center justify-center bg-black/40"
            >
              {state === 'MONITORING' && (
                <ShieldCheck size={32} className="text-white opacity-10" strokeWidth={1} />
              )}
            </motion.div>
          </motion.div>
        </motion.div>

        {/* THREAT NODE */}
        {state !== 'MONITORING' && (
          <motion.div
            initial={{ x: 200, opacity: 0 }}
            animate={{ 
              x: state === 'THREAT_DETECTED' ? 140 : 0, 
              opacity: 1,
              backgroundColor: state === 'ABLATION_ACTIVE' ? '#9CA3AF' : (state === 'THREAT_DETECTED' ? '#ff003d' : '#9D00FF')
            }}
            className={cn(
               "absolute w-4 h-4 rounded-sm shadow-lg z-20",
               state === 'THREAT_DETECTED' ? "shadow-sev-critical/40" : "shadow-cherenkov-accent/40"
            )}
          >
            {state === 'TOKAMAK_EXECUTING' && (
              <motion.div 
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 0.5 }}
                className="absolute -inset-2 border-2 border-cherenkov-accent rounded-sm"
              />
            )}
          </motion.div>
        )}

        {/* ABLATION SCAN LINE */}
        {state === 'ABLATION_ACTIVE' && (
          <motion.div 
            initial={{ x: -150 }}
            animate={{ x: 150 }}
            transition={{ duration: 1.5, ease: "linear", repeat: Infinity }}
            className="absolute h-[80%] w-px bg-hud-cyan shadow-[0_0_15px_rgba(0,224,255,0.8)] z-10"
          />
        )}
      </div>

      {/* FINAL TRACE BADGE */}
      {state === 'TRACE_SIGNED' && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          className="absolute inset-0 flex items-center justify-center z-50 bg-bg-canvas/60 backdrop-blur-sm"
        >
          <div className="bg-bg-surface border-2 border-hud-mint p-6 text-center hud-bracket shadow-[0_0_30px_rgba(0,255,148,0.3)]">
            <div className="flex items-center justify-center gap-3 mb-2 text-hud-mint">
               <ShieldCheck size={32} />
               <h3 className="text-2xl font-bold tracking-tight uppercase">Trace Signed</h3>
            </div>
            <div className="font-mono text-xs text-fg2 bg-black/40 px-4 py-2 mt-4">
               CT-2026-{traceId}
            </div>
            <p className="text-[10px] font-mono text-hud-mint mt-4 uppercase tracking-widest">PoC Execution Verified // Fail-Closed State</p>
          </div>
        </motion.div>
      )}

      {/* COORDINATE MARKERS */}
      <div className="absolute top-4 left-4 font-mono text-[10px] text-fg3 flex flex-col gap-1">
        <span>X_CORD: 0x44.1A</span>
        <span>Y_CORD: 0x88.21</span>
      </div>
    </div>
  );
}
