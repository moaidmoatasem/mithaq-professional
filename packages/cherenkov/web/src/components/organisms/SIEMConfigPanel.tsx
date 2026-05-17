import { useState } from 'react';
import { Share2, Server, Key, Save, CheckCircle } from 'lucide-react';
import { CyberButton } from '../atoms/CyberButton';

export function SIEMConfigPanel() {
  const [syslogHost, setSyslogHost] = useState('localhost');
  const [syslogPort, setSyslogPort] = useState('514');
  const [splunkUrl, setSplunkUrl] = useState('');
  const [splunkToken, setSplunkToken] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
    // In a real app, this would POST to /api/v1/admin/siem/config
  };

  return (
    <div className="bg-bg-surface p-6 border border-white/5 hud-bracket flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Share2 className="text-hud-cyan" size={24} />
        <h2 className="text-lg font-bold text-white uppercase tracking-wider">SIEM_Integration_Bridge</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Syslog Config */}
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-hud-green border-b border-white/10 pb-2">
            <Server size={14} />
            <span className="text-[10px] font-mono uppercase">Syslog_UDP_CEF</span>
          </div>
          
          <div className="flex flex-col gap-1">
            <label className="text-[9px] font-mono text-fg3 uppercase">Target_Host</label>
            <input 
              type="text" 
              value={syslogHost}
              onChange={(e) => setSyslogHost(e.target.value)}
              className="bg-black/50 border border-white/10 p-2 text-[12px] font-mono text-white focus:border-hud-cyan outline-none"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[9px] font-mono text-fg3 uppercase">Port</label>
            <input 
              type="text" 
              value={syslogPort}
              onChange={(e) => setSyslogPort(e.target.value)}
              className="bg-black/50 border border-white/10 p-2 text-[12px] font-mono text-white focus:border-hud-cyan outline-none"
            />
          </div>
        </div>

        {/* Splunk Config */}
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-hud-amber border-b border-white/10 pb-2">
            <Key size={14} />
            <span className="text-[10px] font-mono uppercase">Splunk_HEC_HTTPS</span>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[9px] font-mono text-fg3 uppercase">HEC_URL</label>
            <input 
              type="text" 
              value={splunkUrl}
              onChange={(e) => setSplunkUrl(e.target.value)}
              placeholder="https://splunk:8088/services/collector"
              className="bg-black/50 border border-white/10 p-2 text-[12px] font-mono text-white focus:border-hud-cyan outline-none"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[9px] font-mono text-fg3 uppercase">HEC_Token</label>
            <input 
              type="password" 
              value={splunkToken}
              onChange={(e) => setSplunkToken(e.target.value)}
              placeholder="GUID"
              className="bg-black/50 border border-white/10 p-2 text-[12px] font-mono text-white focus:border-hud-cyan outline-none"
            />
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-white/10 pt-4 mt-2">
        <div className="flex flex-col">
          <span className="text-[10px] font-mono text-fg3 uppercase">Bridge_State</span>
          <span className="text-[11px] font-bold text-hud-cyan uppercase">Authenticated_Handshake</span>
        </div>
        
        <CyberButton 
          onClick={handleSave}
          className="px-8"
          variant="primary"
        >
          {saved ? (
            <div className="flex items-center gap-2">
              <CheckCircle size={14} />
              <span>CONFIG_SYNCED</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Save size={14} />
              <span>SAVE_SIEM_BRIDGE</span>
            </div>
          )}
        </CyberButton>
      </div>
    </div>
  );
}
