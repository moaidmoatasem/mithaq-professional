import { motion } from 'motion/react';
import { cn } from '@/src/lib/utils';
import { ShieldCheck, Crosshair, Zap } from 'lucide-react';

export type ContainmentState = 'MONITORING' | 'THREAT_DETECTED' | 'MEISSNER_LOCKED' | 'ABLATION_ACTIVE' | 'TOKAMAK_EXECUTING' | 'TRACE_SIGNED';

interface VisualizerProps {
  state: ContainmentState;
  traceId: string;
}

export function TridentVisualizer({ state, traceId }: VisualizerProps) {
  return (
    <div className="relative w-full h-full flex items-center justify-center bg-obsidian overflow-hidden">
      {/* HUD GRID */}
      <div className="absolute inset-0 bg-[length:32px_32px] bg-[linear-gradient(to_right,#2F5F8A1A_1px,transparent_1px),linear-gradient(to_bottom,#2F5F8A1A_1px,transparent_1px)]" />
      
      {/* CONCENTRIC RINGS */}
      <div className="relative flex items-center justify-center">
        {/* MEISSNER OUTER RING */}
        <motion.div 
          animate={{ 
            borderColor: state === 'MEISSNER_LOCKED' || state === 'ABLATION_ACTIVE' || state === 'TOKAMAK_EXECUTING' || state === 'TRACE_SIGNED' 
              ? '#00A3FF' 
              : '#2F5F8A',
            scale: state === 'MEISSNER_LOCKED' ? [1, 1.02, 1] : 1,
            borderWidth: state === 'MEISSNER_LOCKED' ? '2px' : '1px'
          }}
          transition={{ duration: 0.3 }}
          className="w-64 h-64 rounded-full border border-cobalt/30 flex items-center justify-center relative"
        >
          {/* ABLATION MIDDLE RING */}
          <motion.div 
            animate={{ 
              borderColor: state === 'ABLATION_ACTIVE' || state === 'TOKAMAK_EXECUTING' || state === 'TRACE_SIGNED' 
                ? '#7B4BFF' 
                : '#2F5F8A33',
            }}
            className="w-48 h-48 rounded-full border border-cobalt/20 flex items-center justify-center"
          >
            {/* TOKAMAK CORE */}
            <motion.div 
              animate={{ 
                scale: state === 'TOKAMAK_EXECUTING' ? [1, 1.1, 1] : 1,
                backgroundColor: state === 'TOKAMAK_EXECUTING' ? 'rgba(123, 75, 255, 0.1)' : 'rgba(0, 0, 0, 0.4)',
              }}
              transition={{ repeat: state === 'TOKAMAK_EXECUTING' ? Infinity : 0, duration: 1 }}
              className="w-32 h-32 rounded-full border border-cobalt/10 flex items-center justify-center bg-black/40"
            >
              {state === 'MONITORING' && (
                <ShieldCheck size={32} className="text-cobalt opacity-20" strokeWidth={1} />
              )}
            </motion.div>
          </motion.div>
        </motion.div>

        {/* THREAT NODE */}
        {(state !== 'MONITORING') && (
          <motion.div
            initial={{ x: 200, opacity: 0 }}
            animate={{ 
              x: state === 'THREAT_DETECTED' ? 140 : 0, 
              opacity: 1,
              backgroundColor: state === 'ABLATION_ACTIVE' ? '#9AA6B2' : (state === 'THREAT_DETECTED' ? '#FF4444' : '#7B4BFF')
            }}
            className={cn(
               "absolute w-4 h-4 rounded-sm shadow-lg",
               state === 'THREAT_DETECTED' ? "shadow-critical/40" : "shadow-bismuth/40"
            )}
          >
            {state === 'TOKAMAK_EXECUTING' && (
              <motion.div 
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 0.5 }}
                className="absolute -inset-2 border-2 border-bismuth rounded-sm"
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
            className="absolute h-full w-px bg-bismuth shadow-[0_0_15px_rgba(123,75,255,0.8)] z-10"
          />
        )}
      </div>

      {/* FINAL TRACE BADGE */}
      {state === 'TRACE_SIGNED' && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          className="absolute inset-0 flex items-center justify-center z-50 bg-obsidian/60 backdrop-blur-sm"
        >
          <div className="bg-surface border-2 border-verity p-6 chamfered text-center shadow-[0_0_30px_rgba(0,163,255,0.3)]">
            <div className="flex items-center justify-center gap-3 mb-2 text-verity">
               <ShieldCheck size={32} />
               <span className="text-2xl font-bold font-sans tracking-tight uppercase">Trace Signed</span>
            </div>
            <div className="font-mono text-xs text-steel/80 bg-black/40 px-4 py-2 mt-4">
               CT-2026-{traceId}
            </div>
            <p className="text-[10px] font-mono text-verity mt-4 uppercase tracking-widest">PoC Execution Verified // Fail-Closed State</p>
          </div>
        </motion.div>
      )}

      {/* COORDINATE MARKERS */}
      <div className="absolute top-4 left-4 font-mono text-[10px] text-cobalt flex flex-col gap-1">
        <span>X_CORD: 0x44.1A</span>
        <span>Y_CORD: 0x88.21</span>
      </div>
    </div>
  );
}
