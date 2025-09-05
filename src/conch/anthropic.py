"""
anthropic.py: Simple interface for Anthropic Claude API (oneshot prompt).
"""

from typing import Optional, Dict, Any
import httpx
import anthropic
from .config import get_anthropic_key

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-3-5-haiku-20241022"


class AnthropicClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_anthropic_key()
        self.model = DEFAULT_MODEL
        self.max_tokens = 512
        self.tools = []
        self.tool_router = None
        self.last_stop_reason = None
        self.system = "You are a helpful assistant."

    async def oneshot(
        self, prompt: str, model: str = None, max_tokens: int = None
    ) -> Optional[str]:
        """
        Send a single prompt to Claude and return the response (async).
        """
        
        if not self.api_key:
            raise ValueError("Anthropic API key not found.")
        if not model:
            model = self.model
        if not max_tokens:
            max_tokens = self.max_tokens
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
        
    def _handle_tool_use(self, content: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Handle tool use requests from Claude.
        """
        tool_responses = []
        for item in content:
            if item.get("type") == "tool_use":
                tool_name = item.get("name")
                tool_input = item.get("input", {})
                if self.tool_router:
                    tool_output = self.tool_router.route(tool_name, **tool_input)
                else:
                    tool_output = f"Executed tool '{tool_name}' with input {tool_input}"
                tool_responses.append({
                    "type": "tool_result",
                    "tool_use_id": item.get("id"),
                    "content": tool_output
                })
        return tool_responses

    async def tool_use_turn(self, messages: list) -> tuple[str, list[Dict[str, Any]]]:
        client = anthropic.Anthropic()

        response = client.messages.create(
            model = self.model,
            max_tokens = self.max_tokens,
            system = self.system,
            tools = self.tools,
            messages = messages
        )
        response = response.model_dump()
        if "error" in response:
            raise Exception(response["error"])
        messages.append({"role": "assistant", "content": response["content"]})

        if "stop_reason" in response:
            self.last_stop_reason = response["stop_reason"]
            if response["stop_reason"] == "tool_use":
                tool_response = self._handle_tool_use(response["content"])
                messages.append(
                    {"role": "user", "content": tool_response}
                )
        else:
            self.last_stop_reason = None

        return self.last_stop_reason, messages