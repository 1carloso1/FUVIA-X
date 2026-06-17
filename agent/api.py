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
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv

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
        # Reconstruir historial completo
        history_messages  = history_to_langchain(request.history)
        current_message   = HumanMessage(content=request.message)
        full_conversation = history_messages + [current_message]

        logger.info(f"Turno recibido — historial: {len(history_messages)} msgs")

        # Invocar el agente
        result = agent_instance.invoke({
            "messages":           full_conversation,
            "normative_response": "",
            "fuvia_response":     "",
            "final_report":       {}
        })

        # Extraer respuesta final
        response_text = extract_final_response(result["messages"])
        tools_called  = extract_tools_called(result["messages"])
        final_report  = result.get("final_report", {})

        # Limpiar report vacío
        if final_report and "error" in final_report:
            final_report = None

        logger.info(f"Respuesta generada — tools: {tools_called}")

        return ChatResponse(
            response=response_text,
            report=final_report if final_report else None,
            tools_called=tools_called
        )

    except Exception as e:
        logger.error(f"Error en el agente: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del agente: {str(e)}"
        )