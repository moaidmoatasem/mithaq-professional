import { motion } from 'motion/react';
import { CherenkovLogo } from '../atoms/Logo';
import { PulseDot } from '../atoms/PulseDot';
import { cn } from '@/src/lib/utils';

export function LogoKit({ onClose }: { onClose: () => void }) {
  const colorPalette = [
    { name: 'Cherenkov_Spectrum', hex: 'GRD_V1', class: 'bg-gradient-to-br from-[#00E0FF] via-[#7000FF] to-[#FF00D6]', primary: true },
    { name: 'Cherenkov_Blue', hex: '#00E0FF', class: 'bg-[#00E0FF]' },
    { name: 'Bismuth_Purple', hex: '#9D00FF', class: 'bg-[#9D00FF]' },
    { name: 'Oversight_Cobalt', hex: '#2F5F8A', class: 'bg-[#2F5F8A]' },
    { name: 'Safe_Status', hex: '#00FF94', class: 'bg-[#00FF94]' },
    { name: 'Critical_Threat', hex: '#FF003D', class: 'bg-[#FF003D]' },
    { name: 'Reactor_Base', hex: '#09090B', class: 'bg-[#09090B] border-white/10' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 z-[2000] flex items-center justify-center p-4 md:p-12 overflow-y-auto bg-[#09090B]/90 backdrop-blur-2xl"
    >
      <div className="max-w-6xl w-full bg-[#09090B] border border-white/10 p-10 relative shadow-[0_0_150px_rgba(43,127,255,0.1)]" style={{ clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))' }}>
        <button 
          onClick={onClose}
          className="absolute top-6 right-6 text-fg3 hover:text-white transition-colors uppercase font-mono text-[10px] tracking-widest bg-white/5 px-4 py-1.5 border border-white/10"
        >
          [TERMINATE_IDENTITY_PREVIEW]
        </button>

        <div className="grid lg:grid-cols-12 gap-16">
          {/* Brand Identity Section */}
          <div className="lg:col-span-7 space-y-10">
            <div>
              <p className="text-[10px] font-mono text-hud-cyan mb-2 tracking-[0.3em] uppercase">System.Visual_Identity_v2.0</p>
              <h2 className="text-5xl font-bold tracking-tighter text-white">THE SENTINEL MARK</h2>
            </div>

            <div className="space-y-8">
              <div className="p-8 border border-white/5 bg-white/[0.03] flex flex-col md:flex-row items-center gap-10 group transition-all hover:bg-white/[0.05]" style={{ clipPath: 'polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 15px 100%, 0 calc(100% - 15px))' }}>
                <CherenkovLogo size={120} variant="full" className="group-hover:scale-105 transition-transform duration-500" />
                <div className="space-y-4">
                  <h3 className="text-3xl font-extrabold tracking-[0.1em] text-white">CHERENKOV</h3>
                  <p className="text-[11px] font-mono text-fg2 tracking-[0.5em] uppercase leading-relaxed opacity-60">
                    The Forensic Reveal<br/>
                    <span className="text-hud-cyan">Forensic_Signature_Alpha</span>
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                <div className="p-6 border border-white/5 bg-white/[0.02] flex flex-col items-center gap-4" style={{ clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))' }}>
                  <CherenkovLogo size={64} variant="cyan" />
                  <span className="text-[9px] font-mono text-hud-cyan/60 uppercase">Operational_Active</span>
                </div>
                <div className="p-6 border border-white/5 bg-white/[0.02] flex flex-col items-center gap-4" style={{ clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))' }}>
                  <CherenkovLogo size={64} variant="purple" />
                  <span className="text-[9px] font-mono text-cherenkov-accent/60 uppercase">Forensic_Deep</span>
                </div>
                <div className="p-6 border border-white/10 bg-black flex flex-col items-center gap-4 col-span-2 md:col-span-1" style={{ clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))' }}>
                   <CherenkovLogo size={64} variant="skeleton" className="opacity-40" />
                   <span className="text-[9px] font-mono text-white/30 uppercase">Structure_Only</span>
                </div>
              </div>
            </div>
          </div>

          {/* Core Specifications Section */}
          <div className="lg:col-span-5 space-y-10 border-l border-white/5 pl-10 hidden lg:block">
             <div className="space-y-6">
                <p className="text-[11px] font-mono text-fg3 tracking-widest uppercase border-b border-white/10 pb-2">Technical_Color_Stack</p>
                <div className="grid grid-cols-1 gap-6">
                  {colorPalette.map(color => (
                    <div key={color.name} className="flex items-center gap-5 group/color">
                      <div className={cn(
                        "h-12 w-12 border border-white/10 relative overflow-hidden transition-all duration-300 group-hover/color:scale-110 group-hover/color:border-white/30 shadow-2xl",
                        color.class
                      )} style={{ clipPath: 'polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px))' }}>
                        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
                      </div>
                      <div className="flex flex-col gap-1">
                         <div className="flex items-center gap-2">
                           <span className="text-[10px] font-bold font-mono text-white tracking-[0.2em] uppercase">{color.name}</span>
                           {color.primary && <span className="text-[8px] bg-hud-cyan/20 text-hud-cyan px-1.5 py-0.5 rounded-sm font-mono border border-hud-cyan/20">CORE_SYSTEM</span>}
                         </div>
                         <span className="text-[9px] font-mono text-fg3 uppercase tracking-widest opacity-60">{color.hex}</span>
                      </div>
                    </div>
                  ))}
                </div>
             </div>

             <div className="p-6 border border-cherenkov-accent/20 bg-cherenkov-accent/5 relative overflow-hidden group" style={{ clipPath: 'polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px))' }}>
                <div className="absolute top-0 right-0 w-24 h-24 bg-cherenkov-accent/10 blur-2xl group-hover:animate-pulse" />
                <p className="text-[10px] font-bold text-cherenkov-accent uppercase mb-3 flex items-center gap-2 relative z-10">
                  <PulseDot color="amber" /> PROTOCOL_AUTHORITY
                </p>
                <p className="text-[10px] text-fg2 leading-relaxed font-mono relative z-10">
                  This identity is derived from the Meissner effect (perfect diamagnetism). It guarantees to stakeholders that CHERENKOV is a closed system that reveals truth without leaking context.
                </p>
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
