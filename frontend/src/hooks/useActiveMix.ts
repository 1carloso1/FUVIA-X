import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ConcreteInputData, PredictionResponse } from '../types/concreteTypes';
import type { ActiveMixPayload, AgentMix } from '../services/agentService';

export type MixOrigin = 'form' | 'copilot';

export interface ActiveMix {
  id:     string;
  origin: MixOrigin;
  label:  string;                 // "Formulario" | "#N"
  inputs: ConcreteInputData;
  result: PredictionResponse;
}

const MAX_COPILOT_MIXES = 5;
const NOTICE_MS = 7000;

export function toActiveMixPayload(mix: ActiveMix | null): ActiveMixPayload | undefined {
  if (!mix) return undefined;
  return {
    id: mix.id,
    origin: mix.origin,
    inputs: mix.inputs,
    result: {
      resistencia_estimada:  mix.result.resistencia_estimada,
      relacion_agua_cemento: mix.result.relacion_agua_cemento,
      relacion_grava_arena:  mix.result.relacion_grava_arena,
      clase_resistencia:     mix.result.clase_resistencia,
    },
  };
}

export function useActiveMix(
  formInputs: ConcreteInputData | null,
  formResult: PredictionResponse | null,
) {
  const [copilotMixes, setCopilotMixes] = useState<ActiveMix[]>([]);
  const [selectedId,   setSelectedId]   = useState<string | null>(null);
  const [notice,       setNotice]       = useState<string | null>(null);
  const counter    = useRef(0);
  const noticeTimer = useRef<number | undefined>(undefined);

  const formMix = useMemo<ActiveMix | null>(
    () => (formInputs && formResult
      ? { id: 'form', origin: 'form', label: 'Formulario', inputs: formInputs, result: formResult }
      : null),
    [formInputs, formResult],
  );

  const mixes = useMemo(
    () => (formMix ? [formMix, ...copilotMixes] : copilotMixes),
    [formMix, copilotMixes],
  );

  // La última escritura gana: un resultado nuevo del formulario pasa a ser la mezcla mostrada
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (formResult) setSelectedId('form');
  }, [formResult]);

  useEffect(() => () => window.clearTimeout(noticeTimer.current), []);

  const active = mixes.find(m => m.id === selectedId) ?? mixes[mixes.length - 1] ?? null;

  const addCopilotMixes = useCallback((items: AgentMix[]) => {
    if (!items.length) return;
    const created: ActiveMix[] = items.map(it => {
      counter.current += 1;
      return {
        id: `copilot-${counter.current}`,
        origin: 'copilot',
        label: `#${counter.current}`,
        inputs: it.inputs,
        result: it.result,
      };
    });
    setCopilotMixes(prev => [...prev, ...created].slice(-MAX_COPILOT_MIXES));
    setSelectedId(created[created.length - 1].id);
    setNotice('El panel se actualizó con la mezcla del copiloto');
    window.clearTimeout(noticeTimer.current);
    noticeTimer.current = window.setTimeout(() => setNotice(null), NOTICE_MS);
  }, []);

  const selectMix     = useCallback((id: string) => setSelectedId(id), []);
  const dismissNotice = useCallback(() => setNotice(null), []);

  return { mixes, active, selectMix, addCopilotMixes, notice, dismissNotice };
}