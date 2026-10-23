"""The command line tool and the names it is given: file names that are not valid Unicode or
very long, and --punct with an explicit --form."""

from __future__ import annotations

import errno
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from unidash._cli import main

ROOT = Path(__file__).resolve().parents[1]
EN, EM = chr(0x2013), chr(0x2014)
LONE = "lone" + chr(0xD800) + ".txt"


class Run:
    def __init__(self, monkeypatch: pytest.MonkeyPatch, stdin: bytes = b"") -> None:
        self.out = io.BytesIO()
        self.err = io.StringIO()
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(stdin)))
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(self.out))
        monkeypatch.setattr(sys, "stderr", self.err)


@pytest.mark.parametrize("form", ["ascii", "tex", "typographic"])
def test_punct_refuses_any_explicit_form(form: str, monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, EM.encode())
    with pytest.raises(SystemExit) as raised:
        main(["--punct", "--form", form])
    assert raised.value.code == 2
    assert "--punct cannot be combined with" in run.err.getvalue()
    assert run.out.getvalue() == b""


def test_an_explicit_ascii_form_is_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, (EM + EN).encode())
    assert main(["--form", "ascii"]) == 0
    assert run.out.getvalue() == b"--"


@pytest.mark.skipif(sys.platform != "win32", reason="only Windows names hold lone surrogates")
def test_check_reports_a_name_with_a_lone_surrogate_escaped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    Path(LONE).write_bytes(("a" + EN + "\n").encode())
    run = Run(monkeypatch)
    assert main(["--check", LONE]) == 1
    assert run.out.getvalue() == b"lone\\ud800.txt:1:2: U+2013 EN DASH\n"
    assert run.err.getvalue() == ""


@pytest.mark.skipif(sys.platform != "win32", reason="only Windows names hold lone surrogates")
def test_the_installed_tool_checks_a_name_with_a_lone_surrogate(tmp_path: Path) -> None:
    (tmp_path / LONE).write_bytes(("a" + EN + "\n").encode())
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "unidash", "--check", LONE],
        capture_output=True,
        cwd=tmp_path,
        env=env,
        timeout=120,
    )
    assert (result.returncode, result.stderr) == (1, b"")
    assert result.stdout.replace(b"\r\n", b"\n") == b"lone\\ud800.txt:1:2: U+2013 EN DASH\n"


@pytest.mark.parametrize("check", [[], ["--check"]])
def test_a_missing_name_with_a_lone_surrogate_is_reported(
    check: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # On POSIX the name cannot even be encoded for the system call; that is reported too.
    monkeypatch.chdir(tmp_path)
    run = Run(monkeypatch)
    assert main([*check, "nope" + chr(0xD800) + ".txt", "-"]) == 2
    assert run.err.getvalue().startswith("unidash: nope")
    assert len(run.err.getvalue().splitlines()) == 1


def test_a_missing_file_is_reported_with_its_name_and_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    run = Run(monkeypatch)
    assert main(["nope.txt"]) == 2
    assert run.err.getvalue() == f"unidash: nope.txt: {os.strerror(errno.ENOENT)}\n"


@pytest.mark.parametrize("check", [[], ["--check"]])
def test_a_huge_file_name_is_cut_short_in_the_error(
    check: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    run = Run(monkeypatch)
    assert main([*check, "S" * 30_000 + ".txt"]) == 2
    error = run.err.getvalue()
    assert len(error) < 500, len(error)
    assert error.startswith(
        "unidash: " + "S" * 100 + "..." + "S" * 96 + ".txt (30004 characters): "
    )
    assert error.count("S") == 196


@pytest.mark.parametrize(("size", "cut"), [(200, False), (201, True)])
def test_file_names_are_shortened_only_past_two_hundred_characters(
    size: int, cut: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    name = "a" + "n" * (size - 5) + ".txt"
    run = Run(monkeypatch)
    assert main([name]) == 2
    shown = f"{name[:100]}...{name[-100:]} ({size} characters)" if cut else name
    assert run.err.getvalue() == f"unidash: {shown}: {os.strerror(errno.ENOENT)}\n"


def test_the_installed_tool_cuts_a_huge_file_name_short(tmp_path: Path) -> None:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "unidash", "S" * 20_000],
        capture_output=True,
        cwd=tmp_path,
        env=env,
        timeout=120,
    )
    assert result.returncode == 2
    assert len(result.stderr) < 500, len(result.stderr)
