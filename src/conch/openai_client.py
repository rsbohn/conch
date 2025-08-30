"""
openai_client.py: Simple interface for OpenAI Chat Completions (oneshot prompt).

Note: We use httpx directly to avoid requiring the openai SDK. This module
is only used when explicitly selected; tests should not hit the network.
"""

from __future__ import annotations

import os
import asyncio
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
        # GPT-5 models use a different parameter name for completion tokens.
        # Use 'max_completion_tokens' for gpt-5* models, and 'max_tokens' for others.
        uses_gpt5_param = str(model).lower().startswith("gpt-5")
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if uses_gpt5_param:
            data["max_completion_tokens"] = max_tokens
        else:
            data["max_tokens"] = max_tokens
        # Simple retry with backoff for transient errors (e.g., 429/503)
        attempt = 0
        last_err: Optional[Exception] = None
        async with httpx.AsyncClient(timeout=30) as client:
            while attempt < 3:
                try:
                    resp = await client.post(OPENAI_API_URL, json=data, headers=headers)
                    resp.raise_for_status()
                    result = resp.json()
                    break
                except httpx.HTTPStatusError as e:
                    last_err = e
                    status = e.response.status_code if e.response is not None else None
                    if status in (429, 503):
                        # Honor Retry-After if present; otherwise exponential backoff
                        retry_after = 0.0
                        try:
                            ra = (
                                e.response.headers.get("Retry-After")
                                if e.response
                                else None
                            )
                            if ra:
                                retry_after = float(ra)
                        except Exception:
                            retry_after = 0.0
                        if retry_after <= 0:
                            retry_after = 1.0 * (2**attempt)
                        await asyncio.sleep(retry_after)
                        attempt += 1
                        continue
                    # Non-retryable status
                    raise
                except httpx.RequestError as e:
                    # Network/transient; retry briefly
                    last_err = e
                    await asyncio.sleep(1.0 * (2**attempt))
                    attempt += 1
                    continue
            else:
                # exhausted retries
                if last_err:
                    raise last_err
                raise RuntimeError("OpenAI request failed without response")
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return None
