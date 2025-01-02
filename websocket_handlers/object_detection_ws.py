from flask_socketio import emit
from app.services.object_detection_service import ObjectDetectionService

def handle_object_detection(data):
    try:
        image_base64 = data.get("image")
        if not image_base64:
            emit("detection_result", {"error": "No image data provided."})
            return

        # Call the object detection service
        result = ObjectDetectionService.detect_objects(image_base64)
        emit("detection_result", result)  # Emit the result as it is
    except Exception as e:
        emit("detection_result", {"error": str(e)})
