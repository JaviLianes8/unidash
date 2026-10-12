"""Vendored mapping from Unicode punctuation to its plain ASCII equivalent.

Keys are code points, so the source stays ASCII and easy to review. Only punctuation is
listed. Letters, accented or not, are deliberately absent, so the fold leaves words intact
and never transliterates.
"""

from __future__ import annotations

_SINGLE_QUOTES = (0x2018, 0x2019, 0x201A, 0x201B, 0x2032, 0x2035)
_DOUBLE_QUOTES = (0x201C, 0x201D, 0x201E, 0x201F, 0x2033, 0x2036)
_DASHES = (0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2015, 0x2212)
_BULLETS = (0x2022, 0x2023, 0x2043, 0x2219, 0x25E6)
_SPACES = (0x00A0, 0x1680, *range(0x2000, 0x200B), 0x202F, 0x205F, 0x3000)

_GROUPS: tuple[tuple[tuple[int, ...], str], ...] = (
    (_SINGLE_QUOTES, "'"),
    (_DOUBLE_QUOTES, '"'),
    (_DASHES, "-"),
    (_BULLETS, "*"),
    (_SPACES, " "),
)


def _build_table() -> dict[int, str]:
    table: dict[int, str] = {}
    for codepoints, replacement in _GROUPS:
        for codepoint in codepoints:
            table[codepoint] = replacement
    table[0x2026] = "..."
    return table


PUNCTUATION_TABLE = _build_table()
