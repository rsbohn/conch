import os
from typing import Tuple, Optional, List, TypeAlias, Union

Pathish = Union[str, os.PathLike]

ResultWithErrorStr: TypeAlias = Tuple[Optional[List[str]], Optional[str]]


def load_file(filename: Pathish) -> ResultWithErrorStr:
    """Read a file and return its contents as a list of lines.

    ``filename`` may be a ``str`` or any ``os.PathLike`` object.  Using
    ``os.fspath`` normalises the value so tests can freely pass ``Path``
    objects without causing a ``TypeError`` on Windows or other
    platforms.
    """
    path = os.fspath(filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content.splitlines(), None
    except FileNotFoundError:
        return None, f"Error: File '{path}' not found"
    except PermissionError:
        return None, f"Error: Permission denied accessing '{path}'"
    except UnicodeDecodeError:
        return None, f"Error: Cannot decode '{path}' as text (binary file?)"
    except Exception as e:
        return None, f"Error accessing '{path}': {e}"
    return None, None  # Added to satisfy return type


def load_folder(foldername: Pathish) -> ResultWithErrorStr:
    """List folder contents, marking directories with a trailing slash."""
    path = os.fspath(foldername)
    try:
        entries = os.listdir(path)
        entries.sort()
        if not entries:
            return ["(empty directory)"], None
        result = []
        for entry in entries:
            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                result.append(f"{entry}/")
            else:
                result.append(entry)
        return result, None
    except PermissionError:
        return None, "Error: Permission denied reading directory"
    except FileNotFoundError:
        return None, f"Error: Directory '{path}' not found"
    except Exception as e:
        return None, f"Error accessing directory '{path}': {e}"
    return None, None  # Added to satisfy return type
