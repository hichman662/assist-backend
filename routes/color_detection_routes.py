from flask_restx import Namespace, Resource
from flask import request
from app.services.color_detection_service import ColorRecognitionService
import os
import uuid

# Initialize namespace
color_detection_ns = Namespace("color_detection", description="API for Color Detection")
color_service = ColorRecognitionService()

UPLOAD_DIR = "uploads"  # Directory to save uploaded images
os.makedirs(UPLOAD_DIR, exist_ok=True)

@color_detection_ns.route("/")
class ColorDetection(Resource):
    def post(self):
        """
        Upload an image and get the dominant colors with names and RGB values.
        """
        try:
            # Retrieve the image file from the request
            image_file = request.files.get("image")
            if not image_file:
                return {"error": "No image file provided"}, 400

            # Save the image temporarily
            file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{image_file.filename}")
            with open(file_path, "wb") as f:
                f.write(image_file.read())

            # Extract dominant colors
            num_colors = int(request.form.get("num_colors", 5))
            dominant_colors = color_service.extract_dominant_colors(file_path, num_colors)

            # Clean up the uploaded file
            os.remove(file_path)

            return {"dominant_colors": dominant_colors}, 200

        except Exception as e:
            print(f"Error in processing image: {e}")
            return {"error": "Failed to process the image. Please try again later."}, 500
