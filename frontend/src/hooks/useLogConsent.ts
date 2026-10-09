import { useCallback, useState } from 'react';

export type ConsentState = 'unset' | 'granted' | 'denied';

// La versión va en la clave: si cambia el texto del aviso, se vuelve a preguntar.
const KEY = 'fuvia_log_consent_v1';

function readStored(): ConsentState {
  try {
    const v = window.localStorage.getItem(KEY);
    return v === 'granted' || v === 'denied' ? v : 'unset';
  } catch {
    return 'unset';
  }
}

export function useLogConsent() {
  const [consent, setConsent] = useState<ConsentState>(readStored);

  const persist = useCallback((value: ConsentState) => {
    setConsent(value);
    try {
      if (value === 'unset') window.localStorage.removeItem(KEY);
      else window.localStorage.setItem(KEY, value);
    } catch {
      /* sin almacenamiento disponible: la decisión vale solo para esta sesión */
    }
  }, []);

  const grant = useCallback(() => persist('granted'), [persist]);
  const deny  = useCallback(() => persist('denied'),  [persist]);

  return { consent, grant, deny };
}