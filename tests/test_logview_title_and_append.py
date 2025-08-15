import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
from conch.tui import LogView


def test_logview_append_and_title():
    lv = LogView()
    lv.set_title("My Title")
    assert hasattr(lv, "border_title")
    assert lv.border_title == "My Title"

    lv.append("line1\nline2")
    # RichLog.write appends to internal buffer, but we can at least ensure no exceptions
    lv.append("")

    # clearing should not raise
    lv.clear()

    # ensure title remains settable after clear
    lv.set_title("Other")
    assert lv.border_title == "Other"
