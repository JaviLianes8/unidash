"""CLI diagnostics and repeated file arguments, through a real subprocess."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, "-m", "unidash", *args],
        input=b"",
        capture_output=True,
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        timeout=300,
    )


@pytest.mark.parametrize("size", [0, 1000])
def test_invalid_cli_forms_omit_the_received_value(size: int, tmp_path: Path) -> None:
    marker = "secret-token-7b41c9a0"
    result = _run(["--form", marker + "x" * size], tmp_path)
    assert result.returncode == 2
    assert result.stdout == b""
    assert marker.encode() not in result.stderr
    assert b"form must be one of ascii, tex, typographic" in result.stderr
    assert len(result.stderr) < 500


@pytest.mark.parametrize("check", [False, True])
def test_repeated_files_preserve_multiplicity_and_order(check: bool, tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a\u2014", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b\u2013", encoding="utf-8")
    result = _run((["--check"] if check else []) + ["a.txt", "b.txt", "a.txt"], tmp_path)
    assert result.returncode == int(check)
    assert result.stderr == b""
    expected = (
        b"a.txt:1:2: U+2014 EM DASH\nb.txt:1:2: U+2013 EN DASH\na.txt:1:2: U+2014 EM DASH\n"
        if check
        else b"a-b-a-"
    )
    assert result.stdout == expected
