"""Fold Unicode punctuation to ASCII in a single pass."""

from __future__ import annotations

from ._mapping import PUNCTUATION_TABLE


def to_ascii_punct(text: str) -> str:
    """Return ``text`` with Unicode punctuation folded to ASCII, letters untouched."""
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    return text.translate(PUNCTUATION_TABLE)
