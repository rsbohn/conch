"""Simple Textual TUI: large log panel + text input.

Run this with `python -m conch.tui` or via the project's `main.py` entry.
"""

from __future__ import annotations

import asyncio
import sys
import os
import signal
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, RichLog, LoadingIndicator, Static, Footer
import pyperclip
import textwrap
from .anthropic import AnthropicClient
from .sam import Sam


class LogView(RichLog):
    """Scrollable log area using RichLog for better performance and scrolling.

    RichLog is designed specifically for logging output with automatic
    scrolling, line wrapping, and proper performance with large amounts of text.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False  # LogView doesn't need focus

    def append(self, text: str) -> None:
        """Add text to the log, automatically scrolling to bottom."""
        for ln in text.splitlines() or [""]:
            self.write(ln)

    def clear(self) -> None:
        """Clear all content from the log."""
        super().clear()

    def set_title(self, title: str) -> None:
        """Set the border title for the log view."""
        self.border_title = title


class Submit(Message):
    def __init__(self, sender, value: str) -> None:
        super().__init__(sender)
        self.value = value


class ConchTUI(App):
    input_modes = [
        {"name": "sh", "description": "Shell mode", "switch": ";", "color": "#44CC88"},
        {"name": "py", "description": "Python mode", "switch": ":", "color": "#CC8844"},
        {"name": "ed", "description": "Sam mode", "switch": "/", "color": "#8844CC"},
        {"name": "ai", "description": "AI mode", "switch": "[", "color": "#729785"}
    ]
    # Help text for the /help command
    HELP_TEXT = """
Available Commands:
  /help           - Show this help message
  /q, /quit       - Exit the application
  /clear, /cls    - Clear the log display
  /lorem          - Add sample text for testing scrolling
  /paste          - Append clipboard contents to the log

File Commands:
  < filename      - Read and display file contents (e.g., "< README.md")
  < directory     - List directory contents (e.g., "< src")

Input Modalities
  ; - shell command mode
  : - python mode
  / - sam (edit) mode

General Usage:
  - Type commands in the input field at the bottom
  - Press Enter to execute
  - The log area shows command output and responses
  - Use scroll or arrow keys to navigate through log history
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

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    placeholder = reactive("Ready.")

    def switch_input_mode(self, mode: str) -> None:
        """Switch the input mode."""
        available_modes = [item["name"] for item in self.input_modes]
        if mode not in available_modes:
            raise RuntimeError(f"Invalid mode: {mode} not in {available_modes}")

        selected_mode = next(item for item in self.input_modes if item["name"] == mode)
        self.log_view.append(f"Switching to {selected_mode['description']}")

        self.input_mode = mode
        self.input.border_title = f"{mode}:"
        self.input.styles.border = ("heavy", selected_mode["color"])
        self.input.value = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.busy = False  # Flag to indicate if the app is busy
        self.ai_model = AnthropicClient()  # Initialize the AI model client
        self.sam = Sam()
        self.buffer = ""  # Main text buffer for ed mode
        self.dot = (0, 0)  # Cursor position in ed mode
        # TODO: Add history stack for undo functionality

    def compose(self) -> ComposeResult:
        with Vertical():
            self.log_view = LogView()
            self.log_view.border_title = "Conch TUI"
            yield self.log_view
            if self.busy:
                yield LoadingIndicator(id="busy-indicator", color="cyan")
            else:
                yield Static(">>>")
            self.input = Input(placeholder="Type and press Enter to send...", id="cmd")
            yield self.input
            yield Footer()

    def set_busy(self, value: bool) -> None:
        self.busy = value
        self.refresh()

    def set_log_title(self, title: str = None) -> None:
        if title is None:
            title = str(self.dot)
        self.log_view.border_title = f"Conch {title}"

    async def on_mount(self) -> None:
        # Seed some example lines into the log
        self.log_view.append("conch TUI — large log + single-line input")
        self.log_view.append("")
        self.log_view.append(
            "Type commands below and press Enter. Press Ctrl+C to quit."
        )
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

            from .files import load_file, load_folder

            # Check if it's a directory
            if os.path.isdir(filename):
                self.log_view.clear()
                dir_title = os.path.basename(filename) or filename
                self.log_view.set_title(dir_title)
                self.log_view.append(f"# {filename}")
                entries, error = load_folder(filename)
                if error:
                    self.log_view.append(error)
                else:
                    for entry in entries:
                        self.log_view.append(entry)
                self.log_view.append("§§§")
            else:
                lines, error = load_file(filename)
                self.log_view.clear()
                file_title = os.path.basename(filename)
                self.log_view.set_title(file_title)
                self.log_view.append(f"# {filename}")
                if error:
                    self.log_view.append(error)
                else:
                    for line in lines:
                        self.log_view.append(line)
                self.log_view.append("§§§")

            self.input.value = ""
            return

        # Slash commands: /q to quit, /clear to clear the log
        if value.startswith("/"):
            cmd = value[1:].strip().lower()
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

        if self.input_mode == "ed":
            # Use Sam to process the command on the buffer
            # use `getattr` because older Textual versions may not have .text
            buffer = [getattr(line, "text", line) for line in self.log_view.lines]
            self.buffer, new_dot = self.sam.exec(value, buffer, self.dot)
            self.dot = new_dot  # Update dot position
            self.set_log_title()  # Update log title with current dot position
            self.log_view.clear()
            for ln in self.buffer:
                self.log_view.append(ln)
            self.input.value = ""  # Clear input after command
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
            # Print the response
            self.set_busy(True)  # Set busy state while waiting for AI response
            response = self.ai_model.oneshot(value)
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
