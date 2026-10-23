"""The command line tool's input and output: long folds, encodings, the byte order mark on
stdin, exact form names, bounded usage errors, a missing stderr and write errors."""

from __future__ import annotations

import errno
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from unidash import fold_dashes
from unidash._cli import _parser, _reader_left, main
from unidash._tables import BLOCK

EM, EN, BOM = chr(0x2014), chr(0x2013), chr(0xFEFF)
ROOT = Path(__file__).resolve().parents[1]


class Run:
    def __init__(self, monkeypatch: pytest.MonkeyPatch, stdin: bytes = b"", err: bool = True):
        self.out = io.BytesIO()
        self.err = io.StringIO()
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(stdin)))
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(self.out))
        monkeypatch.setattr(sys, "stderr", self.err if err else None)


def _file(tmp_path: Path, name: str, data: bytes) -> str:
    path = tmp_path / name
    path.write_bytes(data)
    return str(path)


def _long_text() -> str:
    pattern = "a" + EM + "b" + EN + chr(0x2E3B) + chr(0xAD) + "\r\n"
    return (pattern * (2 * BLOCK // len(pattern) + 2))[: 2 * BLOCK + 1]


@pytest.mark.parametrize("from_file", [False, True])
def test_a_fold_longer_than_one_block_is_written_whole(
    from_file: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = _long_text().encode()
    run = Run(monkeypatch, b"" if from_file else data)
    args = [_file(tmp_path, "long.txt", data)] if from_file else []
    assert main(["--form", "tex", *args]) == 0
    assert run.out.getvalue() == fold_dashes(_long_text(), "tex").encode()


def test_a_file_that_is_not_utf8_is_an_error_and_others_still_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = _file(tmp_path, "latin1.txt", b"caf\xe9 " + EM.encode())
    good = _file(tmp_path, "good.txt", EM.encode())
    run = Run(monkeypatch)
    assert main([bad, good]) == 2
    assert run.out.getvalue() == b"-"
    assert run.err.getvalue().startswith(f"unidash: {bad}: ")


@pytest.mark.parametrize("args", [[], ["-"]])
def test_a_bom_on_stdin_is_kept(args: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, (BOM + EM).encode())
    assert main(args) == 0
    assert run.out.getvalue() == b"\xef\xbb\xbf-"


@pytest.mark.parametrize("form", ["ASCII", "Tex", "TYPOGRAPHIC"])
def test_form_names_are_case_sensitive(form: str, monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, EM.encode())
    with pytest.raises(SystemExit) as raised:
        main(["--form", form])
    assert raised.value.code == 2
    assert run.out.getvalue() == b""


@pytest.mark.parametrize("args", [["--x" + "Q" * 20_000], ["--check=" + "Q" * 20_000]])
def test_a_huge_unknown_argument_is_cut_short(
    args: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    run = Run(monkeypatch)
    with pytest.raises(SystemExit) as raised:
        main(args)
    assert raised.value.code == 2
    error = run.err.getvalue()
    assert len(error) < 1000, len(error)
    assert error.startswith("usage: unidash")
    assert "QQQQ" in error and "characters)" in error


@pytest.mark.parametrize(("size", "cut"), [(199, False), (200, False), (201, True)])
def test_usage_errors_are_cut_only_past_two_hundred_characters(
    size: int, cut: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = Run(monkeypatch)
    message = "m" * (size - 1) + "z"
    with pytest.raises(SystemExit):
        _parser().error(message)
    last = run.err.getvalue().splitlines()[-1]
    whole = f"unidash: error: {message}"
    assert last == (f"{whole[:-1]}... ({size} characters)" if cut else whole)


@pytest.mark.parametrize("check", [[], ["--check"]])
def test_with_no_stderr_diagnostics_stay_out_of_the_output(
    check: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    good = _file(tmp_path, "good.txt", ("x" + EM).encode())
    run = Run(monkeypatch, err=False)
    monkeypatch.setattr(sys, "stdin", None)
    assert main([*check, str(tmp_path / "nope.txt"), "-", good]) == 2
    sys.stdout.flush()
    expected = f"{good}:1:2: U+2014 EM DASH\n".encode() if check else b"x-"
    assert run.out.getvalue() == expected


def test_with_no_stderr_a_usage_error_writes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, err=False)
    with pytest.raises(SystemExit) as raised:
        main(["--form", "latex"])
    assert raised.value.code == 2
    sys.stdout.flush()
    assert run.out.getvalue() == b""


def test_a_process_without_stderr_writes_only_data(tmp_path: Path) -> None:
    good = _file(tmp_path, "good.txt", ("x" + EM).encode())
    code = (
        "import sys; sys.stderr = None; from unidash._cli import main; "
        f"raise SystemExit(main(['nope.txt', {good!r}]))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        timeout=120,
    )
    assert (result.returncode, result.stdout, result.stderr) == (2, b"x-", b"")


class _FullDisk(io.BytesIO):
    def write(self, data: object) -> int:
        raise OSError(errno.ENOSPC, "No space left on device")


def test_a_write_error_other_than_a_closed_reader_is_raised(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    Run(monkeypatch, EM.encode())
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(_FullDisk()))
    with pytest.raises(OSError) as raised:
        main([])
    assert raised.value.errno == errno.ENOSPC


@pytest.mark.parametrize(
    ("error", "platform", "left"),
    [
        (BrokenPipeError(), "linux", True),
        (OSError(errno.EPIPE, "pipe"), "linux", True),
        (OSError(errno.EINVAL, "invalid"), "win32", True),
        (OSError(errno.EINVAL, "invalid"), "linux", False),
        (OSError(errno.ENOSPC, "full"), "win32", False),
        (OSError(errno.ENOSPC, "full"), "linux", False),
    ],
)
def test_only_a_reader_that_left_counts_as_one(
    error: OSError, platform: str, left: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", platform)
    assert _reader_left(error) is left
