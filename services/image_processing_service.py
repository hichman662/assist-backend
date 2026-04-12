from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import io
import gc

# Load the processor and model once
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-large",
    torch_dtype=torch.float32
).to("cpu")

model.eval()

print("Model loaded successfully!")

def process_image(image_file):
    """
    Process the uploaded image and generate a caption using BLIP.
    """
    try:
        # Open the image file
        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")

        # Reduce image size before inference
        image.thumbnail((640, 640))

        print(f"Image loaded: {image.size}")

        # Prepare inputs
        inputs = processor(images=image, return_tensors="pt").to("cpu")

        # Run inference
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                num_beams=3,
                do_sample=True,
                top_p=0.9,
                temperature=0.9
            )

        # Decode output
        description = processor.decode(outputs[0], skip_special_tokens=True).strip()
        print(f"Decoded description: {description}")

        if not description:
            description = "The model generated an incomplete description. Please try another image."

        # Release memory
        del inputs
        del outputs
        gc.collect()

        return {"description": description}, 200

    except Exception as e:
        print(f"Error in processing image: {e}")
        return {"error": "Failed to process the image. Please check the input or try again later."}, 500