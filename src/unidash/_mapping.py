"""Vendored mapping from Unicode punctuation to its plain ASCII equivalent.

Keys are code points, so the source stays ASCII and easy to review. Only punctuation is
listed. Letters, accented or not, are deliberately absent, so the fold leaves words intact
and never transliterates. Dashes come from the ``ascii`` dash form, so both functions agree.
"""

from __future__ import annotations

from ._tables import dash_table

_SINGLE_QUOTES = (0x2018, 0x2019, 0x201A, 0x201B, 0x2032, 0x2035)
_DOUBLE_QUOTES = (0x201C, 0x201D, 0x201E, 0x201F, 0x2033, 0x2036)
_BULLETS = (0x2022, 0x2023, 0x2043, 0x2219, 0x25E6)
# Fullwidth forms of ASCII punctuation (CJK input); their NFKC form is the ASCII character.
# Fullwidth letters and digits are left alone, like every other letter.
_FULLWIDTH_PUNCT = (
    *range(0xFF01, 0xFF10),
    *range(0xFF1A, 0xFF21),
    *range(0xFF3B, 0xFF41),
    *range(0xFF5B, 0xFF5F),
)
_SPACES = (0x00A0, 0x1680, *range(0x2000, 0x200B), 0x202F, 0x205F, 0x3000)

_GROUPS: tuple[tuple[tuple[int, ...], str], ...] = (
    (_SINGLE_QUOTES, "'"),
    (_DOUBLE_QUOTES, '"'),
    (_BULLETS, "*"),
    (_SPACES, " "),
)


def _build_table() -> dict[int, str | None]:
    table = dash_table("ascii")
    for codepoints, replacement in _GROUPS:
        for codepoint in codepoints:
            table[codepoint] = replacement
    table.update({cp: chr(cp - 0xFEE0) for cp in _FULLWIDTH_PUNCT})
    table[0x2026] = "..."
    return table


PUNCTUATION_TABLE = _build_table()
