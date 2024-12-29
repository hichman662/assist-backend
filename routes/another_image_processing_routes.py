from flask import request
from flask_restx import Namespace, Resource
from app.services.another_image_processing_service import process_image

# Define Namespace for image processing
another_image_processing_ns = Namespace(
    "another_image_processing", description="API for Image Captioning"
)

@another_image_processing_ns.route("/")
class AnotherImageProcessing(Resource):
    def post(self):
        """
        Handle image upload and send it to the image processing service.
        """
        try:
            # Retrieve the image file from the request
            image_file = request.files.get("image")
            if not image_file:
                return {"error": "No image file provided"}, 400

            # Process the image and get the response
            response, status_code = process_image(image_file)
            return response, status_code
        except Exception as e:
            print(f"Error in AnotherImageProcessing: {e}")
            return {"error": "An unexpected error occurred while processing the image."}, 500
