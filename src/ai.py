"""AI Service"""
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, PROMPT_ENHANCEMENT


class AIService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env.local")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def generate(self, prompt):
        try:
            enhanced = prompt + PROMPT_ENHANCEMENT
            return self.model.generate_content(enhanced).text
        except Exception as e:
            print(f"Error: {e}")
            return None
