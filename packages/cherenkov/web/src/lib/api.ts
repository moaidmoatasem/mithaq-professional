/**
 * Cherenkov API Client
 * Centralized API configuration and helper functions.
 * In dev, Vite proxies /api/* to the backend.
 * In production builds, the static files are served by the FastAPI backend itself.
 */

// In development, Vite proxies /api and /ws to http://127.0.0.1:8000.
// In production, same-origin requests work directly.
export const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (window.location.origin.endsWith('/api/v1') ? window.location.origin : `${window.location.origin}/api/v1`);

/**
 * Derive the correct WebSocket base URL from the current origin.
 * Vite's proxy forwards /ws → ws://127.0.0.1:8000 in dev,
 * so we always use same-origin (no hard-coded port).
 */
export function getWsUrl(path: string = '/ws/live'): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}${path}`;
}

/**
 * Get unified authorization headers for API requests.
 */
export function getAuthHeaders(): Record<string, string> {
  const token = sessionStorage.getItem("cherenkov_token");
  if (!token) return { "Content-Type": "application/json" };
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

/**
 * Get the current auth token from sessionStorage and return as a Header object.
 * Provided for backward compatibility.
 */
export function getAuthHeader(): Record<string, string> {
  const token = sessionStorage.getItem('cherenkov_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

/**
 * Clear the current auth session.
 */
export function logout(): void {
  sessionStorage.removeItem('cherenkov_token');
  window.location.reload();
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
  trace_hash?: string;
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
  confirmed?: boolean;
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

export interface FindingApproval {
  id?: number;
  finding_id: string;
  severity: string;
  scanner: string;
  title: string;
  status: 'pending' | 'approved' | 'rejected';
  operator_id?: string | null;
  approved_at?: string | null;
  scan_id?: string | null;
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
    headers: getAuthHeaders(),
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
  const res = await fetch(`${API_BASE}/scans/history`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) return [];
  return res.json();
}

/**
 * Fetch pending approvals (HITL gate)
 */
export async function fetchPendingApprovals(): Promise<FindingApproval[]> {
  const res = await fetch(`${API_BASE}/findings/pending`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) return [];
  return res.json();
}

/**
 * Approve a finding
 */
export async function approveFinding(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/findings/${id}/approve`, {
    method: 'POST',
    headers: getAuthHeaders()
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
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    throw new Error(`Failed to reject finding ${id}`);
  }
}

/**
 * Fetch the CHERENKOV audit log (Admin only)
 */
export async function fetchAuditLog(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/audit`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) return [];
  return res.json();
}

/**
 * Fetch compliance report for a specific scan and framework.
 */
export async function fetchComplianceReport(scanId: string, framework: string): Promise<any> {
  const res = await fetch(`${API_BASE}/scan/${scanId}/compliance/${framework}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch compliance report for scan ${scanId} and framework ${framework}`);
  }
  return res.json();
}

/**
 * Fetch active model recommendation and system status configurations.
 */
export async function fetchModelRecommendations(): Promise<any> {
  const res = await fetch(`${API_BASE}/models/recommend`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    throw new Error('Failed to fetch model recommendations');
  }
  return res.json();
}
