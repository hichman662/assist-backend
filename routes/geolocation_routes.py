from flask_restx import Namespace, Resource
from flask import request
from app.services.geolocation_service import GeolocationService

geolocation_ns = Namespace("geolocation", description="Geolocation API")

@geolocation_ns.route("/")
class GeolocationResource(Resource):
    def post(self):
        """
        Get textual feedback for a location.
        """
        try:
            data = request.json
            lat = data.get('lat')
            lon = data.get('lon')

            if lat is None or lon is None:
                return {"error": "Latitude and longitude are required."}, 400

            description = GeolocationService.get_location_description(lat, lon)
            return {"description": description}, 200
        except Exception as e:
            return {"error": str(e)}, 500
