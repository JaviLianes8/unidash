"""The README examples run and print what they say; metadata agrees with the code."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import unidash
from unidash import Form, fold_dashes
from unidash._classes import NAMES

ROOT = Path(__file__).resolve().parents[1]
FORMS: tuple[Form, ...] = ("ascii", "tex", "typographic")
NOTES = "Draft\nDone " + chr(0x2014) + " ship it\nco" + chr(0xAD) + "op\n"


def _readme() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def _blocks() -> list[str]:
    return re.findall(r"```python\n(.*?)```", _readme(), flags=re.DOTALL)


def test_the_readme_has_its_four_examples() -> None:
    assert len(_blocks()) == 4


@pytest.mark.parametrize("index", range(4))
def test_each_example_prints_what_its_comments_say(
    index: int, capsys: pytest.CaptureFixture[str]
) -> None:
    block = _blocks()[index]
    exec(compile(block, "README.md", "exec"), {"__name__": "readme"})
    comments = re.findall(r"^# (.+)$", block, flags=re.MULTILINE)
    printed = capsys.readouterr().out.splitlines()
    assert printed == comments
    assert len(printed) >= 1


def test_the_command_line_example_matches_the_tool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    from unidash._cli import main

    monkeypatch.chdir(tmp_path)
    Path("notes.md").write_bytes(NOTES.encode("utf-8"))
    transcript = []
    for argv in (["--check", "notes.md"], ["--form", "tex", "notes.md"]):
        main(argv)
        out = capsysbinary.readouterr().out.decode("utf-8")
        transcript += [f"$ unidash {' '.join(argv)}", *out.splitlines()]
    assert "```\n" + "\n".join(transcript) + "\n```" in _readme()


def test_the_classification_table_lists_every_known_character() -> None:
    flat = " ".join(_readme().split())
    for codepoint, name in NAMES.items():
        row = f"| U+{codepoint:04X} | {name} |"
        assert f"U+{codepoint:04X} {name}" in flat or row in flat, name


def _cell(char: str, folded: str) -> str:
    if folded == char:
        return "kept"
    if folded == "":
        return "removed"
    return f"`{folded}`" if folded.isascii() else f"U+{ord(folded):04X}"


def test_every_table_cell_matches_the_fold() -> None:
    rows = re.findall(r"^\| U\+([0-9A-F]{4,5}) \| [^|]+ \|(.+)\|$", _readme(), re.MULTILINE)
    assert len(rows) == 22
    for codepoint, cells in rows:
        char = chr(int(codepoint, 16))
        expected = [_cell(char, fold_dashes(char, form)) for form in FORMS]
        assert [cell.strip() for cell in cells.split("|")] == expected, codepoint


def test_every_public_name_appears_in_the_readme() -> None:
    for name in unidash.__all__:
        assert f"`{name}" in _readme() or name == "Form", name


def test_the_guide_covers_every_public_name() -> None:
    guide = (ROOT / "GUIDE.md").read_text(encoding="utf-8")
    for name in unidash.__all__:
        assert f"`{name}" in guide, name


def test_readme_links_are_absolute() -> None:
    for target in re.findall(r"\]\(([^)]+)\)", _readme()):
        assert target.startswith("https://"), target


def test_version_matches_pyproject() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, flags=re.MULTILINE)
    assert match is not None
    assert match.group(1) == unidash.__version__


def test_changelog_has_an_entry_for_this_version() -> None:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{unidash.__version__}]" in text


def _shipped() -> list[Path]:
    return [
        *ROOT.glob("*.md"),
        *ROOT.glob("*.toml"),
        *ROOT.glob("src/**/*.py"),
        *ROOT.glob("tests/*.py"),
        *ROOT.glob("scripts/*"),
        ROOT / "tests" / "vectors" / "unicode" / "MANIFEST.txt",
    ]


def test_no_em_dash_in_any_shipped_text() -> None:
    for path in _shipped():
        assert chr(0x2014) not in path.read_text(encoding="utf-8"), path


def test_sources_are_ascii_so_invisible_dashes_cannot_hide() -> None:
    for path in [*ROOT.glob("src/**/*.py"), *ROOT.glob("tests/*.py"), *ROOT.glob("scripts/*")]:
        assert path.read_text(encoding="utf-8").isascii(), path


def test_every_source_file_stays_under_two_hundred_lines() -> None:
    for path in _shipped():
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 200, path
