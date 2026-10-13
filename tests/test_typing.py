"""The public API is typed: mypy infers results and rejects bad calls."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

api = pytest.importorskip("mypy.api")

SRC = Path(__file__).resolve().parents[1] / "src"

SNIPPET = """
import unidash as u
reveal_type(u.fold_dashes("a"))
reveal_type(u.iter_fold_dashes(["a"], "tex"))
reveal_type(next(u.find_dashes("a")).line)
reveal_type(u.is_dash("a"))
reveal_type(u.dash_table("typographic"))
reveal_type(u.DASHES)
reveal_type(u.to_ascii_punct("a"))
u.fold_dashes("a", "latex")
u.fold_dashes(b"a")
u.fold_dashes("a", "ascii", True)
u.fold_dashes("a", script_hyphens="yes")
u.iter_fold_dashes("a", form="html")
f: u.Form = "typographic"
"""


@pytest.fixture(scope="module")
def mypy_output(tmp_path_factory: pytest.TempPathFactory) -> str:
    folder = tmp_path_factory.mktemp("typing")
    target = folder / "snippet.py"
    target.write_text(SNIPPET, encoding="utf-8")
    config = folder / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {SRC.as_posix()}\n", encoding="utf-8")
    cache = str(folder / "cache")
    out, err, _ = api.run(
        ["--strict", "--config-file", str(config), "--cache-dir", cache, str(target)]
    )
    return str(out) + str(err)


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (3, r"builtins\.str"),
        (4, r"typing\.Iterator\[builtins\.str\]"),
        (5, r"builtins\.int"),
        (6, r"builtins\.bool"),
        (7, r"builtins\.dict\[builtins\.int, builtins\.str \| None\]"),
        (8, r"builtins\.frozenset\[builtins\.str\]"),
        (9, r"builtins\.str"),
    ],
)
def test_results_are_typed(mypy_output: str, line: int, expected: str) -> None:
    # Older mypy releases print the builtins prefix, newer ones do not.
    pattern = expected.replace(r"builtins\.", r"(builtins\.)?")
    assert re.search(rf'snippet\.py:{line}: note: Revealed type is "{pattern}"', mypy_output), (
        mypy_output
    )


@pytest.mark.parametrize(
    ("line", "code"),
    [(10, "arg-type"), (11, "arg-type"), (12, "call-arg"), (13, "arg-type"), (14, "arg-type")],
)
def test_wrong_calls_are_rejected(mypy_output: str, line: int, code: str) -> None:
    assert re.search(rf"snippet\.py:{line}: error: .*\[{code}\]", mypy_output), mypy_output


def test_the_form_alias_accepts_its_values(mypy_output: str) -> None:
    assert not re.search(r"snippet\.py:15: error", mypy_output), mypy_output
