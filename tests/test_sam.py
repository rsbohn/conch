import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from conch.sam import Sam

sam = Sam()
buffer = open("tests/scratch.txt").readlines()
buffer = [line.rstrip() for line in buffer]  # Remove trailing newlines


def test_parse_command_dot_cases():
    dot = (3, 4)
    # '..' should use dot[0] for address, '.' for command, None for text
    addr, cmd, text = sam.parse_command("..", dot)
    assert addr == dot[0] + 1, f"Expected addr={dot[0]+1}, got {addr}"
    assert cmd == ".", f"Expected cmd='.', got {cmd}"
    assert text == "", f"Expected text='', got {text}"

    # '$.' should use -1 for address, '.' for command, None for text
    addr, cmd, text = sam.parse_command("$.", dot)
    assert addr == -1, f"Expected addr=-1, got {addr}"
    assert cmd == ".", f"Expected cmd='.', got {cmd}"
    assert text == "", f"Expected text='', got {text}"

    # '7.' should use 7 for address, '.' for command, None for text
    addr, cmd, text = sam.parse_command("7.", dot)
    assert addr == 7, f"Expected addr=7, got {addr}"
    assert cmd == ".", f"Expected cmd='.', got {cmd}"
    assert text == "", f"Expected text='', got {text}"


def test_sam_a():
    dot = (3, 4)
    result, dot = sam.exec("2a/Hello/", buffer, dot)
    assert result == buffer[:2] + ["Hello"] + buffer[2:]
    assert dot == (2, 3)


def test_sam_c():
    n = 2
    expected = buffer.copy()
    expected[n - 1] = "Hello"
    dot = (3, 4)
    result, dot = sam.exec(f"{n}c/Hello/", buffer, dot)
    assert result[n - 1] == "Hello"
    assert result == expected
    assert dot == (n - 1, n)


def test_sam_c_clear():
    n = 2
    expected = buffer.copy()
    expected[n - 1] = ""
    dot = (3, 4)
    result, dot = sam.exec(f"{n}c", buffer, dot)
    assert result == expected
    assert dot == (n - 1, n)


def test_sam_d():
    # buffer = ["a", "b", "c"]
    dot = (3, 4)
    result, dot = sam.exec("2d", ["a", "b", "c"], dot)
    assert result == ["a", "c"]
    assert dot == (1, 1)


def test_sam_i():
    # cat tests/scratch.txt | sed '2iHello'
    dot = (3, 4)
    result, dot = sam.exec("2iHello", buffer, dot)
    dot_expected = 1
    assert result == buffer[:dot_expected] + ["Hello"] + buffer[dot_expected:]
    assert dot == (dot_expected, dot_expected + 1)


def test_sam_m():
    buffer2 = ["a", "b", "c", "d"]
    expected = ["a", "c", "d", "b"]
    m = 2
    n = 4
    dot = (3, 4)
    result, dot = sam.exec(f"{m}m{n}", buffer2, dot)
    dot_expected = n - 1
    assert result == expected
    assert dot == (dot_expected, dot_expected + 1)


def test_sam_s():
    buffer2 = ["a", "roberta", "bertram", "d"]
    expected = ["a", "robina", "bertram", "d"]
    dot = (3, 4)
    result, dot = sam.exec("2s/bert/bin/", buffer2, dot)
    assert result == expected
    assert dot == (1, 2)


def test_sam_t():
    # copy line
    buffer2 = ["a", "b", "c"]
    expected = ["a", "b", "c", "a"]
    dot = (3, 4)
    result, dot = sam.exec("1t4", buffer2, dot)
    assert result == expected
    assert dot == (4, 4)


def test_sam_q():
    # cat tests/scratch.txt | sed '2q'
    dot = (3, 4)
    result, dot = sam.exec("2q", buffer, dot)
    assert result == buffer[:2]
    assert dot == (2, 2)
