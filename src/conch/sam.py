# sam.py
"""
IMPORTANT: This module implements a subset of the Sam text editor commands.
IMPORTANT: Respect the contract: List[str] in, List[str] out
"""
import re

class Sam:
    def __init__(self):
        pass

    def exec(self, command: str, buffer: list[str], dot=-1) -> list[str]:
        """
        Execute a Sam command on the given buffer.
        Supports commands of the form [addr]K[text], where addr is an integer and K is a single letter.
        Currently supports Nq: return buffer[:N].
        """
        if buffer is None:
            buffer = []
        if isinstance(buffer, str):
            buffer = buffer.splitlines()
        assert isinstance(buffer, list), "Buffer must be a list of strings"
        if len(buffer) > 0:
            assert all(isinstance(line, str) for line in buffer), "Buffer must contain only strings"
        addr, cmd, text = self.parse_command(command)
        if addr < 1:
            raise ValueError("Address must be greater than 0")
        if cmd == "a":
            lines = text.splitlines()
            return buffer[:addr] + lines + buffer[addr:]
        if cmd == "i":
            lines = text.splitlines()
            return buffer[:addr-1] + lines + buffer[addr-1:]
        if cmd == "q":
            return buffer[:addr]
        # Add more commands here as needed
        # If command not recognized, return buffer unchanged
        return buffer

    def parse_command(self,s:str) -> tuple[int, str, str]:
        """
        Parse a Sam command string into its components.
        Returns a tuple of (address, command, text).
        """
        m = re.match(r"^(\d+)([a-zA-Z])(.*)?$", s.strip())
        if m:
            addr = int(m.group(1))
            cmd = m.group(2)
            text = m.group(3) if m.group(3) else ""
            return addr, cmd, text
        return -1, "", ""