"""The dash classes against the fetched Unicode 18.0 data (UCD and UTS #39).

The files are not committed; `python scripts/fetch_vectors.py` fetches them. Without them
these tests skip. Sources are listed in tests/vectors/unicode/MANIFEST.txt.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from unidash import DASHES, fold_dashes
from unidash._classes import GENERAL, KEPT, NAMES, SCRIPT_HYPHENS, SOFT_HYPHEN

FOLDER = Path(__file__).resolve().parent / "vectors" / "unicode"


def _lines(name: str) -> list[str]:
    path = FOLDER / name
    if not path.is_file():
        pytest.skip(f"{name} not fetched; run python scripts/fetch_vectors.py")
    return path.read_text(encoding="utf-8").splitlines()


def _unicode_data() -> dict[int, tuple[str, str]]:
    rows: dict[int, tuple[str, str]] = {}
    for line in _lines("UnicodeData.txt"):
        fields = line.split(";")
        rows[int(fields[0], 16)] = (fields[1], fields[2])
    return rows


def _dash_property() -> set[int]:
    found: set[int] = set()
    for line in _lines("PropList.txt"):
        body = line.split("#")[0]
        if ";" not in body or body.split(";")[1].strip() != "Dash":
            continue
        span = body.split(";")[0].strip()
        first, _, last = span.partition("..")
        found.update(range(int(first, 16), int(last or first, 16) + 1))
    return found


def _confusables() -> dict[int, str]:
    targets: dict[int, str] = {}
    for line in _lines("confusables.txt"):
        body = line.lstrip(chr(0xFEFF)).split("#")[0]
        if body.count(";") < 2:
            continue
        source, target, _ = (part.strip() for part in body.split(";"))
        if " " not in source:
            targets[int(source, 16)] = "".join(chr(int(cp, 16)) for cp in target.split())
    return targets


def test_the_classes_are_exactly_the_dash_property() -> None:
    classified = set(GENERAL) | set(SCRIPT_HYPHENS) | set(KEPT)
    assert classified == _dash_property()
    assert {chr(cp) for cp in _dash_property()} == DASHES


def test_the_classes_do_not_overlap() -> None:
    sizes = len(GENERAL) + len(SCRIPT_HYPHENS) + len(KEPT)
    assert len(set(GENERAL) | set(SCRIPT_HYPHENS) | set(KEPT)) == sizes


def test_every_pd_code_point_is_classified() -> None:
    pd = {cp for cp, (_, category) in _unicode_data().items() if category == "Pd"}
    assert len(pd) == 27
    assert pd <= set(GENERAL) | set(SCRIPT_HYPHENS) | set(KEPT)


def test_the_stored_names_match_the_database() -> None:
    data = _unicode_data()
    for codepoint, name in NAMES.items():
        assert data[codepoint][0] == name, hex(codepoint)


def test_the_soft_hyphen_is_a_format_character() -> None:
    assert _unicode_data()[SOFT_HYPHEN] == ("SOFT HYPHEN", "Cf")
    assert SOFT_HYPHEN not in _dash_property()


def test_the_kept_minus_signs_are_math_symbols() -> None:
    data = _unicode_data()
    assert {data[cp][1] for cp in KEPT if cp != 0x2D} == {"Sm"}


# Confusables of "-" left alone on purpose, each for a reason other than being a letter.
NOT_DASHES = {
    0x02D7: "modifier letter minus sign: a tone mark in phonetic transcription",
    0x06D4: "Arabic full stop: ends a sentence",
    0x2043: "hyphen bullet: folds to * as a bullet in to_ascii_punct",
    0x2796: "heavy minus sign: an emoji",
    0x10191: "Roman uncia sign: a weight unit",
}


def test_every_confusable_of_hyphen_minus_folds_or_is_excluded() -> None:
    data = _unicode_data()
    sources = {cp for cp, target in _confusables().items() if target == "-"}
    assert len(sources) >= 10
    left = {cp for cp in sources if fold_dashes(chr(cp)) != "-"}
    letters = {cp for cp in left if data[cp][1][0] in "LM"}
    assert letters
    assert left - letters == set(NOT_DASHES)


def test_ascii_targets_agree_with_the_confusables() -> None:
    targets = _confusables()
    for codepoint, (ascii_char, _) in GENERAL.items():
        target = targets.get(codepoint)
        if target is not None and target.isascii() and target in "-~":
            assert ascii_char == target, hex(codepoint)


def test_the_wave_and_swung_dashes_are_tilde_confusables() -> None:
    targets = _confusables()
    assert targets[0x301C] == "~"
    assert targets[0x2053] == "~"
