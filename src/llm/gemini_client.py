from google import genai
from src.config import GEMINI_API_KEY


class GeminiClient:
    def __init__(self, model: str = "gemini-2.5-flash"):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text