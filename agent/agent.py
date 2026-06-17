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
from typing import Annotated
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from tools.rag_tool import query_normative_standards, initialize_rag
from tools.fuvia_tool import fuvia_predict_mix_design
from prompts import AGENT_SYSTEM_PROMPT, REPORT_SYNTHESIS_PROMPT

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
    messages: historial completo de la conversación (acumulativo)
    normative_response: última respuesta del RAG (para el sintetizador)
    final_report: JSON estructurado para el frontend React
    """
    messages:           Annotated[list, add_messages]
    normative_response: str
    fuvia_response:     str
    final_report:       dict


# ----------------------------------------------------------------
# INICIALIZACIÓN DEL LLM Y HERRAMIENTAS
# ----------------------------------------------------------------

def build_llm() -> ChatAnthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no encontrada en .env")
    return ChatAnthropic(
        model="claude-sonnet-4-5",
        api_key=api_key,
        max_tokens=800
    )


TOOLS = [query_normative_standards, fuvia_predict_mix_design]


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

    messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + state["messages"]

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

    Ejecuta las herramientas que el clasificador decidió llamar.
    Phase 2 Semana 2: query_normative_standards + fuvia_predict_mix_design.

    El agente puede llamar una o ambas herramientas en la misma consulta
    dependiendo de lo que el clasificador decidió.
    """
    from langchain_core.messages import ToolMessage

    last_message       = state["messages"][-1]
    tool_results       = []
    normative_response = state.get("normative_response", "")
    fuvia_response     = state.get("fuvia_response", "")

    for tool_call in last_message.tool_calls:
        logger.info(f"Ejecutando herramienta: {tool_call['name']}")

        if tool_call["name"] == "query_normative_standards":
            result             = query_normative_standards.invoke(tool_call["args"])
            normative_response = result
            tool_results.append(
                ToolMessage(content=result, tool_call_id=tool_call["id"])
            )

        elif tool_call["name"] == "fuvia_predict_mix_design":
            logger.info("Llamando endpoint FUVIA en Render...")
            result         = fuvia_predict_mix_design.invoke(tool_call["args"])
            fuvia_response = result
            tool_results.append(
                ToolMessage(content=result, tool_call_id=tool_call["id"])
            )

    return {
        "messages":           tool_results,
        "normative_response": normative_response,
        "fuvia_response":     fuvia_response
    }


def node_synthesizer(state: AgentState) -> AgentState:
    """
    Nodo 3 — Sintetizador.

    Genera la respuesta final en dos formatos:
    1. Mensaje conversacional para el historial (en el idioma del usuario)
    2. JSON estructurado para el frontend React (solo si hubo herramientas)

    OPTIMIZACIÓN: Si el clasificador ya generó una respuesta directa
    (sin tool calls), reutiliza ese contenido sin llamar al LLM de nuevo.
    Esto resuelve el problema de respuestas vacías [] en consultas sin herramientas.
    """
    llm = build_llm()

    # Detectar si el último mensaje ya tiene contenido del clasificador
    # (respuesta directa sin tool calls — saludo, pregunta ambigua, fuera de scope)
    last_msg           = state["messages"][-1]
    has_direct_content = (
        isinstance(last_msg, AIMessage)
        and bool(last_msg.content and str(last_msg.content).strip())
        and not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls)
    )

    if has_direct_content and not state.get("normative_response") and not state.get("fuvia_response"):
        # El clasificador ya respondió directamente — usar ese contenido sin re-invocar
        logger.info("Respuesta directa del clasificador — sin re-invocar LLM")
        return {
            "messages":     [last_msg],
            "final_report": {}
        }

    # Si hay respuesta de FUVIA, extraer el f'c exacto y agregarlo
    # al system prompt para evitar que Claude use su propio calculo
    fuvia_resp   = state.get("fuvia_response", "")
    fc_injection = ""
    if fuvia_resp:
        fc_match = re.search(r"\[FUVIA_FC\][^\d]*([\d\.]+)\s*MPa", fuvia_resp)
        if fc_match:
            fc_exact = fc_match.group(1)
            fc_injection = (
                f"\n\nCRITICAL: The FUVIA model predicted exactly {fc_exact} MPa. "
                f"You MUST use this exact value when mentioning f\'c in your response. "
                f"Do not round, recalculate, or use any other value."
            )

    # Generar respuesta conversacional final (cuando hubo herramientas)
    system_with_fc = AGENT_SYSTEM_PROMPT + fc_injection
    messages       = [SystemMessage(content=system_with_fc)] + state["messages"]
    final_message  = llm.invoke(messages)

    # Generar JSON estructurado si hubo cualquier herramienta (normativa o FUVIA)
    final_report = {}
    if state.get("normative_response") or state.get("fuvia_response"):
        last_user_msg = next(
            (m.content for m in reversed(state["messages"])
             if isinstance(m, HumanMessage)),
            ""
        )

        fuvia_resp = state.get("fuvia_response", "")
        synthesis_prompt = REPORT_SYNTHESIS_PROMPT.format(
            query=last_user_msg,
            normative_response=state["normative_response"],
            fuvia_response=fuvia_resp
        )

        json_response = llm.invoke([HumanMessage(content=synthesis_prompt)])

        try:
            # Limpiar posibles backticks de markdown
            json_text = json_response.content
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]

            final_report = json.loads(json_text.strip())
            logger.info("JSON estructurado generado correctamente")
        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando JSON del reporte: {e}")
            final_report = {"error": "No se pudo generar el reporte estructurado"}

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
                "normative_response": "",
                "fuvia_response":     "",
                "final_report":       {}
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