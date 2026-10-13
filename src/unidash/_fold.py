"""Fold Unicode punctuation to ASCII in a single pass."""

from __future__ import annotations

from ._mapping import PUNCTUATION_TABLE


def to_ascii_punct(text: str) -> str:
    """Return ``text`` with Unicode punctuation folded to ASCII, letters untouched.

    Dashes follow ``fold_dashes(text)``: every general dash becomes ``-`` (wavy ones ``~``)
    and soft hyphens are dropped.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, not {type(text).__name__}")
    return text.translate(PUNCTUATION_TABLE)
