"""Simple Textual TUI: large log panel + text input.

Run this with `python -m conch.tui` or via the project's `main.py` entry.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, RichLog
import asyncio
from textual.reactive import reactive
import sys
import os
from textual.message import Message
from textual import events
import signal


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
    # Help text for the /help command
    HELP_TEXT = """
Available Commands:
  /help           - Show this help message
  /q, /quit       - Exit the application
  /clear, /cls    - Clear the log display
  /lorem          - Add sample text for testing scrolling

File Commands:
  < filename      - Read and display file contents (e.g., "< README.md")
  < directory     - List directory contents (e.g., "< src")

Shell Commands:
  > sh: <command> - Execute a shell command (e.g., "> sh: ls -la")
  sh: <command>   - Same as above, shorthand version

Keyboard Shortcuts:
  Ctrl+C          - Exit the application
  Ctrl+L          - Clear the log display

General Usage:
  - Type commands in the input field at the bottom
  - Press Enter to execute
  - The log area shows command output and responses
  - Use scroll or arrow keys to navigate through log history
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
        border-title-align: center;
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

    def compose(self) -> ComposeResult:
        with Vertical():
            self.log_view = LogView()
            self.log_view.border_title = "Conch TUI"
            yield self.log_view
            # Input is not in a container to keep it at the bottom
            self.input = Input(placeholder="Type and press Enter to send...", id="cmd")
            yield self.input

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

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if not value:
            return

        # File reading: < filename
        if value.startswith("< "):
            filename = value[2:].strip()
            if not filename:
                self.log_view.append("Error: No filename specified")
                self.input.value = ""
                return

            try:
                # Check if it's a directory
                if os.path.isdir(filename):
                    # List directory contents
                    self.log_view.clear()

                    # Set title to just the directory name
                    dir_title = os.path.basename(filename) or filename
                    self.log_view.set_title(dir_title)

                    self.log_view.append(f"=== Contents of {filename} ===")
                    self.log_view.append("")

                    # Get directory listing
                    try:
                        entries = os.listdir(filename)
                        entries.sort()  # Sort alphabetically

                        if not entries:
                            self.log_view.append("(empty directory)")
                        else:
                            for entry in entries:
                                entry_path = os.path.join(filename, entry)
                                if os.path.isdir(entry_path):
                                    self.log_view.append(
                                        f"{entry}/"
                                    )  # Mark directories with /
                                else:
                                    self.log_view.append(entry)
                    except PermissionError:
                        self.log_view.append(
                            "Error: Permission denied reading directory"
                        )

                    self.log_view.append("")
                    self.log_view.append(f"=== End of {filename} ===")

                else:
                    # Handle file reading (existing code)
                    with open(filename, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Clear log and show file contents
                    self.log_view.clear()

                    # Set title to just the filename (not the full path)
                    file_title = os.path.basename(filename)
                    self.log_view.set_title(file_title)

                    self.log_view.append(f"=== Contents of {filename} ===")
                    self.log_view.append("")

                    # Add file contents line by line
                    for line in content.splitlines():
                        self.log_view.append(line)

                    self.log_view.append("")
                    self.log_view.append(f"=== End of {filename} ===")

            except FileNotFoundError:
                self.log_view.append(f"Error: File or directory '{filename}' not found")
            except PermissionError:
                self.log_view.append(f"Error: Permission denied accessing '{filename}'")
            except UnicodeDecodeError:
                self.log_view.append(
                    f"Error: Cannot decode '{filename}' as text (binary file?)"
                )
            except Exception as e:
                self.log_view.append(f"Error accessing '{filename}': {e}")

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
                # Add lorem ipsum text for testing scrolling
                lorem_text = [
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
                for line in lorem_text:
                    self.log_view.append(line)
                self.input.value = ""  # Clear input after command
                return
        # Echo command into the log
        self.log_view.append(f"> {value}")
        # A tiny simulated action: if starts with sh: run via subprocess
        if value.startswith("> sh:") or value.startswith("sh:"):
            import shlex, subprocess

            cmd = (
                value.split(":", 1)[1].strip()
                if ":" in value
                else value[len("sh:") :].strip()
            )
            try:
                args = shlex.split(cmd)
                p = subprocess.run(args, capture_output=True, text=True, timeout=10)
                out = p.stdout.strip() or p.stderr.strip() or f"(exit {p.returncode})"
            except Exception as e:
                out = f"[error] {e}"
            for ln in out.splitlines() or ["(no output)"]:
                self.log_view.append("  " + ln)
        else:
            # For anything else, just echo a response
            self.log_view.append(f"(echo) {value}")

        # clear input
        self.input.value = ""

    async def on_key(self, event: events.Key) -> None:
        # Ctrl+C quits the app (some environments don't deliver SIGINT to Textual)
        if event.key == "c" and event.ctrl:
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

        # Ctrl+L clears the log
        if event.key == "l" and event.ctrl:
            # use compatibility clear()
            self.log_view.clear()

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
