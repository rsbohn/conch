#!/usr/bin/env python3
# conch.py — MVP REPL for “executable text menus”

from __future__ import annotations
import json, shlex, subprocess, sys, textwrap, time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

BULLET = "  · "

@dataclass
class Line:
    raw: str
    kind: str = "text"       # sh | py | ai | text
    payload: str = ""        # command/code/prompt
    children: List[str] = field(default_factory=list)

def classify(s: str) -> Line:
    s = s.rstrip("\n")
    if s.startswith("> sh:"):
        return Line(raw=s, kind="sh", payload=s[len("> sh:"):].strip())
    if s.startswith("> py:"):
        return Line(raw=s, kind="py", payload=s[len("> py:"):].strip())
    if s.startswith(":ai "):
        return Line(raw=s, kind="ai", payload=s[len(":ai "):].strip())
    return Line(raw=s)

class PyExec:
    """Tiny shared REPL context."""
    def __init__(self):
        self.globals: Dict[str, Any] = {}

    def run(self, code: str) -> str:
        # Try eval first; fallback to exec. Capture last expression value.
        try:
            result = eval(code, self.globals)  # nosec: user-driven tool
            self.globals["_"] = result
            return repr(result)
        except SyntaxError:
            pass
        buf = []
        def _print(*args, **kwargs):
            buf.append(" ".join(str(a) for a in args))
        self.globals.setdefault("print", _print)
        exec(code, self.globals)              # nosec: user-driven tool
        return "\n".join(buf) if buf else "(ok)"

def run_sh(cmd: str, timeout: int = 30) -> str:
    # Minimal sandbox: no shell=True, split args, pass-through cwd/env.
    try:
        args = shlex.split(cmd)
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        out = p.stdout.strip()
        err = p.stderr.strip()
        rc  = p.returncode
        lines = []
        if out:
            lines.append(out)
        if err:
            lines.append(f"[stderr]\n{err}")
        lines.append(f"[exit {rc}]")
        return "\n".join(lines)
    except Exception as e:
        return f"[error] {e}"

def ai_plan(prompt: str) -> Dict[str, Any]:
    """
    Mock AI: turns a few common intents into a tiny plan.
    Replace this with a real LLM call that MUST return the JSON schema.
    """
    p = prompt.lower()
    actions = []
    if "release" in p or "tests" in p:
        actions = [
            {"type": "sh", "title": "Run tests", "cmd": "pytest -q"},
            {"type": "sh", "title": "Build", "cmd": "uv build"},
            {"type": "explain", "title": "Why these steps?", "text": "Test → build → publish."}
        ]
    elif "big files" in p or "logs" in p:
        actions = [
            {"type": "sh", "title": "Find large logs", "cmd": "find . -name '*.log' -size +10M"},
            {"type": "sh", "title": "Summarize sizes", "cmd": "du -ah . | sort -h | tail -20"}
        ]
    else:
        actions = [{"type": "explain", "title": "No recipe",
                    "text": "I don't have a template for that yet. Edit me!"}]
    return {"actions": actions}

def render_and_print_children(line_prefix: str, content: str) -> None:
    for ln in content.splitlines() or ["(no output)"]:
        print(BULLET + ln)

def render_actions(plan: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for a in plan.get("actions", []):
        t = a.get("type")
        if t == "sh":
            out.append(f"- [ ] {a.get('title','(untitled)')}")
            out.append(f"> sh: {a.get('cmd','')}")
        elif t == "py":
            out.append(f"- [ ] {a.get('title','(untitled)')}")
            out.append(f"> py: {a.get('code','')}")
        elif t == "explain":
            out.append(f"- [?] {a.get('title','Why?')}")
            for ln in textwrap.fill(a.get("text",""), width=78).splitlines():
                out.append("  " + ln)
        else:
            out.append(f"- [?] Unsupported action: {json.dumps(a)}")
    return out

def banner():
    print("conch 🐚  — executable text menus (MVP)")
    print("Enter lines like `> sh: ls -la`, `> py: 1+2`, `:ai make a release menu`.")
    print("Ctrl+C/Ctrl+D to exit.\n")

def repl():
    py = PyExec()
    banner()
    while True:
        try:
            s = input("conch> ").rstrip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye.")
            return
        if not s:
            continue
        line = classify(s)
        print(line.raw)  # echo the parent line, like xiki
        if line.kind == "sh":
            out = run_sh(line.payload)
            render_and_print_children(line.raw, out)
        elif line.kind == "py":
            out = py.run(line.payload)
            render_and_print_children(line.raw, out)
        elif line.kind == "ai":
            try:
                plan = ai_plan(line.payload)   # swap for real LLM call
                children = render_actions(plan)
                for c in children:
                    print(c)
            except Exception as e:
                render_and_print_children(line.raw, f"[ai error] {e}")
        else:
            print(BULLET + "(text)")

if __name__ == "__main__":
    repl()
