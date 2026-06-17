import { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import type { ChatEntry } from '../../hooks/useAgentChat';
import type { AgentReport } from '../../services/agentService';

// ----------------------------------------------------------------
// TIPOS
// ----------------------------------------------------------------

interface CopilotChatProps {
  messages:        ChatEntry[];
  input:           string;
  setInput:        (val: string) => void;
  isLoading:       boolean;
  lastReport:      AgentReport | null;
  bottomRef:       React.RefObject<HTMLDivElement>;
  sendUserMessage:  () => void;
  stopGeneration:   () => void;
  confirmAnalysis:  () => void;
  declineAnalysis:  () => void;
  handleKeyDown:    (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

// ----------------------------------------------------------------
// SUB-COMPONENTES
// ----------------------------------------------------------------

function ToolBadge({ tool }: { tool: string }) {
  const labels: Record<string, string> = {
    query_normative_standards:  'RAG normativo',
    fuvia_predict_mix_design:   'CatBoost',
  };
  return (
    <span className="inline-flex items-center gap-1 text-[10px] text-slate-400 bg-slate-800 border border-slate-700 rounded px-1.5 py-0.5">
      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 inline-block" />
      {labels[tool] ?? tool}
    </span>
  );
}

function ComplianceCheck({ checks }: { checks: AgentReport['normative_compliance']['checks'] }) {
  if (!checks?.length) return null;
  return (
    <div className="mt-2 space-y-1">
      {checks.map((check, i) => (
        <div
          key={i}
          className={`flex items-start gap-2 text-[11px] px-2 py-1.5 rounded ${
            check.status === 'CUMPLE'
              ? 'bg-emerald-950 text-emerald-400 border border-emerald-900'
              : 'bg-red-950 text-red-400 border border-red-900'
          }`}
        >
          <span className="mt-0.5 flex-shrink-0">
            {check.status === 'CUMPLE' ? '✓' : '⚠'}
          </span>
          <span className="ml-1">
            <strong>{check.parameter}:</strong>{' '}
            {check.status} {check.deviation ? `(${check.deviation})` : ''}
            {check.recommendation && (
              <span className="block text-[10px] opacity-75 mt-0.5">{check.recommendation}</span>
            )}
          </span>
        </div>
      ))}
    </div>
  );
}

function AssistantMessage({
  entry,
  onConfirm,
  onDecline,
}: {
  entry:     ChatEntry;
  onConfirm: () => void;
  onDecline: () => void;
}) {
  if (entry.loading) {
    return (
      <div className="flex gap-2 items-start">
        <div className="w-6 h-6 rounded-full bg-blue-900 border border-blue-700 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded-lg rounded-tl-none px-3 py-2">
          <div className="flex gap-1 items-center h-4">
            <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-2 items-start">
      <div className="w-6 h-6 rounded-full bg-blue-900 border border-blue-700 flex items-center justify-center flex-shrink-0 mt-0.5">
        <span className="w-2 h-2 rounded-full bg-blue-400" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="bg-slate-800 border border-slate-700 rounded-lg rounded-tl-none px-3 py-2 text-slate-200 text-[12px] leading-relaxed prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{entry.content}</ReactMarkdown>
        </div>
        {/* Botones de confirmación para análisis normativo */}
        {entry.isPrompt && (
          <div className="flex gap-2 mt-2">
            <button
              onClick={onConfirm}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-semibold rounded-lg transition-colors"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/>
              </svg>
              Sí, analizar
            </button>
            <button
              onClick={onDecline}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 text-[11px] font-semibold rounded-lg transition-colors"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
              </svg>
              No por ahora
            </button>
          </div>
        )}
        {/* Herramientas usadas */}
        {entry.tools && entry.tools.length > 0 && (
          <div className="flex gap-1.5 mt-1 flex-wrap">
            {entry.tools.map(t => <ToolBadge key={t} tool={t} />)}
          </div>
        )}
        {/* Checks de cumplimiento normativo */}
        {entry.report?.normative_compliance?.checks?.length ? (
          <ComplianceCheck checks={entry.report.normative_compliance.checks} />
        ) : null}
      </div>
    </div>
  );
}

function UserMessage({ content }: { content: string }) {
  return (
    <div className="flex justify-end">
      <div className="bg-blue-600 text-white rounded-lg rounded-tr-none px-3 py-2 text-[12px] leading-relaxed max-w-[85%]">
        {content}
      </div>
    </div>
  );
}

// ----------------------------------------------------------------
// COMPONENTE PRINCIPAL
// ----------------------------------------------------------------

export default function CopilotChat({
  messages,
  input,
  setInput,
  isLoading,
  bottomRef,
  sendUserMessage,
  stopGeneration,
  confirmAnalysis,
  declineAnalysis,
  handleKeyDown,
}: CopilotChatProps) {
  return (
    <div className="flex flex-col h-full bg-slate-900 rounded-xl border border-slate-700 overflow-hidden">

      {/* HEADER */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700 bg-slate-900 flex-shrink-0">
        <span className="w-2 h-2 rounded-full bg-blue-400" />
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">
          Copiloto FUVIA X
        </span>
        <span className="ml-auto text-[10px] text-slate-500 bg-slate-800 border border-slate-700 rounded px-2 py-0.5">
          ACI 318 · ACI 211 · ASTM
        </span>
      </div>

      {/* MENSAJES */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3 min-h-0">
        {messages.map((msg, i) =>
          msg.role === 'assistant'
            ? <AssistantMessage key={i} entry={msg} onConfirm={confirmAnalysis} onDecline={declineAnalysis} />
            : <UserMessage      key={i} content={msg.content} />
        )}
        <div ref={bottomRef} />
      </div>

      {/* INPUT */}
      <div className="flex gap-2 px-3 py-3 border-t border-slate-700 bg-slate-900 flex-shrink-0">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Pregunta sobre tu mezcla o normativa ACI/ASTM..."
          className="flex-1 bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 rounded-lg px-3 py-2 text-[12px] focus:outline-none focus:border-blue-500 disabled:opacity-50 transition-colors"
        />
        {isLoading ? (
          <button
            onClick={stopGeneration}
            className="bg-red-600 hover:bg-red-500 text-white rounded-lg px-3 py-2 transition-colors flex-shrink-0"
            aria-label="Detener generación"
            title="Detener"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="1"/>
            </svg>
          </button>
        ) : (
          <button
            onClick={sendUserMessage}
            disabled={!input.trim()}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg px-3 py-2 transition-colors flex-shrink-0"
            aria-label="Enviar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        )}
      </div>

    </div>
  );
}