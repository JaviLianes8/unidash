"""Rejected inputs never become diagnostic contents. Cases are hand-written."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from unidash import dash_table, find_dashes, fold_dashes, is_dash, iter_fold_dashes, to_ascii_punct

FOLDERS: list[Callable[..., Any]] = [fold_dashes, find_dashes, iter_fold_dashes, dash_table]


@pytest.mark.parametrize("function", FOLDERS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("size", [0, 40, 41, 1000, 1_000_000])
def test_invalid_forms_omit_the_received_value(function: Callable[..., Any], size: int) -> None:
    form = "secret-token-7b41c9a0" + "x" * size
    args = [] if function is dash_table else [""]
    with pytest.raises(ValueError) as raised:
        function(*args, form=form)
    assert str(raised.value) == "form must be one of ascii, tex, typographic"


@pytest.mark.parametrize("name", ["X" * 1_000_000, "secret\n\x1b[31m"], ids=["huge", "controls"])
def test_type_errors_omit_received_class_names(name: str) -> None:
    bad = type(name, (), {})()
    calls: list[tuple[str, str, Callable[[], object]]] = [
        ("text", "str", lambda: fold_dashes(bad)),
        ("text", "str", lambda: find_dashes(bad)),
        ("text", "str", lambda: to_ascii_punct(bad)),
        ("char", "str", lambda: is_dash(bad)),
        ("chunk", "str", lambda: next(iter_fold_dashes([bad]))),
    ]
    for function in FOLDERS:
        args = [] if function is dash_table else [""]
        for label, expected in (
            ("form", "str"),
            ("script_hyphens", "bool"),
            ("keep_soft_hyphens", "bool"),
        ):
            with pytest.raises(TypeError) as raised:
                function(*args, **{label: bad})
            assert str(raised.value) == f"{label} must be a {expected}"
    for label, expected, call in calls:
        with pytest.raises(TypeError) as raised:
            call()
        assert str(raised.value) == f"{label} must be a {expected}"
