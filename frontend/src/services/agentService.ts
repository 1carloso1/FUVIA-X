// Mismo patrón que predictionService.ts
import type { ConcreteInputData, PredictionResponse } from '../types/concreteTypes';
const AGENT_URL = import.meta.env.VITE_AGENT_URL || "http://localhost:8001";
const baseUrl = AGENT_URL.replace(/\/+$/, "").replace(/\/api\/chat$/, "");

// ----------------------------------------------------------------
// TIPOS
// ----------------------------------------------------------------

export interface ActiveMixPayload {
  id:     string;
  origin: 'form' | 'copilot';
  inputs: ConcreteInputData;
  result: {
    resistencia_estimada:  number;
    relacion_agua_cemento: number;
    relacion_grava_arena:  number;
    clase_resistencia:     string;
  };
}

export interface AgentMix { inputs: ConcreteInputData; result: PredictionResponse; }

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface NormativeRequirement {
  parameter:  string;
  value:      string;
  standard:   string;
  condition:  string;
}

export interface ComplianceCheck {
  parameter:       string;
  predicted_value?: number | string;
  normative_limit?: number | string;
  status:          string;
  deviation?:      string;
  margin?:         string;
  recommendation?: string;
}

export interface MixDesign {
  cement_content:    number | null;
  slag:              number | null;
  flyash:            number | null;
  water:             number | null;
  superplasticizer:  number | null;
  coarse_aggregate:  number | null;
  fine_aggregate:    number | null;
  age_days:          number | null;
  w_cm_ratio:        number | null;
  gravel_sand_ratio: number | null;
  predicted_fc_mpa:  number | null;
  strength_class:    string | null;
  recommendations:   string[];
  model:             string;
}

export interface AgentReport {
  report_type:             "normative_query" | "mix_design" | "complete_design";
  summary:                 string;
  normative_requirements:  NormativeRequirement[];
  mix_design:              MixDesign;
  normative_compliance: {
    compliant: boolean | null;
    checks:    ComplianceCheck[];
  };
  limitations:      string[];
  sources_consulted: string[];
}

export interface ChatResponse {
  response:     string;
  report:       AgentReport | null;
  tools_called: string[];
  mixes?: AgentMix[] | null;
  turn_id?: string | null;
}

export type FeedbackFlag = 'useful' | 'doubtful';

export interface LoggingOptions {
  sessionId:  string;
  logConsent: boolean;
  turn:       number;
}

// ----------------------------------------------------------------
// FUNCIÓN PRINCIPAL
// ----------------------------------------------------------------

export const sendMessage = async (
  message: string,
  history: ChatMessage[],
  signal?: AbortSignal,
  activeMix?: ActiveMixPayload,
  logging?: LoggingOptions,
): Promise<ChatResponse> => {

  const response = await fetch(`${baseUrl}/api/chat`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({
      message,
      history,
      active_mix:  activeMix ?? null,
      session_id:  logging?.sessionId ?? null,
      log_consent: logging?.logConsent ?? false,
      turn:        logging?.turn ?? null,
    }),
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    if (errorData) throw errorData;
    throw new Error("Error al conectar con el agente FUVIA");
  }

  return await response.json();
};

export const postFeedback = async (
  sessionId: string,
  turnId: string,
  flag: FeedbackFlag,
): Promise<boolean> => {
  try {
    const response = await fetch(`${baseUrl}/api/feedback`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ session_id: sessionId, turn_id: turnId, flag }),
    });
    if (!response.ok) return false;
    const data = await response.json();
    return data.stored === true;
  } catch {
    return false;
  }
};