import os
from dotenv import load_dotenv

load_dotenv()

# Whisper model
WHISPER_MODEL_ID = "ivrit-ai/whisper-large-v3"

# LLM provider: "gemini" | "claude" | "ollama"
LLM_PROVIDER = "gemini"

# API keys (loaded from .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Ollama settings (only used if LLM_PROVIDER = "ollama")
OLLAMA_MODEL = "llama3"
