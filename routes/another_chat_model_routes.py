from flask_restx import Namespace, Resource, fields
from app.services.another_chat_model_service import generate_free_model_response

# Define Namespace
another_chat_model_ns = Namespace("another_chat_model", description="Free Chat Model API")

# Define Input and Output Models
model_input = another_chat_model_ns.model(
    "ChatModelInput",
    {"prompt": fields.String(required=True, description="Input text for the model")}
)

model_output = another_chat_model_ns.model(
    "ChatModelOutput",
    {"response": fields.String(description="Generated response from the model")}
)

# Define Resource
@another_chat_model_ns.route("/")
class ChatModelResource(Resource):
    @another_chat_model_ns.expect(model_input)
    @another_chat_model_ns.response(200, "Success", model_output)
    @another_chat_model_ns.response(500, "Internal Server Error")
    def post(self):
        """
        Generate a response using a free Hugging Face model.
        """
        try:
            data = another_chat_model_ns.payload
            prompt = data.get("prompt")
            response = generate_free_model_response(prompt)
            return {"response": response}, 200
        except Exception as e:
            print(f"Error in ChatModelResource: {e}")
            return {"message": "Error processing your request."}, 500
