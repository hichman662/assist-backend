import cv2
import numpy as np
import base64  # Importing base64
from io import BytesIO
from PIL import Image
from app.data.color_names import CSS3_NAMES_TO_HEX, hex_to_rgb

def decode_image(base64_string):
    """
    Decode a base64-encoded image into an OpenCV image.
    """
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def extract_colors(image, num_colors=5):
    """
    Extract dominant colors from an image using k-means clustering.
    """
    try:
        # Resize the image for faster processing
        image = cv2.resize(image, (150, 150), interpolation=cv2.INTER_AREA)
        data = image.reshape((-1, 3))
        data = np.float32(data)

        # K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Map the colors to CSS names
        dominant_colors = []
        for center in centers:
            rgb = tuple(map(int, center))
            hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
            closest_color = min(CSS3_NAMES_TO_HEX.keys(), key=lambda c: np.linalg.norm(np.array(hex_to_rgb(CSS3_NAMES_TO_HEX[c])) - np.array(rgb)))
            dominant_colors.append({"rgb": rgb, "hex": hex_color, "name": closest_color})
        return dominant_colors
    except Exception as e:
        print(f"Error extracting dominant colors: {e}")
        return []
