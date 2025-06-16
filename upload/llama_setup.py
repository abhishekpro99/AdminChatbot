# upload/llama_setup.py

import os
from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini

# Load environment variables
load_dotenv()

# Function to return Gemini LLM client only when needed
def get_llm():
    return Gemini(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/gemini-1.5-pro-latest"  # Use valid model name for API v1
    )
