"""
agent/tools/fuvia_tool.py
=========================
Wrapper del endpoint de predicción de FUVIA como herramienta LangGraph.

Llama al modelo CatBoost desplegado en Render y retorna la dosificación
predicha con resistencia estimada, clasificaciones y recomendaciones.

ENDPOINT: POST https://firmitas-ai.onrender.com/api/predecir

VALIDACIÓN:
El servidor FUVIA ya implementa un firewall paramétrico completo:
  - Dominio de aplicabilidad Yeh 1998 (rangos del dataset)
  - Límites de edad ACI 209R
  - Inviabilidad física ACI 318 (peso volumétrico)
  - Límites w/cm ACI 211.1
  - Sobredosis de aditivo ACI 212.3R / ASTM C494
  - Relación grava/arena dominio Yeh

El tool maneja los errores HTTP 400 del firewall y los traduce
en mensajes claros para que el agente los comunique al usuario.
"""

import os

import httpx
from langchain_core.tools import tool

FUVIA_API_URL = os.getenv("FUVIA_API_URL", "https://firmitas-ai.onrender.com/api/predecir")
TIMEOUT_SECONDS = 45  # Render puede tener cold start de hasta 30s


@tool
def fuvia_predict_mix_design(
    cement: float,
    slag: float,
    flyash: float,
    water: float,
    superplasticizer: float,
    coarseaggregate: float,
    fineaggregate: float,
    age: int
) -> str:
    """
    Predice la resistencia a compresión (f'c) de una dosificación de concreto
    usando el modelo CatBoost de FUVIA, entrenado con el dataset Yeh 1998.

    Usar cuando el usuario proporcione cantidades específicas de materiales
    y quiera conocer la resistencia estimada, validar su mezcla, o comparar
    la dosificación propuesta contra requisitos normativos ACI/ASTM.

    Todos los materiales en kg/m³. Age en días.
    Usar 0 para materiales no incluidos en la mezcla (slag, flyash, superplasticizer).

    Args:
        cement:           Cemento Portland (kg/m³). Rango típico: 102–540
        slag:             Escoria de alto horno (kg/m³). 0 si no aplica
        flyash:           Ceniza volante (kg/m³). 0 si no aplica
        water:            Agua (kg/m³). Rango típico: 121–247
        superplasticizer: Superplastificante (kg/m³). 0 si no aplica
        coarseaggregate:  Agregado grueso (kg/m³). Rango típico: 801–1145
        fineaggregate:    Agregado fino (kg/m³). Rango típico: 594–993
        age:              Edad de curado en días. Rango válido: 1–365

    Returns:
        Reporte de predicción con f'c estimado, clase de resistencia,
        relaciones w/cm y grava/arena, y recomendaciones de uso.
        Si la dosificación está fuera del dominio del modelo, retorna
        el mensaje de error específico del firewall paramétrico.
    """
    payload = {
        "cement":           cement,
        "slag":             slag,
        "flyash":           flyash,
        "water":            water,
        "superplasticizer": superplasticizer,
        "coarseaggregate":  coarseaggregate,
        "fineaggregate":    fineaggregate,
        "age":              age
    }

    try:
        response = httpx.post(
            FUVIA_API_URL,
            json=payload,
            timeout=TIMEOUT_SECONDS
        )

        # Manejar errores del firewall paramétrico (HTTP 400)
        if response.status_code == 400:
            error_detail = response.json().get("detail", {})
            if isinstance(error_detail, dict):
                campos  = error_detail.get("campos", [])
                mensaje = error_detail.get("mensaje", "Dosificación inválida")
                campos_str = ", ".join(campos) if campos else "parámetros"
                return (
                    f"FUVIA FIREWALL — Dosificación rechazada\n"
                    f"Campo(s) problemático(s): {campos_str}\n"
                    f"Razón: {mensaje}\n\n"
                    f"El agente debe informar al usuario qué parámetro ajustar."
                )
            return f"FUVIA FIREWALL — {error_detail}"

        response.raise_for_status()
        data = response.json()
        return _format_fuvia_response(payload, data)

    except httpx.TimeoutException:
        return (
            "FUVIA TIMEOUT — El servidor tardó más de 45 segundos en responder. "
            "Render puede estar iniciando desde cold start. "
            "Sugiere al usuario intentar de nuevo en 30 segundos."
        )
    except httpx.HTTPStatusError as e:
        return f"FUVIA ERROR {e.response.status_code} — {e.response.text[:200]}"
    except Exception as e:
        return f"FUVIA ERROR inesperado — {str(e)}"


def _format_fuvia_response(inputs: dict, output: dict) -> str:
    """
    Formatea la respuesta de FUVIA en texto estructurado
    para que el agente sintetizador lo incorpore al reporte JSON.
    """
    lines = []

    lines.append("=== PREDICCIÓN FUVIA X — CatBoost (Yeh 1998) ===")
    lines.append("")

    # Dosificación analizada
    lines.append("DOSIFICACIÓN (kg/m³):")
    lines.append(f"  Cemento           : {inputs['cement']}")
    if inputs['slag'] > 0:
        lines.append(f"  Escoria           : {inputs['slag']}")
    if inputs['flyash'] > 0:
        lines.append(f"  Ceniza volante    : {inputs['flyash']}")
    lines.append(f"  Agua              : {inputs['water']}")
    if inputs['superplasticizer'] > 0:
        lines.append(f"  Superplastificante: {inputs['superplasticizer']}")
    lines.append(f"  Agregado grueso   : {inputs['coarseaggregate']}")
    lines.append(f"  Agregado fino     : {inputs['fineaggregate']}")
    lines.append(f"  Edad de curado    : {inputs['age']} días")
    lines.append("")

    # Resultado principal — marcador [FUVIA_FC] para que el sintetizador
    # use este valor exacto en el JSON sin confundirlo con valores del RAG
    fc_value = output.get('resistencia_estimada', 'N/A')
    lines.append("RESULTADO:")
    lines.append(f"  [FUVIA_FC] f'c estimado (USAR ESTE VALOR EN JSON): {fc_value} MPa")
    lines.append(f"  Clase resistencia : {output.get('clase_resistencia', 'N/A')}")
    lines.append(f"  Evaluacion general: {output.get('mensaje', 'N/A')}")
    lines.append("")

    # Relaciones calculadas
    lines.append("RELACIONES DE MEZCLA:")
    lines.append(f"  w/cm              : {output.get('relacion_agua_cemento', 'N/A')}")
    lines.append(f"  Grava/Arena       : {output.get('relacion_grava_arena', 'N/A')}")
    lines.append("")

    # Clasificación w/cm
    clase_ac = output.get('clase_ac', '')
    if clase_ac:
        lines.append(f"CLASIFICACIÓN w/cm: {clase_ac}")
        lines.append(f"  {output.get('descripcion_ac', '')}")
        for c in output.get('caracteristicas_ac', []):
            lines.append(f"  - {c}")
        lines.append("")

    # Clasificación grava/arena
    clase_ga = output.get('clase_ga', '')
    if clase_ga:
        lines.append(f"CLASIFICACIÓN GRAVA/ARENA: {clase_ga}")
        lines.append(f"  {output.get('descripcion_ga', '')}")
        for c in output.get('caracteristicas_ga', []):
            lines.append(f"  - {c}")
        lines.append("")

    # Recomendaciones de uso (usos del concreto según clase)
    recomendaciones = output.get('recomendaciones', [])
    if recomendaciones:
        lines.append("USOS RECOMENDADOS SEGÚN CLASE DE RESISTENCIA:")
        for r in recomendaciones:
            lines.append(f"  • {r}")

    return "\n".join(lines)