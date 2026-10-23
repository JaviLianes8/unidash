"""The 1.0 promise of every public name: signatures, results, errors and their messages."""

from __future__ import annotations

import inspect
import pickle
from collections.abc import Callable
from typing import Any, get_args

import pytest

import unidash
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

EM, EN, SOFT = chr(0x2014), chr(0x2013), chr(0xAD)
OPTIONS = "form='ascii', *, script_hyphens=False, keep_soft_hyphens=False"
SIGNATURES = {
    fold_dashes: f"(text, {OPTIONS})",
    iter_fold_dashes: f"(chunks, {OPTIONS})",
    find_dashes: f"(text, {OPTIONS})",
    dash_table: f"({OPTIONS})",
    is_dash: "(char)",
    to_ascii_punct: "(text)",
}
FOLDERS: list[Callable[..., Any]] = [fold_dashes, iter_fold_dashes, find_dashes, dash_table]


def _call(function: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    if function is dash_table:
        return dash_table(*args[1:], **kwargs)
    if function is iter_fold_dashes:
        return list(iter_fold_dashes([args[0]], *args[1:], **kwargs))
    return function(*args, **kwargs)


@pytest.mark.parametrize("function", list(SIGNATURES), ids=lambda f: f.__name__)
def test_signatures_are_pinned(function: Callable[..., Any]) -> None:
    signature = inspect.signature(function)
    plain = signature.replace(
        parameters=[p.replace(annotation=p.empty) for p in signature.parameters.values()],
        return_annotation=inspect.Signature.empty,
    )
    assert str(plain) == SIGNATURES[function]


def test_the_form_type_lists_the_three_forms() -> None:
    assert get_args(Form) == ("ascii", "tex", "typographic")


def test_dashes_is_the_unicode_dash_property() -> None:
    expected = {0x2D, 0x58A, 0x5BE, 0x1400, 0x1806, 0x2053, 0x207B, 0x208B, 0x2212, 0x301C}
    expected |= {*range(0x2010, 0x2016), 0x2E17, 0x2E1A, 0x2E3A, 0x2E3B, 0x2E40, 0x2E5D}
    expected |= {0x3030, 0x30A0, 0xFE31, 0xFE32, 0xFE58, 0xFE63, 0xFF0D, 0x10D6E, 0x10EAD}
    assert {ord(char) for char in DASHES} == expected
    assert type(DASHES) is frozenset


def test_results_are_plain_types() -> None:
    assert type(fold_dashes(EM)) is str
    assert type(to_ascii_punct(EM)) is str
    assert type(is_dash(EM)) is bool
    assert type(dash_table()) is dict
    (hit,) = find_dashes(EM)
    assert type(hit) is DashHit
    assert all(type(chunk) is str for chunk in iter_fold_dashes([EM, "a"]))


def test_dash_hit_is_a_named_tuple_that_pickles_as_public() -> None:
    hit = DashHit(4, 2, 3, EM, "EM DASH")
    assert DashHit._fields == ("offset", "line", "column", "char", "name")
    assert tuple(hit) == (4, 2, 3, EM, "EM DASH")
    assert DashHit.__module__ == "unidash"
    assert b"unidash._" not in pickle.dumps(hit)
    assert pickle.loads(pickle.dumps(hit)) == hit
    assert repr(hit).startswith("DashHit(offset=4, line=2, column=3, char=")


@pytest.mark.parametrize("function", FOLDERS, ids=lambda f: f.__name__)
def test_every_folder_checks_its_options_the_same_way(function: Callable[..., Any]) -> None:
    with pytest.raises(ValueError, match=r"^form must be one of ascii, tex, typographic, not 'x'$"):
        _call(function, "a", "x")
    with pytest.raises(TypeError, match=r"^form must be a str, not NoneType$"):
        _call(function, "a", None)
    for flag in ("script_hyphens", "keep_soft_hyphens"):
        with pytest.raises(TypeError, match=f"^{flag} must be a bool, not str$"):
            _call(function, "a", **{flag: "yes"})
        with pytest.raises(TypeError, match=f"^{flag} must be a bool, not int$"):
            _call(function, "a", **{flag: 0})
    with pytest.raises(TypeError):
        _call(function, "a", "ascii", True)


@pytest.mark.parametrize("function", [fold_dashes, find_dashes, to_ascii_punct])
def test_text_must_be_a_str(function: Callable[..., Any]) -> None:
    for bad, name in ((b"a", "bytes"), (None, "NoneType"), (["a"], "list")):
        with pytest.raises(TypeError, match=f"^text must be a str, not {name}$"):
            function(bad)


def test_a_bad_chunk_is_named_when_it_is_read() -> None:
    stream = iter_fold_dashes(["a", 5])  # type: ignore[list-item]
    assert next(stream) == "a"
    with pytest.raises(TypeError, match=r"^chunk must be a str, not int$"):
        next(stream)


def test_is_dash_errors() -> None:
    with pytest.raises(TypeError, match=r"^char must be a str, not int$"):
        is_dash(45)  # type: ignore[arg-type]
    for bad, count in (("", 0), ("--", 2), (EM * 3, 3)):
        with pytest.raises(ValueError, match=f"^char must be a single character, not {count} "):
            is_dash(bad)


@pytest.mark.parametrize("size", [41, 1000, 1_000_000])
def test_messages_quote_at_most_forty_characters(size: int) -> None:
    form = "x" * size
    with pytest.raises(ValueError) as raised:
        fold_dashes("a", form)  # type: ignore[arg-type]
    message = str(raised.value)
    assert message.endswith(f"not {'x' * 40!r}... ({size} characters)")
    assert len(message) < 120


def test_a_forty_character_form_is_quoted_whole() -> None:
    with pytest.raises(ValueError, match=f"not {'y' * 40!r}$"):
        fold_dashes("a", "y" * 40)  # type: ignore[arg-type]


class Sneaky(str):
    def translate(self, table: Any) -> str:
        return "overridden"

    def __iter__(self) -> Any:
        return iter("")

    def __eq__(self, other: object) -> bool:
        return True

    def __hash__(self) -> int:
        return 0


def test_str_subclasses_are_read_as_their_characters() -> None:
    text = Sneaky("a" + EM + SOFT)
    assert fold_dashes(text) == "a-"
    assert type(fold_dashes(text)) is str
    assert to_ascii_punct(text) == "a-"
    assert [hit.offset for hit in find_dashes(text)] == [1, 2]
    assert list(iter_fold_dashes([text], "tex")) == ["a---"]
    assert is_dash(Sneaky(EM))
    assert not is_dash(Sneaky("a"))


def test_a_str_subclass_form_must_spell_a_form() -> None:
    with pytest.raises(ValueError, match="not 'zzz'"):
        fold_dashes(EM, Sneaky("zzz"))  # type: ignore[arg-type]
    assert fold_dashes(EM, Sneaky("tex")) == "---"  # type: ignore[arg-type]


def test_dash_table_is_fresh_and_equals_what_fold_uses() -> None:
    for form in get_args(Form):
        for script in (False, True):
            for keep in (False, True):
                table = dash_table(form, script_hyphens=script, keep_soft_hyphens=keep)
                every = "".join(sorted(DASHES)) + SOFT
                expected = fold_dashes(every, form, script_hyphens=script, keep_soft_hyphens=keep)
                assert every.translate(table) == expected
                assert table is not dash_table(form, script_hyphens=script, keep_soft_hyphens=keep)


def test_find_dashes_reports_exactly_what_fold_changes() -> None:
    text = "a" + EM + "-" + chr(0x5BE) + SOFT + EN + chr(0x207B)
    for form in get_args(Form):
        for script in (False, True):
            hits = list(find_dashes(text, form, script_hyphens=script))
            changed = [
                i
                for i, char in enumerate(text)
                if fold_dashes(char, form, script_hyphens=script) != char
            ]
            assert [hit.offset for hit in hits] == changed
            assert all(text[hit.offset] == hit.char for hit in hits)


def test_the_package_lists_nothing_private() -> None:
    assert all(not name.startswith("_") for name in unidash.__all__)
    public = {name for name in vars(unidash) if not name.startswith("_")}
    assert public == set(unidash.__all__)
