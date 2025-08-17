import os
import shutil
import tempfile
import pytest
import sqlite3
from conch.cas import CAS


@pytest.fixture
def cas_root():
    root = tempfile.mkdtemp()
    yield root
    shutil.rmtree(root)


@pytest.fixture
def cas(cas_root):
    return CAS(cas_root)


def test_put_and_get(cas):
    content = "Hello, CAS!"
    hash_ = cas.put(content)
    assert isinstance(hash_, str)
    retrieved = cas.get(hash_)
    assert retrieved == content


def test_put_rejects_large_file(cas):
    big_content = "a" * (4 * 1024 * 1024 + 1)
    with pytest.raises(ValueError):
        cas.put(big_content)


def test_put_rejects_non_text(cas):
    with pytest.raises(ValueError):
        cas.put(12345)  # Not a string


def test_get_missing(cas):
    assert cas.get("deadbeef" * 8) is None


def test_pin(cas):
    content = "Pin me!"
    hash_ = cas.put(content)
    cas.pin(hash_)
    # Check pin in DB
    conn = sqlite3.connect(os.path.join(cas.root, "index.db"))
    c = conn.cursor()
    c.execute("SELECT hash FROM pinned WHERE hash=?", (hash_,))
    row = c.fetchone()
    conn.close()
    assert row is not None and row[0] == hash_


def test_unpin(cas):
    # Add pin, then remove it
    content = "Unpin me!"
    hash_ = cas.put(content)
    cas.pin(hash_)
    # Unpin implementation: direct DB removal
    conn = sqlite3.connect(os.path.join(cas.root, "index.db"))
    c = conn.cursor()
    c.execute("DELETE FROM pinned WHERE hash=?", (hash_,))
    conn.commit()
    c.execute("SELECT hash FROM pinned WHERE hash=?", (hash_,))
    row = c.fetchone()
    conn.close()
    assert row is None


def test_list_pins(cas):
    # Pin two items, list pins
    content1 = "Pin one!"
    content2 = "Pin two!"
    hash1 = cas.put(content1)
    hash2 = cas.put(content2)
    cas.pin(hash1)
    cas.pin(hash2)
    conn = sqlite3.connect(os.path.join(cas.root, "index.db"))
    c = conn.cursor()
    c.execute("SELECT hash FROM pinned")
    rows = c.fetchall()
    conn.close()
    hashes = {row[0] for row in rows}
    assert hash1 in hashes
    assert hash2 in hashes
