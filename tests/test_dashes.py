"""fold_dashes: the three forms, script hyphens, soft hyphens and argument checks."""

from __future__ import annotations

import pytest

from unidash import fold_dashes

HYPHEN, NB_HYPHEN, FIGURE = chr(0x2010), chr(0x2011), chr(0x2012)
EN, EM, BAR, MINUS = chr(0x2013), chr(0x2014), chr(0x2015), chr(0x2212)
TWO_EM, THREE_EM = chr(0x2E3A), chr(0x2E3B)
SMALL_EM, SMALL_HM, FULL_HM = chr(0xFE58), chr(0xFE63), chr(0xFF0D)
VERT_EM, VERT_EN = chr(0xFE31), chr(0xFE32)
WAVE, WAVY, SWUNG = chr(0x301C), chr(0x3030), chr(0x2053)
SOFT = chr(0xAD)
ARMENIAN, MAQAF, KANA_DOUBLE = chr(0x58A), chr(0x5BE), chr(0x30A0)
SUP_MINUS, SUB_MINUS = chr(0x207B), chr(0x208B)
HEBREW = chr(0x5E2) + MAQAF + chr(0x5D1)


def test_ascii_folds_every_general_dash_to_one_hyphen() -> None:
    source = HYPHEN + NB_HYPHEN + FIGURE + EN + EM + BAR + MINUS + TWO_EM + THREE_EM
    assert fold_dashes(source + SMALL_EM + SMALL_HM + FULL_HM + VERT_EM + VERT_EN) == "-" * 14


def test_wavy_dashes_become_a_tilde() -> None:
    assert fold_dashes("1" + WAVE + "2" + WAVY + SWUNG) == "1~2~~"


def test_ascii_is_the_default_form() -> None:
    assert fold_dashes(EM + EN) == fold_dashes(EM + EN, "ascii") == "--"


def test_tex_uses_two_hyphens_for_en_and_three_for_em() -> None:
    assert fold_dashes("1" + EN + "2", "tex") == "1--2"
    assert fold_dashes("a" + EM + "b" + BAR, "tex") == "a---b---"
    assert fold_dashes(VERT_EN + VERT_EM + SMALL_EM, "tex") == "-----" + "---"


def test_tex_widens_the_long_dashes() -> None:
    assert fold_dashes(TWO_EM, "tex") == "-" * 6
    assert fold_dashes(THREE_EM, "tex") == "-" * 9


def test_tex_keeps_hyphens_and_minus_single() -> None:
    assert fold_dashes(HYPHEN + NB_HYPHEN + FIGURE + MINUS + FULL_HM, "tex") == "-----"


def test_typographic_keeps_the_real_dashes() -> None:
    kept = HYPHEN + NB_HYPHEN + FIGURE + EN + EM + BAR + MINUS + TWO_EM + THREE_EM + WAVE
    assert fold_dashes(kept, "typographic") == kept


def test_typographic_unifies_the_compatibility_forms() -> None:
    source = SMALL_EM + VERT_EM + VERT_EN + SMALL_HM + FULL_HM
    assert fold_dashes(source, "typographic") == EM + EM + EN + "--"


def test_script_hyphens_stay_by_default() -> None:
    assert fold_dashes(HEBREW + ARMENIAN + KANA_DOUBLE) == HEBREW + ARMENIAN + KANA_DOUBLE


def test_script_hyphens_fold_on_request() -> None:
    folded = fold_dashes(MAQAF + ARMENIAN + KANA_DOUBLE, script_hyphens=True)
    assert folded == "---"
    assert fold_dashes(MAQAF + EN, "tex", script_hyphens=True) == "---"


def test_typographic_script_hyphens_become_the_unicode_hyphen() -> None:
    assert fold_dashes(MAQAF + ARMENIAN, "typographic", script_hyphens=True) == HYPHEN * 2


def test_soft_hyphens_are_dropped_by_default_in_every_form() -> None:
    for form in ("ascii", "tex", "typographic"):
        assert fold_dashes("co" + SOFT + "op" + SOFT, form) == "coop"


def test_soft_hyphens_can_be_kept() -> None:
    assert fold_dashes("co" + SOFT + "op" + EM, keep_soft_hyphens=True) == "co" + SOFT + "op-"


def test_superscript_and_subscript_minus_are_kept() -> None:
    text = "x" + SUP_MINUS + chr(0xB9) + " H" + SUB_MINUS
    for form in ("ascii", "tex", "typographic"):
        assert fold_dashes(text, form, script_hyphens=True) == text


def test_negative_numbers_keep_a_single_minus_in_every_ascii_form() -> None:
    assert fold_dashes(MINUS + "5 " + EN + " " + MINUS + "3", "tex") == "-5 -- -3"
    assert fold_dashes(MINUS + "5" + EN + MINUS + "3") == "-5--3"


def test_ascii_text_is_never_changed() -> None:
    text = "a-b -- --- 1-2 ~x~ = _"
    for form in ("ascii", "tex", "typographic"):
        assert fold_dashes(text, form, script_hyphens=True) == text


def test_letters_and_other_punctuation_are_untouched() -> None:
    text = "caf" + chr(0xE9) + " " + chr(0x201C) + chr(0x4E2D) + chr(0x2026) + chr(0x2043)
    assert fold_dashes(text) == text


def test_empty_text_stays_empty() -> None:
    assert fold_dashes("") == ""


def test_text_must_be_a_str() -> None:
    with pytest.raises(TypeError, match="text must be a str, not bytes"):
        fold_dashes(b"a")  # type: ignore[arg-type]


def test_unknown_form_is_rejected() -> None:
    with pytest.raises(ValueError, match="form must be one of ascii, tex, typographic"):
        fold_dashes("a", "latex")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="form"):
        fold_dashes("a", ["ascii"])  # type: ignore[arg-type]


@pytest.mark.parametrize("option", ["script_hyphens", "keep_soft_hyphens"])
def test_flags_must_be_bools(option: str) -> None:
    with pytest.raises(TypeError, match=f"{option} must be a bool, not int"):
        fold_dashes("a", **{option: 1})  # type: ignore[arg-type]


def test_options_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        fold_dashes("a", "ascii", True)  # type: ignore[misc]
