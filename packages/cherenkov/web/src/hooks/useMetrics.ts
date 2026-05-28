import { useState, useEffect, useCallback } from 'react';
import { API_BASE, getAuthHeaders } from '@/src/lib/api';
import type { FindingApproval } from '@/src/lib/api';

function usePolling<T>(fetcher: () => Promise<T>, intervalMs: number, initial: T) {
  const [data, setData] = useState<T>(initial);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        const result = await fetcher();
        if (mounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err : new Error('Unknown error'));
        }
      }
    };

    fetchData();
    const int = setInterval(fetchData, intervalMs);
    return () => {
      mounted = false;
      clearInterval(int);
    };
  }, [intervalMs]);

  return { data, error };
}

export function useHealth(intervalMs = 5000) {
  const fetcher = useCallback(async () => {
    const res = await fetch(`${API_BASE}/health`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Backend offline');
    return res.json();
  }, []);

  return usePolling(fetcher, intervalMs, null);
}

export function useAblationStats(intervalMs = 10000) {
  const fetcher = useCallback(async () => {
    const res = await fetch(`${API_BASE}/ablation/stats`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Backend offline');
    return res.json();
  }, []);

  return usePolling(fetcher, intervalMs, null);
}

export function useQueueDepth(intervalMs = 5000) {
  const [history, setHistory] = useState<number[]>([]);
  const [current, setCurrent] = useState<number>(0);

  useEffect(() => {
    let mounted = true;
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`, { headers: getAuthHeaders() });
        if (!res.ok) return;
        const json = await res.json();
        if (mounted) {
          const depth = json?.queue?.scan_jobs_pending ?? 0;
          setCurrent(depth);
          setHistory(prev => {
            const next = [...prev, depth];
            if (next.length > 20) return next.slice(next.length - 20);
            return next;
          });
        }
      } catch (err) {
        // ignore
      }
    };

    fetchHealth();
    const int = setInterval(fetchHealth, intervalMs);
    return () => {
      mounted = false;
      clearInterval(int);
    };
  }, [intervalMs]);

  return { history, current };
}

export function usePendingApprovals(intervalMs = 5000) {
  const fetcher = useCallback(async () => {
    const res = await fetch(`${API_BASE}/findings/pending`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch pending approvals');
    return res.json() as Promise<FindingApproval[]>;
  }, []);

  return usePolling(fetcher, intervalMs, [] as FindingApproval[]);
}
