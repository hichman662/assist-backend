import requests

class GeolocationService:
    @staticmethod
    def get_location_description(lat, lon):
        """
        Get a cleaned textual description of the location based on GPS coordinates.
        """
        try:
            # Use OpenStreetMap's Nominatim API
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {'User-Agent': 'GeolocationApp'}
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})

                # Clean and construct description
                description = GeolocationService.clean_address(address)
                return description or "Location details not available."
            else:
                return f"Error fetching location details: {response.status_code}"
        except Exception as e:
            return f"An error occurred: {e}"

    @staticmethod
    def clean_address(address):
        """
        Clean and format the address details to remove redundancy and keep it concise.
        """
        # Define the hierarchy of fields to include in the description
        fields = [
            'amenity', 'tourism', 'road', 'neighbourhood', 
            'suburb', 'town', 'city', 'province', 'state', 'country'
        ]

        # Create a cleaned description
        description_parts = []
        for field in fields:
            if field in address:
                value = address[field]
                # Avoid duplicates or redundancy (e.g., "X / X")
                if " / " in value:
                    value = value.split(" / ")[0]  # Take the first part of the duplicate
                description_parts.append(value)
        
        # Join parts into a concise description
        return ', '.join(description_parts)
