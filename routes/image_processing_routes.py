from flask import request
from flask_restx import Namespace, Resource
from app.services.image_processing_service import process_image

# Create a namespace for image processing
image_processing_ns = Namespace("image_processing", description="API for Image Processing")  # Use a unique name

@image_processing_ns.route("/")
class ImageProcessing(Resource):
    def post(self):
        """Handle image upload and send it to the processing service."""
        try:
            # Retrieve the image file from the request
            image_file = request.files.get("image")
            if not image_file:
                return {"error": "No image file provided"}, 400

            # Call the service and unpack the response
            response, status_code = process_image(image_file)
            return response, status_code
        except Exception as e:
            print(f"Error occurred: {e}")
            return {"error": "An unexpected error occurred"}, 500
