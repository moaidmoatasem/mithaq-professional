import React, { useState } from 'react';
import { CyberButton } from '../atoms/CyberButton';
import { X, Globe, Shield, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '@/src/lib/utils';

interface NewScanFormProps {
  onSubmit: (data: any) => Promise<void>;
  onClose: () => void;
  isOpen: boolean;
}

export function NewScanForm({ onSubmit, onClose, isOpen }: NewScanFormProps) {
  const [target, setTarget] = useState('https://target.example.com');
  const [profile, setProfile] = useState('web');
  const [rps, setRps] = useState(5);
  const [burhan, setBurhan] = useState(true);
  const [compliance, setCompliance] = useState('egyfincsf');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await onSubmit({
        target,
        profile,
        rps,
        burhan,
        compliance_framework: compliance
      });
      onClose();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Unknown error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="w-full max-w-lg bg-[#0a0a0a] border border-white/10 p-6 hud-bracket relative shadow-2xl overflow-hidden"
          >
            <button 
              onClick={onClose}
              className="absolute top-6 right-6 text-fg3 hover:text-white transition-colors"
            >
              <X size={20} />
            </button>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 flex items-center justify-center bg-cherenkov-accent/10 border border-cherenkov-accent/20">
                <Globe size={20} className="text-cherenkov-accent" />
              </div>
              <div>
                <h3 className="text-lg font-black text-white uppercase tracking-tight">Configure New Scan</h3>
                <p className="text-[10px] font-mono text-fg3 uppercase tracking-widest leading-none mt-1">Initiate Operational Sequence</p>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-fg2 uppercase tracking-widest">Target URL</label>
                <input 
                  type="text" 
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 p-2 text-xs font-mono text-white outline-none focus:border-hud-cyan transition-colors"
                  required
                />
                {error && (
                  <p className="text-sev-critical text-[10px] font-mono uppercase mt-1 animate-pulse">{error}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-fg2 uppercase tracking-widest">Profile</label>
                  <select 
                    value={profile}
                    onChange={(e) => setProfile(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 p-2 text-xs font-mono text-fg1 outline-none focus:border-hud-cyan transition-colors appearance-none"
                  >
                    <option value="web">Web Application</option>
                    <option value="mobile">Mobile API</option>
                    <option value="infrastructure">Infrastructure</option>
                    <option value="ai_surface">AI Surface</option>
                  </select>
                </div>
                
                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-fg2 uppercase tracking-widest">Compliance</label>
                  <select 
                    value={compliance}
                    onChange={(e) => setCompliance(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 p-2 text-xs font-mono text-fg1 outline-none focus:border-hud-cyan transition-colors appearance-none"
                  >
                    <option value="egyfincsf">EGY-FIN CSF</option>
                    <option value="samacsf">SAMA CSF</option>
                    <option value="dora">DORA</option>
                    <option value="owasp">OWASP Top 10</option>
                  </select>
                </div>
              </div>

              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity size={14} className="text-fg2" />
                    <label className="text-[10px] font-mono text-fg2 uppercase tracking-widest">Rate Limit (RPS)</label>
                  </div>
                  <span className="text-[10px] font-mono text-hud-cyan font-bold">{rps} Req/s</span>
                </div>
                <input 
                  type="range" 
                  min="1" max="50" 
                  value={rps}
                  onChange={(e) => setRps(parseInt(e.target.value))}
                  className="w-full accent-hud-cyan h-1 bg-white/10 appearance-none rounded-none"
                />
              </div>

              <div className="pt-2 border-t border-white/5 mt-4">
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className={cn(
                    "w-4 h-4 border flex items-center justify-center transition-colors",
                    burhan ? "bg-hud-cyan/20 border-hud-cyan" : "bg-black/40 border-white/20"
                  )}>
                    {burhan && <Shield size={10} className="text-hud-cyan" />}
                  </div>
                  <span className="text-[10px] font-mono text-fg2 uppercase tracking-widest group-hover:text-white transition-colors">Enable Burhan (PoC Validation)</span>
                  <input type="checkbox" className="hidden" checked={burhan} onChange={(e) => setBurhan(e.target.checked)} />
                </label>
              </div>

              <div className="flex gap-3 pt-6 border-t border-white/10">
                <CyberButton 
                  variant="ghost"
                  className="flex-1"
                  onClick={onClose}
                  type="button"
                >
                  CANCEL
                </CyberButton>
                <CyberButton 
                  variant="primary"
                  className="flex-1"
                  type="submit"
                  loading={loading}
                >
                  LAUNCH SCAN
                </CyberButton>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
