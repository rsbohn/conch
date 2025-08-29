import asyncio
import os, sys

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


def test_use_switches_model_and_passes_to_oneshot():
    app = ConchTUI()
    app.log_view = LogView()
    app.input = DummyInput()
    app.input_mode = "sh"
    app.busy_indicator = type("Dummy", (), {"update": lambda self, value: None})()

    asyncio.run(app.on_input_submitted(DummyEvent(":use test-model")))
    assert app.ai_model_name == "test-model"

    captured = {}

    class DummyAI:
        async def oneshot(self, prompt, model: str = "", max_tokens: int = 512):
            captured["model"] = model
            return "ok"

    app.ai_model = DummyAI()

    app.input_mode = "ai"
    asyncio.run(app.on_input_submitted(DummyEvent("hello")))

    assert captured["model"] == "test-model"
