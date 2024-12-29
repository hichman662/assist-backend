import logging
from paddleocr import PaddleOCR
from PIL import Image, ImageEnhance, ImageFilter
import io
import os

# Suppress PaddleOCR debug logs
logging.getLogger("ppocr").setLevel(logging.WARNING)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Add 'ch' for Chinese or other languages if needed
print("PaddleOCR Handwriting OCR model loaded successfully!")

def preprocess_image(image):
    """
    Enhance the image for better OCR results.
    
    Args:
        image (PIL.Image.Image): The input image.

    Returns:
        PIL.Image.Image: The enhanced image.
    """
    image = image.convert("L")  # Convert to grayscale
    image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
    enhancer = ImageEnhance.Contrast(image)  # Enhance contrast
    image = enhancer.enhance(2.0)
    return image.convert("RGB")  # Convert back to RGB

def process_text_image(image_file):
    """
    Process the uploaded image and extract handwritten text using PaddleOCR.

    Args:
        image_file: The uploaded image file.
    
    Returns:
        tuple: A response dictionary and an HTTP status code.
    """
    try:
        # Open the image file
        image = Image.open(io.BytesIO(image_file.read()))
        print(f"Original Image size: {image.size}")

        # Preprocess the image
        image = preprocess_image(image)
        print(f"Preprocessed Image size: {image.size}")

        # Save the processed image temporarily (PaddleOCR works on file paths)
        temp_image_path = "temp_processed_image.jpg"
        image.save(temp_image_path)

        # Perform OCR on the image
        results = ocr.ocr(temp_image_path, cls=True)
        os.remove(temp_image_path)  # Clean up the temporary file after processing

        # Extract text from OCR results
        text = " ".join([line[1][0] for line in results[0]])
        print(f"OCR Result: {text}")

        # Validate the OCR result
        if not text.strip():
            return {"error": "OCR did not return any text. Ensure the handwriting is legible."}, 400

        return {"text": text.strip()}, 200

    except Exception as e:
        print(f"Error in processing OCR: {e}")
        return {"error": "Failed to process the image. Please try again later."}, 500
