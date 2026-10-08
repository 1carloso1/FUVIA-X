"""
agent/citation_check.py
=======================
Verificador de citas (W4, fase 1: solo registro).

Extrae de la respuesta del agente: normas, números de sección, tablas y
textos entre comillas, y comprueba si aparecen en la evidencia del turno
(texto completo de los chunks recuperados).

QUÉ VERIFICA: que el identificador APARECE en el texto recuperado.
QUÉ NO VERIFICA: que el valor o la afirmación asociada sea correcta.

Función pura: depende solo de (response, chunks, user_message), de modo que
puede recalcularse sobre los registros JSONL.
"""

import re

# Documentos con detalle citable (los mismos de AGENT_SYSTEM_PROMPT)
CORPUS = {
    ("ACI", "211.1"):  "ACI 211.1-22",
    ("ACI", "211.4R"): "ACI 211.4R-08",
    ("ACI", "318"):    "ACI 318-19",
    ("ASTM", "C150"):  "ASTM C150/C150M-22",
    ("ASTM", "C33"):   "ASTM C33/C33M-13",
    ("ASTM", "C494"):  "ASTM C494/C494M-19",
}
_FAMILY_OK = {("ACI", "211")}   # "ACI 211" sin sufijo: se acepta como familia del corpus

_ACI   = re.compile(r"\bACI\s*(?:PRC[-\s]?)?(\d{2,3}(?:\.\d+)?R?)(?:\s*[-–]\s*\d{2})?")
_ASTM  = re.compile(r"\bASTM\s*([A-Z])\s?(\d{1,4})([A-Z]?)(?:/[A-Z]\d{1,4}M)?(?:\s*[-–]\s*\d{2})?")
_OTHER = re.compile(r"\b(NMX[-\s]?[A-Z]?[-\s]?\d+(?:-[A-Z0-9]+)*|ISO\s?\d{3,6})")

_SECTION = re.compile(
    r"(?:§+\s*|\b(?:[Ss]ecci[oó]n(?:es)?|[Ss]ection|[Ss]ec\.|[Cc]l[aá]usula|[Cc]lause"
    r"|[Cc]omentario|[Cc]ommentary)\s+)(R?\d+(?:\.\d+)+[a-z]?)"
)
_TABLE = re.compile(r"\b(?:[Tt]able|[Tt]abla)s?\s+(\d+(?:\.\d+)*[a-z]?)")
_QUOTE_PAIRS = re.compile(r"[“«]([^”»\n]{25,400})[”»]")

_ES_STOP = {"de", "la", "el", "los", "las", "que", "en", "del", "para", "con", "por",
            "una", "un", "se", "debe", "según", "y", "o", "su", "al"}


def _extract_standards(text: str) -> dict:
    found = {}
    for m in _ACI.finditer(text):
        sid = m.group(1)
        if sid == "211.4":
            sid = "211.4R"
        found.setdefault(("ACI", sid), m.group(0).strip())
    for m in _ASTM.finditer(text):
        sid = f"{m.group(1)}{m.group(2)}{m.group(3)}"
        found.setdefault(("ASTM", sid), m.group(0).strip())
    for m in _OTHER.finditer(text):
        sid = re.sub(r"\s+", "", m.group(1))
        found.setdefault(("NMX" if sid.startswith("NMX") else "ISO", sid), m.group(0).strip())
    return found


def _extract_quotes(text: str) -> list:
    quotes = list(_QUOTE_PAIRS.findall(text))
    parts = text.split('"')
    if len(parts) % 2 == 1:            # número par de comillas rectas: se pueden emparejar
        quotes += parts[1::2]
    out = [q.strip() for q in quotes
           if 25 <= len(q.strip()) <= 400 and len(q.split()) >= 4]
    return list(dict.fromkeys(out))


def _norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"-\s+", "", s)                       # "require- ments" (OCR) -> "requirements"
    s = re.sub(r"[^a-z0-9áéíóúüñ]+", " ", s)
    return s.strip()


def _looks_spanish(qn: str) -> bool:
    words = qn.split()
    es = sum(w in _ES_STOP for w in words)
    return bool(words) and es >= 2 and es / len(words) >= 0.15


def _section_pat(ref: str):
    return re.compile(rf"(?<![\d.]){re.escape(ref.lstrip('R'))}(?!\d|\.\d)")


def _table_pat(ref: str):
    return re.compile(rf"table\s+{re.escape(ref)}(?![A-Za-z0-9]|\.\d)", re.I)


def _id_pat(sid: str):
    return re.compile(rf"(?<![A-Za-z0-9.]){re.escape(sid)}(?![A-Za-z0-9])")


def _docs_with(pattern, chunks: list) -> list:
    docs = {c.get("doc") for c in chunks if pattern.search(c.get("text") or "")}
    return sorted(d for d in docs if d)


def check_citations(response: str, chunks: list, user_message: str = "") -> dict:
    response, chunks, user_message = response or "", chunks or [], user_message or ""

    standards, out_of_corpus = [], []
    for (system, sid), raw in _extract_standards(response).items():
        name = f"{system} {sid}"
        if (system, sid) in CORPUS or (system, sid) in _FAMILY_OK:
            standards.append(name)
        else:
            pat = _id_pat(sid)
            out_of_corpus.append({
                "id": name, "raw": raw,
                "in_chunks": bool(_docs_with(pat, chunks)),
                "in_user_message": bool(pat.search(user_message)),
            })

    sections = []
    for ref in dict.fromkeys(_SECTION.findall(response)):
        docs = _docs_with(_section_pat(ref), chunks)
        sections.append({"ref": ref, "supported": bool(docs), "found_in_docs": docs})

    tables = []
    for ref in dict.fromkeys(_TABLE.findall(response)):
        docs = _docs_with(_table_pat(ref), chunks)
        tables.append({"ref": ref, "supported": bool(docs), "found_in_docs": docs})

    chunk_norms = [_norm(c.get("text") or "") for c in chunks]
    quotes = []
    for q in _extract_quotes(response):
        qn = _norm(q)
        if qn and any(qn in cn for cn in chunk_norms):
            status = "supported"
        elif _looks_spanish(qn):
            status = "translated"        # cita en español de evidencia en inglés: no verificable
        else:
            status = "unsupported"
        quotes.append({"text": q[:200], "status": status})

    summary = {
        "evidence_chunks":      len(chunks),
        "n_sections":           len(sections),
        "sections_unsupported": sum(not s["supported"] for s in sections),
        "n_tables":             len(tables),
        "tables_unsupported":   sum(not t["supported"] for t in tables),
        "n_quotes":             len(quotes),
        "quotes_unsupported":   sum(q["status"] == "unsupported" for q in quotes),
        "quotes_translated":    sum(q["status"] == "translated" for q in quotes),
        "out_of_corpus_unseen": [o["id"] for o in out_of_corpus
                                 if not o["in_chunks"] and not o["in_user_message"]],
    }
    summary["unsupported_total"] = (summary["sections_unsupported"]
                                    + summary["tables_unsupported"]
                                    + summary["quotes_unsupported"])

    return {
        "version":             1,
        "standards_in_corpus": sorted(set(standards)),
        "out_of_corpus":       out_of_corpus,
        "sections":            sections,
        "tables":              tables,
        "quotes":              quotes,
        "summary":             summary,
    }