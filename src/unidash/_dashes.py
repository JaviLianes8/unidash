"""Fold, find and recognise dashes."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from ._checks import checked_table, require_text
from ._classes import DASH_CODEPOINTS
from ._hit import DashHit, scan
from ._tables import Form

DASHES: frozenset[str] = frozenset(chr(cp) for cp in DASH_CODEPOINTS)


def fold_dashes(
    text: str,
    form: Form = "ascii",
    *,
    script_hyphens: bool = False,
    keep_soft_hyphens: bool = False,
) -> str:
    r"""Return ``text`` with its dashes folded to ``form``; everything else is untouched.

    ``ascii`` turns every general dash into ``-`` (wavy dashes into ``~``), ``tex`` writes
    en dashes as ``--`` and em dashes as ``---``, and ``typographic`` keeps real dashes and
    replaces only the small, vertical and fullwidth forms. Soft hyphens are removed unless
    ``keep_soft_hyphens`` is true; script hyphens fold only when ``script_hyphens`` is true.

    Raises ``TypeError`` when ``text`` or ``form`` is not a str or a flag is not a bool,
    and ``ValueError`` for an unknown form.

    >>> from unidash import fold_dashes
    >>> fold_dashes("10\u201320 \u2014 \u22125")
    '10-20 - -5'
    >>> fold_dashes("10\u201320 \u2014 \u22125", "tex")
    '10--20 --- -5'
    >>> print(ascii(fold_dashes("a\uFE58b\uFF0Dc", "typographic")))
    'a\u2014b-c'
    >>> fold_dashes("co\u00ADop")
    'coop'
    """
    table = checked_table(form, script_hyphens, keep_soft_hyphens)
    return require_text(text).translate(table)


def iter_fold_dashes(
    chunks: Iterable[str],
    form: Form = "ascii",
    *,
    script_hyphens: bool = False,
    keep_soft_hyphens: bool = False,
) -> Iterator[str]:
    r"""Fold each chunk lazily; the joined result equals folding the joined text.

    The options are checked at once; each chunk is checked when it is read and must be a
    str (``TypeError`` otherwise).

    >>> from unidash import iter_fold_dashes
    >>> list(iter_fold_dashes(["a\u2013", "\u2014b"], "tex"))
    ['a--', '---b']
    """
    table = checked_table(form, script_hyphens, keep_soft_hyphens)
    return (require_text(chunk, "chunk").translate(table) for chunk in chunks)


def is_dash(char: str) -> bool:
    r"""Return whether ``char`` has the Unicode Dash property (``-`` included).

    The answer comes from the Unicode 18.0 data built into the library, not from the
    interpreter. Raises ``TypeError`` for a non-str and ``ValueError`` unless ``char`` is
    exactly one character.

    >>> from unidash import is_dash
    >>> is_dash("\u2212"), is_dash("-"), is_dash("\u00AD"), is_dash("a")
    (True, True, False, False)
    """
    char = require_text(char, "char")
    if len(char) != 1:
        raise ValueError(f"char must be a single character, not {len(char)} characters")
    return char in DASHES


def find_dashes(
    text: str,
    form: Form = "ascii",
    *,
    script_hyphens: bool = False,
    keep_soft_hyphens: bool = False,
) -> Iterator[DashHit]:
    r"""Yield a ``DashHit`` for every character ``fold_dashes`` with the same options changes.

    Arguments are checked at once (same errors as ``fold_dashes``); the hits come lazily,
    in text order.

    >>> from unidash import find_dashes
    >>> for hit in find_dashes("ok\u2014\nso\u00ADft"):
    ...     print(hit.line, hit.column, hit.codepoint, hit.name)
    1 3 U+2014 EM DASH
    2 3 U+00AD SOFT HYPHEN
    >>> list(find_dashes("\u2013", "typographic"))
    []
    """
    table = checked_table(form, script_hyphens, keep_soft_hyphens)
    return scan(require_text(text), table)


def dash_table(
    form: Form = "ascii", *, script_hyphens: bool = False, keep_soft_hyphens: bool = False
) -> dict[int, str | None]:
    r"""Return a fresh ``str.translate`` table for ``form``; ``None`` values delete.

    The table maps code points to their replacement, exactly as ``fold_dashes`` uses it, and
    is a new dict on every call, so changing it changes nothing else.

    >>> from unidash import dash_table
    >>> table = dash_table("tex")
    >>> table[0x2014], table[0x00AD]
    ('---', None)
    >>> "a\u2014b".translate(table)
    'a---b'
    """
    return dict(checked_table(form, script_hyphens, keep_soft_hyphens))
