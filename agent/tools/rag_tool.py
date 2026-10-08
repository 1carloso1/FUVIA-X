"""
agent/tools/rag_tool.py
=======================
Wrapper del RAG de Phase 1 como herramienta de LangGraph.

Importa directamente desde rag/query.py — sin overhead de API intermedia.
El agente llama esta función cuando necesita consultar el stack normativo.
"""

import sys
import os
import time

# Agregar el directorio raíz al path para importar desde rag/
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langchain_core.tools import tool
from rag.query import run_query, setup_settings


def initialize_rag():
    """
    Inicializa el RAG una sola vez al arrancar el agente.
    Evita re-inicializar el modelo de embeddings en cada llamada.
    """
    setup_settings()


@tool(response_format="content_and_artifact")
def query_normative_standards(question: str) -> str:
    """
    Consulta el stack normativo ACI/ASTM para obtener requisitos,
    límites y especificaciones de diseño de concreto.

    Usar cuando el usuario pregunte sobre:
    - Requisitos de durabilidad (w/cm, f'c mínimo, clases de exposición)
    - Especificaciones de materiales (cemento, agregados, aditivos)
    - Requisitos sísmicos para elementos estructurales
    - Dosificación normativa de mezclas de concreto
    - Cualquier pregunta que requiera consultar ACI 318, ACI 211 o ASTM

    Args:
        question: Pregunta técnica en español o inglés

    Returns:
        Respuesta normativa con citación de fuentes (estándar y cláusula)
    """
    t0, result, error = time.perf_counter(), None, None
    try:
        import io
        from contextlib import redirect_stdout

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = run_query(question)          # CAMBIO: se conserva el retorno

        output = buffer.getvalue()

        # content: misma lógica de v1.0, sin tocar
        if "RESPUESTA NORMATIVA:" in output:
            start = output.find("RESPUESTA NORMATIVA:") + len("RESPUESTA NORMATIVA:")
            end   = output.find("─" * 20)
            content = output[start:end].strip() if end > start else output[start:].strip()
        else:
            content = output.strip()

    except Exception as e:
        error   = f"{type(e).__name__}: {e}"
        content = f"Error consultando el stack normativo: {str(e)}"

    if result is None and error is None:
        error = "no_result"                       # p. ej. colección no encontrada
    r = result or {}

    artifact = {
        "tool":             "query_normative_standards",
        "args":             {"question": question},
        "latency_ms":       int((time.perf_counter() - t0) * 1000),
        "lang_detected":    r.get("lang_detected"),
        "was_translated":   r.get("was_translated"),
        "translated_query": r.get("translated_query"),
        "llm_model":        r.get("llm_model"),
        "chunks":           r.get("chunks", []),
        "error":            error,
        "timings_ms": r.get("timings_ms"),
    }
    return content, artifact