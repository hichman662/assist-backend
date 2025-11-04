# app/services/agent_service.py
from typing import Any, Dict, Optional

from app.services.intent_table import INTENT_ROUTES
from app.services.dotnet_client import dotnet_client
from app.services.rag_client import explain_care_activities  # <-- add this

class AgentService:
    """
    Reads intents and dispatches to the right target using INTENT_ROUTES.
    """
    def handle_intent(self, body: Dict[str, Any], auth_header: Optional[str]) -> Dict[str, Any]:
        intent  = (body.get("intent") or "").lower()
        text    = body.get("text")
        context = body.get("context") or {}
        payload = body.get("payload")  # may contain query/body params

        route = INTENT_ROUTES.get(intent)
        if not route:
            return {"action": "speak", "speech": "I didn't understand that."}

        target = route["target"]

        # ===== FRONTEND ACTIONS =====
        if target == "frontend":
            return {
                "action":    route["action"],
                "autostart": route.get("autostart", False),
                "speech":    route.get("speech"),
                "payload":   route.get("payload")
            }

        # ===== .NET BACKEND ACTIONS =====
        if target == "dotnet":
            method = route.get("method", "GET").upper()
            path   = route["path"]

            if method == "POST":
                res = dotnet_client.post(
                    path,
                    auth_header=auth_header,
                    json=payload if isinstance(payload, dict) else None
                )
            else:
                res = dotnet_client.get(
                    path,
                    auth_header=auth_header,
                    params=payload if isinstance(payload, dict) else None
                )

            return {
                "action": route.get("action", "show_payload"),
                "speech": route.get("speech") or ("Done." if res.get("ok") else "I couldn't retrieve that."),
                "payload": {"source": "dotnet", **res}
            }

        # ===== RAG PIPELINE: .NET → retrieve KB → explain =====
        if target == "rag":
            src_path   = route.get("source_path")
            src_method = (route.get("source_method") or "GET").upper()

            if src_method == "POST":
                raw = dotnet_client.post(
                    src_path,
                    auth_header=auth_header,
                    json=payload if isinstance(payload, dict) else None
                )
            else:
                raw = dotnet_client.get(
                    src_path,
                    auth_header=auth_header,
                    params=payload if isinstance(payload, dict) else None
                )

            data_list = (raw.get("data") or []) if raw.get("ok") else []
            summary = explain_care_activities(data_list, lang=route.get("lang", "es"))

            return {
                "action": route.get("action", "show_summary"),
                "speech": route.get("speech") or ("Resumen listo." if raw.get("ok") else "No pude resumir."),
                "payload": {
                    "source": "dotnet+rag",
                    "raw_ok": raw.get("ok"),
                    "raw_status": raw.get("status"),
                    "summary": summary
                }
            }

        # ===== FALLBACK =====
        return {"action": "speak", "speech": "Unsupported route."}

agent_service = AgentService()
