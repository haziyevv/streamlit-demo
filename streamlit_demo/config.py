import os

OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
SERPER_API_URL = os.getenv("SERPER_API_URL", "https://google.serper.dev/search")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")