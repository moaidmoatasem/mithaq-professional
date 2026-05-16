/**
 * Cherenkov API Client
 * Centralized API configuration and helper functions.
 * In dev, Vite proxies /api/* to the backend.
 * In production builds, the static files are served by the FastAPI backend itself.
 */

// In development, Vite proxies /api -> http://localhost:8000/api
// In production, same-origin requests work directly.
export const API_BASE = '/api/v1';
export const WS_BASE = `ws://${window.location.hostname}:8000`;

export interface ScanRequestPayload {
  url: string;
  profile?: string;
  rps?: number;
  burhan?: boolean;
  compliance_framework?: string;
}

export interface ScanResult {
  scan_id: string;
  target: string;
  timestamp: string;
  vulnerabilities: Vulnerability[];
  count: number;
}

export interface Vulnerability {
  scanner: string;
  title: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  cwe: string;
  description: string;
  remediation: string;
}

export interface HealthResponse {
  status: string;
  agents: string;
  queue: { scan_jobs_pending: number };
  uptime: number;
  nodes: Record<string, NodeInfo>;
  meissner: { state: string };
  active_scans: number;
}

export interface NodeInfo {
  status: 'ready' | 'busy' | 'offline';
  model?: string;
  ram_gb?: number;
  vector_count?: number;
  active_containers?: number;
}

/**
 * POST a new scan request to the backend.
 */
export async function submitScan(payload: ScanRequestPayload): Promise<ScanResult> {
  const res = await fetch(`${API_BASE}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: payload.url }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Scan failed with status ${res.status}`);
  }

  return res.json();
}

/**
 * Fetch scan history from the backend.
 */
export async function fetchScanHistory(): Promise<ScanResult[]> {
  const res = await fetch(`${API_BASE}/scans/history`);
  if (!res.ok) return [];
  return res.json();
}
