# app/data/color_names.py

def hex_to_rgb(hex_color):
    """
    Convert a hexadecimal color string to an RGB tuple.
    """
    try:
        if not (hex_color.startswith("#") and len(hex_color) == 7):
            raise ValueError(f"Invalid hex color format: {hex_color}")
        return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    except Exception as e:
        raise ValueError(f"Invalid hex color: {hex_color}. Error: {e}")

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
    # Add more valid colors as needed
}
