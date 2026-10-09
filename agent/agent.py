"""
agent/agent.py
==============
Agente LangGraph — Phase 2, Semana 2.
RAG + FUVIA como herramientas activas.

ARQUITECTURA:
    START → [Clasificador] → [RAG Tool?] → [Sintetizador] → END

    - Clasificador: decide si la pregunta necesita consultar el RAG
    - RAG Tool: consulta ChromaDB y retorna respuesta normativa
    - Sintetizador: genera JSON estructurado para el frontend React

MEMORIA:
    El historial completo de la conversación se pasa en cada llamada.
    LangGraph maneja el estado del grafo entre turnos.

USO:
    python agent/agent.py
"""

import os
import re
import json
import logging
import operator 
from typing import Annotated
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from tools.rag_tool import query_normative_standards, initialize_rag
from tools.fuvia_tool import fuvia_predict_mix_design
from prompts import AGENT_SYSTEM_PROMPT, REPORT_SYNTHESIS_PROMPT, MODEL_ID

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
# ESTADO DEL AGENTE
# ----------------------------------------------------------------

class AgentState(TypedDict):
    """
    Estado del grafo LangGraph.
    messages:           historial completo de la conversación (acumulativo)
    normative_response: una entrada por llamada al RAG en este turno
    fuvia_response:     una entrada por llamada a FUVIA en este turno
    final_report:       JSON estructurado para el frontend React
    tool_runs:          un artifact por llamada a herramienta
    """
    messages:           Annotated[list, add_messages]
    normative_response: Annotated[list, operator.add]   # CAMBIO: antes str
    fuvia_response:     Annotated[list, operator.add]   # CAMBIO: antes str
    final_report:       dict
    tool_runs:          Annotated[list, operator.add]
    active_mix: str


# ----------------------------------------------------------------
# INICIALIZACIÓN DEL LLM Y HERRAMIENTAS
# ----------------------------------------------------------------

REPORT_MAX_TOKENS = 1500   # presupuesto de la llamada que genera el reporte JSON (D5)


def build_llm(max_tokens: int = 800) -> ChatAnthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no encontrada en .env")
    return ChatAnthropic(
        model=MODEL_ID,
        api_key=api_key,
        max_tokens=max_tokens          # CAMBIO: parámetro; el valor por defecto sigue siendo 800
    )


TOOLS = [query_normative_standards, fuvia_predict_mix_design]

def _join_calls(items: list, label: str) -> str:
    """Una sola llamada: el texto tal cual. Varias: bloques '[Mix 1]', '[Mix 2]'..."""
    if len(items) <= 1:
        return items[0] if items else ""
    return "\n\n".join(f"[{label} {i}]\n{t}" for i, t in enumerate(items, 1))


def _fc_injection(tool_runs: list) -> str:
    """Restricción de f'c exacto, una entrada por mezcla calculada en este turno."""
    runs = [r for r in tool_runs
            if r.get("tool") == "fuvia_predict_mix_design"
            and isinstance(r.get("response"), dict)
            and r["response"].get("resistencia_estimada") is not None]
    if not runs:
        return ""
    if len(runs) == 1:      # mismo texto que la versión anterior
        fc_exact = runs[0]["response"]["resistencia_estimada"]
        return (
            f"\n\nCRITICAL: The FUVIA model predicted exactly {fc_exact} MPa. "
            f"You MUST use this exact value when mentioning f'c in your response. "
            f"Do not round, recalculate, or use any other value."
        )
    lines = []
    for i, r in enumerate(runs, 1):
        a, resp = r.get("args", {}), r["response"]
        lines.append(
            f"- Mix {i} (cement={a.get('cement')}, water={a.get('water')}, "
            f"age={a.get('age')} d, w/cm={resp.get('relacion_agua_cemento')}): "
            f"{resp['resistencia_estimada']} MPa"
        )
    return (
        "\n\nCRITICAL: The FUVIA model predicted exactly these values, one per mix:\n"
        + "\n".join(lines)
        + "\nYou MUST use these exact values when mentioning f'c, each with its own mix. "
          "Do not round, recalculate, or swap values between mixes."
    )

def _active_mix_block(state: AgentState) -> str:
    """Bloque ACTIVE MIX para el system prompt (vacío si el frontend no envió active_mix)."""
    txt = (state.get("active_mix") or "").strip()
    if not txt:
        return ""
    return ("\n\nACTIVE MIX (the mix currently shown in the user's results panel; "
            "reference for \"my mix\"):\n" + txt)

# ----------------------------------------------------------------
# NODOS DEL GRAFO
# ----------------------------------------------------------------

def node_classifier(state: AgentState) -> AgentState:
    """
    Nodo 1 — Clasificador.

    Analiza el último mensaje del usuario y decide si necesita
    consultar el RAG normativo. Si lo necesita, llama la herramienta.
    Si no (saludos, preguntas fuera de scope), responde directamente.

    LangGraph maneja el tool calling automáticamente cuando el LLM
    retorna un tool_use block.
    """
    llm = build_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT + _active_mix_block(state))] + state["messages"]

    logger.info("Clasificador analizando la consulta...")
    response = llm_with_tools.invoke(messages)

    # Fix: si el LLM no llamó herramientas y el content está vacío,
    # forzar una respuesta conversacional directa sin tools
    has_tool_calls = hasattr(response, "tool_calls") and response.tool_calls
    has_content    = bool(response.content and str(response.content).strip())

    if not has_tool_calls and not has_content:
        logger.info("Respuesta vacía detectada — generando respuesta directa...")
        # Segunda llamada sin tools para forzar respuesta conversacional
        direct_response = llm.invoke(messages)
        return {"messages": [direct_response]}

    return {"messages": [response]}


def node_rag_tool(state: AgentState) -> AgentState:
    """
    Nodo 2 — Ejecutor de herramientas.

    Ejecuta las herramientas que el clasificador decidió llamar. Devuelve solo
    las entradas NUEVAS de esta ejecución: el reducer del estado las acumula.
    """
    last_message       = state["messages"][-1]
    tool_results       = []
    tool_runs          = []
    normative_response = []       # CAMBIO: una entrada por llamada
    fuvia_response     = []       # CAMBIO

    for tool_call in last_message.tool_calls:
        logger.info(f"Ejecutando herramienta: {tool_call['name']}")
        full_call = {**tool_call, "type": "tool_call"}

        if tool_call["name"] == "query_normative_standards":
            tm     = query_normative_standards.invoke(full_call)
            result = tm.content
            normative_response.append(result)                 # CAMBIO
            if tm.artifact:
                tool_runs.append(tm.artifact)
            tool_results.append(
                ToolMessage(content=result, tool_call_id=tool_call["id"])
            )

        elif tool_call["name"] == "fuvia_predict_mix_design":
            logger.info("Llamando endpoint FUVIA en Render...")
            tm     = fuvia_predict_mix_design.invoke(full_call)
            result = tm.content
            fuvia_response.append(result)                     # CAMBIO
            if tm.artifact:
                tool_runs.append(tm.artifact)
            tool_results.append(
                ToolMessage(content=result, tool_call_id=tool_call["id"])
            )

    return {
        "messages":           tool_results,
        "normative_response": normative_response,
        "fuvia_response":     fuvia_response,
        "tool_runs":          tool_runs,
    }


def node_synthesizer(state: AgentState) -> AgentState:
    """
    Nodo 3 — Sintetizador.

    Genera la respuesta final en dos formatos:
    1. Mensaje conversacional para el historial (en el idioma del usuario)
    2. JSON estructurado para el frontend React (solo si hubo herramientas)

    Si el clasificador ya respondió directamente (sin tool calls), reutiliza
    ese contenido sin llamar al LLM de nuevo.
    """
    llm = build_llm()

    last_msg           = state["messages"][-1]
    has_direct_content = (
        isinstance(last_msg, AIMessage)
        and bool(last_msg.content and str(last_msg.content).strip())
        and not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls)
    )

    if has_direct_content and not state.get("normative_response") and not state.get("fuvia_response"):
        logger.info("Respuesta directa del clasificador — sin re-invocar LLM")
        return {
            "messages":     [last_msg],
            "final_report": {}
        }

    # f'c exacto de CADA mezcla calculada en este turno (tomado de los artifacts)
    system_with_fc = AGENT_SYSTEM_PROMPT + _active_mix_block(state) + _fc_injection(state.get("tool_runs", []))
    messages       = [SystemMessage(content=system_with_fc)] + state["messages"]
    final_message  = llm.invoke(messages)

    final_report = {}
    if state.get("normative_response") or state.get("fuvia_response"):
        last_user_msg = next(
            (m.content for m in reversed(state["messages"])
             if isinstance(m, HumanMessage)),
            ""
        )

        synthesis_prompt = REPORT_SYNTHESIS_PROMPT.format(
            query=last_user_msg,
            normative_response=_join_calls(state.get("normative_response", []), "Query"),
            fuvia_response=_join_calls(state.get("fuvia_response", []), "Mix"),
        )

        report_llm    = build_llm(max_tokens=REPORT_MAX_TOKENS)
        json_response = report_llm.invoke([HumanMessage(content=synthesis_prompt)])
        stop_reason   = (getattr(json_response, "response_metadata", None) or {}).get("stop_reason")

        try:
            json_text = json_response.content
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]

            final_report = json.loads(json_text.strip())
            logger.info("JSON estructurado generado correctamente")
        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando JSON del reporte: {e} (stop_reason={stop_reason})")
            final_report = {
                "error": "No se pudo generar el reporte estructurado",
                "error_detail": {
                    "type":        "truncated" if stop_reason == "max_tokens" else "invalid_json",
                    "stop_reason": stop_reason,
                    "position":    e.pos,
                    "max_tokens":  REPORT_MAX_TOKENS,
                },
            }

    return {
        "messages":     [final_message],
        "final_report": final_report
    }

# ----------------------------------------------------------------
# ROUTER — DECIDE QUÉ NODO SIGUE DESPUÉS DEL CLASIFICADOR
# ----------------------------------------------------------------

def route_after_classifier(state: AgentState) -> str:
    """
    Decide el siguiente nodo después del clasificador:
    - Si el LLM llamó una herramienta → ir a node_rag_tool
    - Si el LLM respondió directamente → ir a node_synthesizer
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "rag_tool"
    return "synthesizer"


# ----------------------------------------------------------------
# CONSTRUCCIÓN DEL GRAFO
# ----------------------------------------------------------------

def build_agent():
    """Construye y compila el grafo LangGraph."""
    graph = StateGraph(AgentState)

    # Agregar nodos
    graph.add_node("classifier",  node_classifier)
    graph.add_node("rag_tool",    node_rag_tool)
    graph.add_node("synthesizer", node_synthesizer)

    # Definir flujo
    graph.add_edge(START, "classifier")
    graph.add_conditional_edges(
        "classifier",
        route_after_classifier,
        {
            "rag_tool":    "rag_tool",
            "synthesizer": "synthesizer"
        }
    )
    graph.add_edge("rag_tool",    "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()


# ----------------------------------------------------------------
# TERMINAL DE PRUEBAS
# ----------------------------------------------------------------

def run_agent_terminal():
    """Terminal interactivo para probar el agente con memoria multi-turno."""

    print("\n" + "=" * 60)
    print("  FUVIA AGENT — Phase 2 Terminal")
    print("  RAG Tool activo | FUVIA Tool activo")
    print("  Memoria multi-turno: activada")
    print("  Escribe 'exit' para salir | 'reporte' para ver el JSON")
    print("=" * 60 + "\n")

    # Inicializar RAG una sola vez
    logger.info("Inicializando RAG...")
    initialize_rag()

    agent         = build_agent()
    conversation  = []   # Historial acumulativo de la conversación
    last_report   = {}

    while True:
        try:
            user_input = input("Usuario> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCerrando agente...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "salir", "quit"]:
            print("Cerrando agente...")
            break

        if user_input.lower() == "reporte":
            if last_report:
                print("\n--- REPORTE JSON ESTRUCTURADO ---")
                print(json.dumps(last_report, indent=2, ensure_ascii=False))
                print("-" * 40 + "\n")
            else:
                print("No hay reporte generado aún.\n")
            continue

        # Agregar mensaje del usuario al historial
        conversation.append(HumanMessage(content=user_input))

        print("\nAgente procesando...\n")

        try:
            result = agent.invoke({
                "messages":           conversation,
                "normative_response": [],       # CAMBIO: antes ""
                "fuvia_response":     [],       # CAMBIO: antes ""
                "final_report":       {},
                "tool_runs":          [],
            })

            # Actualizar historial con los mensajes del agente
            conversation = result["messages"]
            last_report  = result.get("final_report", {})

            # Mostrar respuesta final (último AIMessage)
            final_response = next(
                (m.content for m in reversed(result["messages"])
                 if isinstance(m, AIMessage)),
                "Sin respuesta"
            )

            print(f"FUVIA Agent> {final_response}\n")

            if last_report and "error" not in last_report:
                print("  [JSON estructurado disponible — escribe 'reporte' para verlo]\n")

        except Exception as e:
            logger.error(f"Error en el agente: {e}")
            print(f"Error: {e}\n")


if __name__ == "__main__":
    run_agent_terminal()