"""Hand-written exact-form contracts for every form-taking API and the CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from unidash import dash_table, find_dashes, fold_dashes, iter_fold_dashes

ROOT = Path(__file__).resolve().parents[1]
FORMS = ("ascii", "tex", "typographic")
INVALID_FORMS = (
    [
        pytest.param(value, id=f"padded-{form}-{index}")
        for form in FORMS
        for index, value in enumerate((f" {form}", f"{form} ", f" {form} ", f"\t{form}\n"))
    ]
    + [
        pytest.param(form[:length], id=f"prefix-{form[:length]}")
        for form in FORMS
        for length in range(1, len(form))
    ]
    + [pytest.param("", id="empty")]
    + [
        pytest.param(
            "".join(chr(start + ord(char) - ord("a")) for char in form),
            id=f"compatibility-{style}-{form}",
        )
        for style, start in (("fullwidth", 0xFF41), ("circled", 0x24D0), ("bold", 0x1D41A))
        for form in FORMS
    ]
)


@pytest.mark.parametrize("form", INVALID_FORMS)
@pytest.mark.parametrize("function", [fold_dashes, iter_fold_dashes, find_dashes, dash_table])
def test_every_api_rejects_nonexact_forms(function: Callable[..., Any], form: str) -> None:
    # Iterator-returning APIs must reject options at the call, before any iteration.
    with pytest.raises(ValueError, match=r"^form must be one of ascii, tex, typographic$"):
        if function is dash_table:
            function(form=form)
        elif function is iter_fold_dashes:
            function(["x\u2014"], form=form)
        else:
            function("x\u2014", form=form)


@pytest.mark.parametrize("form", INVALID_FORMS)
@pytest.mark.parametrize("check", [False, True])
def test_cli_rejects_nonexact_forms(form: str, check: bool, tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "unidash", *(["--check"] if check else []), "--form", form],
        input="x\u2014".encode(),
        capture_output=True,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        timeout=300,
    )
    assert result.returncode == 2
    assert result.stdout == b""
    assert b"form must be one of ascii, tex, typographic" in result.stderr
