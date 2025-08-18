"""
anthropic.py: Simple interface for Anthropic Claude API (oneshot prompt).
"""

import httpx
from typing import Optional
from .config import get_anthropic_key

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-3-haiku-20240307"


class AnthropicClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_anthropic_key()

    async def oneshot(
        self, prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 512
    ) -> Optional[str]:
        """
        Send a single prompt to Claude and return the response (async).
        """
        if not self.api_key:
            raise ValueError("Anthropic API key not found.")
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(API_URL, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
        # Claude's response is in result['content'][0]['text'] for this API
        try:
            return result["content"][0]["text"]
        except (KeyError, IndexError):
            return None
