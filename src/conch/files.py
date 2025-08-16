import os
from typing import Tuple, Optional, List, TypeAlias

ResultWithErrorStr: TypeAlias = Tuple[Optional[List[str]], Optional[str]]

def load_file(filename: str) -> ResultWithErrorStr:
    """Read a file and return its contents as a list of lines."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return content.splitlines(), None
    except FileNotFoundError:
        return None, f"Error: File '{filename}' not found"
    except PermissionError:
        return None, f"Error: Permission denied accessing '{filename}'"
    except UnicodeDecodeError:
        return None, f"Error: Cannot decode '{filename}' as text (binary file?)"
    except Exception as e:
        return None, f"Error accessing '{filename}': {e}"
    return None, None  # Added to satisfy return type


def load_folder(foldername: str) -> ResultWithErrorStr:
    """List the contents of a folder, marking directories with a trailing slash."""
    try:
        entries = os.listdir(foldername)
        entries.sort()
        if not entries:
            return ["(empty directory)"], None
        result = []
        for entry in entries:
            entry_path = os.path.join(foldername, entry)
            if os.path.isdir(entry_path):
                result.append(f"{entry}/")
            else:
                result.append(entry)
        return result, None
    except PermissionError:
        return None, "Error: Permission denied reading directory"
    except FileNotFoundError:
        return None, f"Error: Directory '{foldername}' not found"
    except Exception as e:
        return None, f"Error accessing directory '{foldername}': {e}"
    return None, None  # Added to satisfy return type
