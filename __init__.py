from flask import Flask
from flask_cors import CORS
from flask_restx import Api

# Initialize Flask-RESTX API
api = Api(
    title="MoSIoT API",
    version="1.0",
    description="API for MoSIoT functionalities",
)

def create_app():
    """Application factory function to create and configure the Flask app"""
    app = Flask(__name__)  # Initialize the Flask app
    CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)
    api.init_app(app)  # Attach the API to the app
    return app