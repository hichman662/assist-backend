# app/services/agent_service.py
from typing import Any, Dict, Optional

from app.services.intent_table import INTENT_ROUTES
#from app.services.dotnet_client import dotnet_client
#from app.services.python_ai_client import py_ai_client
#from app.services.rag_client import rag_client

class AgentService:
    """
    Reads intents and dispatches to the right target using INTENT_ROUTES.
    """
    def handle_intent(self, body: Dict[str, Any], auth_header: Optional[str]) -> Dict[str, Any]:
        intent  = (body.get("intent") or "").lower()
        text    = body.get("text")
        context = body.get("context") or {}

        route = INTENT_ROUTES.get(intent)

        if not route:
            return {"action": "speak", "speech": "I didn't understand that."}

        target = route["target"]

        # FRONTEND: just tell the UI what to do
        if target == "frontend":
            return {
                "action":    route["action"],
                "autostart": route.get("autostart", False),
                "speech":    route.get("speech")
            }
  
        # .NET BACKEND: future CarePlan or IoT actions
        #if target == "dotnet":
        #    data = dotnet_client.get(route["path"], auth_header)
         #   return {"action": "show_careplan", "payload": data, "speech": route.get("speech")}

        # PYTHON AI BACKEND
        #if target == "python_ai":
         #   res = py_ai_client.call(route["path"], body.get("payload"))
          #  return {"action": "speak", "speech": res.get("message", route.get("speech") or "Done.")}

        # RAG (QA/Summaries)
        #if target == "rag":
         #   ans = rag_client.query(route["path"], {"text": text, "context": context})
         #   return {"action": "speak", "speech": ans}

        return {"action": "speak", "speech": "Unsupported route."}


agent_service = AgentService()
