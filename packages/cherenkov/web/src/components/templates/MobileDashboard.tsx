import React, { useState } from 'react';
import { MainLayout } from './MainLayout';
import { ForensicHeader } from '../organisms/ForensicHeader';
import { ThreatIntelPanel } from '../organisms/ThreatIntelPanel';
import { MobileTargetForm } from '../organisms/MobileTargetForm';
import { MobileResultsPanel } from '../organisms/MobileResultsPanel';
import { motion, AnimatePresence } from 'motion/react';

export function MobileDashboard() {
  const [scanResult, setScanResult] = useState<any>(null);
  const [isScanning, setIsScanning] = useState(false);

  const handleScanComplete = (result: any) => {
    setScanResult(result);
    setIsScanning(false);
  };

  return (
    <MainLayout
      header={<ForensicHeader />}
      sidebar={<ThreatIntelPanel />}
      content={
        <div className="flex flex-col gap-6 h-full overflow-hidden">
          <div className="flex items-center gap-3">
            <div className="w-1.5 h-6 bg-cherenkov-accent" />
            <h2 className="text-xl font-bold tracking-tight text-white uppercase">Mobile Triage Dashboard</h2>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 flex-1 overflow-hidden">
            <div className="flex flex-col gap-6">
              <MobileTargetForm 
                onScanStart={() => setIsScanning(true)}
                onScanComplete={handleScanComplete} 
              />
              
              <div className="bg-bg-surface p-6 border border-white/5 hud-bracket fx-sweep overflow-hidden">
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] font-mono text-fg3 uppercase tracking-widest">Sovereign_Compliance</span>
                  <div className="flex gap-4">
                    <div className="flex items-center gap-2 text-hud-mint">
                      <div className="w-2 h-2 rounded-full bg-hud-mint shadow-[0_0_8px_rgba(0,255,136,0.5)]" />
                      <span className="text-[11px] font-mono">SAMA_CSF</span>
                    </div>
                    <div className="flex items-center gap-2 text-hud-cyan">
                      <div className="w-2 h-2 rounded-full bg-hud-cyan shadow-[0_0_8px_rgba(43,127,255,0.5)]" />
                      <span className="text-[11px] font-mono">OWASP_MSTG</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="min-h-[400px] xl:min-h-0 relative">
              <AnimatePresence mode="wait">
                {isScanning ? (
                  <motion.div 
                    key="scanning"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-bg-surface border border-white/5 flex flex-col items-center justify-center gap-4"
                  >
                    <div className="w-16 h-16 border-2 border-cherenkov-accent/20 border-t-cherenkov-accent rounded-full animate-spin" />
                    <span className="text-xs font-mono text-cherenkov-accent animate-pulse uppercase tracking-widest">Analyzing_Binary_Integrity...</span>
                  </motion.div>
                ) : scanResult ? (
                  <MobileResultsPanel key="results" result={scanResult} />
                ) : (
                  <motion.div 
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="absolute inset-0 bg-bg-surface border border-white/5 flex flex-col items-center justify-center opacity-40 grayscale"
                  >
                    <div className="text-4xl mb-4">📱</div>
                    <span className="text-[10px] font-mono uppercase tracking-[0.2em]">Awaiting_Binary_Upload</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      }
    />
  );
}
