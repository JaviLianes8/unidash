"""The Markdown block rules the GUIDE names, checked with full renders of the `tex` form.

Python-Markdown (`smarty`) and the markdown-it-py typographer are optional, as in
test_oracles.py; each test skips when either package is absent.
"""

from __future__ import annotations

import html
from collections.abc import Callable

import pytest

from unidash import fold_dashes

EN, EM = chr(0x2013), chr(0x2014)
Render = Callable[[str], str]


def _python_markdown(text: str) -> str:
    markdown = pytest.importorskip("markdown")
    out = markdown.markdown(fold_dashes(text, "tex"), extensions=["smarty"])
    return html.unescape(out).strip()


def _markdown_it(text: str) -> str:
    markdown_it = pytest.importorskip("markdown_it")
    md = markdown_it.MarkdownIt("commonmark", {"typographer": True}).enable("replacements")
    return html.unescape(md.render(fold_dashes(text, "tex"))).strip()


BOTH = [_python_markdown, _markdown_it]


@pytest.mark.parametrize("render", BOTH)
def test_a_line_that_starts_the_text_follows_the_block_rules(render: Render) -> None:
    # Indented code keeps its hyphens; a line of only dashes and spaces that folds to three
    # hyphens or more is a thematic break, and a lone en dash reads back.
    for indent in ("    ", "\t"):
        assert render(indent + "pages 10" + EN + "20") == "<pre><code>pages 10--20\n</code></pre>"
    assert "<pre>" not in render("   pages 10" + EN + "20")
    for rule in (EM, " " + EM + " ", EN + " " + EM, EN + "  " + EN, EM + "  " + EM):
        assert render(rule) == "<hr />"
    assert render(EN) == "<p>" + EN + "</p>"


@pytest.mark.parametrize("render", BOTH)
def test_a_line_after_a_blank_line_follows_the_same_rules(render: Render) -> None:
    assert render("Title\n\n" + EM) == "<p>Title</p>\n<hr />"
    assert render("Title\n\n" + EN) == "<p>Title</p>\n<p>" + EN + "</p>"
    code = "<p>Some text</p>\n<pre><code>pages 10--20\n</code></pre>"
    assert render("Some text\n\n    pages 10" + EN + "20") == code


@pytest.mark.parametrize("render", BOTH)
def test_touching_dashes_under_a_line_of_text_make_it_a_heading(render: Render) -> None:
    # A setext underline, even a single en dash: the dashes are lost.
    for line in (EN, EM, EN + " ", EM + " ", EN + EM):
        assert render("Title\n" + line) == "<h2>Title</h2>"


@pytest.mark.parametrize("render", BOTH)
def test_an_indented_line_under_a_line_of_text_continues_the_paragraph(render: Render) -> None:
    for indent in ("    ", "\t"):
        out = render("Some text\n" + indent + "pages 10" + EN + "20")
        assert out.startswith("<p>Some text\n") and out.endswith("pages 10" + EN + "20</p>")


@pytest.mark.parametrize("render", BOTH)
def test_spaced_dashes_under_a_line_of_text_are_a_thematic_break(render: Render) -> None:
    for line in (EN + " " + EN, EN + " " + EM, EN + "  " + EM):
        assert render("Title\n" + line) == "<p>Title</p>\n<hr />"


def test_python_markdown_reads_back_dashes_three_spaces_apart() -> None:
    for line in (EN + "   " + EN, EM + "   " + EM, EM + "    " + EN):
        assert _python_markdown(line) == "<p>" + line + "</p>"
        assert _python_markdown("Title\n" + line) == "<p>Title\n" + line + "</p>"
        assert _markdown_it(line) == "<hr />"
        assert _markdown_it("Title\n" + line) == "<p>Title</p>\n<hr />"


def test_only_markdown_it_takes_an_underline_after_leading_spaces() -> None:
    for line in (" " + EN, "   " + EN, " " + EM):
        assert _markdown_it("Title\n" + line) == "<h2>Title</h2>"
    assert _python_markdown("Title\n " + EN) == "<p>Title\n " + EN + "</p>"
    assert _python_markdown("Title\n " + EM) == "<p>Title</p>\n<hr />"


def test_markdown_it_underlines_the_whole_paragraph() -> None:
    for text in ("A\nB", "A\nB\nC"):
        for line in (EN, EM, EN + EN, EN + EM, " " + EN):
            assert _markdown_it(text + "\n" + line) == "<h2>" + text + "</h2>"


def test_python_markdown_reads_dashes_under_a_later_line_as_a_rule_or_text() -> None:
    # Only the first line of a block takes an underline there; later lines use the
    # thematic break rule, so a lone en dash reads back.
    for text in ("A\nB", "A\nB\nC"):
        for line in (EN, EN + " ", " " + EN):
            assert _python_markdown(text + "\n" + line) == "<p>" + text + "\n" + line + "</p>"
        for line in (EM, EN + EN, EN + EM, " " + EM):
            assert _python_markdown(text + "\n" + line) == "<p>" + text + "</p>\n<hr />"


def test_python_markdown_underlines_any_first_line_of_a_block() -> None:
    cases = {
        EM + "\n" + EN: ("<h2>" + EM + "</h2>", "<hr />\n<p>" + EN + "</p>"),
        EM + "\n" + EM: ("<h2>" + EM + "</h2>", "<hr />\n<hr />"),
        EN + " " + EN + "\n" + EM: ("<h2>" + EN + " " + EN + "</h2>", "<hr />\n<hr />"),
        "Intro\n\n" + EM + "\n" + EN: (
            "<p>Intro</p>\n<h2>" + EM + "</h2>",
            "<p>Intro</p>\n<hr />\n<p>" + EN + "</p>",
        ),
        "- item\n" + EN: ("<h2>- item</h2>", "<ul>\n<li>item\n" + EN + "</li>\n</ul>"),
        "> q\n" + EN: ("<h2>> q</h2>", "<blockquote>\n<p>q\n" + EN + "</p>\n</blockquote>"),
    }
    for text, (python_markdown, markdown_it) in cases.items():
        assert _python_markdown(text) == python_markdown, text
        assert _markdown_it(text) == markdown_it, text


@pytest.mark.parametrize("render", BOTH)
def test_a_block_starts_after_a_heading_or_a_thematic_break(render: Render) -> None:
    assert render("# H\nTitle\n" + EN) == "<h1>H</h1>\n<h2>Title</h2>"
    assert render("Title\n" + EN + "\nNext\n" + EN) == "<h2>Title</h2>\n<h2>Next</h2>"
    assert render(EM + "\nA\n" + EN) == "<hr />\n<h2>A</h2>"
    assert render("A\n" + EM + " " + EM + "\nB\n" + EN) == "<p>A</p>\n<hr />\n<h2>B</h2>"
    # A code line or a `#` heading never takes an underline.
    assert render("    code\n" + EN) == "<pre><code>code\n</code></pre>\n<p>" + EN + "</p>"
    assert render("# H\n" + EN) == "<h1>H</h1>\n<p>" + EN + "</p>"


def test_after_a_rule_in_a_paragraph_python_markdown_starts_a_new_block() -> None:
    text = "A\nB\n" + EM + "\nC\n" + EN
    assert _python_markdown(text) == "<p>A\nB</p>\n<hr />\n<h2>C</h2>"
    assert _markdown_it(text) == "<h2>A\nB</h2>\n<h2>C</h2>"
