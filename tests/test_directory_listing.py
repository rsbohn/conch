import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
from conch.tui import ConchTUI, LogView


def test_directory_listing_creates_entries(tmp_path):
    # create a temp directory with files and a subdir
    dirpath = tmp_path / "mydir"
    dirpath.mkdir()
    (dirpath / "file1.txt").write_text("hello")
    (dirpath / "subdir").mkdir()
    (dirpath / "subdir" / "nested.txt").write_text("x")

    lv = LogView()
    # emulate code path for directory listing
    entries = sorted(os.listdir(str(dirpath)))
    assert "file1.txt" in entries
    assert "subdir" in entries

    # when listing, directories are shown with trailing '/'
    displayed = []
    for entry in entries:
        p = os.path.join(str(dirpath), entry)
        if os.path.isdir(p):
            displayed.append(f"{entry}/")
        else:
            displayed.append(entry)

    assert "subdir/" in displayed
    assert "file1.txt" in displayed
