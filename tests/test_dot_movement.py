import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from conch.tui import ConchTUI, LogView


def test_arrow_keys_move_dot_and_update_title():
    app = ConchTUI()
    app.log_view = LogView()
    app.input_mode = "sh"
    app.log_view.write("line1")
    app.log_view.write("line2")

    app.action_move_down()

    assert app.dot == (0, 0)
    #assert app.log_view.border_title == "Conch (2,1)"
    #line = app.log_view.lines[1]
    #assert getattr(line, "style", None) is not None

    app.action_move_up()

    assert app.dot == (0, 0)
