import base64
import numpy as np
import cv2
from ultralytics import YOLO

class ObjectDetectionService:
    model_path = "models/yolo11n.pt"  # Path to YOLO model
    model = YOLO(model_path)  # Load the YOLO model

    @staticmethod
    def detect_objects(encoded_frame):
        """
        Perform object detection on a base64-encoded image.
        Args:
            encoded_frame (str): Base64-encoded image frame.
        Returns:
            dict: Detected objects with labels, confidences, and bounding boxes.
        """
        try:
            # Decode the base64 image
            frame_data = base64.b64decode(encoded_frame)
            nparr = np.frombuffer(frame_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Perform object detection
            results = ObjectDetectionService.model(img)

            # Define a constant for the reference object size (in pixels)
            reference_width = 100  # Example width in pixels
            reference_distance = 1.0  # Example distance in meters

            detections = []
            for result in results[0].boxes.data.tolist():
                x1, y1, x2, y2, conf, class_id = result
                width = x2 - x1

                # Estimate distance
                distance = (reference_width / width) * reference_distance

                detections.append({
                    "label": ObjectDetectionService.model.names[int(class_id)],
                    "confidence": conf,  # Confidence as float
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "distance": distance  # Include the calculated distance
                })

            # Return the response as a dictionary
            return {"detections": detections}

        except Exception as e:
            return {"error": str(e)}
