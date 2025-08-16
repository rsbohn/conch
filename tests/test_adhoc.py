import pytest
from textual.app import App, ComposeResult
from textual.widgets import RichLog
from conch.tui import LogView

class AdhocApp(App):
    def compose(self) -> ComposeResult:
        yield LogView(id="log")

@pytest.mark.asyncio
async def test_logview_line_extraction():
    async with AdhocApp().run_test() as pilot:
        log = pilot.app.query_one("#log", LogView)

        log.append("one eye dog")
        log.append("cat with two tails")

        # Let the message loop process the append() calls
        await pilot.pause()

        assert len(log.lines) == 2

        # Newer Textual: LogLine.text is a Rich Text
        first_line = getattr(log.lines[0], "text", log.lines[0])
        assert first_line == "one eye dog"
