"""
cas_demo.py — Demo script for CAS operations

Usage:
    python src/scripts/cas_demo.py

This script demonstrates basic usage of the CAS class:
- Store content
- Retrieve content
- Pin content
- List pins
- Unpin content
"""

import os
import tempfile
from conch.cas import CAS
import shutil
import sqlite3


def main():
    # Create a temporary CAS root
    cas_root = tempfile.mkdtemp()
    print(f"CAS root: {cas_root}")
    cas = CAS(cas_root)

    # Put content
    content = "Hello, CAS demo!"
    hash_ = cas.put(content)
    print(f"Stored content with hash: {hash_}")

    # Get content
    retrieved = cas.get(hash_)
    print(f"Retrieved content: {retrieved}")

    # Pin content
    cas.pin(hash_)
    print(f"Pinned hash: {hash_}")

    # List pins
    db_path = os.path.join(cas_root, "index.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT hash FROM pinned")
    rows = c.fetchall()
    conn.close()
    print("Pinned hashes:", [row[0] for row in rows])

    # Unpin content
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM pinned WHERE hash=?", (hash_,))
    conn.commit()
    c.execute("SELECT hash FROM pinned WHERE hash=?", (hash_,))
    row = c.fetchone()
    conn.close()
    print(f"Unpinned hash {hash_}:", "Not found" if row is None else row)

    # Cleanup
    shutil.rmtree(cas_root)
    print("Cleaned up CAS root.")


if __name__ == "__main__":
    main()
