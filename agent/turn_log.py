"""
agent/turn_log.py
=================
Registro JSONL por turno (W1). Toda la escritura pasa por write_turn(),
de modo que migrar a otro destino (p. ej. Supabase) solo cambia este archivo.

Se escribe SOLO si el request trae log_consent=true Y el servidor tiene
FUVIA_LOG_ENABLED=1. Directorio: FUVIA_LOG_DIR (por defecto agent/logs/).
Un archivo por día: turns-YYYY-MM-DD.jsonl, una línea por turno.
"""

import os
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
_LOCK = threading.Lock()


def _log_dir() -> Path:
    return Path(os.getenv("FUVIA_LOG_DIR", str(Path(__file__).parent / "logs")))


def build_turn_record(*, session_id, turn, user_message, history_len, tool_runs,
                      final_response, report, report_parse_error,
                      latency_ms_total, versions) -> dict:
    rag = next((r for r in tool_runs if r.get("tool") == "query_normative_standards"), None)

    tools = []
    for r in tool_runs:
        entry = {k: v for k, v in r.items()
                 if k not in ("tool", "lang_detected", "was_translated", "translated_query")}
        tools.append({"name": r.get("tool"), **entry})

    return {
        "schema_version":     SCHEMA_VERSION,
        "session_id":         session_id,
        "turn":               turn,
        "ts":                 datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "versions":           versions,
        "user_message":       user_message,
        "history_len":        history_len,
        "lang_detected":      rag.get("lang_detected") if rag else None,
        "translated_query":   rag.get("translated_query") if rag else None,
        "tools":              tools,
        "final_response":     final_response,
        "report":             report,
        "report_parse_error": report_parse_error,
        "latency_ms_total":   latency_ms_total,
        "labels":             {"user_flag": None, "human_verdict": None},
    }


def write_turn(record: dict) -> bool:
    """Devuelve True si escribió, False si el registro está desactivado en el servidor."""
    if os.getenv("FUVIA_LOG_ENABLED", "0") != "1":
        return False
    d = _log_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"turns-{datetime.now(timezone.utc):%Y-%m-%d}.jsonl"
    line = json.dumps(record, ensure_ascii=False, default=str)
    with _LOCK:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    return True