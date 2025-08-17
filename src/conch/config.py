"""
config.py: Configuration for Anthropic API key management.
"""

import os
from typing import Optional


def get_anthropic_key() -> Optional[str]:
    """Read the Anthropic API key from the keyfile."""
    keyfile = os.environ.get("keyfile")
    if not keyfile:
        raise RuntimeError("Environment variable 'keyfile' not set.")

    with open(keyfile, "r", encoding="utf-8") as f:
        return f.read().strip()
