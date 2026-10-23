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
# U+DC80 to U+DCFF stand for undecodable bytes only in POSIX names; in Windows names they are
# lone surrogates like the others.
SURROGATES = [0xD800, 0xDBFF, 0xDC00, 0xDC7F, 0xDC80, 0xDCFF, 0xDD00, 0xDFFF]


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


def _escaped(point: int) -> bytes:
    return f"lone\\u{point:04x}.txt:1:2: U+2013 EN DASH\n".encode()


@pytest.mark.skipif(sys.platform != "win32", reason="only Windows names hold lone surrogates")
@pytest.mark.parametrize("point", SURROGATES)
def test_check_reports_a_name_with_a_lone_surrogate_escaped(
    point: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    name = "lone" + chr(point) + ".txt"
    Path(name).write_bytes(("a" + EN + "\n").encode())
    run = Run(monkeypatch)
    assert main(["--check", name]) == 1
    assert run.out.getvalue() == _escaped(point)
    assert run.err.getvalue() == ""


@pytest.mark.skipif(sys.platform != "win32", reason="only Windows names hold lone surrogates")
@pytest.mark.parametrize("point", [0xD800, 0xDC80, 0xDCFF])
def test_the_installed_tool_checks_a_name_with_a_lone_surrogate(point: int, tmp_path: Path) -> None:
    name = "lone" + chr(point) + ".txt"
    (tmp_path / name).write_bytes(("a" + EN + "\n").encode())
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "unidash", "--check", name],
        capture_output=True,
        cwd=tmp_path,
        env=env,
        timeout=120,
    )
    assert (result.returncode, result.stderr) == (1, b"")
    assert result.stdout.replace(b"\r\n", b"\n") == _escaped(point)


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


@pytest.mark.parametrize(
    ("handler", "expected"),
    [("surrogateescape", b"x\x80"), ("surrogatepass", b"x\\udc80"), ("strict", b"x\\udc80")],
)
def test_report_names_follow_the_file_system_error_handler(
    handler: str, expected: bytes, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Only POSIX (surrogateescape) names stand for bytes; elsewhere every lone surrogate is
    # escaped. A POSIX system cannot open a name holding any other surrogate, so such a name
    # is never reported by --check and is simply escaped whole here.
    from unidash import _cli

    monkeypatch.setattr(sys, "getfilesystemencodeerrors", lambda: handler)
    assert _cli._name_bytes("x" + chr(0xDC80)) == expected
    assert _cli._name_bytes("x" + chr(0xDC80) + chr(0xD800)) == b"x\\udc80\\ud800"
    assert _cli._name_bytes("x" + chr(0x1F600)) == b"x" + chr(0x1F600).encode()


def test_check_writes_a_long_readable_name_whole(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Only the unreadable-file message is shortened; the --check prefix is the name as given.
    monkeypatch.chdir(tmp_path)
    name = "a" * 206 + ".txt"
    try:
        Path(name).write_bytes(("x" + EM + "\n").encode())
    except OSError:
        pytest.skip("this system refuses paths this long")
    run = Run(monkeypatch)
    assert main(["--check", name, "b" * 206 + ".txt"]) == 2
    assert run.out.getvalue() == (name + ":1:2: U+2014 EM DASH\n").encode()
    shown = "b" * 100 + "..." + "b" * 96 + ".txt (210 characters)"
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


@pytest.mark.parametrize("check", [[], ["--check"]])
def test_a_name_with_a_nul_is_reported_and_others_still_run(
    check: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The system call refuses the name with ValueError, on every platform.
    monkeypatch.chdir(tmp_path)
    run = Run(monkeypatch, EM.encode())
    assert main([*check, "a" + chr(0) + "b.txt", "-"]) == 2
    assert run.err.getvalue().startswith("unidash: a")
    assert run.out.getvalue() == (b"<stdin>:1:1: U+2014 EM DASH\n" if check else b"-")
