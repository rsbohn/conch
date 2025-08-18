from textual.app import App, ComposeResult
from textual.widgets import RichLog
from textual import events
from rich.text import Text


LOREM_LINES = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
    "Nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore.",
    "Eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident.",
    "Sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Curabitur non nulla sit amet nisl tempus convallis quis ac lectus.",
    "Praesent sapien massa, convallis a pellentesque nec, egestas non nisi.",
    "Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a.",
]

HILITE_BG = "#729789"  # highlight color for the 'dot' line
HILITE_BG = "#A692C9"


class RichLogDotDemo(App):
    CSS = """
    RichLog {
        border: solid #729789;
        height: 1fr;
        border-title-align: left;
    }
    """

    def compose(self) -> ComposeResult:
        # auto_scroll=False so the view doesn't jump while we re-render
        yield RichLog(auto_scroll=False, wrap=False, markup=False, name="log")

    def on_mount(self) -> None:
        self.dot = 0
        self.lines = list(LOREM_LINES)
        self._render_log()

    def _render_log(self) -> None:
        log: RichLog = self.query_one("RichLog")
        # Show dot in the title
        dot = self.dot
        log.border_title = f"{dot+1}/{len(log.children)}"
        for i, line in enumerate(log.children):
            if i == dot:
                # Highlight current line ('dot') with more contrast
                log.children[i].style = f"black on {HILITE_BG}"
            else:
                log.children[i].style = ""
        # Keep the highlighted line in view (scroll_end for now; scroll_to_line not supported)
        log.scroll_to(dot)

    def on_key(self, event: events.Key) -> None:
        key = event.key

        if key in ("up", "left"):
            if self.dot > 0:
                self.dot -= 1
                self._render_log()
            event.stop()
        elif key in ("down", "right"):
            if self.dot < len(self.lines) - 1:
                self.dot += 1
                self._render_log()
            event.stop()
        elif key == "delete":
            self.exit()
        # Optional: Home/End jump
        elif key == "home":
            if self.dot != 0:
                self.dot = 0
                self._render_log()
        elif key == "end":
            if self.dot != len(self.lines) - 1:
                self.dot = len(self.lines) - 1
                self._render_log()


if __name__ == "__main__":
    RichLogDotDemo().run()
