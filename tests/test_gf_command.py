import os
import sys
import asyncio

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


def test_gf_opens_file_from_listing(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    f = d / "file.txt"
    f.write_text("hello")

    app = ConchTUI()
    app.log_view = LogView()
    app.input = DummyInput()
    app.input_mode = "sh"

    app.log_view.append(f"# {d}")
    app.log_view.append("file.txt")
    app.log_view.append("§§§")
    app.dot = (1, 0)

    asyncio.run(app.on_input_submitted(DummyEvent("/gf")))

    lines = [line.plain for line in app.log_view.lines]
    assert len(lines) == 0
