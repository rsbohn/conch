from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any, Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Input, Static


class MCPClient(App):
    """Minimal TUI for interacting with an MCP server over stdio."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #log {
        height: 1fr;
        border: round $accent;
        padding: 1;
        overflow-y: auto;
    }
    #input {
        dock: bottom;
    }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self, cmd: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._cmd = cmd
        self._proc: Optional[asyncio.subprocess.Process] = None
        self._id = 0

    async def compose(self) -> ComposeResult:  # type: ignore[override]
        with Vertical():
            self.log = Static(id="log")
            yield self.log
            self.input = Input(placeholder="Tool invocation JSON", id="input")
            yield self.input
            yield Footer()

    async def on_mount(self) -> None:
        self._proc = await asyncio.create_subprocess_shell(
            self._cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        tools = await self.list_tools()
        if tools:
            self.log.write("Available tools:\n")
            for t in tools:
                name = t.get("name", "<unknown>")
                desc = t.get("description", "")
                self.log.write(f"- {name}: {desc}\n")
            # Pre-fill input with first tool template
            tpl = self.template_for_tool(tools[0])
            self.input.value = json.dumps(tpl, indent=2)
        else:
            self.log.write("(No tools reported)\n")

    async def rpc_call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self._proc or not self._proc.stdin or not self._proc.stdout:
            raise RuntimeError("Server process not running")
        self._id += 1
        req: Dict[str, Any] = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            req["params"] = params
        msg = json.dumps(req) + "\n"
        self._proc.stdin.write(msg.encode())
        await self._proc.stdin.drain()
        line = await self._proc.stdout.readline()
        if not line:
            raise RuntimeError("Server closed connection")
        resp = json.loads(line.decode())
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return resp.get("result")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Return the list of tools from the server."""
        result = await self.rpc_call("list_tools")
        if isinstance(result, dict) and "tools" in result:
            return result["tools"]
        if isinstance(result, list):
            return result
        # Try alternative method name
        alt = await self.rpc_call("tools/list")
        if isinstance(alt, dict) and "tools" in alt:
            return alt["tools"]
        return []

    def template_for_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        name = tool.get("name", "")
        schema = tool.get("input_schema", {}).get("properties", {})
        args = {k: "" for k in schema.keys()}
        return {"name": name, "arguments": args}

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            payload = json.loads(event.value)
        except json.JSONDecodeError as e:
            self.log.write(f"Invalid JSON: {e}\n")
            return
        name = payload.get("name")
        args = payload.get("arguments", {})
        try:
            result = await self.rpc_call("call_tool", {"name": name, "arguments": args})
        except Exception:
            result = await self.rpc_call("tools/call", {"name": name, "arguments": args})
        self.log.write(json.dumps(result, indent=2) + "\n")
        self.input.value = ""


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="TUI client for MCP servers")
    parser.add_argument("cmd", help="Command to run the MCP server")
    args = parser.parse_args(argv)
    MCPClient(args.cmd).run()


if __name__ == "__main__":
    main()
