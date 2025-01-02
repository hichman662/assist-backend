from flask_socketio import emit
from flask import Blueprint
from app.services.object_detection_service import ObjectDetectionService

object_detection_routes = Blueprint("object_detection_routes", __name__)

@object_detection_routes.route("/object-detection", methods=["GET"])
def test():
    return {"message": "Object Detection WebSocket is live!"}, 200

def handle_object_detection(data):
    """
    WebSocket handler for processing frames.
    """
    try:
        encoded_frame = data.get("frame")
        if not encoded_frame:
            emit("error", {"error": "Frame data is missing"})
            return

        # Perform object detection
        detections = ObjectDetectionService.detect_objects(encoded_frame)

        # Emit results back to the frontend
        emit("detection_results", {"detections": detections})

    except Exception as e:
        emit("error", {"error": str(e)})
