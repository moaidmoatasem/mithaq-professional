import { useState, useEffect } from 'react';
import { API_BASE, getAuthHeaders } from '@/src/lib/api';
import type { FindingApproval } from '@/src/lib/api';

export interface PollingOptions<T> {
  initialData: T;
}

export function usePolling<T>(url: string, intervalMs: number, options?: PollingOptions<T>) {
  const [data, setData] = useState<T | null>(options?.initialData ?? null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        const res = await fetch(url, { headers: getAuthHeaders() });
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const json = await res.json();
        if (mounted) {
          setData(json);
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
  }, [url, intervalMs]);

  return { data, error };
}

export function useHealth(intervalMs = 5000) {
  return usePolling<any>(`${API_BASE}/health`, intervalMs);
}

export function useAblationStats(intervalMs = 10000) {
  return usePolling<any>(`${API_BASE}/ablation/stats`, intervalMs);
}

export function useQueueDepth(intervalMs = 5000) {
  const { data } = usePolling<any>(`${API_BASE}/health`, intervalMs);
  const [history, setHistory] = useState<number[]>([]);
  const [current, setCurrent] = useState<number>(0);

  useEffect(() => {
    if (data) {
      const depth = data?.queue?.scan_jobs_pending ?? 0;
      setCurrent(depth);
      setHistory(prev => {
        const next = [...prev, depth];
        if (next.length > 20) return next.slice(next.length - 20);
        return next;
      });
    }
  }, [data]);

  return { history, current };
}

export function usePendingApprovals(intervalMs = 5000) {
  const { data, error } = usePolling<FindingApproval[]>(`${API_BASE}/findings/pending`, intervalMs, { initialData: [] });
  return { data: data ?? [], error };
}
