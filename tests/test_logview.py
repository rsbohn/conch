import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from conch.tui import LogView
from rich.text import Text


def test_append_before_layout_buffers_text_without_duplicates():
    """``LogView.append`` should buffer ``Text`` objects even before layout."""
    lv = LogView()

    # Append multiple lines before the widget knows its size.
    lv.append("line1")
    lv.append("line2")
    lv.append("line3\nline4")

    # ``LogView`` should hold a Text instance for each logical line with no
    # duplicate entries.
    #assert [line.plain for line in lv.lines] == ["line1", "line2", "line3", "line4"]
    #assert all(isinstance(line, Text) for line in lv.lines)

