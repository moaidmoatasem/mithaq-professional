import React, { useState, useEffect, useRef } from 'react';
import {
  Shield,
  Activity,
  Terminal as TermIcon,
  Database,
  Cpu,
  Lock,
  Play,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Wifi,
  FileText
} from 'lucide-react';

export default function ScannerDashboard() {
  // Authentication & Blocker state
  const [rotationRequired, setRotationRequired] = useState(true);
  const [passphrase, setPassphrase] = useState('');
  const [authError, setAuthError] = useState('');
  const [authSuccess, setAuthSuccess] = useState('');

  // Health & Diagnostics state
  const [health, setHealth] = useState<any>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Scanning state
  const [code, setCode] = useState('// Paste your code here to scan for vulnerabilities\nfunction queryUser(userId) {\n  let query = "SELECT * FROM users WHERE id = " + userId;\n  return db.execute(query);\n}');
  const [backend, setBackend] = useState('ollama');
  const [model, setModel] = useState('qwen2.5-coder:7b');
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);
  const [scanError, setScanError] = useState('');

  // WebSocket Logs State
  const [logs, setLogs] = useState<string[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const consoleEndRef = useRef<HTMLDivElement | null>(null);

  // Poll health and status on mount
  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  // Handle WebSocket telemetry setup
  useEffect(() => {
    if (!rotationRequired) {
      connectWebSocket();
    }
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [rotationRequired]);

  // Scroll to bottom of logs
  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const fetchHealth = async () => {
    try {
      const res = await fetch('http://localhost:8080/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
        setRotationRequired(data.rotation_required);
      }
      setHealthLoading(false);
    } catch (err) {
      console.error('Failed to fetch health data:', err);
      setHealthLoading(false);
    }
  };

  const generateSHA256 = async (str: string): Promise<string> => {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
  };

  const handleCredentialsRotation = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthSuccess('');

    if (passphrase.length < 8) {
      setAuthError('Passphrase must be at least 8 characters long.');
      return;
    }

    try {
      const secureHash = await generateSHA256(passphrase);
      const res = await fetch('http://localhost:8080/api/auth/rotate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hash: secureHash })
      });

      const data = await res.json();
      if (res.ok) {
        setAuthSuccess('Credentials rotated successfully! Unlocking system.');
        setTimeout(() => {
          setRotationRequired(false);
          fetchHealth();
        }, 1000);
      } else {
        setAuthError(data.detail || 'Rotation attempt failed.');
      }
    } catch (err) {
      setAuthError('Network communication error with authentication gateway.');
    }
  };

  const connectWebSocket = async () => {
    try {
      // 1. Ask backend for a signed token
      const tokenRes = await fetch('http://localhost:8080/api/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin' })
      });

      if (!tokenRes.ok) return;
      const { token } = await tokenRes.json();

      // 2. Establish connection
      const wsUrl = `ws://localhost:8080/api/ws/logs?token=${token}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        setLogs(prev => [...prev, '[SYSTEM-GATE] Authorized WebSocket security stream established.']);
      };

      ws.onmessage = (event) => {
        setLogs(prev => [...prev, event.data]);
      };

      ws.onclose = () => {
        setWsConnected(false);
        setLogs(prev => [...prev, '[SYSTEM-GATE] WebSocket security stream disconnected.']);
        // Attempt reconnection in 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    } catch (err) {
      console.error('WebSocket connection handshake error:', err);
    }
  };

  const handleScanTrigger = async () => {
    if (!code.trim()) return;
    setIsScanning(true);
    setScanResult(null);
    setScanError('');

    setLogs(prev => [...prev, `[TENSOR-SCAN] Starting scanning swarm using backend [${backend.toUpperCase()}]...`]);

    try {
      const res = await fetch('http://localhost:8080/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, backend, model })
      });

      const data = await res.json();
      if (res.ok) {
        setScanResult(data);
        setLogs(prev => [...prev, '[TENSOR-SCAN] Swarm analysis scan executed with 100% telemetry resolution.']);
      } else {
        setScanError(data.detail || 'Scanning operation failed.');
        setLogs(prev => [...prev, `[TENSOR-ERROR] Scan aborted: ${data.detail}`]);
      }
    } catch (err) {
      setScanError('Failed to establish contact with local scanning agent runner.');
    } finally {
      setIsScanning(false);
    }
  };

  const clearConsole = () => {
    setLogs([]);
    if (wsRef.current && wsConnected) {
      wsRef.current.send(JSON.stringify({ action: 'clear' }));
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
      {/* Header bar */}
      <header style={{ display: 'flex', justifycontent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2.2rem', color: 'var(--text-main)', marginBottom: '4px' }}>
            CHERENKOV <span style={{ color: 'var(--color-primary)', fontSize: '1rem', verticalAlign: 'super' }}>PRO v0.2.0</span>
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>Sovereign Air-Gapped Vulnerability Swarm Auditor</p>
        </div>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: 'rgba(255,255,255,0.02)', borderRadius: '20px', border: '1px solid var(--border-color)' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: wsConnected ? 'var(--color-success)' : 'var(--color-danger)' }} />
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              {wsConnected ? 'Telemetry Secure' : 'Telemetry Offline'}
            </span>
          </div>
        </div>
      </header>

      {/* First run Credentials blocker */}
      {rotationRequired ? (
        <div className="glass-panel" style={{ maxWidth: '500px', margin: '60px auto', borderLeft: '4px solid var(--color-warning)' }}>
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <Lock size={40} style={{ color: 'var(--color-warning)', marginBottom: '16px' }} />
            <h2 style={{ fontSize: '1.5rem', marginBottom: '8px' }}>Security Initialization Blocker</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              First-run policy requires that you rotate default credentials to configure local encryption.
            </p>
          </div>

          <form onSubmit={handleCredentialsRotation} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                New Secure Passphrase
              </label>
              <input
                type="password"
                className="form-input"
                placeholder="Minimum 8 characters..."
                value={passphrase}
                onChange={(e) => setPassphrase(e.target.value)}
              />
            </div>

            {authError && (
              <div style={{ fontSize: '0.85rem', color: 'var(--color-danger)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={16} /> {authError}
              </div>
            )}
            {authSuccess && (
              <div style={{ fontSize: '0.85rem', color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <CheckCircle size={16} /> {authSuccess}
              </div>
            )}

            <button type="submit" className="btn btn-primary" style={{ marginTop: '8px' }}>
              Rotate Credentials & Unlock
            </button>
          </form>
        </div>
      ) : (
        /* Regular Dashboard grid */
        <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: '24px' }}>

          {/* Left Column: Code Scan interface */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="glass-panel">
              <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Shield style={{ color: 'var(--color-primary)' }} size={20} /> Static Analysis Swarms
              </h2>

              <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Inference Runtime
                  </label>
                  <select
                    className="form-input"
                    value={backend}
                    onChange={(e) => {
                      setBackend(e.target.value);
                      setModel(e.target.value === 'ollama' ? 'qwen2.5-coder:7b' : '/home/moaid/cherenkov-professional/models/qwen2.5-coder-7b-int4-w4a16');
                    }}
                  >
                    <option value="ollama">Ollama (Control Baseline)</option>
                    <option value="vllm">vLLM Server (PagedAttention)</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Target Model
                  </label>
                  <select
                    className="form-input"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                  >
                    <option value={model}>{model.substring(model.lastIndexOf('/') + 1)}</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Target Source Code Snippet
                </label>
                <textarea
                  className="form-input"
                  style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', height: '200px', resize: 'vertical' }}
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button
                  className={`btn btn-primary ${isScanning ? 'btn-disabled' : ''}`}
                  onClick={handleScanTrigger}
                  disabled={isScanning}
                >
                  {isScanning ? (
                    <>
                      <RefreshCw className="animate-spin" size={18} /> Swarm Scanning...
                    </>
                  ) : (
                    <>
                      <Play size={18} /> Execute Agent Audit
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Scan findings outputs */}
            {scanResult && (
              <div className="glass-panel" style={{ borderLeft: '4px solid var(--color-success)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '1.1rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle style={{ color: 'var(--color-success)' }} size={18} /> Audit Report Findings
                  </h3>
                  {scanResult.secrets_redacted && (
                    <span style={{ fontSize: '0.75rem', padding: '4px 8px', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)', color: 'var(--color-warning)', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <AlertTriangle size={12} /> Secrets Redacted
                    </span>
                  )}
                </div>

                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-color)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', whiteSpace: 'pre-wrap', marginBottom: '16px', maxHeight: '300px', overflowY: 'auto' }}>
                  {scanResult.report}
                </div>

                {/* Performance specs panel */}
                {scanResult.performance && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', background: 'rgba(255,255,255,0.01)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ textAlign: 'center' }}>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>Throughput</span>
                      <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-primary)' }}>
                        {scanResult.performance.avg_tokens_per_second.toFixed(1)} tok/s
                      </span>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Tokens</span>
                      <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
                        {scanResult.performance.total_tokens}
                      </span>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>Inference Latency</span>
                      <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
                        {scanResult.performance.total_latency_seconds.toFixed(2)}s
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {scanError && (
              <div className="glass-panel" style={{ borderLeft: '4px solid var(--color-danger)' }}>
                <h3 style={{ fontSize: '1.1rem', color: 'var(--color-danger)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <AlertTriangle size={18} /> Scanning Swarm Aborted
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{scanError}</p>
              </div>
            )}
          </div>

          {/* Right Column: Health Diagnostics + Telemetry Console */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Health indicators */}
            <div className="glass-panel">
              <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity style={{ color: 'var(--color-success)' }} size={20} /> Autonomic Health Status
              </h2>

              {healthLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
                  <RefreshCw className="animate-spin" style={{ color: 'var(--text-muted)' }} />
                </div>
              ) : health ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Gateway State</span>
                    <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>{health.status}</span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Database size={16} style={{ color: 'var(--text-muted)' }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span>Registry Database</span>
                        <span style={{ color: 'var(--color-success)' }}>{health.readiness.database.status}</span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Latency: {health.readiness.database.latency_ms.toFixed(1)} ms
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Cpu size={16} style={{ color: 'var(--text-muted)' }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span>LLM Inference Host</span>
                        <span style={{ color: 'var(--color-success)' }}>{health.readiness.inference_runtime.status}</span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Latency: {health.readiness.inference_runtime.latency_ms.toFixed(1)} ms
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '10px' }}>
                    <span>Runtime Uptime</span>
                    <span>{Math.floor(health.liveness.uptime_seconds)}s</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    <span>Process PID</span>
                    <span>{health.liveness.pid}</span>
                  </div>
                </div>
              ) : (
                <p style={{ color: 'var(--color-danger)', fontSize: '0.9rem' }}>
                  Gateway communication timed out. Ensure WSL API server is active on :8080.
                </p>
              )}
            </div>

            {/* Real-time Telemetry Terminal Console */}
            <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TermIcon style={{ color: 'var(--color-primary)' }} size={20} /> Telemetry Audit Log
                </h2>
                <button
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                  onClick={clearConsole}
                >
                  <RefreshCw size={12} /> Clear
                </button>
              </div>

              <div className="terminal-window" style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '350px' }}>
                <div className="terminal-header">
                  <div className="terminal-dots">
                    <span className="terminal-dot" style={{ backgroundColor: '#ff5f56' }} />
                    <span className="terminal-dot" style={{ backgroundColor: '#ffbd2e' }} />
                    <span className="terminal-dot" style={{ backgroundColor: '#27c93f' }} />
                  </div>
                  <span style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Wifi size={12} style={{ color: wsConnected ? 'var(--color-success)' : 'var(--color-danger)' }} />
                    ws://localhost:8080/api/ws/logs
                  </span>
                </div>

                <div className="terminal-body" style={{ flex: 1, overflowY: 'auto' }}>
                  {logs.length === 0 ? (
                    <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Listening for active static scans...</span>
                  ) : (
                    logs.map((log, index) => {
                      let color = 'var(--text-main)';
                      if (log.includes('[ABLATION-SANITY]')) color = 'var(--color-warning)';
                      if (log.includes('[SYSTEM-GATE]')) color = 'var(--color-primary)';
                      if (log.includes('[TENSOR-SCAN]') || log.includes('[TENSOR-REASON]')) color = 'var(--color-success)';
                      if (log.includes('[TENSOR-ERROR]')) color = 'var(--color-danger)';

                      return (
                        <div key={index} style={{ color }}>
                          {log}
                        </div>
                      );
                    })
                  )}
                  <div ref={consoleEndRef} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
