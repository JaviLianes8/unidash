"""Argument checks shared by the public functions, with short messages."""

from __future__ import annotations

from ._tables import FORMS, Table, cached_table

# Error messages quote at most this many characters of a value the caller passed.
QUOTE_LIMIT = 40


def exact_str(value: str) -> str:
    # A str subclass may override translate or iteration; work on the plain characters.
    return str.__str__(value)


def require_text(text: object, label: str = "text") -> str:
    if not isinstance(text, str):
        raise TypeError(f"{label} must be a str, not {type(text).__name__}")
    return exact_str(text)


def quote(value: str) -> str:
    if len(value) <= QUOTE_LIMIT:
        return repr(value)
    return f"{value[:QUOTE_LIMIT]!r}... ({len(value)} characters)"


def check_form(form: object) -> str:
    text = require_text(form, "form")
    if text not in FORMS:
        raise ValueError(f"form must be one of {', '.join(FORMS)}, not {quote(text)}")
    return text


def check_flag(label: str, flag: object) -> bool:
    if not isinstance(flag, bool):
        raise TypeError(f"{label} must be a bool, not {type(flag).__name__}")
    return flag is True


def checked_table(form: object, script_hyphens: object, keep_soft_hyphens: object) -> Table:
    return cached_table(
        check_form(form),
        check_flag("script_hyphens", script_hyphens),
        check_flag("keep_soft_hyphens", keep_soft_hyphens),
    )
