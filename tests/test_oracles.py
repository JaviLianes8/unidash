"""Independent programs agree with the library: regex for the Unicode properties, and four
typography converters for the TeX convention (two hyphens for an en dash, three for an em).

The oracles are optional (requirements-oracles.txt pins the versions used for 1.0.0); each
test skips when its package is absent.
"""

from __future__ import annotations

import html
import random
import sys
from collections.abc import Callable

import pytest

from unidash import DASHES, fold_dashes
from unidash._classes import GENERAL, KEPT, SCRIPT_HYPHENS

EN, EM = chr(0x2013), chr(0x2014)
WORDS = ["a", "word", "10", "x1", "Pages", "z"]


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
    # Words joined by single en or em dashes, with or without spaces around them. Adjacent
    # dashes are left out: in the TeX convention "-----" has no single reading.
    rng = random.Random(seed)
    texts = []
    for _ in range(count):
        parts = [rng.choice(WORDS)]
        for _ in range(rng.randrange(1, 6)):
            space = rng.choice(["", " "])
            parts += [space + rng.choice([EN, EM, " "]) + space, rng.choice(WORDS)]
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


@pytest.mark.parametrize("oracle", [_python_markdown, _markdown_it, _docutils, _smartypants])
def test_converters_read_the_tex_form_back_as_the_original_dashes(
    oracle: Callable[[str], str],
) -> None:
    for seed in (1, 2):
        for text in _texts(seed):
            assert oracle(fold_dashes(text, "tex")) == text, ascii(text)


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
