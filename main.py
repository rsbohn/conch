def main():
    """Launch the Textual TUI if available; fall back to a simple message.

    By default this will execute the TUI module at src/conch/tui.py so the
    project does not need to be installed into the environment.
    """
    import os
    import runpy
    import sys

    # If the user explicitly asks for the old repl behavior, keep it simple.
    if len(sys.argv) > 1 and sys.argv[1] in ("repl", "mvp"):
        print("Hello from conch!")
        return

    # If stdin is not a terminal (piped input), fall back to MVP mode
    # since Textual can't handle piped input properly
    if not sys.stdin.isatty():
        print("Hello from conch!")
        print("(Non-interactive mode - stdin is piped)")
        return

    # Run the TUI script from the repository layout.
    script_path = os.path.join(os.path.dirname(__file__), "src", "conch", "tui.py")
    if not os.path.exists(script_path):
        print("TUI script not found:", script_path)
        return

    # Execute the tui.py as a script (it will call App.run()).
    try:
        runpy.run_path(script_path, run_name="__main__")
    except ModuleNotFoundError as e:
        missing = getattr(e, "name", str(e))
        print(f"Missing dependency for TUI: {missing}.")
        print("Install with: python -m pip install textual")
        print("Falling back to simple message.")
        print("Hello from conch!")
    except Exception as e:
        print("Error running TUI:", e)
        return


if __name__ == "__main__":
    main()
