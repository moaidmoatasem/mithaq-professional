import { useState } from 'react';
import { cn } from '@/src/lib/utils';
import { motion, AnimatePresence } from 'motion/react';
import { CyberBadge } from '../atoms/CyberBadge';
import { PulseDot } from '../atoms/PulseDot';
import { CyberButton } from '../atoms/CyberButton';

type Severity = 'critical' | 'high' | 'medium' | 'low' | 'safe';

export interface VulnCardProps {
  title: string;
  severity: Severity;
  score: string;
  description?: string;
  scanner?: string;
  cve?: string;
  traceId?: string;
  onViewProof?: () => void;
  className?: string;
  key?: string | number;
}

export function VulnCard({
  title,
  severity,
  score,
  description,
  scanner,
  cve,
  traceId,
  onViewProof,
  className
}: VulnCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const severityColors: Record<Severity, string> = {
    critical: 'border-sev-critical',
    high: 'border-sev-critical/70',
    medium: 'border-sev-medium',
    low: 'border-sev-low',
    safe: 'border-hud-mint',
  };

  const bgStyles: Record<Severity, string> = {
    critical: 'bg-gradient-to-r from-sev-critical/10 to-transparent',
    high: 'bg-gradient-to-r from-sev-critical/5 to-transparent',
    medium: 'bg-transparent',
    low: 'bg-transparent',
    safe: 'bg-transparent',
  };

  const isFailClosed = !traceId;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
      className={cn(
        "relative border-l-3 bg-bg-surface overflow-hidden group cursor-pointer transition-colors hover:bg-white/[0.02]",
        severityColors[severity],
        bgStyles[severity],
        className
      )}
      style={{
        clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))'
      }}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center gap-2">
            <CyberBadge text={severity} type={severity === 'safe' ? 'safe' : severity === 'critical' || severity === 'high' ? 'critical' : severity === 'medium' ? 'medium' : 'low'} />
            <span className="text-[10px] font-mono text-fg2">SCORE: {score}</span>
          </div>
          <PulseDot color={severity === 'critical' ? 'red' : severity === 'high' ? 'red' : severity === 'safe' ? 'green' : 'amber'} />
        </div>

        <h4 className="text-white font-bold text-sm mb-1 group-hover:text-hud-cyan transition-colors">
          {isFailClosed && <span className="text-hud-amber mr-2">[UNVERIFIED]</span>}
          {title}
        </h4>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-4 pt-4 border-t border-white/5 space-y-3"
            >
              {description && <p className="text-xs text-soft leading-relaxed">{description}</p>}
              
              <div className="grid grid-cols-2 gap-4">
                {scanner && (
                  <div className="space-y-1">
                    <p className="text-[9px] font-mono text-fg3 uppercase">Scanner</p>
                    <p className="text-[10px] font-mono text-fg2">{scanner}</p>
                  </div>
                )}
                {cve && (
                  <div className="space-y-1">
                    <p className="text-[9px] font-mono text-fg3 uppercase">CVE_ID</p>
                    <p className="text-[10px] font-mono text-fg2">{cve}</p>
                  </div>
                )}
              </div>

              {traceId && (
                <div className="space-y-1">
                  <p className="text-[9px] font-mono text-fg3 uppercase">Cherenkov_Trace</p>
                  <p className="text-[10px] font-mono text-hud-cyan truncate uppercase tracking-widest">{traceId}</p>
                </div>
              )}

              {!isFailClosed && onViewProof && (
                <div className="pt-2">
                  <CyberButton 
                    text="VIEW PROOF" 
                    variant="ghost" 
                    className="w-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      onViewProof();
                    }}
                  />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      {/* HUD Active Bar */}
      <div className="absolute top-0 right-0 w-8 h-px bg-hud-cyan opacity-20" />
      <div className="absolute bottom-0 left-0 w-8 h-px bg-hud-cyan opacity-20" />
    </motion.div>
  );
}
