import { useState, useEffect, useRef } from 'react';
import { sendMessage } from '../services/agentService';
import type { ChatMessage, AgentReport } from '../services/agentService';
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
  isPrompt?: boolean;  // true cuando espera confirmación del usuario
}

// ----------------------------------------------------------------
// HOOK
// ----------------------------------------------------------------

export function useAgentChat(
  resultado: PredictionResponse | null,
  form:      ConcreteInputData | null
) {
  const [messages,   setMessages]   = useState<ChatEntry[]>([]);
  const [input,      setInput]      = useState('');
  const [isLoading,  setIsLoading]  = useState(false);
  const [lastReport, setLastReport] = useState<AgentReport | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);
  const abortRef  = useRef<AbortController | null>(null);

  // ----------------------------------------------------------------
  // STOP — cancela la generación en curso
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

  // Guardamos los datos de la mezcla para usarlos si el usuario confirma
  const pendingAnalysisRef = useRef<string | null>(null);

  useEffect(() => {
    if (!resultado || !form) return;

    const wcm   = resultado.relacion_agua_cemento;
    const fc    = resultado.resistencia_estimada;
    const clase = resultado.clase_resistencia;

    // Guardamos el mensaje completo para enviarlo si el usuario confirma
    pendingAnalysisRef.current = (
      `Se acaba de calcular una mezcla con los siguientes datos:\n` +
      `- Cemento: ${Number(form.cement)} kg/m³\n` +
      `- Agua: ${Number(form.water)} kg/m³\n` +
      `- Agregado grueso: ${Number(form.coarseaggregate)} kg/m³\n` +
      `- Agregado fino: ${Number(form.fineaggregate)} kg/m³\n` +
      `- Edad de curado: ${Number(form.age)} días\n\n` +
      `Resultado del modelo CatBoost:\n` +
      `- f'c estimado: ${fc} MPa\n` +
      `- Relación w/cm: ${wcm}\n` +
      `- Clase de resistencia: ${clase}\n\n` +
      `Analiza estos resultados y dime si la mezcla presenta alguna observación normativa importante. ` +
      `Si detectas algún potencial incumplimiento con ACI/ASTM, menciónalo directamente.`
    );

    // Solo mostrar pregunta — sin llamar al agente aún
    setMessages(prev => [
      ...prev,
      {
        role:    'assistant',
        content: `✅ **Mezcla calculada** — f'c **${fc} MPa** · w/cm **${wcm}** · ${clase}\n\n¿Deseas que analice normativamente esta mezcla con ACI/ASTM?`,
        isPrompt: true,  // marca especial para mostrar botones de confirmación
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

    // Reemplazar el mensaje de pregunta por el de carga
    setMessages(prev => [
      ...prev.filter(m => !(m as ChatEntry & { isPrompt?: boolean }).isPrompt),
      { role: 'assistant', content: '', loading: true }
    ]);
    setIsLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    sendMessage(pendingMessage, [], controller.signal)
      .then(response => {
        if (controller.signal.aborted) return;
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
      ...prev.filter(m => !(m as ChatEntry & { isPrompt?: boolean }).isPrompt),
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

    setMessages(prev => [...prev, { role: 'user', content: trimmed }, { role: 'assistant', content: '', loading: true }]);
    setInput('');
    setIsLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await sendMessage(trimmed, history, controller.signal);
      if (controller.signal.aborted) return;
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