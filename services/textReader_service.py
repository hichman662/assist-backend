import os
import uuid
import io
import cv2
import numpy as np
import traceback
from PIL import Image
import pytesseract
from collections import defaultdict

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def upscale_image(image, scale=2):
    """Upscale image to improve OCR accuracy."""
    width, height = image.size
    return image.resize((width * scale, height * scale), Image.LANCZOS)

def preprocess_image_for_ocr(image):
    """Convert to grayscale, blur, and apply adaptive thresholding."""
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 31, 15
    )
    kernel = np.ones((1, 1), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    final = cv2.bitwise_not(closed)
    return final

def process_text_image(image_file, ocr_type='ocr'):
    try:
        temp_dir = os.path.join(os.getcwd(), "temp_images")
        os.makedirs(temp_dir, exist_ok=True)

        temp_filename = f"{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(temp_dir, temp_filename)

        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
        image = upscale_image(image, scale=2)
        image.save(temp_path)

        processed_img = preprocess_image_for_ocr(image)

        data = pytesseract.image_to_data(
            processed_img,
            lang='eng',
            output_type=pytesseract.Output.DICT
        )

        lines = defaultdict(list)

        for i in range(len(data['text'])):
            text = data['text'][i].strip()

            try:
                conf = float(data['conf'][i])
            except:
                conf = -1

            if conf > 60 and text:
                line_no = data['line_num'][i]
                lines[line_no].append(text)

        text_result = '\n'.join([' '.join(words) for _, words in sorted(lines.items())])

        os.remove(temp_path)

        if not text_result.strip():
            return {"error": "OCR returned no confident text."}, 400

        print("Final OCR Result:", text_result)
        return {"text": text_result.strip()}, 200

    except Exception as e:
        traceback.print_exc()
        return {"error": f"Error during OCR processing: {str(e)}"}, 500