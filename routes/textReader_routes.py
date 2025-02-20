from flask import request
from flask_restx import Namespace, Resource
from app.services.textReader_service import process_text_image

# Create a namespace for text reader
text_reader_ns = Namespace("text_reader", description="API for Text Reader")

@text_reader_ns.route("/")
class TextReader(Resource):
    def post(self):
        """
        Handle image upload and send it to the OCR processing service.
        """
        try:
            # Retrieve the image file from the request
            image_file = request.files.get("image")
            if not image_file:
                return {"status": "error", "message": "No image file provided"}, 400

            print(f"Received file: {image_file.filename}, Content-Type: {image_file.content_type}")

            # Call the service and unpack the response
            response, status_code = process_text_image(image_file)
            return response, status_code

        except Exception as e:
            print(f"Error occurred in text reader API: {e}")
            return {"status": "error", "message": "An unexpected error occurred"}, 500
