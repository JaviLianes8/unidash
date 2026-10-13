"""The command line tool: filter, check, options and exit codes."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

import unidash
from unidash._cli import main

EM, EN, SOFT, MAQAF = chr(0x2014), chr(0x2013), chr(0xAD), chr(0x5BE)


class Run:
    def __init__(self, monkeypatch: pytest.MonkeyPatch, stdin: bytes = b"") -> None:
        self.out = io.BytesIO()
        self.err = io.StringIO()
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(stdin)))
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(self.out))
        monkeypatch.setattr(sys, "stderr", self.err)


def _file(tmp_path: Path, name: str, text: str) -> str:
    path = tmp_path / name
    path.write_bytes(text.encode("utf-8"))
    return str(path)


def test_stdin_is_filtered_to_stdout_byte_exactly(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, ("a" + EM + "b\r\nc" + SOFT + "d\n").encode())
    assert main([]) == 0
    assert run.out.getvalue() == b"a-b\r\ncd\n"


def test_files_are_written_in_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    one, two = _file(tmp_path, "1.txt", EN), _file(tmp_path, "2.txt", "x" + EM)
    run = Run(monkeypatch)
    assert main(["--form", "tex", one, two]) == 0
    assert run.out.getvalue() == b"--x---"


def test_dash_options_reach_the_fold(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, (MAQAF + SOFT + chr(0xFF0D) + EM).encode())
    assert main(["--form", "typographic", "--script-hyphens", "--keep-soft-hyphens", "-"]) == 0
    assert run.out.getvalue().decode() == chr(0x2010) + SOFT + "-" + EM


def test_punct_folds_all_punctuation(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, (chr(0x201C) + "q" + chr(0x201D) + EM).encode())
    assert main(["--punct"]) == 0
    assert run.out.getvalue() == b'"q"-'


def test_punct_refuses_dash_options(monkeypatch: pytest.MonkeyPatch) -> None:
    Run(monkeypatch)
    for extra in (["--form", "tex"], ["--script-hyphens"], ["--keep-soft-hyphens"]):
        with pytest.raises(SystemExit) as raised:
            main(["--punct", *extra])
        assert raised.value.code == 2


def test_check_lists_each_change_and_exits_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dirty = _file(tmp_path, "a.md", "ok\nx" + EM + "y" + SOFT + "\n")
    clean = _file(tmp_path, "b.md", "plain - text\n")
    run = Run(monkeypatch)
    assert main(["--check", dirty, clean]) == 1
    assert run.out.getvalue().decode().splitlines() == [
        f"{dirty}:2:2: U+2014 EM DASH",
        f"{dirty}:2:4: U+00AD SOFT HYPHEN",
    ]
    assert Path(dirty).read_text(encoding="utf-8") == "ok\nx" + EM + "y" + SOFT + "\n"


def test_check_is_clean_when_nothing_would_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _file(tmp_path, "a.md", EM + EN)
    run = Run(monkeypatch)
    assert main(["--check", "--form", "typographic", path]) == 0
    assert run.out.getvalue() == b""


def test_check_with_punct_names_other_characters(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, chr(0x2026).encode())
    assert main(["--check", "--punct", "-"]) == 1
    assert run.out.getvalue() == b"<stdin>:1:1: U+2026 HORIZONTAL ELLIPSIS\n"


def test_missing_file_is_an_error_but_others_still_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    good = _file(tmp_path, "good.txt", EM)
    run = Run(monkeypatch)
    assert main([str(tmp_path / "nope.txt"), good]) == 2
    assert run.out.getvalue() == b"-"
    assert "nope.txt" in run.err.getvalue()


def test_errors_win_over_findings_in_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dirty = _file(tmp_path, "a.txt", EM)
    Run(monkeypatch)
    assert main(["--check", dirty, str(tmp_path / "missing")]) == 2


def test_non_utf8_input_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Run(monkeypatch, b"caf\xe9")
    assert main([]) == 2
    assert run.err.getvalue().startswith("unidash: <stdin>: ")
    assert run.out.getvalue() == b""


def test_stdin_twice_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    Run(monkeypatch)
    with pytest.raises(SystemExit) as raised:
        main(["-", "-"])
    assert raised.value.code == 2


def test_unknown_form_is_a_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    Run(monkeypatch)
    with pytest.raises(SystemExit) as raised:
        main(["--form", "latex"])
    assert raised.value.code == 2


def test_version_flag(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--version"])
    assert raised.value.code == 0
    assert capsys.readouterr().out.strip() == f"unidash {unidash.__version__}"
