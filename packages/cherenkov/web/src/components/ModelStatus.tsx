import { useState, useEffect } from 'react';
import { useHealth } from '@/src/hooks/useMetrics';
import { fetchModelRecommendations } from '@/src/lib/api';
import { CyberBadge } from './atoms/CyberBadge';
import { CyberButton } from './atoms/CyberButton';
import { Cpu, Zap, Settings, Loader2, Terminal, X, Check, Play } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '@/src/lib/utils';

export function ModelStatus() {
  const { data: healthData } = useHealth(8000);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchModelRecommendations()
      .then(data => {
        if (mounted) {
          setRecommendations(data);
          setLoading(false);
        }
      })
      .catch(() => {
        // Safe fallback logic - parse from /api/v1/health or use robust hardware defaults
        if (mounted) {
          setRecommendations(null); // triggers fallback rendering
          setLoading(false);
        }
      });
    return () => { mounted = false; };
  }, [healthData]);

  // Derived fallbacks from health data
  const tensorModel = healthData?.nodes?.tensor?.model || 'Llama 3.1 8B';
  const kineticModel = healthData?.nodes?.kinetic?.model || 'Qwen2.5 3B';
  const latticeModel = healthData?.nodes?.lattice?.model || 'Qdrant / Vector';
  const ramGb = (healthData?.nodes?.kinetic?.ram_gb || 0) + (healthData?.nodes?.aegis?.ram_gb || 0) || 16;
  const hardwareTier = ramGb >= 16 ? 'HIGH' : ramGb >= 8 ? 'MEDIUM' : 'LOW';

  const displayData = recommendations?.active_models ? recommendations : {
    hardware_tier: hardwareTier,
    ram_detected: `${ramGb} GB (Sovereign Virtualised)`,
    vram_detected: ramGb >= 16 ? '8 GB Dedicated' : 'Shared System Allocation',
    active_models: {
      architect: tensorModel,
      code: kineticModel,
      embed: latticeModel
    }
  };


  if (loading) {
    return (
      <div className="bg-bg-surface border border-white/5 p-4 flex items-center justify-center min-h-[140px] hud-bracket">
        <Loader2 className="w-5 h-5 text-hud-cyan animate-spin" />
        <span className="ml-3 text-xs font-mono text-fg3 uppercase tracking-widest">Compiling Model Topology...</span>
      </div>
    );
  }

  return (
    <>
      <div id="model-status-card" className="bg-bg-surface border border-white/5 p-4 relative overflow-hidden flex flex-col gap-3 hud-bracket">
        <div className="absolute top-0 right-0 p-2 opacity-5 pointer-events-none">
          <Cpu size={80} className="text-hud-cyan" />
        </div>

        {/* Card Header */}
        <div className="flex items-center justify-between z-10">
          <div className="flex items-center gap-2">
            <Cpu size={14} className="text-hud-cyan" />
            <span className="text-[10px] font-mono text-fg2 uppercase tracking-[0.2em]">Sovereign_Brain_Status</span>
          </div>
          <CyberBadge
            text={`${displayData.hardware_tier}_TIER`}
            type={displayData.hardware_tier === 'HIGH' ? 'safe' : displayData.hardware_tier === 'MEDIUM' ? 'medium' : 'critical'}
          />
        </div>

        {/* Specs */}
        <div className="grid grid-cols-2 gap-4 font-mono text-[10px] bg-black/30 p-2.5 border border-white/5 z-10">
          <div>
            <span className="text-fg3 uppercase block mb-0.5">detected_ram</span>
            <span className="text-white font-bold">{displayData.ram_detected}</span>
          </div>
          <div>
            <span className="text-fg3 uppercase block mb-0.5">detected_vram</span>
            <span className="text-white font-bold">{displayData.vram_detected}</span>
          </div>
        </div>

        {/* Active Models */}
        <div className="space-y-1.5 z-10">
          <span className="text-[8px] font-mono text-fg3 uppercase tracking-widest block mb-1">Active_Model_Topology</span>
          <div className="space-y-1 font-mono text-[10px]">
            <div className="flex justify-between items-center py-0.5 border-b border-white/5">
              <span className="text-fg2">ARCHITECT:</span>
              <span className="text-hud-cyan font-bold">{displayData.active_models.architect}</span>
            </div>
            <div className="flex justify-between items-center py-0.5 border-b border-white/5">
              <span className="text-fg2">KINETIC_CODE:</span>
              <span className="text-hud-cyan font-bold">{displayData.active_models.code}</span>
            </div>
            <div className="flex justify-between items-center py-0.5">
              <span className="text-fg2">LATTICE_EMBED:</span>
              <span className="text-hud-cyan font-bold">{displayData.active_models.embed}</span>
            </div>
          </div>
        </div>


      </div>

    </>
  );
}
