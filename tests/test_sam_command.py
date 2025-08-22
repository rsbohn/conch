import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import pytest
from conch.sam import Sam

sam = Sam()
dot = (3, 4)

def test_command_detection():
    # Valid commands
    assert sam.is_sam_command('2q')
    assert sam.is_sam_command('.')
    assert sam.is_sam_command('5a/some text/')
    assert sam.is_sam_command('3c/some text/')
    assert sam.is_sam_command('2,3d')
    # Invalid commands (should be treated as text)
    assert not sam.is_sam_command('  1,3d')
    assert not sam.is_sam_command('This is just text')
    assert not sam.is_sam_command('')
    assert not sam.is_sam_command('   ')
    assert not sam.is_sam_command('q')
    # Escaped commands (should be treated as text)
    assert not sam.is_sam_command('\\2q')
    assert not sam.is_sam_command('\\.q')
    assert not sam.is_sam_command('\\This is just text')
    # Edge cases
    assert not sam.is_sam_command('\\')
    assert sam.is_sam_command('1a')
    assert not sam.is_sam_command('a line of text')

def test_parse_command():
    assert sam.parse_command('2q', dot) == (2, 'q', '')
    assert sam.parse_command('2c', dot) == (2, 'c', '')
    assert sam.parse_command('2m8', dot) == (2, 'm', '8')
    assert sam.parse_command('2t8', dot) == (2, 't', '8')
