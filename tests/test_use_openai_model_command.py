import asyncio
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from conch.tui import ConchTUI, LogView


class DummyInput:
    def __init__(self):
        self.value = ""


class DummyEvent:
    def __init__(self, value: str):
        self.value = value


def test_use_switches_to_openai_and_passes_model():
    app = ConchTUI()
    app.log_view = LogView()
    app.input = DummyInput()
    app.input_mode = "ai"
    app.busy_indicator = type("Dummy", (), {"update": lambda self, value: None})()

    # Switch to OpenAI with a specific model
    asyncio.run(app.on_input_submitted(DummyEvent(":use openai:gpt-4o-mini")))
    assert app.ai_provider == "openai"
    assert app.ai_model_name == "gpt-4o-mini"

    # Capture the model passed to oneshot
    captured = {}

    class DummyAI:
        async def oneshot(self, prompt, model: str = "", max_tokens: int = 512):
            captured["model"] = model
            return "ok"

    # Inject dummy client to avoid network
    app.ai_model = DummyAI()

    asyncio.run(app.on_input_submitted(DummyEvent("hello from openai")))

    assert captured["model"] == "gpt-4o-mini"
