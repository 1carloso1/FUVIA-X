import { useState, useEffect } from 'react';

const BACKEND_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  .replace(/\/+$/, '').replace(/\/api\/predecir$/, '');

const AGENT_URL = (import.meta.env.VITE_AGENT_URL || 'http://localhost:8001')
  .replace(/\/+$/, '').replace(/\/api\/chat$/, '');

// Configuración de reintentos
const MAX_RETRIES    = 20;    // 20 intentos
const RETRY_INTERVAL = 3000;  // 3s entre reintentos  
const PING_TIMEOUT   = 5000;  // 5s por intento

export type ServerStatus = 'warming' | 'ready' | 'error';

export interface WarmupState {
  backend:       ServerStatus;
  agent:         ServerStatus;
  ready:         boolean;
  elapsed:       number;
  backendRetry:  number;
  agentRetry:    number;
}

async function pingOnce(url: string): Promise<boolean> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), PING_TIMEOUT);
  try {
    const response = await fetch(`${url}/api/health`, {
      signal: controller.signal,
      cache:  'no-store',
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

async function pingWithRetry(
  url:        string,
  maxRetries: number,
  onRetry:    (attempt: number) => void,
  signal:     AbortSignal
): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    if (signal.aborted) return false;

    const ok = await pingOnce(url);
    if (ok) return true;

    onRetry(i + 1);

    // Esperar antes del siguiente intento (excepto en el último)
    if (i < maxRetries - 1) {
      await new Promise<void>(resolve => {
        const t = setTimeout(resolve, RETRY_INTERVAL);
        signal.addEventListener('abort', () => { clearTimeout(t); resolve(); });
      });
    }
  }
  return false;
}

export function useSystemWarmup() {
  const [state, setState] = useState<WarmupState>({
    backend:      'warming',
    agent:        'warming',
    ready:        false,
    elapsed:      0,
    backendRetry: 0,
    agentRetry:   0,
  });

  useEffect(() => {
  const controller = new AbortController();
  let seconds      = 0;

  const ticker = setInterval(() => {
    seconds += 1;
    setState(prev => ({ ...prev, elapsed: seconds }));
  }, 1000);

  // Delay de 2s antes del primer ping — da tiempo a uvicorn de estar escuchando
  const start = setTimeout(() => {
    pingWithRetry(
      BACKEND_URL, MAX_RETRIES,
      attempt => setState(prev => ({ ...prev, backendRetry: attempt })),
      controller.signal
    ).then(ok => {
      if (controller.signal.aborted) return;
      setState(prev => {
        const next = { ...prev, backend: (ok ? 'ready' : 'error') as ServerStatus };
        next.ready = next.backend === 'ready' && next.agent === 'ready';
        return next;
      });
    });

    pingWithRetry(
      AGENT_URL, MAX_RETRIES,
      attempt => setState(prev => ({ ...prev, agentRetry: attempt })),
      controller.signal
    ).then(ok => {
      if (controller.signal.aborted) return;
      setState(prev => {
        const next = { ...prev, agent: (ok ? 'ready' : 'error') as ServerStatus };
        next.ready = next.backend === 'ready' && next.agent === 'ready';
        return next;
      });
    });
  }, 2000); // 2 segundos de delay inicial

  return () => {
    controller.abort();
    clearInterval(ticker);
    clearTimeout(start);
  };
}, []);

  return state;
}