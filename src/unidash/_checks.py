"""Argument checks shared by the public functions, with short messages."""

from __future__ import annotations

from ._tables import FORMS, Table, cached_table


def exact_str(value: str) -> str:
    # A str subclass may override translate or iteration; work on the plain characters.
    return str.__str__(value)


def require_text(text: object, label: str = "text") -> str:
    if not isinstance(text, str):
        raise TypeError(f"{label} must be a str")
    return exact_str(text)


def check_form(form: object) -> str:
    text = require_text(form, "form")
    if text not in FORMS:
        raise ValueError(f"form must be one of {', '.join(FORMS)}")
    return text


def check_flag(label: str, flag: object) -> bool:
    if not isinstance(flag, bool):
        raise TypeError(f"{label} must be a bool")
    return flag is True


def checked_table(form: object, script_hyphens: object, keep_soft_hyphens: object) -> Table:
    return cached_table(
        check_form(form),
        check_flag("script_hyphens", script_hyphens),
        check_flag("keep_soft_hyphens", keep_soft_hyphens),
    )
