import { useState, useEffect } from 'react';
import { API_BASE } from '@/src/lib/api';
import type { FindingApproval } from '@/src/lib/api';

export function useHealth(intervalMs = 5000) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error('Backend offline');
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

    fetchHealth();
    const int = setInterval(fetchHealth, intervalMs);
    return () => {
      mounted = false;
      clearInterval(int);
    };
  }, [intervalMs]);

  return { data, error };
}

export function useAblationStats(intervalMs = 10000) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/ablation/stats`);
        if (!res.ok) throw new Error('Backend offline');
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

    fetchStats();
    const int = setInterval(fetchStats, intervalMs);
    return () => {
      mounted = false;
      clearInterval(int);
    };
  }, [intervalMs]);

  return { data, error };
}

export function useQueueDepth(intervalMs = 5000) {
  const [history, setHistory] = useState<number[]>([]);
  const [current, setCurrent] = useState<number>(0);

  useEffect(() => {
    let mounted = true;
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
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
  const [data, setData] = useState<FindingApproval[]>([]);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchApprovals = async () => {
      try {
        const res = await fetch(`${API_BASE}/findings/pending`);
        if (!res.ok) throw new Error('Failed to fetch pending approvals');
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

    fetchApprovals();
    const int = setInterval(fetchApprovals, intervalMs);
    return () => {
      mounted = false;
      clearInterval(int);
    };
  }, [intervalMs]);

  return { data, error };
}
