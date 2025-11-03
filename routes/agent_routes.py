from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.agent_service import agent_service

agent_ns = Namespace("agent", description="AgentBot API")

IntentReq = agent_ns.model("IntentRequest", {
    "intent": fields.String(required=False, example="start_detection"),
    "text": fields.String(required=False),
    "context": fields.Raw(required=False),
})

AgentResp = agent_ns.model("AgentResponse", {
    "action": fields.String(required=True, example="open_object_detection"),
    "autostart": fields.Boolean(required=False, example=True),
    "payload": fields.Raw(required=False),
    "speech": fields.String(required=False, example="Starting object detection.")
})

@agent_ns.route("/intent")
class AgentIntent(Resource):
    @agent_ns.expect(IntentReq)
    @agent_ns.marshal_with(AgentResp)
    def post(self):
        body = request.get_json(silent=True) or {}
        auth = request.headers.get("Authorization")
        return agent_service.handle_intent(body, auth), 200
