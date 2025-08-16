# sam.py
"""
IMPORTANT: This module implements a subset of the Sam text editor commands.
IMPORTANT: Respect the contract: List[str] in, List[str] out
"""
import re

class Sam:
    def __init__(self):
        pass

    def exec(self, command: str, buffer: list[str], dot=-1) -> tuple[list[str], tuple[int, int]]:
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
            addr = 1  # Adjust to 1-based index
        if addr > len(buffer):
            addr = len(buffer)  # Adjust to buffer length
        if cmd == "a":
            lines = text.splitlines()
            return (buffer[:addr] + lines + buffer[addr:], (addr, addr + len(lines)))
        if cmd == 'c':
            lines = text.splitlines() if text else [""]
            return (buffer[:addr-1] + lines + buffer[addr:], (addr-1, addr-1 + len(lines)))
        if cmd == "d":
            return (buffer[:addr-1] + buffer[addr:], (addr-1, addr-1))
        if cmd == "i":
            lines = text.splitlines()
            return (buffer[:addr-1] + lines + buffer[addr-1:], (addr-1, addr-1 + len(lines)))
        if cmd == "m":
            target = int(text) if text else -1
            if 1 <= target <= len(buffer):
                # Move the line at addr to the position at target
                line_to_move = buffer[addr-1]
                new_buffer = buffer[:addr-1] + buffer[addr:]
                new_buffer.insert(target-1, line_to_move)
                return (new_buffer, (target, target))
            return (buffer, dot)  # If target is out of bounds, return unchanged
        
        if cmd == "q":
            return (buffer[:addr], (addr, addr))
        if cmd == "t":
            target = int(text) if text else -1
            hold = buffer[addr-1]
            new_buffer = buffer[:target-1] + [hold] + buffer[target-1:]
            return (new_buffer, (target, target))
        
        # Add more commands here as needed
        # If command not recognized, return buffer unchanged
        return (buffer, (0, 0))

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