from flask_restx import Namespace, Resource, fields
from app.services.rag_index import rag_index

rag_ns = Namespace("rag", description="RAG utilities")

RebuildReq = rag_ns.model("RebuildReq", {
    "folder": fields.String(required=False, example="./knowledge_base")
})

@rag_ns.route("/rebuild")
class RagRebuild(Resource):
    @rag_ns.expect(RebuildReq)
    def post(self):
        body = rag_ns.payload or {}
        folder = body.get("folder") or "./knowledge_base"
        rag_index.rebuild_from_folder(folder)
        return {"ok": True, "folder": folder}, 200
