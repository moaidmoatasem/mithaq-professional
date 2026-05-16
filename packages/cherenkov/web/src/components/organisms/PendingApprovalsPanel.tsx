import { useState } from 'react';
import { usePendingApprovals } from '@/src/hooks/useMetrics';
import { approveFinding, rejectFinding } from '@/src/lib/api';
import { CyberBadge } from '../atoms/CyberBadge';
import { CyberButton } from '../atoms/CyberButton';
import { ShieldAlert, Check, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export function PendingApprovalsPanel() {
  const { data: pendingFindings } = usePendingApprovals(5000);
  const [loading, setLoading] = useState<string | null>(null);

  const handleApprove = async (id: string) => {
    setLoading(id);
    try {
      await approveFinding(id);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(null);
    }
  };

  const handleReject = async (id: string) => {
    setLoading(id);
    try {
      await rejectFinding(id);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(null);
    }
  };

  if (!pendingFindings || pendingFindings.length === 0) {
    return (
      <div className="bg-bg-surface p-4 border border-white/5 hud-bracket flex flex-col items-center justify-center py-8 opacity-50">
        <ShieldAlert size={24} className="text-fg3 mb-3" />
        <span className="text-[10px] font-mono text-fg3 uppercase tracking-widest">No pending approvals</span>
      </div>
    );
  }

  return (
    <div className="bg-bg-surface p-4 border border-white/5 hud-bracket flex flex-col gap-4 max-h-[400px] overflow-y-auto custom-scrollbar">
      <div className="flex items-center gap-2 mb-2">
        <ShieldAlert size={14} className="text-hud-amber" />
        <span className="text-[10px] font-mono text-hud-amber uppercase tracking-[0.2em]">Pending_HITL_Approvals</span>
      </div>
      <AnimatePresence>
        {pendingFindings.map((finding: any) => (
          <motion.div
            key={finding.id}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border border-white/10 bg-black/40 p-3 flex flex-col gap-3"
          >
            <div className="flex items-start justify-between">
              <div className="flex flex-col">
                <span className="text-[11px] font-bold text-white uppercase">{finding.title}</span>
                <span className="text-[9px] font-mono text-fg3">{finding.scanner}</span>
              </div>
              <CyberBadge 
                text={finding.severity} 
                type={finding.severity === 'critical' ? 'critical' : finding.severity === 'high' ? 'high' : finding.severity === 'medium' ? 'medium' : 'low'} 
              />
            </div>
            <div className="flex gap-2 mt-2">
              <CyberButton 
                variant="primary" 
                className="flex-1 py-1 text-[9px]"
                disabled={loading === finding.id}
                onClick={() => handleApprove(finding.id)}
              >
                <Check size={12} className="mr-1" /> Approve
              </CyberButton>
              <CyberButton 
                variant="danger" 
                className="flex-1 py-1 text-[9px]"
                disabled={loading === finding.id}
                onClick={() => handleReject(finding.id)}
              >
                <X size={12} className="mr-1" /> Reject
              </CyberButton>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
