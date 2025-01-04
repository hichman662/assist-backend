import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image


CSS3_NAMES_TO_HEX = {
    "white": "#FFFFFF",
    "black": "#000000",
    "red": "#FF0000",
    "lime": "#00FF00",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "silver": "#C0C0C0",
    "gray": "#808080",
    "maroon": "#800000",
    "olive": "#808000",
    "green": "#008000",
    "purple": "#800080",
    "teal": "#008080",
    "navy": "#000080",
    "orange": "#FFA500",
    "pink": "#FFC0CB",
    "gold": "#FFD700",
    "brown": "#A52A2A",
    "chocolate": "#D2691E",
    "coral": "#FF7F50",
    "crimson": "#DC143C",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9",
    "darkgreen": "#006400",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00",
    "darkorchid": "#9932CC",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deepskyblue": "#00BFFF",
    "dimgray": "#696969",
    "dodgerblue": "#1E90FF",
    "firebrick": "#B22222",
    "forestgreen": "#228B22",
    "fuchsia": "#FF00FF",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "goldenrod": "#DAA520",
    "greenyellow": "#ADFF2F",
    "honeydew": "#F0FFF0",
    "hotpink": "#FF69B4",
    "indianred": "#CD5C5C",
    "indigo": "#4B0082",
    "ivory": "#FFFFF0",
    "khaki": "#F0E68C",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lightblue": "#ADD8E6",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "oldlace": "#FDF5E6",
    "olivedrab": "#6B8E23",
    "orangered": "#FF4500",
    "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "plum": "#DDA0DD",
    "powderblue": "#B0E0E6",
    "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seashell": "#FFF5EE",
    "sienna": "#A0522D",
    "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD",
    "slategray": "#708090",
    "snow": "#FFFAFA",
    "springgreen": "#00FF7F",
    "steelblue": "#4682B4",
    "tan": "#D2B48C",
    "thistle": "#D8BFD8",
    "tomato": "#FF6347",
    "turquoise": "#40E0D0",
    "violet": "#EE82EE",
    "wheat": "#F5DEB3",
    "whitesmoke": "#F5F5F5",
    "yellowgreen": "#9ACD32",
}

def hex_to_rgb(hex_color):
    """
    Convert a hexadecimal color string to an RGB tuple.
    """
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


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
        used_names = set()

        for center in centers:
            rgb = tuple(map(int, center))
            hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)

            # Find the closest CSS color name
            closest_color = min(
                CSS3_NAMES_TO_HEX.keys(),
                key=lambda c: np.linalg.norm(np.array(hex_to_rgb(CSS3_NAMES_TO_HEX[c])) - np.array(rgb))
            )

            # Avoid duplicate names
            if closest_color in used_names:
                closest_color += " (Variant)"
            used_names.add(closest_color)

            dominant_colors.append({"rgb": rgb, "hex": hex_color, "name": closest_color})

        return dominant_colors
    except Exception as e:
        print(f"Error extracting dominant colors: {e}")
        return []
