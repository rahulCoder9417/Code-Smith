from openai import OpenAI

from app.config.providers import PROVIDER_CONFIG
from app.config.settings import LLM_API_KEY, LLM_MODEL, LLM_PROVIDER

class ChatClient:
    def __init__(self):
        if LLM_PROVIDER not in PROVIDER_CONFIG:
            raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
        
        self.client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=PROVIDER_CONFIG[LLM_PROVIDER]["base_url"]
        )
        
    def generate_response(self, prompt:str) -> str:
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content