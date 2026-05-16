import React, { useState } from 'react';
import { CyberButton } from '../atoms/CyberButton';
import { Upload, Smartphone, ShieldCheck } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { submitScan } from '@/src/lib/api';

interface MobileTargetFormProps {
  onScanStart: () => void;
  onScanComplete: (result: any) => void;
}

export function MobileTargetForm({ onScanStart, onScanComplete }: MobileTargetFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    onScanStart();
    
    // In a real implementation, we'd use a multipart upload endpoint
    // For now, we simulate the scan with the current API
    try {
      const result = await submitScan({ url: `mobile://${file.name}` });
      onScanComplete(result);
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-bg-surface p-6 border border-white/5 relative overflow-hidden flex flex-col gap-6">
      <div className="absolute top-0 right-0 p-4 opacity-5">
        <Smartphone size={80} />
      </div>

      <div className="flex flex-col gap-1">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Upload size={16} className="text-cherenkov-accent" />
          Binary_Ingestion_Port
        </h3>
        <p className="text-[10px] text-fg3 font-mono">Upload .IPA or .APK for forensic decomposition</p>
      </div>

      <div 
        className={cn(
          "h-32 border border-dashed rounded-lg flex flex-col items-center justify-center gap-3 transition-colors relative group",
          file ? "border-hud-mint/40 bg-hud-mint/5" : "border-white/10 hover:border-cherenkov-accent/40"
        )}
      >
        <input 
          type="file" 
          accept=".ipa,.apk" 
          onChange={handleFileChange}
          className="absolute inset-0 opacity-0 cursor-pointer z-10"
        />
        {file ? (
          <>
            <ShieldCheck className="text-hud-mint" size={24} />
            <div className="flex flex-col items-center">
              <span className="text-xs font-mono text-white">{file.name}</span>
              <span className="text-[10px] font-mono text-fg3">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
            </div>
          </>
        ) : (
          <>
            <Upload className="text-fg3 group-hover:text-cherenkov-accent transition-colors" size={24} />
            <span className="text-[10px] font-mono text-fg3 uppercase tracking-widest">Drop_Binary_Here</span>
          </>
        )}
      </div>

      <div className="flex gap-4">
        <CyberButton 
          text={isUploading ? "PROCESS_ACTIVE..." : "INITIATE_DECOMPOSITION"}
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="flex-1"
        />
        <CyberButton 
          text="CLEAR"
          variant="ghost"
          onClick={() => setFile(null)}
          disabled={!file || isUploading}
        />
      </div>
    </div>
  );
}
