from flask_restx import Namespace, Resource
from app.services.text_service import get_text

# Create a namespace for the text API
text_ns = Namespace("text", description="Text Retrieval API")

@text_ns.route("/")
class Text(Resource):
    def get(self):
        """Retrieve a simple text message"""
        return {"message": get_text()}