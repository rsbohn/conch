"""Simple Textual TUI: large log panel + text input.

Run this with `python -m conch.tui` or via the project's `main.py` entry.
"""

from __future__ import annotations

import asyncio
import sys
import os
import signal
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, RichLog, LoadingIndicator, Static, Footer
import pyperclip
import textwrap
from .anthropic import AnthropicClient, DEFAULT_MODEL
from .sam import Sam, SamParseError


class LogView(RichLog):
    """Scrollable log area using RichLog for better performance and scrolling.

    RichLog is designed specifically for logging output with automatic
    scrolling, line wrapping, and proper performance with large amounts of text.
    """

    def __init__(self, *args, **kwargs):
        # Maintain a buffer of Text instances that have been written to the log.
        # Using ``Text`` ensures the Rich renderer can always display the lines.
        self._lines_buf: list[Text] = []
        super().__init__(*args, **kwargs)
        self.can_focus = False  # LogView doesn't need focus

    def append(self, text: str) -> None:
        """Add text to the log, automatically scrolling to bottom."""
        for ln in text.splitlines() or [""]:
            try:
                # Attempt to write the line immediately. ``RichLog.write``
                # will append a ``Text`` instance to ``self.lines`` when
                # the widget knows its size.
                self.write(ln)
            except Exception:
                # Prior to layout the widget may not yet be able to write.
                # Fallback to buffering the line as ``Text`` so rendering
                # succeeds once the widget is ready.
                self._lines_buf.append(Text(ln))

    def clear(self) -> None:
        """Clear all content from the log."""
        super().clear()
        self.lines = []

    def set_title(self, title: str) -> None:
        """Set the border title for the log view."""
        self.border_title = title

    @property
    def lines(self) -> list[Text]:  # type: ignore[override]
        return self._lines_buf

    @lines.setter
    def lines(self, value: list[Text | str]) -> None:  # type: ignore[override]
        # Ensure the buffer always contains ``Text`` objects.
        self._lines_buf = [v if isinstance(v, Text) else Text(v) for v in value]


class Submit(Message):
    def __init__(self, sender, value: str) -> None:
        super().__init__(sender)
        self.value = value


class ConchTUI(App):
    input_modes = [
        {"name": "sh", "description": "Shell mode", "switch": ";", "color": "#44CC88"},
        {"name": "py", "description": "Python mode", "switch": ":", "color": "#CC8844"},
        {"name": "ed", "description": "Sam mode", "switch": "/", "color": "#A692C9"},
        {"name": "ai", "description": "AI mode", "switch": "[", "color": "#729789"}
    ]
    # Help text for the /help command
    HELP_TEXT = """
Available Commands:
  /help           - Show this help message
  /q, /quit       - Exit the application
  /clear, /cls    - Clear the log display
  /lorem          - Add sample text for testing scrolling
  /paste          - Append clipboard contents to the log
  /use MODEL     - Set AI model for responses

File Commands:
  < filename      - Read and display file contents (e.g., "< README.md")
  < directory     - List directory contents (e.g., "< src")
  /gf             - Goto file at current dot

Input Modalities
  ; - shell command mode
  : - python mode
  / - sam (edit) mode

General Usage:
  - Type commands in the input field at the bottom
  - Press Enter to execute
  - The log area shows command output and responses
  - Use scroll or arrow keys to navigate through log history
  - Use up/down arrow keys to move the dot and highlight the line
"""
    LOREM = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor",
        "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis",
        "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore",
        "eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident,",
        "sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut",
        "perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque",
        "laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et",
        "quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem",
        "quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni",
        "dolores eos qui ratione voluptatem sequi nesciunt.",
    ]
    CSS = """
    ConchTUI {
        background: black;
        color: white;
    }
    
    /* Layout: log takes 80% of screen height, input takes remaining space */
    Vertical > LogView {
        height: 80%;
        border: round white;
        border-title-align: left;
        border-title-style: bold;
        border-title-color: cyan;
    }

    Input {
        height: auto;
        min-height: 3;
        border: heavy #666666;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("up", "move_up", "Dot up"),
        ("down", "move_down", "Dot down"),
    ]

    placeholder = reactive("Ready.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.busy = False  # Flag to indicate if the app is busy
        self.ai_model = None  # Anthropic client, lazily initialized
        self.ai_model_name = DEFAULT_MODEL  # Current model name
        self.sam = Sam()
        self.buffer: list[str] = []  # Main text buffer for log contents
        self.dot = (0, 0)  # Cursor position in log
        # TODO: Add history stack for undo functionality
    
    def switch_input_mode(self, mode: str) -> None:
        """Switch the input mode."""
        available_modes = [item["name"] for item in self.input_modes]
        if mode not in available_modes:
            raise RuntimeError(f"Invalid mode: {mode} not in {available_modes}")

        selected_mode = next(item for item in self.input_modes if item["name"] == mode)
        self.input_mode = mode
        self.input.border_title = f"{mode}:"
        self.input.styles.border = ("heavy", selected_mode["color"])
        self.input.value = ""


    def compose(self) -> ComposeResult:
        with Vertical():
            self.log_view = LogView()
            self.log_view.border_title = "Conch TUI"
            yield self.log_view
            self.busy_indicator = Static(":idle", id="busy-indicator")
            yield self.busy_indicator
            self.input = Input(placeholder="Type and press Enter to send...", id="cmd")
            yield self.input
            yield Footer()

    def set_busy(self, value: bool) -> None:
        self.busy = value
        self.busy_indicator.update(":busy" if value else ":idle")
        self.refresh()

    def set_log_title(self, title: str = None) -> None:
        a = self.dot[0] + 1  # Convert to 1-based index for display
        b = self.dot[1] + 1  # Convert to 1-based index for display
        if title is None:
            title = str((a,b))
        self.log_view.border_title = f"Conch {title}"

    def render_buffer(self) -> None:
        """Render current buffer highlighting the dot."""
        if not self.buffer:
            # Capture current log view lines if buffer is empty
            self.buffer = [getattr(line, "text", str(line)) for line in self.log_view.lines]

        mode_name = getattr(self, "input_mode", "sh")
        mode_color = next(
            (item["color"] for item in self.input_modes if item["name"] == mode_name),
            "#729789",
        )
        self.log_view.clear()
        for i, line in enumerate(self.buffer):
            if i == self.dot[0]:
                self.log_view.write(Text(line, style=f"black on {mode_color}"))
            else:
                self.log_view.write(line)
        self.set_log_title()

    def move_dot(self, delta: int) -> None:
        """Move the dot up or down by delta lines and refresh display."""
        self.buffer = [getattr(line, "text", str(line)) for line in self.log_view.lines]
        if not self.buffer:
            return
        new_line = max(0, min(self.dot[0] + delta, len(self.buffer) - 1))
        self.dot = (new_line, min(self.dot[1], len(self.buffer[new_line])))
        self.render_buffer()

    def action_move_up(self) -> None:
        self.move_dot(-1)

    def action_move_down(self) -> None:
        self.move_dot(1)

    def _read_path(self, filename: str) -> bool:
        """Load a file or directory into the log view.

        Returns True on success, False if an error occurred."""
        from .files import load_file, load_folder

        if os.path.isdir(filename):
            entries, error = load_folder(filename)
            self.log_view.clear()
            dir_title = os.path.basename(filename) or filename
            self.log_view.set_title(dir_title)
            self.log_view.append(f"# {filename}")
            if error:
                self.log_view.append(error)
                self.log_view.append("§§§")
                return False
            for entry in entries:
                self.log_view.append(entry)
            self.log_view.append("§§§")
            return True
        else:
            lines, error = load_file(filename)
            self.log_view.clear()
            file_title = os.path.basename(filename)
            self.log_view.set_title(file_title)
            self.log_view.append(f"# {filename}")
            if error:
                self.log_view.append(error)
                self.log_view.append("§§§")
                return False
            for line in lines:
                self.log_view.append(line)
            self.log_view.append("§§§")
            return True

    async def on_mount(self) -> None:
        # Hint for slash commands and quitting
        self.log_view.append("Type /help for available commands, or /q to quit.")

        # Focus input for immediate typing. set_focus may be a coroutine in
        # some Textual versions or a plain method in others; handle both.
        _maybe = self.set_focus(self.input)
        if asyncio.iscoroutine(_maybe):
            await _maybe

        # If the test flag is present, schedule an immediate shutdown so the
        # runner can verify the app starts and then exits without user input.
        if "--test" in sys.argv:
            asyncio.create_task(self._test_delayed_exit())

        # Default mode is shell
        self.input_mode = "sh"
        self.switch_input_mode("sh")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if not value:
            return

        # Mode switching: ';' for shell, ':' for python
        if value == ";":
            self.switch_input_mode("sh")
            return
        if value == ":":
            self.switch_input_mode("py")
            return
        if value == "/":
            self.switch_input_mode("ed")
            return
        if value == "[":
            self.switch_input_mode("ai")
            return

        # File reading: < filename
        if value.startswith("< "):
            filename = value[1:].strip()
            if not filename:
                self.log_view.append("Error: No filename specified")
                self.input.value = ""
                return

            self._read_path(filename)
            self.input.value = ""
            return

        # Slash commands: /q to quit, /clear to clear the log, /w to save buffer to CAS
        if value.startswith("/"):
            cmd_line = value[1:].strip()
            cmd = cmd_line.lower()
            if cmd in ("q", "quit"):
                # user requested quit
                try:
                    res = self.exit()
                    if asyncio.iscoroutine(res):
                        await res
                except Exception:
                    try:
                        res2 = self.action_quit()
                        if asyncio.iscoroutine(res2):
                            await res2
                    except Exception:
                        pass
                return
            if cmd == "w":
                # Save buffer to CAS and update busy indicator
                from .cas import CAS
                # TODO: move this to config.py
                cas_root = "e:/rsbohn/cas-01"
                cas = CAS(cas_root)
                # Get buffer content as a single string
                buffer_content = "\n".join([getattr(line, "text", str(line)) for line in self.log_view.lines])
                hash_value = cas.put(buffer_content)
                self.busy_indicator.update(f"Saved: {hash_value}")
                self.input.value = ""
                return
            if cmd in ("clear", "cls"):
                self.log_view.clear()
                self.log_view.set_title("Conch TUI")  # Reset title to default
                self.input.value = ""  # Clear input after command
                return
            if cmd == "help":
                # Show help text
                for line in self.HELP_TEXT.strip().split("\n"):
                    self.log_view.append(line)
                self.input.value = ""  # Clear input after command
                return
            if cmd.startswith("use "):
                self.ai_model_name = cmd_line.split(maxsplit=1)[1]
                self.log_view.append(f"[model] {self.ai_model_name}")
                self.input.value = ""
                return
            if cmd == "lorem":
                for line in self.LOREM:
                    self.log_view.append(line)
                self.input.value = ""
                return
            if cmd == "paste":
                try:
                    clipboard_text = pyperclip.paste()
                    if clipboard_text:
                        self.log_view.append(f"[clipboard]\n{clipboard_text}")
                    else:
                        self.log_view.append("[clipboard] No text in clipboard")
                except Exception as e:
                    self.log_view.append(f"[error] Clipboard access failed: {e}")
                self.input.value = ""
                return
            if cmd == "gf":
                buffer = [getattr(line, "text", str(line)) for line in self.log_view.lines]
                if self.dot[0] < len(buffer):
                    filename = buffer[self.dot[0]].strip()
                    if os.path.exists(filename):
                        self._read_path(filename)
                    elif self.dot[0] != 0:
                        base = buffer[0].strip()
                        if base.startswith("#"):
                            base = base[1:].strip()
                        if base and os.path.exists(base):
                            candidate = os.path.join(base, filename)
                            if os.path.exists(candidate):
                                self._read_path(candidate)
                            else:
                                self.log_view.append(f"Error: File '{filename}' not found")
                        else:
                            self.log_view.append(f"Error: File '{filename}' not found")
                    else:
                        self.log_view.append(f"Error: File '{filename}' not found")
                self.input.value = ""
                return

        if self.input_mode == "ed":
            # Use Sam to process the command on the buffer
            buffer = [getattr(line, "text", line) for line in self.log_view.lines]
            try:
                self.buffer, self.dot = self.sam.exec(value, buffer, self.dot)
                self.render_buffer()
                self.input.value = ""  # Clear input after command
            except SamParseError as e:
                self.log_view.append(f"SamParseError: {e}")
            return
        
        # Echo command into the log
        self.log_view.append(f"> {value}")

        # Use input_mode to determine how to handle input
        if self.input_mode == "sh":
            # Handle shell commands: sh:
            if value.startswith("sh:"):
                import shlex, subprocess

                cmd = (
                    value.split(":", 1)[1].strip()
                    if ":" in value
                    else value[len("sh:") :].strip()
                )
                try:
                    args = shlex.split(cmd)
                    p = subprocess.run(args, capture_output=True, text=True, timeout=10)
                    out = (
                        p.stdout.strip() or p.stderr.strip() or f"(exit {p.returncode})"
                    )
                except Exception as e:
                    out = f"[error] {e}"
                for ln in out.splitlines() or ["(no output)"]:
                    self.log_view.append("  " + ln)
            else:
                # Treat as shell command
                import shlex, subprocess

                try:
                    args = shlex.split(value)
                    p = subprocess.run(args, capture_output=True, text=True, timeout=10)
                    out = (
                        p.stdout.strip() or p.stderr.strip() or f"(exit {p.returncode})"
                    )
                except Exception as e:
                    out = f"[error] {e}"
                for ln in out.splitlines() or ["(no output)"]:
                    self.log_view.append("  " + ln)

        elif self.input_mode == "py":
            # Python mode: evaluate as Python code
            import io
            import contextlib

            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(value, globals())
                out = buf.getvalue().strip()
            except Exception as e:
                out = f"[error] {e}"
            for ln in out.splitlines() or ["(no output)"]:
                self.log_view.append("  " + ln)

        elif self.input_mode == "ai":
            # AI mode: send the prompt to the AI model
            self.set_busy(True)  # Set busy state while waiting for AI response
            if self.ai_model is None:
                self.ai_model = AnthropicClient()
            response = await self.ai_model.oneshot(value, model=self.ai_model_name)
            for ln in response.splitlines() or ["(no output)"]:
                for wrapped_ln in textwrap.wrap(ln, width=72) or [""]:
                    self.log_view.append("  " + wrapped_ln)
            self.set_busy(False)  # Reset busy state after getting AI response

        # clear input
        self.input.value = ""

    async def _test_delayed_exit(self) -> None:
        """Test helper: wait 2 seconds then exit for --test flag."""
        await asyncio.sleep(2)
        await self._test_auto_exit()

    async def _test_auto_exit(self) -> None:
        """Auto-exit helper used for --test: yield control then exit."""
        # allow the app to finish mounting and render once, then exit
        await asyncio.sleep(0.1)
        # call exit to stop the App run loop. Some Textual versions have
        # exit() as synchronous, others return a coroutine; handle both.
        try:
            res = self.exit()
            if asyncio.iscoroutine(res):
                await res
        except Exception:
            # some Textual versions may provide action_quit or different API
            try:
                res2 = self.action_quit()
                if asyncio.iscoroutine(res2):
                    await res2
            except Exception:
                pass


def main() -> None:
    """Main entry point to run the Conch TUI application."""
    if not os.environ.get("keyfile"):
        print("Error: keyfile environment variable not set.")
        print("    $env:keyfile = /path/to/your/keyfile")
        print("    export keyfile=/path/to/your/keyfile")
        sys.exit(1)
    app = ConchTUI()
    # Install a SIGINT handler so Ctrl+C from Windows Terminal triggers a
    # shutdown even if Textual doesn't get the key event.
    try:

        def _sigint(signum, frame):
            try:
                res = app.exit()
                if asyncio.iscoroutine(res):
                    try:
                        loop = asyncio.get_event_loop()
                        loop.create_task(res)
                    except Exception:
                        pass
            except Exception:
                try:
                    res2 = app.action_quit()
                    if asyncio.iscoroutine(res2):
                        try:
                            loop = asyncio.get_event_loop()
                            loop.create_task(res2)
                        except Exception:
                            pass
                except Exception:
                    try:
                        sys.exit(0)
                    except Exception:
                        pass

        signal.signal(signal.SIGINT, _sigint)
    except Exception:
        # if signal isn't available or registration fails, continue anyway
        pass

    try:
        app.run()
    except KeyboardInterrupt:
        # final fallback if SIGINT was delivered as exception
        try:
            app.exit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
