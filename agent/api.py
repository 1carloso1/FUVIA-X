"""
agent/api.py
============
FastAPI que expone el agente LangGraph al frontend React.

ENDPOINTS:
  POST /api/chat     — envía mensaje al agente, retorna respuesta + JSON
  GET  /api/health   — verifica que el servidor está activo

CORS configurado para desarrollo local (localhost:5173)
y producción (fuvia.vercel.app).

USO LOCAL:
  cd fuvia-x/agent
  uvicorn api:app --reload --port 8001
"""

import os
import re
import json
import logging
import time
from functools import lru_cache
from turn_log import build_turn_record, write_turn
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv
from citation_check import check_citations


import hashlib
import subprocess
from prompts import PROMPT_VERSION, MODEL_ID
from rag.query import RAG_MODEL_ID

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar el agente — se inicializa una vez en el lifespan
from agent import build_agent, AgentState
from tools.rag_tool import initialize_rag
from prompts import AGENT_SYSTEM_PROMPT

# ----------------------------------------------------------------
# SCHEMAS DE REQUEST / RESPONSE
# ----------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str        # "user" o "assistant"
    content: str


class ChatRequest(BaseModel):
    message:  str
    history:  list[ChatMessage] = []
    session_id:  Optional[str] = None   # NUEVO: UUID anónimo generado en el frontend
    log_consent: bool = False           # NUEVO: sin consentimiento no se escribe nada


class ChatResponse(BaseModel):
    response:     str
    report:       Optional[dict] = None
    tools_called: list[str] = []


# ----------------------------------------------------------------
# LIFESPAN — inicializar RAG una sola vez al arrancar
# ----------------------------------------------------------------

agent_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance

    # Correr ingest si chroma_db no existe (primera vez en Render)
    chroma_path = os.path.join(os.path.dirname(__file__), 'rag', 'chroma_db')
    if not os.path.exists(chroma_path):
        logger.info("chroma_db no encontrado — indexando documentos...")
        import subprocess
        subprocess.run(['python', 'rag/ingest.py'], check=True)
        logger.info("Indexado completado.")

    logger.info("Inicializando RAG y agente LangGraph...")
    initialize_rag()
    agent_instance = build_agent()
    logger.info("Agente listo.")
    yield
    logger.info("Apagando servidor del agente.")


# ----------------------------------------------------------------
# APP
# ----------------------------------------------------------------

app = FastAPI(
    title="FUVIA X — Agent API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://fuvia.vercel.app",
        "https://fuvia.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------
# UTILIDADES
# ----------------------------------------------------------------

def history_to_langchain(history: list[ChatMessage]) -> list:
    """
    Convierte el historial del frontend (lista de dicts)
    a mensajes de LangChain para el estado del agente.
    """
    messages = []
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    return messages


def extract_final_response(messages: list) -> str:
    """
    Extrae el último AIMessage con contenido real del historial.
    Ignora ToolMessages y AIMessages vacíos.
    """
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                # Manejar content blocks (tool_use, text)
                text_parts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                content = " ".join(text_parts).strip()
            if content and str(content).strip() and str(content).strip() != "[]":
                return str(content).strip()
    return "No se pudo generar una respuesta."


def extract_tools_called(messages: list) -> list[str]:
    """
    Extrae los nombres de las herramientas que fueron llamadas
    en este turno para informar al frontend.
    """
    tools = []
    for msg in messages:
        if isinstance(msg, AIMessage):
            tool_calls = getattr(msg, "tool_calls", [])
            for tc in tool_calls:
                name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
                if name and name not in tools:
                    tools.append(name)
    return tools


# ----------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------

@app.get("/api/health")
def health():
    """Verifica que el servidor está activo."""
    return {"status": "ok", "agent": "ready" if agent_instance else "initializing"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal del agente conversacional.

    Recibe el mensaje del usuario y el historial completo de la conversación.
    El frontend es responsable de mantener y enviar el historial en cada request.

    Retorna:
      - response: texto conversacional para mostrar en el chat
      - report:   JSON estructurado (si hubo consulta normativa o predicción)
      - tools_called: herramientas usadas en este turno
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agente inicializando, intenta en unos segundos.")

    try:
        t_start = time.perf_counter()

        # Reconstruir historial completo
        history_messages  = history_to_langchain(request.history)
        current_message   = HumanMessage(content=request.message)
        full_conversation = history_messages + [current_message]

        logger.info(f"Turno recibido — historial: {len(history_messages)} msgs")

        # Invocar el agente
        result = agent_instance.invoke({
            "messages":           full_conversation,
            "normative_response": [],       # CAMBIO: antes ""
            "fuvia_response":     [],       # CAMBIO: antes ""
            "final_report":       {},
            "tool_runs":          [],
        })

        # Extraer respuesta final
        response_text = extract_final_response(result["messages"])
        tools_called  = extract_tools_called(result["messages"])
        final_report  = result.get("final_report", {})

        report_parse_error = bool(final_report and "error" in final_report)
        report_error = final_report.get("error_detail") if report_parse_error else None   # NUEVO
        # Limpiar report vacío
        if final_report and "error" in final_report:
            final_report = None

        # Registro con consentimiento; un fallo aquí nunca rompe la respuesta
        if request.log_consent:
            try:
                rag_chunks = [
                    c for r in result.get("tool_runs", [])
                    if r.get("tool") == "query_normative_standards"
                    for c in r.get("chunks", [])
                ]
                try:
                    citation_check = check_citations(response_text, rag_chunks, request.message)
                    logger.info(f"Verificación de citas: {citation_check['summary']}")
                except Exception as cc_err:
                    citation_check = {"error": f"{type(cc_err).__name__}: {cc_err}"}

                write_turn(build_turn_record(
                    session_id=request.session_id,
                    turn=sum(1 for m in request.history if m.role == "user") + 1,
                    user_message=request.message,
                    history_len=len(history_messages),
                    tool_runs=result.get("tool_runs", []),
                    final_response=response_text,
                    report=final_report if final_report else None,
                    report_parse_error=report_parse_error,
                    report_error=report_error,
                    latency_ms_total=int((time.perf_counter() - t_start) * 1000),
                    versions=_get_versions(),
                    citation_check=citation_check,
                ))
            except Exception as log_err:
                logger.warning(f"No se pudo escribir el registro del turno: {log_err}")

        logger.info(f"Respuesta generada — tools: {tools_called}")

        return ChatResponse(
            response=response_text,
            report=final_report if final_report else None,
            tools_called=tools_called
        )

    except Exception as e:
        logger.exception("Error en el agente")      # antes: logger.error(f"Error en el agente: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del agente: {str(e)}"
        )


@lru_cache(maxsize=1)
def _get_versions() -> dict:
    # Commit actual del repositorio
    try:
        app_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        app_commit = "unknown"

    # Hash del corpus normativo (chroma_db como proxy)
    try:
        chroma_path = os.path.join(os.path.dirname(__file__), "rag", "chroma_db")
        h = hashlib.md5()
        for root, _, files in os.walk(chroma_path):
            for f in sorted(files):
                with open(os.path.join(root, f), "rb") as fh:
                    h.update(fh.read(4096))  # solo los primeros 4KB por archivo
        kb_hash = h.hexdigest()[:8]
    except Exception:
        kb_hash = "unknown"

    return {
        "app_commit":     app_commit,
        "prompt_version": PROMPT_VERSION,
        "model":          MODEL_ID,
        "rag_model":      RAG_MODEL_ID,
        "kb_hash":        kb_hash,
    }

@app.get("/api/version")
def version():
    """Snapshot de versión del sistema para trazabilidad y reproducibilidad."""
    return _get_versions()