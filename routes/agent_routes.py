# app/routes/agent_routes.py
from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.agent_service import agent_service

agent_ns = Namespace("agent", description="AgentBot API")

# ---- OpenAPI input schema (informational; not used to marshal the response) ----
IntentReq = agent_ns.model(
    "IntentRequest",
    {
        "intent":  fields.String(
            required=False,
            example="get_care_activities_explained",
            description="Intent name from frontend (see intent_table.py).",
        ),
        "text":    fields.String(required=False, description="Free text (optional)."),
        "context": fields.Raw(required=False, description="Any context dict (optional)."),
        # For .NET / RAG calls we pass query/body params here (e.g., idscenario)
        "payload": fields.Raw(
            required=False,
            example={"idscenario": 720896},
            description="Intent parameters (forwarded as query/body to backends).",
        ),
    },
)

@agent_ns.route("/intent", methods=["POST", "OPTIONS"])
class AgentIntent(Resource):
    def options(self):
        """
        CORS preflight handler. Flask-CORS will add the headers.
        We just need to return 200 so the browser can proceed with POST.
        """
        return {"ok": True}, 200

    @agent_ns.expect(IntentReq)
    def post(self):
        """
        Single entry point for all Agent intents.
        Returns a raw dict (no marshal) so dynamic payloads (RAG summaries, etc.)
        don't break due to schema constraints.
        """
        body = request.get_json(silent=True) or {}
        auth = request.headers.get("Authorization")  # passed to .NET when present

        try:
            resp = agent_service.handle_intent(body, auth)
            # resp is a dict like:
            # { action: "...", autostart?: bool, speech?: str, payload?: any }
            return resp, 200
        except Exception as e:
            # Log for server debugging
            import traceback
            traceback.print_exc()
            # Return a safe error envelope that FE can 'speak' if needed
            return {
                "action": "speak",
                "speech": "Server error al procesar la intención.",
                "payload": {"error": str(e)},
            }, 500
