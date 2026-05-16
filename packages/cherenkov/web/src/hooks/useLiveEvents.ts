import { useState, useEffect } from 'react';

let wsInstance: WebSocket | null = null;
let eventListeners = new Set<(event: any) => void>();
let statusListeners = new Set<(connected: boolean) => void>();
let reconnectTimeout: any;
let isConnected = false;

function getWsUrl(): string {
  // In development (Vite on :3000), connect directly to the backend on :8000.
  // In production (served by FastAPI on :8000), use same-origin WebSocket.
  const loc = window.location;
  if (loc.port === '3000') {
    return `ws://${loc.hostname}:8000/ws/live`;
  }
  const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${loc.host}/ws/live`;
}

function connectWs() {
  if (wsInstance) return;
  wsInstance = new WebSocket(getWsUrl());
  
  wsInstance.onopen = () => {
    isConnected = true;
    statusListeners.forEach(listener => listener(true));
  };
  wsInstance.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      eventListeners.forEach(listener => listener(data));
    } catch (e) {
      console.error('Failed to parse WS message', e);
    }
  };
  wsInstance.onclose = () => {
    isConnected = false;
    wsInstance = null;
    statusListeners.forEach(listener => listener(false));
    clearTimeout(reconnectTimeout);
    reconnectTimeout = setTimeout(connectWs, 3000);
  };
  wsInstance.onerror = () => {
    if (wsInstance) wsInstance.close();
  };
}

export function useLiveEvents() {
  const [lastEvent, setLastEvent] = useState<any>(null);
  const [connected, setConnected] = useState(isConnected);

  useEffect(() => {
    if (!wsInstance) {
      connectWs();
    }
    
    const onEvent = (data: any) => setLastEvent(data);
    const onStatus = (status: boolean) => setConnected(status);

    eventListeners.add(onEvent);
    statusListeners.add(onStatus);
    
    setConnected(isConnected);

    return () => {
      eventListeners.delete(onEvent);
      statusListeners.delete(onStatus);
    };
  }, []);

  return { lastEvent, connected };
}
