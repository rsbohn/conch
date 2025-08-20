from textual.widgets import RichLog
from rich.segment import Segment

class LogView(RichLog):
    """Scrollable log area using RichLog for better performance and scrolling.

    RichLog is designed specifically for logging output with automatic
    scrolling, line wrapping, and proper performance with large amounts of text.
    """

    def __init__(self, *args, **kwargs):
        self._lines_buf: list[Segment] = []
        super().__init__(*args, **kwargs)
        self.can_focus = False

    def append(self, text: str) -> None:
        for ln in text.splitlines() or [""]:
            try:
                self.write(ln)
            except Exception:
                self._lines_buf.append(Segment(ln))

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
        
