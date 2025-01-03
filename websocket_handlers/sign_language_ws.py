from flask_socketio import emit
from app.services.sign_language_service import SignLanguageService

def handle_sign_language(data):
    """
    WebSocket handler for processing sign language frames.
    Args:
        data (dict): Data received from the client, including the video frame in base64 format.
    """
    try:
        image_base64 = data.get("image")
        if not image_base64:
            emit("translation_result", {"error": "No image data provided."})
            return

        # Process the frame to translate sign language
        translation = SignLanguageService.translate(image_base64)
        emit("translation_result", {"translation": translation})
    except Exception as e:
        emit("translation_result", {"error": str(e)})
