"""Build the ``str.translate`` tables for each dash form."""

from __future__ import annotations

from functools import cache
from typing import Literal, get_args

from ._classes import (
    COMPATIBILITY,
    GENERAL,
    SCRIPT_HYPHENS,
    SOFT_HYPHEN,
    TEX_WIDTHS,
    TYPOGRAPHIC_HYPHEN,
)

Form = Literal["ascii", "tex", "typographic"]
FORMS: tuple[str, ...] = get_args(Form)

Table = dict[int, str | None]


@cache
def cached_table(form: str, script_hyphens: bool, keep_soft_hyphens: bool) -> Table:
    # Callers pass checked, exact values only, so the cache holds at most twelve tables.
    table: Table
    if form == "typographic":
        table = dict(COMPATIBILITY.items())
        script_target = TYPOGRAPHIC_HYPHEN
    else:
        table = {cp: ascii_char for cp, (ascii_char, _) in GENERAL.items()}
        if form == "tex":
            table.update({cp: "-" * width for cp, width in TEX_WIDTHS.items()})
        script_target = "-"
    if script_hyphens:
        table.update(dict.fromkeys(SCRIPT_HYPHENS, script_target))
    if not keep_soft_hyphens:
        table[SOFT_HYPHEN] = None
    return table
