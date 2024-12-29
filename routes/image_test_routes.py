from flask import request
from flask_restx import Namespace, Resource
from app.services.image_test_service import handle_image_upload  # Import the service

# Create a namespace for image testing
image_ns = Namespace("image_test", description="Image Test API")

@image_ns.route("/")
class ImageTest(Resource):
    def post(self):
        """Handle image upload and delegate to the service"""
        try:
            # Retrieve the image file from the request
            image_file = request.files.get("image")
            print("Received file:", image_file)

            # Call the service and unpack the response and status code
            response, status_code = handle_image_upload(image_file)
            print("Service response:", response)
            print("Service status code:", status_code)

            # Directly return the response and status code
            return response, status_code
        except Exception as e:
            # Log the error and return a generic error response
            print(f"Error occurred: {e}")
            return {"error": "An unexpected error occurred"}, 500
