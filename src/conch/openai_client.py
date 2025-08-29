"""
openai_client.py: Simple interface for OpenAI Chat Completions (oneshot prompt).

Note: We use httpx directly to avoid requiring the openai SDK. This module
is only used when explicitly selected; tests should not hit the network.
"""

from __future__ import annotations

import os
from typing import Optional
import httpx

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def get_openai_key() -> Optional[str]:
    # Prefer the standard env var; allow fallback to a generic keyfile if set
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key.strip()
    keyfile = os.environ.get("openai_keyfile") or os.environ.get("keyfile")
    if keyfile and os.path.exists(keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_openai_key()

    async def oneshot(
        self, prompt: str, model: str = DEFAULT_OPENAI_MODEL, max_tokens: int = 512
    ) -> Optional[str]:
        """
        Send a single prompt to OpenAI and return the response (async).
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not found.")
        headers = {
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
        }
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(OPENAI_API_URL, json=data, headers=headers)
            resp.raise_for_status()
            result = resp.json()
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return None
