import os
import sys
import types
import pytest

# Ensure src/ is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from conch.anthropic import AnthropicClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def model_dump(self):
        return self._payload


class FakeMessages:
    def __init__(self, payload):
        self._payload = payload

    def create(self, **kwargs):
        # Return a minimal object that mimics anthropic SDK's response
        return FakeResponse(self._payload)


class FakeAnthropic:
    def __init__(self, payload):
        self._payload = payload
        self.messages = FakeMessages(payload)


@pytest.mark.asyncio
async def test_tool_use_turn_no_tool_use(monkeypatch):
    # Simulate a normal text response with end_turn
    payload = {
        "content": [{"type": "text", "text": "Hello!"}],
        "stop_reason": "end_turn",
    }

    # Patch anthropic.Anthropic to our fake
    import conch.anthropic as ca

    monkeypatch.setattr(ca, "anthropic", types.SimpleNamespace(Anthropic=lambda: FakeAnthropic(payload)))

    client = AnthropicClient(api_key="test-key")
    messages = [{"role": "user", "content": "Hi"}]

    stop_reason, updated = await client.tool_use_turn(messages)

    assert stop_reason == "end_turn"
    # Assistant reply appended
    assert len(updated) == 2
    assert updated[-1]["role"] == "assistant"
    assert updated[-1]["content"][0]["type"] == "text"
    assert client.last_stop_reason == "end_turn"


@pytest.mark.asyncio
async def test_tool_use_turn_with_tool_use(monkeypatch):
    # Simulate a tool_use stop with one tool call
    payload = {
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_123",
                "name": "consult_rulebook",
                "input": {"query": "rules"},
            }
        ],
        "stop_reason": "tool_use",
    }

    import conch.anthropic as ca

    # Patch SDK client
    monkeypatch.setattr(ca, "anthropic", types.SimpleNamespace(Anthropic=lambda: FakeAnthropic(payload)))

    client = AnthropicClient(api_key="test-key")

    # Patch the internal tool handler to return a tool_result content block
    def fake_handle_tool_use(content_blocks):
        assert isinstance(content_blocks, list)
        assert content_blocks and content_blocks[0]["type"] == "tool_use"
        return [
            {
                "type": "tool_result",
                "tool_use_id": content_blocks[0]["id"],
                "content": "ok",
            }
        ]

    monkeypatch.setattr(client, "_handle_tool_use", fake_handle_tool_use)

    messages = [{"role": "user", "content": "Who may look at the queen?"}]

    stop_reason, updated = await client.tool_use_turn(messages)

    # Should reflect tool_use and append assistant + tool_result-as-user
    assert stop_reason == "tool_use"
    assert client.last_stop_reason == "tool_use"
    assert len(updated) == 3
    assert updated[1]["role"] == "assistant"
    assert updated[2]["role"] == "user"
    # The user message content should be the tool_result list we returned
    assert isinstance(updated[2]["content"], list)
    assert updated[2]["content"][0]["type"] == "tool_result"
    assert updated[2]["content"][0]["tool_use_id"] == "toolu_123"

