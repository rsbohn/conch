from textual.widgets import RichLog
from rich.text import Text

class LogView(RichLog):
    """Scrollable log area using RichLog for better performance and scrolling.

    RichLog is designed specifically for logging output with automatic
    scrolling, line wrapping, and proper performance with large amounts of text.
    """

    def __init__(self, *args, **kwargs):
        self._lines_buf: list[Text] = []
        super().__init__(*args, **kwargs)
        self.can_focus = False

    def append(self, text: str) -> None:
        for ln in text.splitlines() or [""]:
            try:
                self.write(ln)
            except Exception:
                self._lines_buf.append(Text(ln))

    def clear(self) -> None:
        super().clear()
        self.lines = []

    def set_title(self, title: str) -> None:
        self.border_title = title

    @property
    def lines(self) -> list[Text]:
        return self._lines_buf

    @lines.setter
    def lines(self, value: list[Text | str]) -> None:
        self._lines_buf = [v if isinstance(v, Text) else Text(v) for v in value]
