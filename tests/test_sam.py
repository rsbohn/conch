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
    result = sam.exec("2aHello", buffer)
    assert result == buffer[:2] + ["Hello"] + buffer[2:]

def test_sam_i():
    # cat tests/scratch.txt | sed '2iHello'
    result = sam.exec("2iHello", buffer)
    dot = 1
    assert result == buffer[:dot] + ["Hello"] + buffer[dot:]

def test_sam_q():
    # cat tests/scratch.txt | sed '2q'
    result = sam.exec("2q", buffer)
    assert result == buffer[:2]