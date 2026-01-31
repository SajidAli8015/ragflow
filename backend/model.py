# backend/model.py

import os
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.config import MODEL_NAME


def get_chat_model():
    """
    Initialize and return the Gemini chat model.

    This is the ONLY place in the backend that:
    - reads environment variables
    - knows about the specific LLM provider

    Everything else receives the model as a dependency.
    """
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
