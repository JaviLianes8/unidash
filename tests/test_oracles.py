"""Independent programs agree with the library: regex for the Unicode properties, and four
typography converters for the TeX convention (two hyphens for an en dash, three for an em).

The oracles are optional (requirements-oracles.txt pins the versions used for 1.0.0); each
test skips when its package is absent.
"""

from __future__ import annotations

import html
import random
import re
import sys
from collections.abc import Callable

import pytest

from unidash import DASHES, fold_dashes
from unidash._classes import GENERAL, KEPT, SCRIPT_HYPHENS

EN, EM = chr(0x2013), chr(0x2014)
WORDS = ["a", "word", "10", "x1", "Pages", "z", "caf" + chr(0xE9), chr(0x4E2D) + chr(0x6587)]
# The sentence punctuation the GUIDE promises may touch a dash.
BEFORE, AFTER = ["", "", "("], ["", "", ".", ",", ";", ":", "?", "!", ")"]


def test_regex_dash_property_equals_the_dashes() -> None:
    regex = pytest.importorskip("regex")
    pattern = regex.compile(r"\p{Dash}")
    found = {chr(cp) for cp in range(sys.maxunicode + 1) if pattern.match(chr(cp))}
    assert found == DASHES


def test_regex_pd_category_is_classified() -> None:
    regex = pytest.importorskip("regex")
    pattern = regex.compile(r"\p{Pd}")
    found = {cp for cp in range(sys.maxunicode + 1) if pattern.match(chr(cp))}
    assert len(found) == 27
    assert found <= set(GENERAL) | set(SCRIPT_HYPHENS) | set(KEPT)


def _texts(seed: int, count: int = 300) -> list[str]:
    # Words (letters, digits, CJK) with sentence punctuation around them, joined by single en
    # or em dashes, with or without a space on each side, chosen apart. Adjacent dashes are
    # left out: in the TeX convention "-----" has no single reading. The first word is bare,
    # so the text never opens with a Markdown list marker.
    rng = random.Random(seed)
    texts = []
    for _ in range(count):
        parts = [rng.choice(WORDS)]
        for _ in range(rng.randrange(1, 6)):
            dash = rng.choice(["", " "]) + rng.choice([EN, EM, " "]) + rng.choice(["", " "])
            parts += [dash, rng.choice(BEFORE) + rng.choice(WORDS) + rng.choice(AFTER)]
        texts.append("".join(parts))
    return texts


def _python_markdown(text: str) -> str:
    markdown = pytest.importorskip("markdown")
    out = str(markdown.markdown(text, extensions=["smarty"]))
    assert out.startswith("<p>") and out.endswith("</p>"), out
    return html.unescape(out[3:-4])


def _markdown_it(text: str) -> str:
    markdown_it = pytest.importorskip("markdown_it")
    md = markdown_it.MarkdownIt("commonmark", {"typographer": True}).enable("replacements")
    return str(md.renderInline(text))


def _docutils(text: str) -> str:
    smartquotes = pytest.importorskip("docutils.utils.smartquotes")
    return str(smartquotes.educateDashesOldSchool(text))


def _smartypants(text: str) -> str:
    smartypants = pytest.importorskip("smartypants")
    return html.unescape(smartypants.smartypants(text, smartypants.Attr.D))


# markdown-it-py reads "--" as an en dash only with whitespace on both sides or on neither.
LOPSIDED_EN = re.compile(rf"(?<=\s){EN}(?=\S)|(?<=\S){EN}(?=\s)")


def _as_written(text: str) -> str:
    return text


def _lopsided_en_dashes_stay_hyphens(text: str) -> str:
    return LOPSIDED_EN.sub("--", text)


@pytest.mark.parametrize(
    ("oracle", "expected"),
    [
        (_python_markdown, _as_written),
        (_markdown_it, _lopsided_en_dashes_stay_hyphens),
        (_docutils, _as_written),
        (_smartypants, _as_written),
    ],
)
def test_converters_read_the_tex_form_back_as_the_original_dashes(
    oracle: Callable[[str], str], expected: Callable[[str], str]
) -> None:
    texts = _texts(1) + _texts(2)
    assert sum(1 for text in texts if LOPSIDED_EN.search(text)) > 50
    for text in texts:
        assert oracle(fold_dashes(text, "tex")) == expected(text), ascii(text)


def test_sentence_punctuation_touches_dashes_in_the_texts() -> None:
    texts = _texts(1) + _texts(2)
    touching = re.compile(rf"[.,;:?!()][{EN}{EM}]|[{EN}{EM}][(]")
    assert sum(1 for text in texts if touching.search(text)) > 50


@pytest.mark.parametrize("oracle", [_python_markdown, _markdown_it, _smartypants])
def test_a_backslash_before_a_dash_escapes_its_first_hyphen(
    oracle: Callable[[str], str],
) -> None:
    # The GUIDE names this exception; docutils has no escapes and reads the dash back.
    slash = chr(92)
    assert oracle(fold_dashes("a" + slash + EM + "b", "tex")) == "a-" + EN + "b"
    assert _docutils(fold_dashes("a" + slash + EM + "b", "tex")) == "a" + slash + EM + "b"


def test_markdown_it_reads_a_plus_before_a_dash_as_plus_minus() -> None:
    # The GUIDE names this exception: the replacements rule turns "+-" into U+00B1.
    assert _markdown_it(fold_dashes("a+" + EM + "b", "tex")) == "a" + chr(0xB1) + EN + "b"
    for oracle in (_python_markdown, _docutils, _smartypants):
        assert oracle(fold_dashes("a+" + EM + "b", "tex")) == "a+" + EM + "b"


def test_markdown_converters_leave_code_spans_as_written() -> None:
    # The GUIDE names this exception too.
    code = "x `a" + fold_dashes(EN, "tex") + "b` y"
    assert _python_markdown(code) == _markdown_it(code) == "x <code>a--b</code> y"


def test_markdown_it_leaves_an_en_dash_spaced_on_one_side_as_hyphens() -> None:
    for text in ("pages 10 " + EN + "20", "a" + EN + " b"):
        assert _markdown_it(fold_dashes(text, "tex")) == text.replace(EN, "--")


@pytest.mark.parametrize("oracle", [_python_markdown, _markdown_it, _docutils, _smartypants])
def test_the_other_short_dashes_read_back_as_en_or_em_dashes(
    oracle: Callable[[str], str],
) -> None:
    # Many to one, as the GUIDE says: the bar and the compatibility forms lose their identity.
    for codepoint, dash in ((0x2015, EM), (0xFE31, EM), (0xFE58, EM), (0xFE32, EN)):
        assert oracle("a " + fold_dashes(chr(codepoint), "tex") + " b") == "a " + dash + " b"


def test_smartypants_needs_old_school_dashes() -> None:
    smartypants = pytest.importorskip("smartypants")
    assert html.unescape(smartypants.smartypants("a -- b")) == "a " + EM + " b"


@pytest.mark.parametrize("oracle", [_docutils, _smartypants])
def test_converters_read_long_dashes_as_em_dashes(oracle: Callable[[str], str]) -> None:
    # The two-em and three-em dashes are as long as two and three em dashes.
    for char, count in ((chr(0x2E3A), 2), (chr(0x2E3B), 3)):
        assert oracle("a" + fold_dashes(char, "tex") + "b") == "a" + EM * count + "b"
