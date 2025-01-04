from flask_restx import Namespace, Resource
from flask import request
import base64  # Importing base64 module
from app.services.color_detection_service import decode_image, extract_colors

# Initialize namespace
color_detection_ns = Namespace("color-detection", description="API for Color Detection")

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

            # Decode the image
            image_data = image_file.read()
            image = decode_image(base64.b64encode(image_data).decode("utf-8"))
            if image is None:
                return {"error": "Failed to decode the image"}, 400

            # Extract dominant colors
            num_colors = int(request.form.get("num_colors", 5))
            dominant_colors = extract_colors(image, num_colors)

            # Return colors with names and RGB values
            return {"colors": dominant_colors}, 200

        except Exception as e:
            print(f"Error in processing image: {e}")
            return {"error": "Failed to process the image. Please try again later."}, 500
