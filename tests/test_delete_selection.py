import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from conch.tui import ConchTUI, LogView


def test_delete_key_removes_selection():
    app = ConchTUI()
    app.log_view = LogView()
    app.log_view.write("line1")
    app.log_view.write("line2")
    app.log_view.write("line3")
    app.dot = (0, 1)
    app.action_delete_selection()
    remaining = [getattr(line, "text", str(line)) for line in app.log_view.lines]
    assert remaining == ["line3"]
    assert app.dot == (0, 0)
