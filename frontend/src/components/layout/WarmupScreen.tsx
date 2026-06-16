import type { WarmupState } from '../../hooks/useSystemWarmup';

interface WarmupScreenProps {
  state: WarmupState;
}

function ServerRow({
  label, status, retry,
}: {
  label:  string;
  status: 'warming' | 'ready' | 'error';
  retry:  number;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0">
      <span className="text-[12px] text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        {status === 'warming' && (
          <>
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-[11px] text-amber-400">
              {retry > 0 ? `Reintentando (${retry})...` : 'Iniciando...'}
            </span>
          </>
        )}
        {status === 'ready' && (
          <>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span className="text-[11px] text-emerald-400">Listo</span>
          </>
        )}
        {status === 'error' && (
          <>
            <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
            <span className="text-[11px] text-red-400">Sin conexión</span>
          </>
        )}
      </div>
    </div>
  );
}

export default function WarmupScreen({ state }: WarmupScreenProps) {
  const hasError = state.backend === 'error' || state.agent === 'error';

  return (
    <div className="min-h-screen w-full bg-slate-950 flex flex-col items-center justify-center px-4">

      {/* Línea de acento superior */}
      <div className="fixed top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-60" />

      {/* Logo */}
      <div className="mb-10 text-center">
        <h1 className="text-3xl font-black tracking-[0.3em] text-slate-100 uppercase">
          FUVIA<span className="text-blue-400 ml-2">X</span>
        </h1>
        <p className="text-[11px] text-slate-500 tracking-[0.15em] uppercase mt-1">
          Plataforma de Inteligencia para Concreto
        </p>
      </div>

      {/* Card de estado */}
      <div className="w-full max-w-sm bg-slate-900 border border-slate-700 rounded-xl overflow-hidden">

        <div className="px-5 py-4 border-b border-slate-800">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">
            Estado del sistema
          </p>
        </div>

        <div className="px-5 py-2">
          <ServerRow label="Motor de predicción (CatBoost)" status={state.backend} retry={state.backendRetry} />
          <ServerRow label="Agente normativo (ACI/ASTM)"   status={state.agent}   retry={state.agentRetry} />
        </div>

        <div className="px-5 py-4 border-t border-slate-800">
          {!hasError ? (
            <div className="flex items-center gap-3">
              {/* Spinner */}
              <svg
                className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0"
                fill="none" viewBox="0 0 24 24"
              >
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <p className="text-[11px] text-slate-500">
                {state.elapsed < 5
                  ? 'Conectando con los servidores...'
                  : `Despertando servidores... ${state.elapsed}s`
                }
              </p>
            </div>
          ) : (
            <div className="text-center">
              <p className="text-[11px] text-red-400 mb-2">
                No se pudo conectar con uno o más servidores.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="text-[11px] text-blue-400 hover:text-blue-300 underline transition-colors"
              >
                Reintentar
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Nota discreta */}
      {!hasError && state.elapsed > 10 && (
        <p className="mt-6 text-[10px] text-slate-600 text-center max-w-xs">
          Los servidores se activan automáticamente. Esto solo ocurre en el primer acceso del día.
        </p>
      )}

    </div>
  );
}