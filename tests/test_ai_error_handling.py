import asyncio
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

import httpx
from conch.tui import ConchTUI, LogView


class DummyInput:
    def __init__(self):
        self.value = ""


class DummyEvent:
    def __init__(self, value: str):
        self.value = value


def _lines_text(app: ConchTUI):
    return [getattr(seg, "text", str(seg)) for seg in app.log_view.lines]


def test_ai_handles_429_error_gracefully():
    app = ConchTUI()
    app.log_view = LogView()
    app.input = DummyInput()
    app.input_mode = "ai"
    app.busy_indicator = type("Dummy", (), {"update": lambda self, value: None})()

    # Switch to OpenAI just to exercise that path
    asyncio.run(app.on_input_submitted(DummyEvent(":use openai:gpt-4o-mini")))

    # Dummy AI that raises HTTPStatusError 429
    class DummyAI:
        async def oneshot(self, prompt, model: str = "", max_tokens: int = 512):
            req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
            resp = httpx.Response(429, request=req)
            raise httpx.HTTPStatusError("Too Many Requests", request=req, response=resp)

    app.ai_model = DummyAI()

    asyncio.run(app.on_input_submitted(DummyEvent("hi")))

    buf = _lines_text(app)
    # Ensure an error line mentioning 429 is present and app didn't crash
    assert any("[error]" in ln and "429" in ln for ln in buf)


def test_ai_handles_none_response_without_crash():
    app = ConchTUI()
    app.log_view = LogView()
    app.input = DummyInput()
    app.input_mode = "ai"
    app.busy_indicator = type("Dummy", (), {"update": lambda self, value: None})()

    class DummyAI:
        async def oneshot(self, prompt, model: str = "", max_tokens: int = 512):
            return None

    app.ai_model = DummyAI()

    asyncio.run(app.on_input_submitted(DummyEvent("hi")))

    buf = _lines_text(app)
    # Should include a placeholder line for no output
    assert any("(no output)" in ln for ln in buf)


def test_openai_insufficient_quota_message():
    app = ConchTUI()
    app.log_view = LogView()
    app.input = DummyInput()
    app.input_mode = "ai"
    app.busy_indicator = type("Dummy", (), {"update": lambda self, value: None})()

    # Switch to OpenAI path
    asyncio.run(app.on_input_submitted(DummyEvent(":use openai:gpt-4o-mini")))

    class DummyAI:
        async def oneshot(self, prompt, model: str = "", max_tokens: int = 512):
            req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
            # Simulate OpenAI 429 insufficient_quota payload
            payload = {
                "error": {
                    "message": "You exceeded your current quota, please check your plan and billing details.",
                    "type": "insufficient_quota",
                    "param": None,
                    "code": "insufficient_quota",
                }
            }
            resp = httpx.Response(429, request=req, json=payload)
            raise httpx.HTTPStatusError("Too Many Requests", request=req, response=resp)

    app.ai_model = DummyAI()

    asyncio.run(app.on_input_submitted(DummyEvent("hi")))

    buf = _lines_text(app)
    assert any("quota" in ln.lower() for ln in buf)
