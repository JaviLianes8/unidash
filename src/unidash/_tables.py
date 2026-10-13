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


def check_options(form: object, script_hyphens: object, keep_soft_hyphens: object) -> None:
    if not isinstance(form, str) or form not in FORMS:
        raise ValueError(f"form must be one of {', '.join(FORMS)}, not {form!r}")
    for label, flag in (
        ("script_hyphens", script_hyphens),
        ("keep_soft_hyphens", keep_soft_hyphens),
    ):
        if not isinstance(flag, bool):
            raise TypeError(f"{label} must be a bool, not {type(flag).__name__}")


@cache
def cached_table(form: str, script_hyphens: bool, keep_soft_hyphens: bool) -> Table:
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


def dash_table(
    form: Form = "ascii", *, script_hyphens: bool = False, keep_soft_hyphens: bool = False
) -> dict[int, str | None]:
    """Return a fresh ``str.translate`` table for ``form``; ``None`` values delete."""
    check_options(form, script_hyphens, keep_soft_hyphens)
    return dict(cached_table(form, script_hyphens, keep_soft_hyphens))
