"""Simple Textual TUI: large log panel + text input.

Run this with `python -m conch.tui` or via the project's `main.py` entry.
"""

from __future__ import annotations

import asyncio
import sys
import os
import signal
import shlex, subprocess
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Static, Footer
import textwrap
from .anthropic import AnthropicClient, DEFAULT_MODEL
from .sam import Sam, SamParseError
from .logview import LogView
from .commands import (
    command_clear,
    command_gf,
    command_help,
    command_lorem,
    command_paste,
    command_select,
    command_use,
    command_w,
)
from conch import commands


class Submit(Message):
    def __init__(self, sender, value: str) -> None:
        super().__init__(sender)
        self.value = value


class ConchTUI(App):
    input_modes = [
        {"name": "sh", "description": "Shell mode", "switch": ";", "color": "#DDA777"},
        {"name": "ed", "description": "Sam mode", "switch": "/", "color": "#A692C9"},
        {"name": "ai", "description": "AI mode", "switch": "[", "color": "#729789"},
    ]
    # Help text for the :help command
    HELP_TEXT = """
Available Commands:
  :help           - Show this help message
  :q, :quit       - Exit the application
  :clear, :cls    - Clear the log display
  :lorem          - Add sample text for testing scrolling
  :paste          - Append clipboard contents to the log
  :use MODEL      - Set AI model for responses

File Commands:
  < filename      - Read and display file contents (e.g., "< README.md")
  < directory     - List directory contents (e.g., "< src")
  :gf             - Goto file at current dot

General Usage:
  - Type commands in the input field at the bottom
  - Press Enter to execute
  - The log area shows command output and responses
  - Use scroll or arrow keys to navigate through log history
  - Use up/down arrow keys to move the dot and highlight the line
"""

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
        ("f8", "delete_selection", "Delete selection"),
        ("up", "move_up", "Dot up"),
        ("down", "move_down", "Dot down"),
        ("shift+up", "select_up", "Selection start up"),
        ("shift+down", "select_down", "Selection end down"),
        ("f9", "switch_mode", "Switch input mode"),
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
            title = str((a, b))
        self.log_view.border_title = f"Conch {title}"

    def render_buffer(self) -> None:
        """Render current buffer highlighting the dot."""
        if not self.buffer:
            # Capture current log view lines if buffer is empty
            self.buffer = [
                getattr(line, "text", str(line)) for line in self.log_view.lines
            ]

        mode_name = getattr(self, "input_mode", "sh")
        mode_color = next(
            (item["color"] for item in self.input_modes if item["name"] == mode_name),
            "#729789",
        )
        self.log_view.clear()
        # Highlight selection range if dot[1] > dot[0]
        start = min(self.dot[0], self.dot[1])
        end = max(self.dot[0], self.dot[1])
        for i, line in enumerate(self.buffer):
            if start <= i <= end:
                self.log_view.write(Text(line, style=f"black on {mode_color}"))
            else:
                self.log_view.write(line)
        self.set_log_title()
        self._center_on_selection()

    def _center_on_selection(self) -> None:
        """Scroll the log so the current selection is centered when possible."""
        # Determine the line we want centered (top of the selection).
        start_line = min(self.dot[0], self.dot[1])
        try:
            height = self.log_view.size.height
        except Exception:
            # If size isn't available (e.g., during tests before mount) skip.
            return
        if not height:
            return
        # Calculate the top line so the selection appears roughly in the middle
        # of the visible region.
        top_line = max(0, start_line - height // 2)
        try:
            # ``scroll_to`` is available on Textual scrollable widgets.
            self.log_view.scroll_to(y=top_line)
        except Exception:
            # In case the underlying Textual version differs, fail silently.
            pass

    def action_delete_selection(self) -> None:
        """Delete the current selection."""
        start, end = self.dot
        if start != end:
            self.buffer = self.buffer[:start] + self.buffer[end:]
            self.dot = (start, start)
            self.render_buffer()

    def move_dot(self, delta: int) -> None:
        """Move the dot up or down by delta lines and refresh display."""
        self.buffer = [getattr(line, "text", str(line)) for line in self.log_view.lines]
        if not self.buffer:
            return
        new_line = max(0, min(self.dot[0] + delta, len(self.buffer) - 1))
        self.dot = (new_line, new_line)
        self.render_buffer()

    def action_move_up(self) -> None:
        self.move_dot(-1)

    def action_move_down(self) -> None:
        self.move_dot(1)

    def action_select_up(self) -> None:
        """Move the start of the selection up by one line."""
        start, end = self.dot
        if start > 0:
            self.dot = (start - 1, end)
            self.render_buffer()

    def action_select_down(self) -> None:
        """Move the end of the selection down by one line."""
        start, end = self.dot
        if end < len(self.buffer) - 1:
            self.dot = (start, end + 1)
            self.render_buffer()

    def action_switch_mode(self) -> None:
        """Cycle through input modes using hot-key."""
        available_modes = [item["name"] for item in self.input_modes]
        current_index = available_modes.index(self.input_mode)
        next_index = (current_index + 1) % len(available_modes)
        self.switch_input_mode(available_modes[next_index])

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
        self.log_view.append("Type :help for available commands, or :q to quit.")

        # Focus input for immediate typing. set_focus may be a coroutine in
        # some Textual versions or a plain method in others; handle both.
        _maybe = self.set_focus(self.input)
        if asyncio.iscoroutine(_maybe):
            await _maybe

        # If the test flag is present, schedule an immediate shutdown so the
        # runner can verify the app starts and then exits without user input.
        if "--test" in sys.argv:
            asyncio.create_task(self._test_delayed_exit())

        # Default mode is ai
        self.input_mode = "ai"
        self.switch_input_mode(self.input_mode)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if not value:
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

        # colon commands: delegate (most) to commands.py
        if value.startswith(":"):
            cmd_line = value[1:].strip()
            cmd = cmd_line.lower()
            if cmd in ("q", "quit"):
                # Handle quit directly: exit the app
                res = self.exit()
                if asyncio.iscoroutine(res):
                    await res
                return
            if cmd == "w":
                command_w(self)
                return
            if cmd in ("clear", "cls"):
                command_clear(self)
                return
            if cmd == "help":
                command_help(self)
                return
            if cmd.startswith("use "):
                command_use(self, cmd_line)
                return
            if cmd == "lorem":
                command_lorem(self)
                return
            if cmd == "paste":
                command_paste(self)
                return
            if cmd == "gf":
                command_gf(self)
                return

        # Interpolate the user input
        # unless the input is quoted
        if value[0] == "\"":
            if value[-1] == "\"":
                value = value[1:-1]
            else:
                value = value[1:]  # Remove leading quote
        else:
            # interpolate
            value = self.interpolate(value)

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

        if value.startswith("!"):
            self.do_shell_command(value[1:])
            self.input.value = ""
            return

        if self.input_mode == "sh":
            self.do_shell_command(value)

        if self.input_mode == "ai":
            # AI mode: send the prompt to the AI model
            self.set_busy(True)  # Set busy state while waiting for AI response
            if self.ai_model is None:
                self.ai_model = AnthropicClient()
            response = await self.ai_model.oneshot(value, model=self.ai_model_name)
            if response is not None:
                hash = commands.save_to_cas(response)
                self.log_view.append(f"[model] {self.ai_model_name} -> {hash}")
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

    # Shell command execution
    # TODO: operate on selection
    def do_shell_command(self, command:str) -> None:
        try:
            args = shlex.split(command)
            p = subprocess.run(args, capture_output=True, text=True, timeout=10)
            out = p.stdout.strip() or p.stderr.strip() or f"(exit {p.returncode})"
        except Exception as e:
            out = f"[error] {e}"
        for ln in out.splitlines() or ["(no output)"]:
            self.log_view.append("  " + ln)
            
    def interpolate(self, value: str) -> str:
        a = self.dot[0]
        b = self.dot[1]
        payload = self.log_view.get_lines(a, b)
        return value.replace("%%", "\n" + "\n".join(payload) + "\n")

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
