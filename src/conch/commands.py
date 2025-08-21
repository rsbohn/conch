import os
import pyperclip
from .cas import CAS

# Sample LOREM text for /lorem command
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

def command_select(app, sel):
    """
    Implements colon-prefixed global selection commands (e.g., :a,b, :dot,b, :a,dot, :a,$, :a,+n, :a,-n).
    Updates app.dot and display selection accordingly.
    """
    import re
    m = re.match(r"^(dot|\d+|a|\$|\.)(,)(dot|\d+|b|\$|\.|\+\d+|-\d+)$", sel)
    if m:
        a_raw, _, b_raw = m.groups()
        def parse_pos(pos):
            if pos in ("dot", "."):
                return app.dot[0]
            if pos in ("b",):
                return app.dot[1]
            if pos in ("a",):
                return 0
            if pos in ("$",):
                return len(app.buffer) - 1 if app.buffer else 0
            if pos.startswith("+"):
                return app.dot[0] + int(pos[1:])
            if pos.startswith("-"):
                return app.dot[0] - int(pos[1:])
            try:
                return int(pos) - 1
            except Exception:
                return app.dot[0]
        a = max(0, min(parse_pos(a_raw), len(app.buffer) - 1 if app.buffer else 0))
        b = max(0, min(parse_pos(b_raw), len(app.buffer) - 1 if app.buffer else 0))
        app.dot = (a, b)
        app.render_buffer()
        app.input.value = ""
        return True
    app.log_view.append(f"Invalid selection: {sel}")
    app.input.value = ""
    return False

def command_w(app):
    cas_root = os.environ.get("CONCH_CAS_ROOT")
    if cas_root is None:
        home = os.environ.get("HOME") or os.path.expanduser("~")
        cas_root = os.path.join(home, ".conch", "cas")
    os.makedirs(cas_root, exist_ok=True)
    cas = CAS(cas_root)
    buffer_content = "\n".join([getattr(line, "text", str(line)) for line in app.log_view.lines])
    hash_value = cas.put(buffer_content)
    app.busy_indicator.update(f"Saved: {hash_value}")
    app.input.value = ""

def command_clear(app):
    app.log_view.clear()
    app.log_view.set_title("Conch TUI")
    app.input.value = ""

def command_help(app):
    for line in app.HELP_TEXT.strip().split("\n"):
        app.log_view.append(line)
    app.input.value = ""

def command_use(app, cmd_line):
    app.ai_model_name = cmd_line.split(maxsplit=1)[1]
    app.log_view.append(f"[model] {app.ai_model_name}")
    app.input.value = ""

def command_lorem(app):
    for line in LOREM:
        app.log_view.append(line)
    app.input.value = ""

def command_paste(app):
    try:
        clipboard_text = pyperclip.paste()
        if clipboard_text:
            app.log_view.append(f"[clipboard]\n{clipboard_text}")
        else:
            app.log_view.append("[clipboard] No text in clipboard")
    except Exception as e:
        app.log_view.append(f"[error] Clipboard access failed: {e}")
    app.input.value = ""

def command_gf(app):
    """Placeholder gf command for test environment."""
    app.log_view.clear()
    app.input.value = ""
