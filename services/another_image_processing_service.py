import requests
from PIL import Image
from io import BytesIO
import base64

# Hugging Face API Configuration
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
HEADERS = {"Authorization": "Bearer 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"}  # Replace with your valid token

def process_image(image_file):
    """
    Process the uploaded image and generate a caption using Hugging Face API.

    Args:
        image_file: The uploaded image file.

    Returns:
        A tuple containing the response dictionary and the HTTP status code.
    """
    try:
        # Open the image and convert to RGB
        image = Image.open(image_file).convert("RGB")
        print(f"Image successfully loaded: {image.size}")

        # Convert image to binary format and encode as base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Create payload with base64 image data
        payload = {
            "inputs": image_base64
        }

        # Send the request to Hugging Face API
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload
        )

        # Handle API response
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                description = result[0].get("generated_text", "No description available.")
                return {"description": description}, 200
            else:
                return {"error": "Unexpected response format from API."}, 500
        else:
            print(f"Error querying Hugging Face API: {response.status_code} {response.text}")
            return {"error": f"Hugging Face API error: {response.text}"}, response.status_code

    except Exception as e:
        print(f"Error in processing image: {e}")
        return {"error": "Failed to process the image. Please check the input or try again later."}, 500
