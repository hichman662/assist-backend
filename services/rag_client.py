# app/services/rag_client.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import re
from datetime import datetime
from app.services.rag_index import rag_index

# Map numeric TypeActivity → human label (ES)
TYPE_MAP = {1: "medicación", 2: "nutrición", 3: "mensaje", 4: "cita"}
_heading_re = re.compile(r"^\s*#+\s*")  # strip markdown headings like "## "

# -----------------------------
# Utilities
# -----------------------------
def _clean_line(s: str) -> str:
    s = _heading_re.sub("", s or "").strip()
    s = s.replace("→", "-").strip()
    return s

def _safe_dt(iso: Optional[str], lang: str = "es") -> str:
    """Convert ISO to natural ES text; fallback to raw on parse errors."""
    if not iso or not isinstance(iso, str):
        return ""
    try:
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        except ValueError:
            core = iso.split(".")[0]
            dt = datetime.fromisoformat(core)
        meses = [
            "enero","febrero","marzo","abril","mayo","junio",
            "julio","agosto","septiembre","octubre","noviembre","diciembre"
        ]
        h = dt.hour
        ampm = "de la mañana" if h < 12 else "de la tarde" if h < 20 else "de la noche"
        return f"{dt.day} de {meses[dt.month-1]} a las {dt.hour:02d}:{dt.minute:02d} {ampm}"
    except Exception:
        return iso

def _coerce_type_label(type_code: Any) -> str:
    try:
        t = int(type_code)
    except Exception:
        return "actividad"
    return TYPE_MAP.get(t, "actividad")

# -----------------------------
# Normalize one CareActivity
# -----------------------------
def _short_item(ca: Dict[str, Any], lang: str = "es") -> Dict[str, Any]:
    if not isinstance(ca, dict):
        return {"id": None, "when": "", "title": "Elemento inválido", "type": "actividad", "note": ""}

    v = ca.get("valueCareActivity") or {}
    title = (v.get("name") or ca.get("name") or "").strip() or "(sin título)"
    note  = (v.get("description") or ca.get("description") or "").strip()
    when  = _safe_dt(ca.get("timeAct"), lang)
    type_label = _coerce_type_label(v.get("typeActivity"))
    location   = v.get("location") or ca.get("location") or ""

    item: Dict[str, Any] = {
        "id": ca.get("id"),
        "when": when,
        "title": title,
        "type": type_label,
        "note": note,
        "location": location,
    }

    med = v.get("medications")
    if isinstance(med, dict):
        item["medication"] = {
            "name": med.get("name"),
            "dosage": med.get("dosage"),
            "instructions": med.get("description"),
        }

    nut = v.get("nutritionOrders")
    if isinstance(nut, dict):
        item["nutrition"] = {
            "name": nut.get("name"),
            "instructions": nut.get("description"),
        }

    apps = v.get("appointments")
    if isinstance(apps, dict):
        item["appointment"] = {
            "virtual": bool(apps.get("isVirtual")),
            "where": apps.get("direction"),
            "reason": apps.get("description"),
        }

    comms = v.get("comunications") or []
    if isinstance(comms, list) and comms:
        msgs = []
        for c in comms:
            if isinstance(c, dict):
                msgs.append({
                    "severity": c.get("severity"),
                    "message": c.get("message"),
                    "when": _safe_dt(c.get("sendDate"), lang),
                })
        if msgs:
            item["messages"] = msgs

    return item

# -----------------------------
# KB query (hints)
# -----------------------------
def _build_query_from_item(it: Dict[str, Any]) -> str:
    parts: List[str] = []
    if it.get("type"): parts.append(it["type"])
    if it.get("title"): parts.append(it["title"])
    if it.get("medication"): parts.append(it["medication"].get("name", ""))
    if it.get("nutrition"): parts.append(it["nutrition"].get("name", ""))
    if it.get("appointment"):
        parts.append("cita virtual" if it["appointment"].get("virtual") else "cita presencial")
    if it.get("messages"):
        parts.append(it["messages"][0].get("message", ""))
    return " | ".join([p for p in parts if p])

def _preferred_order_for(it: Dict[str, Any]) -> List[str]:
    t = it.get("type")
    if t == "medicación":
        return ["meds.md", "mosiot_codes.md", "appointments.md", "nutrition.md"]
    if t == "nutrición":
        return ["nutrition.md", "meds.md", "mosiot_codes.md", "appointments.md"]
    if t == "cita":
        return ["appointments.md", "mosiot_codes.md", "meds.md", "nutrition.md"]
    return ["mosiot_codes.md", "meds.md", "nutrition.md", "appointments.md"]

def _retrieve_hints(it: Dict[str, Any], k: int = 3) -> List[str]:
    hits = rag_index.query(_build_query_from_item(it), k=max(k, 3))
    order = _preferred_order_for(it)
    hits_sorted = sorted(
        hits,
        key=lambda h: (
            order.index(h["meta"].get("path"))
            if h.get("meta") and h["meta"].get("path") in order
            else 999
        ),
    )
    out: List[str] = []
    seen = set()
    for h in hits_sorted:
        first = _clean_line(
            (h.get("text") or "").splitlines()[0] if h.get("text") else ""
        )
        if not first:
            continue
        key = first.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(first[:200])
        if len(out) >= k:
            break
    return out

# -----------------------------
# TTS-friendly activity line
# -----------------------------
def _fmt_activity_for_tts(it: Dict[str, Any]) -> str:
    ttl = (it.get("title") or it.get("type") or "").strip()
    when = it.get("when") or ""
    extras: List[str] = []
    if it.get("medication"):
        name = it["medication"].get("name") or ""
        dose = it["medication"].get("dosage") or ""
        if name and dose:
            extras.append(f"{name} ({dose})")
        elif name:
            extras.append(name)
    if it.get("nutrition"):
        nname = it["nutrition"].get("name") or ""
        if nname:
            extras.append(nname)
    if it.get("appointment"):
        extras.append("cita virtual" if it["appointment"].get("virtual") else "cita presencial")
    if it.get("messages"):
        msg = it["messages"][0].get("message") or ""
        if msg:
            extras.append(msg)
    extra_txt = f" — {' — '.join(extras)}" if extras else ""
    when_txt  = f" — {when}" if when else ""
    return f"{ttl}{extra_txt}{when_txt}".strip(" —")

# -----------------------------
# Main summarizer (public)
# -----------------------------
def explain_care_activities(raw_list: Any, lang: str = "es") -> Dict[str, Any]:
    # Normalize input to list[dict] and filter invalid rows
    if isinstance(raw_list, dict):
        raw_list = [raw_list]
    elif not isinstance(raw_list, list):
        raw_list = []

    valid: List[Dict[str, Any]] = []
    skipped = 0
    for row in raw_list:
        if isinstance(row, dict):
            valid.append(row)
        else:
            skipped += 1

    if not valid:
        empty = "No hay actividades disponibles en este momento."
        return {
            "summary_text": empty,
            "items": [],
            "by_type": {},
            "count": 0,
            "skipped": skipped,
        }

    # Build items + hints
    items = [_short_item(x, lang=lang) for x in valid]
    for it in items:
        it["hints"] = _retrieve_hints(it, k=3)

    # Counts per type
    by_type: Dict[str, int] = {}
    for it in items:
        t = it.get("type") or "actividad"
        by_type[t] = by_type.get(t, 0) + 1

    total = len(items)

    # Header with ordered types
    order = ["nutrición", "medicación", "mensaje", "cita", "actividad"]
    counts_txt = ", ".join([f"{t}: {by_type[t]}" for t in order if by_type.get(t)])
    skipped_note = f" (se omitieron {skipped} elementos inválidos)" if skipped > 0 else ""
    header = f"Tienes {total} actividades de cuidado{skipped_note}"
    header += f" ({counts_txt})." if counts_txt else "."

    # Activity lines (good for TTS too)
    acts = [f"{i+1}) {_fmt_activity_for_tts(it)}" for i, it in enumerate(items)]
    activities_text = " Actividades: " + "; ".join(acts) + "." if acts else ""

    # Quick tips (first hint of first few items)
    tips_pairs = []
    for it in items[:3]:
        ttl = (it.get("title") or it.get("type") or "").strip()
        hint = (it.get("hints") or [""])[0]
        if ttl and hint:
            tips_pairs.append(f"{ttl}: {hint}")
    tips_text = f" Consejos rápidos: {'; '.join(tips_pairs)}." if tips_pairs else ""

    summary_text = (header + activities_text + tips_text).strip()

    return {
        "summary_text": summary_text,   # single field; FE uses this for TTS
        "items": items,
        "by_type": by_type,
        "count": total,
        "skipped": skipped,
    }
