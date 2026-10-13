"""Fold, find and recognise dashes."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Iterator
from typing import NamedTuple

from ._classes import DASH_CODEPOINTS, NAMES
from ._tables import Form, Table, cached_table, check_options

BOM, CR, LF = chr(0xFEFF), chr(13), chr(10)

DASHES: frozenset[str] = frozenset(chr(cp) for cp in DASH_CODEPOINTS)


class DashHit(NamedTuple):
    """One character that a fold would change, with its place in the text."""

    offset: int
    line: int
    column: int
    char: str
    name: str

    @property
    def codepoint(self) -> str:
        """The code point in ``U+XXXX`` notation."""
        return f"U+{ord(self.char):04X}"


def _require_text(text: object) -> str:
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, not {type(text).__name__}")
    return text


def _table(form: Form, script_hyphens: bool, keep_soft_hyphens: bool) -> Table:
    check_options(form, script_hyphens, keep_soft_hyphens)
    return cached_table(form, script_hyphens, keep_soft_hyphens)


def fold_dashes(
    text: str,
    form: Form = "ascii",
    *,
    script_hyphens: bool = False,
    keep_soft_hyphens: bool = False,
) -> str:
    """Return ``text`` with its dashes folded to ``form``; everything else is untouched."""
    table = _table(form, script_hyphens, keep_soft_hyphens)
    return _require_text(text).translate(table)


def iter_fold_dashes(
    chunks: Iterable[str],
    form: Form = "ascii",
    *,
    script_hyphens: bool = False,
    keep_soft_hyphens: bool = False,
) -> Iterator[str]:
    """Fold each chunk lazily; the joined result equals folding the joined text."""
    table = _table(form, script_hyphens, keep_soft_hyphens)
    return (_require_text(chunk).translate(table) for chunk in chunks)


def is_dash(char: str) -> bool:
    """Return whether ``char`` has the Unicode Dash property (``-`` included)."""
    if not isinstance(char, str):
        raise TypeError(f"char must be a str, not {type(char).__name__}")
    if len(char) != 1:
        raise ValueError(f"char must be a single character, not {len(char)}")
    return char in DASHES


def char_name(char: str) -> str:
    known = NAMES.get(ord(char))
    if known is not None:
        return known
    fallback = f"U+{ord(char):04X}"
    return unicodedata.name(char, fallback)


def scan(text: str, table: Table) -> Iterator[DashHit]:
    # Lines end at LF, CR or CRLF, as editors count them; a leading BOM takes no column.
    text = _require_text(text)
    line, line_start = 1, 1 if text.startswith(BOM) else 0
    previous = ""
    for offset, char in enumerate(text):
        if char == LF and previous == CR:
            line_start = offset + 1
        elif char in (CR, LF):
            line, line_start = line + 1, offset + 1
        elif ord(char) in table:
            yield DashHit(offset, line, offset - line_start + 1, char, char_name(char))
        previous = char


def find_dashes(
    text: str,
    form: Form = "ascii",
    *,
    script_hyphens: bool = False,
    keep_soft_hyphens: bool = False,
) -> Iterator[DashHit]:
    """Yield every character that ``fold_dashes`` with the same options would change."""
    table = _table(form, script_hyphens, keep_soft_hyphens)
    return scan(_require_text(text), table)
