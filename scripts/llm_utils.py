import os

from google import genai
from google.genai import types


def _build_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not found")
    return genai.Client(api_key=api_key)


def generate_response(prompt: str, model: str = "gemini-2.5-flash-preview-05-20"):
    client = _build_client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.9),
    )
    return response.text
