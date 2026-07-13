import os

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

if not LLM_PROVIDER:
    raise ValueError("LLM_PROVIDER is missing.")

if not LLM_MODEL:
    raise ValueError("LLM_MODEL is missing.")

if not LLM_API_KEY:
    raise ValueError("LLM_API_KEY is missing.")