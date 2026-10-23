"""find_dashes, is_dash, DASHES, dash_table, iter_fold_dashes and interpreter checks."""

from __future__ import annotations

import random
import sys
import unicodedata

import pytest

import unidash._hit
from unidash import (
    DASHES,
    DashHit,
    Form,
    dash_table,
    find_dashes,
    fold_dashes,
    is_dash,
    iter_fold_dashes,
    to_ascii_punct,
)
from unidash._classes import COMPATIBILITY, GENERAL, KEPT, SCRIPT_HYPHENS
from unidash._hit import scan

EM, EN, SOFT, MAQAF = chr(0x2014), chr(0x2013), chr(0xAD), chr(0x5BE)
FORMS: tuple[Form, ...] = ("ascii", "tex", "typographic")


def test_find_reports_line_column_and_name() -> None:
    hits = list(find_dashes("ok\nab" + EM + "c\n" + SOFT))
    assert hits == [DashHit(5, 2, 3, EM, "EM DASH"), DashHit(8, 3, 1, SOFT, "SOFT HYPHEN")]
    assert hits[0].codepoint == "U+2014"
    assert hits[1].codepoint == "U+00AD"


def test_find_follows_the_fold_options() -> None:
    assert list(find_dashes(MAQAF + SOFT, keep_soft_hyphens=True)) == []
    assert [h.char for h in find_dashes(MAQAF, script_hyphens=True)] == [MAQAF]
    assert list(find_dashes(EM + EN, "typographic")) == []


def test_find_names_do_not_depend_on_the_interpreter_tables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class NoNames:
        @staticmethod
        def name(char: str, default: str) -> str:
            return default

    monkeypatch.setattr(unidash._hit, "unicodedata", NoNames)
    (hit,) = find_dashes(chr(0x10EAD), script_hyphens=True)
    assert (hit.name, hit.codepoint) == ("YEZIDI HYPHENATION MARK", "U+10EAD")
    (unknown,) = scan("a" + chr(0x378), {0x378: "x"})
    assert (unknown.name, unknown.column) == ("U+0378", 2)


def test_find_counts_lines_like_an_editor() -> None:
    cr, lf = chr(13), chr(10)
    text = "a" + cr + "b" + EM + cr + lf + EM + lf + lf + "x" + EM
    assert [(h.line, h.column) for h in find_dashes(text)] == [(2, 2), (3, 1), (5, 2)]


def test_a_leading_bom_takes_no_column() -> None:
    bom = chr(0xFEFF)
    assert [(h.line, h.column) for h in find_dashes(bom + EM + chr(10) + EM)] == [(1, 1), (2, 1)]
    assert next(find_dashes("a" + bom + EM)).column == 3


def test_find_ignores_plain_ascii_and_counts_code_points() -> None:
    assert list(find_dashes("a-b -- c")) == []
    (hit,) = find_dashes(chr(0x1F600) + EM)
    assert (hit.offset, hit.column) == (1, 2)


def test_find_checks_its_arguments_eagerly() -> None:
    with pytest.raises(TypeError):
        find_dashes(5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        find_dashes("a", "none")  # type: ignore[arg-type]


def test_is_dash_follows_the_dash_property() -> None:
    assert is_dash("-") and is_dash(EM) and is_dash(MAQAF) and is_dash(chr(0x207B))
    assert not is_dash(SOFT) and not is_dash("a") and not is_dash(chr(0x2043))


@pytest.mark.parametrize("bad", ["", "--"])
def test_is_dash_needs_one_character(bad: str) -> None:
    with pytest.raises(ValueError, match="single character"):
        is_dash(bad)


def test_is_dash_needs_a_str() -> None:
    with pytest.raises(TypeError, match="not int"):
        is_dash(45)  # type: ignore[arg-type]


def test_dashes_is_a_frozenset_of_single_characters() -> None:
    assert isinstance(DASHES, frozenset)
    assert len(DASHES) == len(GENERAL) + len(SCRIPT_HYPHENS) + len(KEPT) == 31
    assert all(len(char) == 1 for char in DASHES)


def test_dash_table_matches_fold_and_is_a_fresh_copy() -> None:
    table = dash_table("tex", script_hyphens=True)
    assert (EM + MAQAF + SOFT).translate(table) == fold_dashes(
        EM + MAQAF + SOFT, "tex", script_hyphens=True
    )
    table[0x2014] = "X"
    assert dash_table("tex", script_hyphens=True)[0x2014] == "---"
    assert dash_table(keep_soft_hyphens=True).get(0xAD, "absent") == "absent"


def test_dash_table_checks_its_arguments() -> None:
    with pytest.raises(ValueError):
        dash_table("ASCII")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        dash_table(script_hyphens="yes")  # type: ignore[arg-type]


def test_chunked_folding_equals_whole_folding() -> None:
    rng = random.Random(7)
    alphabet = [*DASHES, SOFT, "a", "-", "\n", chr(0xE9)]
    for _ in range(200):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randrange(40)))
        cuts = sorted(rng.sample(range(len(text) + 1), min(3, len(text) + 1)))
        chunks = [text[a:b] for a, b in zip([0, *cuts], [*cuts, len(text)], strict=True)]
        for form in FORMS:
            joined = "".join(iter_fold_dashes(chunks, form, script_hyphens=True))
            assert joined == fold_dashes(text, form, script_hyphens=True)


def test_streaming_is_lazy_but_checks_options_eagerly() -> None:
    def chunks() -> object:
        yield EM
        raise AssertionError("read too far")

    stream = iter_fold_dashes(chunks())  # type: ignore[arg-type]
    assert next(stream) == "-"
    with pytest.raises(ValueError):
        iter_fold_dashes([], "nope")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be a str, not bytes"):
        list(iter_fold_dashes([b"a"]))  # type: ignore[list-item]


def test_every_pd_known_to_this_interpreter_is_classified() -> None:
    known = set(GENERAL) | set(SCRIPT_HYPHENS) | set(KEPT)
    pd = {cp for cp in range(sys.maxunicode + 1) if unicodedata.category(chr(cp)) == "Pd"}
    assert len(pd) >= 25
    assert pd <= known


def test_typographic_targets_are_the_nfkc_forms() -> None:
    for codepoint, target in COMPATIBILITY.items():
        assert unicodedata.normalize("NFKC", chr(codepoint)) == target, hex(codepoint)
    decomposable = {cp for cp in GENERAL if unicodedata.decomposition(chr(cp))}
    # The non-breaking hyphen decomposes to the hyphen, but its no-break promise is the point.
    assert set(COMPATIBILITY) == decomposable - {0x2011}


@pytest.mark.parametrize("form", ["ascii", "tex"])
def test_ascii_forms_always_produce_ascii(form: str) -> None:
    every = "".join(sorted(DASHES - {chr(cp) for cp in KEPT})) + SOFT
    assert fold_dashes(every, form, script_hyphens=True).isascii()  # type: ignore[arg-type]


def test_the_ascii_form_keeps_the_length_apart_from_soft_hyphens() -> None:
    every = "".join(sorted(DASHES))
    assert len(fold_dashes(every + SOFT, script_hyphens=True)) == len(every)


def test_to_ascii_punct_and_the_ascii_form_agree_on_every_dash() -> None:
    for char in [*DASHES, SOFT]:
        assert to_ascii_punct(char) == fold_dashes(char), hex(ord(char))
