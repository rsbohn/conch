from textual.widgets import RichLog
from rich.segment import Segment


class LogView(RichLog):
    """Minimal log view used for tests without requiring full Textual/Rich."""

    def __init__(self, *args, **kwargs):
        self._lines_buf: list[Segment] = []
        super().__init__(*args, **kwargs)
        self.can_focus = False
        self.auto_scroll = False

    def append(self, text: str) -> None:
        for ln in text.splitlines() or [""]:
            self.write(ln)

    def write(self, text):
        try:
            super().write(text)
        except Exception:
            pass
        if hasattr(text, "plain"):
            self._lines_buf.append(Segment(text.plain))
        else:
            self._lines_buf.append(Segment(str(text)))

    def clear(self) -> None:
        super().clear()
        self.lines = []

    def set_title(self, title: str) -> None:
        self.border_title = title

    def get_lines(self, a:int=0, b:int=-1) -> list[str]:
        """
        Get lines from the buffer between indices a and b.
        """
        if a < 0: a = len(self._lines_buf) + a
        if b < 0: b = len(self._lines_buf) + b
        if a > b: return self.get_lines(b, a)
        if a == b: return self.get_lines(a, a+1)
        selection = self._lines_buf[a:b]
        # Segment.text is not available, use Segment's 'text' attribute
        return [seg.text if hasattr(seg, "text") else str(seg) for seg in selection]

    @property
    def lines(self) -> list[Segment]:
        return self._lines_buf

    @lines.setter
    def lines(self, value: list[Segment | str]) -> None:
        self._lines_buf = [v if isinstance(v, Segment) else Segment(v) for v in value]
        
