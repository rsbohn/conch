import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from conch.tui import ConchTUI


def test_help_contains_commands():
    help_text = ConchTUI.HELP_TEXT
    assert "/help" in help_text
    assert "< filename" in help_text
    assert "< directory" in help_text
    # Boundary tests
    assert "Ctrl+C" not in help_text  # Removed command should not be present
    assert help_text.strip() != ""  # Help text should not be empty
    assert "  " in help_text  # Help text should contain some whitespace for formatting
