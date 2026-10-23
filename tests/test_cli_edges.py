"""The command line tool at the edges: a reader that leaves early, missing standard streams,
a huge --form value and each dash option on its own."""

from __future__ import annotations

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from unidash._cli import main

ROOT = Path(__file__).resolve().parents[1]
EM, SOFT, MAQAF = chr(0x2014), chr(0xAD), chr(0x5BE)


def _env() -> dict[str, str]:
    # The tool runs from the source tree, the same code the rest of the suite imports.
    env = dict(os.environ)
    parts = [str(ROOT / "src"), env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(part for part in parts if part)
    return env


def _close_early(args: list[str]) -> tuple[int, bytes]:
    process = subprocess.Popen(
        [sys.executable, "-m", "unidash", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_env(),
    )
    assert process.stdout is not None and process.stderr is not None
    assert process.stdout.read(64)
    process.stdout.close()
    errors = process.stderr.read()
    process.stderr.close()
    return process.wait(timeout=120), errors


def test_a_reader_that_leaves_early_stops_check_quietly(tmp_path: Path) -> None:
    big = tmp_path / "big.txt"
    big.write_bytes(("line " + EM + " x\n").encode() * 400_000)
    assert _close_early(["--check", str(big)]) == (1, b"")


def test_a_reader_that_leaves_early_stops_the_fold_quietly(tmp_path: Path) -> None:
    part = tmp_path / "part.txt"
    part.write_bytes(("x" + EM + "\n").encode() * 3000)
    assert _close_early([str(part)] * 300) == (1, b"")


class Streams:
    def __init__(self, monkeypatch: pytest.MonkeyPatch, stdin: bool, stdout: bool) -> None:
        self.out = io.BytesIO()
        self.err = io.StringIO()
        wrapped_in = io.TextIOWrapper(io.BytesIO(EM.encode()))
        monkeypatch.setattr(sys, "stdin", wrapped_in if stdin else None)
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(self.out) if stdout else None)
        monkeypatch.setattr(sys, "stderr", self.err)


def _file(tmp_path: Path) -> str:
    path = tmp_path / "a.txt"
    path.write_bytes(("a" + EM).encode())
    return str(path)


def test_files_do_not_need_stdin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    streams = Streams(monkeypatch, stdin=False, stdout=True)
    assert main([_file(tmp_path)]) == 0
    assert streams.out.getvalue() == b"a-"
    assert streams.err.getvalue() == ""


def test_a_missing_stdin_is_reported_and_other_files_still_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    streams = Streams(monkeypatch, stdin=False, stdout=True)
    assert main(["-", _file(tmp_path)]) == 2
    assert streams.out.getvalue() == b"a-"
    assert streams.err.getvalue() == "unidash: <stdin>: no standard input\n"


@pytest.mark.parametrize("check", [[], ["--check"]])
def test_a_missing_stdout_is_an_error(
    check: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    streams = Streams(monkeypatch, stdin=True, stdout=False)
    assert main([*check, _file(tmp_path)]) == 2
    assert streams.err.getvalue() == "unidash: no standard output\n"


def test_a_huge_form_value_is_quoted_short(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--form", "S" * 20_000])
    assert raised.value.code == 2
    error = capsys.readouterr().err
    assert len(error) < 500, len(error)
    assert "(20000 characters)" in error
    assert "ascii, tex, typographic" in error


def test_the_help_still_lists_the_forms(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--help"])
    assert "--form {ascii,tex,typographic}" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("option", "expected"),
    [("--script-hyphens", "-"), ("--keep-soft-hyphens", MAQAF + SOFT)],
)
def test_each_dash_option_works_on_its_own(
    option: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    streams = Streams(monkeypatch, stdin=True, stdout=True)
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO((MAQAF + SOFT).encode())))
    assert main([option]) == 0
    assert streams.out.getvalue().decode() == expected
