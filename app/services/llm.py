import requests

from app.core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


class OllamaClient:

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
    ) -> str:

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]