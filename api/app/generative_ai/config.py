# app/generative_ai/config.py
import os
import google.generativeai as genai
import logging
# Configure the Generative AI API key
genai.configure(api_key="AIzaSyA6PanoKCq945enwgph8CU8tt0fqIm3X8Q")

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the Generative AI model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

#extra
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)