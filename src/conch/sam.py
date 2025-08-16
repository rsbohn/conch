class Sam:
    def __init__(self):
        pass

    def exec(self, command: str, buffer: str) -> str:
        """
        Execute a Sam command on the given buffer.
        If command starts with '/', perform a dry run (test mode):
        parse and preview the effect, but do not modify the buffer.
        Returns the modified buffer or a preview.
        """
        if command.startswith("/"):
            # Dry run: show what would happen
            preview_cmd = command[1:]
            # For now, just return a message indicating dry run
            return f"[dry run] Would execute: '{preview_cmd}' on buffer of length {len(buffer)}"
        # Placeholder: parse and execute command
        # For now, just return the buffer unchanged
        return buffer
