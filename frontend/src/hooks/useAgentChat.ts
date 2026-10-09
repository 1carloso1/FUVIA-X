import { useState, useEffect, useRef } from 'react';
import { sendMessage } from '../services/agentService';
import type { ChatMessage, AgentReport, AgentMix, ChatResponse } from '../services/agentService';
import { toActiveMixPayload } from './useActiveMix';
import type { ActiveMix } from './useActiveMix';
import type { PredictionResponse, ConcreteInputData } from '../types/concreteTypes';

// ----------------------------------------------------------------
// TIPOS
// ----------------------------------------------------------------

export interface ChatEntry {
  role:      'user' | 'assistant';
  content:   string;
  report?:   AgentReport | null;
  tools?:    string[];
  loading?:  boolean;
  isPrompt?: boolean;
  chosenOption?: 'confirmed' | 'declined';
}

// ----------------------------------------------------------------
// HOOK
// ----------------------------------------------------------------

export function useAgentChat(
  resultado: PredictionResponse | null,
  form:      ConcreteInputData | null,
  activeMix: ActiveMix | null = null,                    
  onMixes?:  (mixes: AgentMix[]) => void                 
) {
  const [messages,   setMessages]   = useState<ChatEntry[]>([]);
  const [input,      setInput]      = useState('');
  const [isLoading,  setIsLoading]  = useState(false);
  const [lastReport, setLastReport] = useState<AgentReport | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);
  const abortRef  = useRef<AbortController | null>(null);

  const applyMixes = (r: ChatResponse) => {
    if (r.mixes?.length && onMixes) onMixes(r.mixes);
  };

  // ----------------------------------------------------------------
  // STOP
  // ----------------------------------------------------------------

  const stopGeneration = () => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setIsLoading(false);
    setMessages(prev => [
      ...prev.filter(m => !m.loading),
      { role: 'assistant', content: '_Generación cancelada._' }
    ]);
  };

  // ----------------------------------------------------------------
  // BIENVENIDA
  // ----------------------------------------------------------------

  useEffect(() => {
    setMessages([{
      role:    'assistant',
      content: 'Hola, soy tu **Copiloto FUVIA X**. Calcula una mezcla y te daré un análisis normativo inmediato basado en ACI/ASTM.\n\nTambién puedes preguntarme sobre requisitos de durabilidad, exposición ambiental o especificaciones de materiales.',
    }]);
  }, []);

  // ----------------------------------------------------------------
  // TRIGGER al recibir resultado — pregunta si desea análisis
  // ----------------------------------------------------------------

  const pendingAnalysisRef = useRef<string | null>(null);

  useEffect(() => {
    if (!resultado || !form) return;

    const wcm   = resultado.relacion_agua_cemento;
    const fc    = resultado.resistencia_estimada;
    const clase = resultado.clase_resistencia;

    // Construir sección SHAP si está disponible
    const shapSection = resultado.shap_contributions?.length
      ? (
          `\nCONTRIBUCIONES SHAP (top 4 — influencia de cada insumo en MPa):\n` +
          resultado.shap_contributions.slice(0, 4).map(c =>
            `- ${c.feature}: ${c.value >= 0 ? '+' : ''}${c.value.toFixed(3)} MPa`
          ).join('\n') +
          `\nValor base del modelo: ${resultado.shap_base_value?.toFixed(2)} MPa` +
          `\n(Estos valores indican cuánto suma o resta cada insumo al valor base para llegar a f'c = ${fc} MPa)`
        )
      : '';

    pendingAnalysisRef.current = (
      `Se acaba de calcular una mezcla con los siguientes datos:\n` +
      `- Cemento: ${Number(form.cement)} kg/m³\n` +
      `- Escoria: ${Number(form.slag)} kg/m³\n` +
      `- Ceniza volante: ${Number(form.flyash)} kg/m³\n` +
      `- Superplastificante: ${Number(form.superplasticizer)} kg/m³\n` +
      `- Agua: ${Number(form.water)} kg/m³\n` +
      `- Agregado grueso: ${Number(form.coarseaggregate)} kg/m³\n` +
      `- Agregado fino: ${Number(form.fineaggregate)} kg/m³\n` +
      `- Edad de curado: ${Number(form.age)} días\n\n` +
      `Resultado del modelo CatBoost:\n` +
      `- f'c estimado: ${fc} MPa\n` +
      `- Relación w/cm: ${wcm}\n` +
      `- Clase de resistencia: ${clase}\n` +
      shapSection +
      `\n\nAnaliza estos resultados y dime si la mezcla presenta alguna observación normativa importante. ` +
      `Si detectas algún potencial incumplimiento con ACI/ASTM, menciónalo directamente. ` +
      `IMPORTANTE: Los valores SHAP anteriores son solo contexto de referencia. NO los menciones ni los interpretes en tu análisis inicial — solo úsalos si el usuario pregunta explícitamente sobre SHAP o sobre la contribución de cada insumo.`
    );

    setMessages(prev => [
      ...prev,
      {
        role:    'assistant',
        content: `✅ **Mezcla calculada** — f'c **${fc} MPa** · w/cm **${wcm}** · ${clase}\n\n¿Deseas que analice normativamente esta mezcla con ACI/ASTM?`,
        isPrompt: true,
        chosenOption: undefined,
      } as ChatEntry,
    ]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resultado]);

  // ----------------------------------------------------------------
  // CONFIRMAR análisis normativo
  // ----------------------------------------------------------------

  const confirmAnalysis = () => {
    const pendingMessage = pendingAnalysisRef.current;
    if (!pendingMessage || isLoading) return;

    pendingAnalysisRef.current = null;

    setMessages(prev => [
      ...prev.map(m =>
        (m as ChatEntry & { isPrompt?: boolean }).isPrompt
          ? { ...m, isPrompt: false, chosenOption: 'confirmed' as const }
          : m
      ),
      { role: 'assistant', content: '', loading: true }
    ]);
    setIsLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    sendMessage(pendingMessage, [], controller.signal, toActiveMixPayload(activeMix))  
      .then(response => {
        if (controller.signal.aborted) return;
        applyMixes(response);                                                          
        setMessages(prev => [
          ...prev.filter(m => !m.loading),
          {
            role:    'assistant',
            content: response.response,
            report:  response.report,
            tools:   response.tools_called,
          }
        ]);
        if (response.report) setLastReport(response.report);
      })
      .catch(err => {
        if (err?.name === 'AbortError') return;
        setMessages(prev => [
          ...prev.filter(m => !m.loading),
          { role: 'assistant', content: 'No pude analizar la mezcla en este momento. Puedes preguntarme directamente sobre los resultados.' }
        ]);
      })
      .finally(() => {
        abortRef.current = null;
        setIsLoading(false);
      });
  };

  // ----------------------------------------------------------------
  // RECHAZAR análisis normativo
  // ----------------------------------------------------------------

  const declineAnalysis = () => {
    pendingAnalysisRef.current = null;
    setMessages(prev => [
      ...prev.map(m =>
        (m as ChatEntry & { isPrompt?: boolean }).isPrompt
          ? { ...m, isPrompt: false, chosenOption: 'declined' as const }
          : m
      ),
      {
        role:    'assistant',
        content: 'Entendido. Si necesitas el análisis normativo en cualquier momento, solo pídelo.',
      }
    ]);
  };

  // ----------------------------------------------------------------
  // SCROLL AUTOMÁTICO
  // ----------------------------------------------------------------

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ----------------------------------------------------------------
  // ENVIAR MENSAJE DEL USUARIO
  // ----------------------------------------------------------------

  const sendUserMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const history: ChatMessage[] = messages
      .filter(m => !m.loading && m.content)
      .map(m => ({ role: m.role, content: m.content }));

    setMessages(prev => [...prev,
      { role: 'user', content: trimmed },
      { role: 'assistant', content: '', loading: true }
    ]);
    setInput('');
    setIsLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await sendMessage(trimmed, history, controller.signal, toActiveMixPayload(activeMix));   // CAMBIO
      if (controller.signal.aborted) return;
      applyMixes(response);  
      setMessages(prev => [
        ...prev.filter(m => !m.loading),
        {
          role:    'assistant',
          content: response.response,
          report:  response.report,
          tools:   response.tools_called,
        }
      ]);
      if (response.report) setLastReport(response.report);
    } catch (err: unknown) {
      if ((err as { name?: string })?.name === 'AbortError') return;
      setMessages(prev => [
        ...prev.filter(m => !m.loading),
        { role: 'assistant', content: 'Hubo un error al conectar con el agente. Intenta de nuevo.' }
      ]);
    } finally {
      abortRef.current = null;
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendUserMessage();
    }
  };

  return {
    messages,
    input,
    setInput,
    isLoading,
    lastReport,
    bottomRef,
    sendUserMessage,
    stopGeneration,
    confirmAnalysis,
    declineAnalysis,
    handleKeyDown,
  };
}