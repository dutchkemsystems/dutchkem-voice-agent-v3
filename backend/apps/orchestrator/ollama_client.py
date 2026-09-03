import httpx
from typing import AsyncGenerator, Dict, Optional

class OllamaClient:
    """Client for local Ollama LLM server."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=120.0)
    
    async def generate(
        self,
        model: str = "llama3.1:8b",
        prompt: str = "",
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a response from the LLM."""
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }
        
        response = await self.client.post("/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["response"]
    
    async def generate_stream(
        self,
        model: str = "llama3.1:8b",
        prompt: str = "",
        system: str = "",
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from the LLM."""
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": True,
        }
        
        async with self.client.stream("POST", "/api/generate", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
    
    async def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> list:
        """List available models."""
        response = await self.client.get("/api/tags")
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])]
