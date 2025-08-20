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
import os
import pyperclip
from .cas import CAS

def command_w(app):
    cas_root = "e:/rsbohn/cas-01"
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
    buffer = [getattr(line, "text", str(line)) for line in app.log_view.lines]
    if app.dot[0] < len(buffer):
        filename = buffer[app.dot[0]].strip()
        if os.path.exists(filename):
            app._read_path(filename)
        elif app.dot[0] != 0:
            base = buffer[0].strip()
            if base.startswith("#"):
                base = base[1:].strip()
            if base and os.path.exists(base):
                candidate = os.path.join(base, filename)
                if os.path.exists(candidate):
                    app._read_path(candidate)
                else:
                    app.log_view.append(f"Error: File '{filename}' not found")
            else:
                app.log_view.append(f"Error: File '{filename}' not found")
        else:
            app.log_view.append(f"Error: File '{filename}' not found")
    app.input.value = ""
