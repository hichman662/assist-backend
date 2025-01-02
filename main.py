import multiprocessing
multiprocessing.set_start_method("spawn", force=True)
import sys
import os
from flask_socketio import SocketIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, api
from app.routes.chatbot_routes import chatbot_ns
#from app.routes.object_routes import object_ns
#from app.routes.text_routes import text_ns  # Import the new namespace
#from app.routes.image_test_routes import image_ns  # Import the unique namespace
from app.routes.image_processing_routes import image_processing_ns  # Import the unique namespace
from app.routes.textReader_routes import text_reader_ns
from app.routes.another_chat_model_routes import another_chat_model_ns
from app.routes.another_image_processing_routes import another_image_processing_ns
from app.routes.color_detection_routes import color_detection_ns
from app.routes.geolocation_routes import geolocation_ns
#from app.routes.object_detection_routes import object_detection_ns

# Import WebSocket handlers
from app.websocket_handlers.object_detection_ws import handle_object_detection

# Create Flask app
app = create_app()

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Register namespaces
api.add_namespace(chatbot_ns, path="/api/v1/chatbot")
#api.add_namespace(object_ns, path="/api/v1/object-detection")
#api.add_namespace(text_ns, path="/api/v1/text")  # Register the new text namespace
#api.add_namespace(image_ns, path="/api/v1/image_test")  # Add new image namespace
api.add_namespace(image_processing_ns, path="/api/v1/image_processing")
api.add_namespace(text_reader_ns, path="/api/v1/text_reader")
api.add_namespace(another_chat_model_ns, path="/api/v1/another_chat_model")
api.add_namespace(another_image_processing_ns, path="/api/v1/another_image_processing")
api.add_namespace(color_detection_ns, path="/api/v1/color-detection")
api.add_namespace(geolocation_ns, path="/api/v1/geolocation")
#api.add_namespace(object_detection_ns, path="/api/v1/object-detection")

# WebSocket handler registration
socketio.on_event("object_detection", handle_object_detection)

if __name__ == "__main__":
    
          
    # Register namespaces
    print("Starting the MoSIoT accessibility app...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)