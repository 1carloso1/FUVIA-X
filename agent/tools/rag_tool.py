"""
agent/tools/rag_tool.py
=======================
Wrapper del RAG de Phase 1 como herramienta de LangGraph.

Importa directamente desde rag/query.py — sin overhead de API intermedia.
El agente llama esta función cuando necesita consultar el stack normativo.
"""

import sys
import os

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


@tool
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
    try:
        # run_query imprime a consola — capturamos el resultado
        # redirigiendo stdout temporalmente
        import io
        from contextlib import redirect_stdout

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            run_query(question)

        output = buffer.getvalue()

        # Extraer solo la respuesta normativa del output
        # (omitir logs de ChromaDB y metadata de fuentes)
        if "RESPUESTA NORMATIVA:" in output:
            start   = output.find("RESPUESTA NORMATIVA:") + len("RESPUESTA NORMATIVA:")
            end     = output.find("─" * 20)
            if end > start:
                return output[start:end].strip()
            return output[start:].strip()

        return output.strip()

    except Exception as e:
        return f"Error consultando el stack normativo: {str(e)}"