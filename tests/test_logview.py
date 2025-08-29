import asyncio
import os
import sys

import pytest
from rich.text import Text
from rich.segment import Segment

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
from conch.logview import LogView


def test_get_lines_basic():
    lv = LogView()
    lv.lines = ["line1", "line2", "line3", "line4", "line5"]

    # Positive indices
    assert lv.get_lines(1, 3) == ["line2", "line3"]
    assert lv.get_lines(0, 5) == ["line1", "line2", "line3", "line4", "line5"]

    # Negative indices
    assert lv.get_lines(-2, -1) == ["line4"]
    assert lv.get_lines(-5, -3) == ["line1", "line2"]

    # a > b (should swap)
    assert lv.get_lines(3, 1) == ["line2", "line3"]

    # Out-of-bounds indices (should not raise, just slice)
    assert lv.get_lines(0, 10) == ["line1", "line2", "line3", "line4", "line5"]
    assert lv.get_lines(-10, 2) == ["line1", "line2"]


def test_get_lines_empty():
    lv = LogView()
    lv.lines = []
    assert lv.get_lines(0, 1) == []
    assert lv.get_lines(-1, 0) == []


def test_clear_resets_lines():
    lv = LogView()
    lv.append("A")
    lv.append("B")
    lv.clear()
    assert lv.get_lines(0, 2) == []
    assert lv.get_lines() == []


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


def test_logview_append_get_lines():
    lv = LogView()
    lv.set_title("My Title")
    payload = "line1\nline2\nline3".splitlines()
    lv.lines = [Segment(item) for item in payload]
    assert lv.get_lines(0, 2) == ["line1", "line2"]
    assert lv.get_lines(1, 3) == ["line2", "line3"]
    assert lv.get_lines(0, 3) == ["line1", "line2", "line3"]
    assert lv.get_lines(1, 1) == ["line2"]
