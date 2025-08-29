import asyncio
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from conch.openai_client import OpenAIClient
import conch.openai_client as oai_module


class _DummyResponse:
    def __init__(self, json_payload):
        self._json = json_payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._json


class _DummyAsyncClient:
    last_json = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None, headers=None):
        # capture the json payload for assertions
        type(self).last_json = json
        # return a minimal response resembling OpenAI
        return _DummyResponse({"choices": [{"message": {"content": "ok"}}]})


def _run(coro):
    return asyncio.run(coro)


def test_non_gpt5_uses_max_tokens(monkeypatch):
    monkeypatch.setattr(
        oai_module, "httpx", type("HX", (), {"AsyncClient": _DummyAsyncClient})
    )
    client = OpenAIClient(api_key="test")
    _run(client.oneshot("hi", model="gpt-4o-mini", max_tokens=123))
    sent = _DummyAsyncClient.last_json
    assert sent["model"] == "gpt-4o-mini"
    assert sent.get("max_tokens") == 123
    assert "max-completion-tokens" not in sent


def test_gpt5_uses_max_completion_tokens(monkeypatch):
    monkeypatch.setattr(
        oai_module, "httpx", type("HX", (), {"AsyncClient": _DummyAsyncClient})
    )
    client = OpenAIClient(api_key="test")
    _run(client.oneshot("hi", model="gpt-5", max_tokens=321))
    sent = _DummyAsyncClient.last_json
    assert sent["model"] == "gpt-5"
    assert sent.get("max-completion-tokens") == 321
    assert "max_tokens" not in sent
