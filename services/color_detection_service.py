# app/services/color_detection_service.py

from PIL import Image
from sklearn.cluster import KMeans
import numpy as np
from app.data.color_names import CSS3_NAMES_TO_HEX, hex_to_rgb

class ColorRecognitionService:
    @staticmethod
    def closest_color(requested_color):
        """
        Find the closest color name for an RGB value.
        """
        min_colors = {}
        for hex_code, name in CSS3_NAMES_TO_HEX.items():
            try:
                r_c, g_c, b_c = hex_to_rgb(hex_code)
                rd = (r_c - requested_color[0]) ** 2
                gd = (g_c - requested_color[1]) ** 2
                bd = (b_c - requested_color[2]) ** 2
                min_colors[(rd + gd + bd)] = name
            except ValueError as e:
                print(f"Skipping invalid hex color {hex_code}: {name}. Error: {e}")
        if not min_colors:
            return "Unknown"
        return min_colors[min(min_colors.keys())]

    @staticmethod
    def extract_dominant_colors(image_path: str, num_colors: int = 5):
        """
        Extract dominant colors using K-Means clustering for improved results.

        Args:
            image_path (str): Path to the image file.
            num_colors (int): Number of dominant colors to return.

        Returns:
            list: List of dominant colors with their names and RGB values.
        """
        image = Image.open(image_path).convert("RGB")
        image = image.resize((200, 200))  # Resize for efficiency
        pixels = np.array(image).reshape((-1, 3))

        # Apply K-Means clustering
        kmeans = KMeans(n_clusters=num_colors, random_state=0).fit(pixels)
        centers = kmeans.cluster_centers_

        dominant_colors = []
        for center in centers:
            rgb = tuple(map(int, center))
            color_name = ColorRecognitionService.closest_color(rgb)
            dominant_colors.append({"name": color_name, "rgb": list(rgb)})

        return dominant_colors
