from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import io

# Load the processor and model once
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large", torch_dtype=torch.float32).to("cpu")

print("Model loaded successfully!")

def process_image(image_file):
    """
    Process the uploaded image and generate a long, detailed caption using BLIP.

    Args:
        image_file: The uploaded image file.
    
    Returns:
        A tuple containing the response dictionary and the HTTP status code.
    """
    try:
        # Open the image file
        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
        print(f"Image loaded: {image.size}")

        # Prepare inputs for the model without a prompt
        inputs = processor(images=image, return_tensors="pt").to("cpu")

        # Generate output with optimized parameters for balanced performance
        outputs = model.generate(
            **inputs,
            max_length=150,  # Limit caption length to improve response time
            num_beams=4,     # Reduce beams to speed up generation
            repetition_penalty=1.1,  # Avoid repetition
            length_penalty=2.0,      # Encourage moderately longer captions
            do_sample=True,          # Allow for sampling diversity
            top_p=0.85,               # Diversity threshold
            temperature=0.5          # Randomness in word selection
        )
        print(f"Raw model output tensor: {outputs}")

        # Decode the output
        description = processor.decode(outputs[0], skip_special_tokens=True).strip()
        print(f"Decoded description: {description}")

        # Validate the description
        if not description:
            description = "The model generated an incomplete or meaningless description. Please try with another image."

        return {"description": description}, 200

    except Exception as e:
        print(f"Error in processing image: {e}")
        return {"error": "Failed to process the image. Please check the input or try again later."}, 500
