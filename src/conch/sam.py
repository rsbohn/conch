# sam.py
"""
IMPORTANT: This module implements a subset of the Sam text editor commands.
IMPORTANT: Respect the contract: List[str] in, List[str] out
"""
import re

class SamParseError(Exception):
    pass

class Sam:
    def __init__(self):
        pass

    def exec(
        self, command: str, buffer: list[str], dot: tuple[int, int]
    ) -> tuple[list[str], tuple[int, int]]:
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
            assert all(
                isinstance(line, str) for line in buffer
            ), "Buffer must contain only strings"
        addr, cmd, text = self.parse_command(command, dot)
        if addr == 0:
            addr = 1  # Adjust to 1-based index
        if addr < 0:
            addr = len(buffer) - addr  # Negative index means from the end
        if addr > len(buffer):
            addr = len(buffer)  # Adjust to buffer length
        if cmd == ".":
            # No-op. Use to move the dot.
            return (buffer, (addr-1, addr))
        if cmd == "a":
            lines = text.splitlines()
            return (buffer[:addr] + lines + buffer[addr:], (addr, addr + len(lines)))
        if cmd == "c":
            lines = text.splitlines() if text else [""]
            return (
                buffer[: addr - 1] + lines + buffer[addr:],
                (addr - 1, addr - 1 + len(lines)),
            )
        if cmd == "d":
            # TODO: delete multiple lines dot[0]:dot[1]
            return (buffer[: addr - 1] + buffer[addr:], (addr - 1, addr - 1))
        if cmd == "i":
            lines = text.splitlines()
            return (
                buffer[: addr - 1] + lines + buffer[addr - 1 :],
                (addr - 1, addr - 1 + len(lines)),
            )
        if cmd == "m":
            target = int(text) if text else -1
            if 1 <= target <= len(buffer):
                # Move the line at addr to the position at target
                line_to_move = buffer[addr - 1]
                new_buffer = buffer[: addr - 1] + buffer[addr:]
                new_buffer.insert(target - 1, line_to_move)
                return (new_buffer, (target-1, target))
            return (buffer, dot)  # If target is out of bounds, return unchanged

        if cmd == "q":
            return (buffer[:addr], (addr, addr))

        if cmd == "s":
            if addr < 1 or addr > len(buffer):
                return (buffer, dot)
            if not text:
                return (buffer, dot)
            try:
                pattern, replacement = text.split("/")[1:3]
                regex = re.compile(pattern)
                new_buffer = buffer[: addr - 1] + buffer[addr:]
                new_buffer.insert(addr - 1, regex.sub(replacement, buffer[addr - 1]))
                return (new_buffer, (addr-1, addr))
            # need some way to reflect the error in TUI
            except Exception as e:
                raise SamParseError(f"Failed to parse command: {e}")

        if cmd == "t":
            target = int(text) if text else -1
            hold = buffer[addr - 1]
            new_buffer = buffer[: target - 1] + [hold] + buffer[target - 1 :]
            return (new_buffer, (target, target))

        # Add more commands here as needed
        # If command not recognized, return buffer unchanged
        return (buffer, (0, 0))

    def parse_command(self, s: str, dot: tuple[int,int] = (-1,-1)) -> tuple[int, str, str]:
        """
        Parse a Sam command string into its components.
        Returns a tuple of (address, command, text).
        """
        # Special case for '^.'
        if s.startswith("."):
            addr = dot[0] + 1  # Use current line number
            cmd = s[1] if len(s) > 1 else '.'
            text = ''
            if len(s) > 2:
                text = s[2:]
            return addr, cmd, text

        m = re.match(r"^(\$|\d+)([a-zA-Z\.])(.*)?$", s.strip())
        if m:
            if m.group(1) == "$":
                addr = -1
            else:
                addr = int(m.group(1))
            cmd = m.group(2)
            text = m.group(3) if m.group(3) else ""
            return addr, cmd, text
        return -1, "", ""
