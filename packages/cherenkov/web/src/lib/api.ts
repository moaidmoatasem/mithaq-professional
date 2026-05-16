/**
 * Cherenkov API Client
 * Centralized API configuration and helper functions.
 * In dev, Vite proxies /api/* to the backend.
 * In production builds, the static files are served by the FastAPI backend itself.
 */

// In development, Vite proxies /api and /ws to http://127.0.0.1:8000.
// In production, same-origin requests work directly.
export const API_BASE = '/api/v1';

/**
 * Derive the correct WebSocket base URL from the current origin.
 * Vite's proxy forwards /ws → ws://127.0.0.1:8000 in dev,
 * so we always use same-origin (no hard-coded port).
 */
export function getWsUrl(path: string = '/ws/live'): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}${path}`;
}

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
  id?: string;
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

/**
 * Fetch pending approvals (HITL gate)
 */
export async function fetchPendingApprovals(): Promise<Vulnerability[]> {
  const res = await fetch(`${API_BASE}/findings/pending`);
  if (!res.ok) return [];
  return res.json();
}

/**
 * Approve a finding
 */
export async function approveFinding(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/findings/${id}/approve`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to approve finding ${id}`);
  }
}

/**
 * Reject a finding
 */
export async function rejectFinding(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/findings/${id}/reject`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to reject finding ${id}`);
  }
}
