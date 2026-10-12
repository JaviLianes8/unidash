"""Fold Unicode punctuation to plain ASCII while leaving letters untouched."""

from __future__ import annotations

from ._fold import to_ascii_punct

__version__ = "0.1.0"

__all__ = ["to_ascii_punct"]
