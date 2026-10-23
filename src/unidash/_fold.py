"""Fold Unicode punctuation to ASCII in a single pass."""

from __future__ import annotations

from ._checks import require_text
from ._mapping import PUNCTUATION_TABLE


def to_ascii_punct(text: str) -> str:
    r"""Return ``text`` with Unicode punctuation folded to ASCII, letters untouched.

    Curly quotes become ``'`` and ``"``, the ellipsis ``...``, Unicode spaces a plain space,
    bullets ``*`` and fullwidth punctuation its ASCII character. Dashes follow
    ``fold_dashes(text)``: every general dash becomes ``-`` (wavy ones ``~``) and soft
    hyphens are dropped. Raises ``TypeError`` when ``text`` is not a str.

    >>> from unidash import to_ascii_punct
    >>> print(to_ascii_punct("\u201cHi\u201d\u2014it\u2019s 100\u00a0%\u2026"))
    "Hi"-it's 100 %...
    >>> to_ascii_punct("\uff081\uff09\u301c caf\u00e9") == "(1)~ caf\u00e9"
    True
    """
    return require_text(text).translate(PUNCTUATION_TABLE)
