import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from conch.sam import Sam

sam = Sam()
buffer = open("tests/scratch.txt").readlines()
buffer = [line.rstrip() for line in buffer]  # Remove trailing newlines

def test_sam_a():
    # cat tests/scratch.txt | sed '2aHello'
    result, dot = sam.exec("2aHello", buffer)
    assert result == buffer[:2] + ["Hello"] + buffer[2:]
    assert dot == (2, 3)

def test_sam_c():
    n=2
    expected = buffer.copy()
    expected[n-1] = "Hello"
    result, dot = sam.exec(f"{n}cHello", buffer)
    assert result[n-1] == "Hello"
    assert result == expected
    assert dot == (n-1, n)

def test_sam_c_clear():
    n = 2
    expected = buffer.copy()
    expected[n-1] = ""
    result, dot = sam.exec(f"{n}c", buffer)
    assert result == expected
    assert dot == (n-1, n)

def test_sam_d():
    # buffer = ["a", "b", "c"]
    result, dot = sam.exec("2d", ["a", "b", "c"])
    assert result == ["a", "c"]
    assert dot == (1, 1)

def test_sam_i():
    # cat tests/scratch.txt | sed '2iHello'
    result, dot = sam.exec("2iHello", buffer)
    dot_expected = 1
    assert result == buffer[:dot_expected] + ["Hello"] + buffer[dot_expected:]
    assert dot == (dot_expected, dot_expected + 1)

def test_sam_q():
    # cat tests/scratch.txt | sed '2q'
    result, dot = sam.exec("2q", buffer)
    assert result == buffer[:2]
    assert dot == (2, 2)