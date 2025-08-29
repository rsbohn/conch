import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from conch.tui import ConchTUI


def test_help_mentions_ai_providers_and_model_command():
    help_text = ConchTUI.HELP_TEXT
    assert ":model" in help_text
    assert "OpenAI" in help_text
    assert "Anthropic" in help_text
    assert ":use openai:" in help_text
    assert ":use claude" in help_text or ":use anthropic:" in help_text
