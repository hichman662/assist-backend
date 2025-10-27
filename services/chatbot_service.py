from transformers import AutoModelForCausalLM, AutoTokenizer
import re

# Use a smaller and more efficient model: "distilgpt2"
MODEL_NAME = "distilgpt2"

print("Loading model...")
try:
    # Load tokenizer and add padding token
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})

    # Load model and resize token embeddings for the added token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype="auto"  # Automatically choose the best dtype
    )
    model.resize_token_embeddings(len(tokenizer))
    
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    raise


def generate_chat_response(prompt, max_length=150):
    """
    Generate a chatbot response to a given prompt.

    Args:
        prompt (str): User input to the chatbot.
        max_length (int): Maximum length of the response.

    Returns:
        dict: Response text.
    """
    try:
        # Encode the input prompt without adding extra context
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)

        # Generate a response
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,  # Limit response length
            no_repeat_ngram_size=3,  # Prevent repetitive phrases
            top_p=1.9,  # Diverse response
            temperature=2.0,  # Balanced creativity and coherence
            early_stopping=True,
            pad_token_id=tokenizer.pad_token_id,  # Use the defined padding token
        )

        # Decode the response
        raw_response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        # Remove any part of the prompt echoed in the response
        clean_response = raw_response[len(prompt):].strip() if raw_response.startswith(prompt) else raw_response

        # Truncate the response to ensure brevity
        if len(clean_response.split()) > 100:  # Arbitrary word limit
            clean_response = " ".join(clean_response.split()[:100]) + "..."

        return {"response": clean_response}, 200
    except Exception as e:
        print(f"Error generating response: {e}")
        return {"error": "Failed to generate a response. Please try again later."}, 500

