import pytest
import sys
from types import SimpleNamespace

sys.modules.setdefault("pyperclip", SimpleNamespace(paste=lambda: ""))

from conch.commands import command_w

class DummyLogView:
    def __init__(self, lines=None):
        self.lines = lines or []

class DummyBusyIndicator:
    def __init__(self):
        self.message = None
    def update(self, msg):
        self.message = msg

class DummyInput:
    def __init__(self):
        self.value = ""

class DummyApp:
    def __init__(self):
        self.log_view = DummyLogView(["test content"])
        self.busy_indicator = DummyBusyIndicator()
        self.input = DummyInput()


def test_command_w_uses_env_var(tmp_path, monkeypatch):
    cas_path = tmp_path / "casdir"
    monkeypatch.setenv("CONCH_CAS_ROOT", str(cas_path))
    app = DummyApp()
    command_w(app)
    assert cas_path.exists()
    assert (cas_path / "store").exists()
    assert app.busy_indicator.message and app.busy_indicator.message.startswith("Saved: ")


def test_command_w_defaults_to_home(tmp_path, monkeypatch):
    monkeypatch.delenv("CONCH_CAS_ROOT", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    app = DummyApp()
    command_w(app)
    cas_path = tmp_path / ".conch" / "cas"
    assert cas_path.exists()
    assert (cas_path / "store").exists()
    assert app.busy_indicator.message and app.busy_indicator.message.startswith("Saved: ")
