import pytest

from unidash import to_ascii_punct

LSQUO, RSQUO = chr(0x2018), chr(0x2019)
LDQUO, RDQUO = chr(0x201C), chr(0x201D)
LOW_DQUO = chr(0x201E)
PRIME, DOUBLE_PRIME = chr(0x2032), chr(0x2033)
EN_DASH, EM_DASH = chr(0x2013), chr(0x2014)
MINUS = chr(0x2212)
ELLIPSIS = chr(0x2026)
NBSP, THIN_SPACE, NNBSP, IDEO_SPACE = chr(0xA0), chr(0x2009), chr(0x202F), chr(0x3000)
BULLET = chr(0x2022)
ACCENTED = "caf" + chr(0xE9) + " na" + chr(0xEF) + "ve " + chr(0xF1) + "andu " + chr(0x4E2D)


def test_curly_single_quotes_become_straight() -> None:
    assert to_ascii_punct(LSQUO + "a" + RSQUO) == "'a'"


def test_curly_double_quotes_become_straight() -> None:
    assert to_ascii_punct(LDQUO + "word" + RDQUO) == '"word"'


def test_low_quotes_and_primes_fold() -> None:
    assert to_ascii_punct(LOW_DQUO + "a" + DOUBLE_PRIME) == '"a"'
    assert to_ascii_punct("5" + PRIME) == "5'"


def test_em_dash_becomes_hyphen() -> None:
    assert to_ascii_punct("a" + EM_DASH + "b") == "a-b"


def test_en_dash_becomes_hyphen() -> None:
    assert to_ascii_punct("1" + EN_DASH + "2") == "1-2"


def test_minus_sign_becomes_hyphen() -> None:
    assert to_ascii_punct(MINUS + "5") == "-5"


def test_ellipsis_char_becomes_three_dots() -> None:
    assert to_ascii_punct("wait" + ELLIPSIS) == "wait..."


def test_nbsp_becomes_space() -> None:
    assert to_ascii_punct("a" + NBSP + "b") == "a b"


def test_various_unicode_spaces_become_space() -> None:
    assert to_ascii_punct("a" + THIN_SPACE + "b" + NNBSP + "c" + IDEO_SPACE + "d") == "a b c d"


def test_bullet_becomes_asterisk() -> None:
    assert to_ascii_punct(BULLET + " item") == "* item"


def test_accented_letters_pass_through_unchanged() -> None:
    assert to_ascii_punct(ACCENTED) == ACCENTED


def test_plain_ascii_passes_through_unchanged() -> None:
    text = "Plain ASCII: 'quotes', -dash-, dots..."
    assert to_ascii_punct(text) == text


def test_mixed_string_folds_only_punctuation() -> None:
    cafe = "Caf" + chr(0xE9)
    source = LDQUO + cafe + RDQUO + EM_DASH + "it" + RSQUO + "s 100" + NBSP + "%" + ELLIPSIS
    assert to_ascii_punct(source) == '"' + cafe + "\"-it's 100 %..."


def test_empty_string_stays_empty() -> None:
    assert to_ascii_punct("") == ""


def test_non_string_input_is_rejected() -> None:
    with pytest.raises(TypeError):
        to_ascii_punct(123)  # type: ignore[arg-type]
