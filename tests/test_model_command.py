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


def test_model_command_prints_current_selection():
    app = ConchTUI()
    app.log_view = LogView()
    app.input = DummyInput()
    app.input_mode = "ai"
    app.busy_indicator = type("Dummy", (), {"update": lambda self, value: None})()

    app.ai_provider = "openai"
    app.ai_model_name = "gpt-4o-mini"

    asyncio.run(app.on_input_submitted(DummyEvent(":model")))

    # The model should be visible in the border title
    title = app.log_view.border_title or ""
    assert "[openai:gpt-4o-mini]" in title
