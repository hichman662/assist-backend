import requests

# Hugging Face API Configuration
API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"  # Replace with your chosen free model
API_TOKEN = "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"  # Your provided token
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def generate_free_model_response(prompt, max_new_tokens=150, temperature=0.7):
    """
    Query the Hugging Face Inference API for a free model response.
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 50,
        },
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        # Extract only the generated text
        return response.json()[0]["generated_text"].replace(prompt, "").strip()
    else:
        raise Exception(f"Error querying Hugging Face API: {response.status_code} {response.text}")
