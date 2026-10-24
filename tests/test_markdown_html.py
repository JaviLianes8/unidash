"""The raw HTML block rules the GUIDE names, checked with full renders of the `tex` form.

Python-Markdown (`smarty`) and the markdown-it-py typographer are optional, as in
test_oracles.py; each test skips when either package is absent.
"""

from __future__ import annotations

import html

import pytest

from unidash import fold_dashes

EN, EM = chr(0x2013), chr(0x2014)
CODE = "<pre><code>pages 10--20\n</code></pre>"


def _python_markdown(text: str) -> str:
    markdown = pytest.importorskip("markdown")
    out = markdown.markdown(fold_dashes(text, "tex"), extensions=["smarty"])
    return html.unescape(out).strip()


def _markdown_it(text: str) -> str:
    markdown_it = pytest.importorskip("markdown_it")
    md = markdown_it.MarkdownIt("commonmark", {"typographer": True}).enable("replacements")
    return html.unescape(md.render(fold_dashes(text, "tex"))).strip()


def test_raw_html_keeps_the_hyphens_as_written() -> None:
    for tag in (
        "<div>a" + EN + "b</div>",
        "<p>a " + EM + " b</p>",
        "<pre>a" + EN + "b</pre>",
        "<!-- a " + EM + " b -->",
    ):
        assert _python_markdown(tag) == _markdown_it(tag) == fold_dashes(tag, "tex")


def test_only_python_markdown_ends_html_that_markdown_it_ends_at_a_blank_line() -> None:
    cases = {
        "<div>x</div>\n" + EN: ("<div>x</div>\n<p>" + EN + "</p>", "<div>x</div>\n--"),
        "<div>x</div>\n" + EM: ("<div>x</div>\n<hr />", "<div>x</div>\n---"),
        "<p>x</p>\n" + EN: ("<p>x</p>\n<p>" + EN + "</p>", "<p>x</p>\n--"),
        "<hr>\n" + EN: ("<hr>\n<p>" + EN + "</p>", "<hr>\n--"),
        "<hr>\n" + EM: ("<hr>\n<hr />", "<hr>\n---"),
        "<hr />\n" + EN: ("<hr />\n<p>" + EN + "</p>", "<hr />\n--"),
        "<section>x</section>\n" + EM: (
            "<section>x</section>\n<hr />",
            "<section>x</section>\n---",
        ),
        "<div><p>x</p></div>\n" + EN: (
            "<div><p>x</p></div>\n<p>" + EN + "</p>",
            "<div><p>x</p></div>\n--",
        ),
        "<div>x</div>\nTitle\n" + EN: ("<div>x</div>\n<h2>Title</h2>", "<div>x</div>\nTitle\n--"),
        "<div>x</div>\n    pages 10" + EN + "20": (
            "<div>x</div>\n" + CODE,
            "<div>x</div>\n    pages 10--20",
        ),
    }
    for text, (python_markdown, markdown_it) in cases.items():
        assert _python_markdown(text) == python_markdown, text
        assert _markdown_it(text) == markdown_it, text


@pytest.mark.parametrize(
    "block",
    [
        "<!-- c -->",
        "<!--\nc\n-->",
        "<pre>x</pre>",
        "<pre>\nx\n</pre>",
        "<script>x</script>",
        "<script>\nx\n</script>",
        "<style>x</style>",
        "<textarea>x</textarea>",
        "<?x?>",
        "<?php echo 1; ?>",
        "<!DOCTYPE html>",
        "<![CDATA[x]]>",
        "<![CDATA[a\nb]]>",
    ],
)
def test_both_start_a_new_block_after_html_that_ends_on_its_closing_line(block: str) -> None:
    cases = {
        EN: block + "\n<p>" + EN + "</p>",
        EM: block + "\n<hr />",
        "Title\n" + EN: block + "\n<h2>Title</h2>",
        "    pages 10" + EN + "20": block + "\n" + CODE,
    }
    for line, expected in cases.items():
        text = block + "\n" + line
        assert _python_markdown(text) == expected, text
        assert _markdown_it(text) == expected, text


def test_both_take_the_lines_under_a_tag_left_open_into_the_html_block() -> None:
    for tag in ("<div>", "<p>", "<div>x"):
        assert _python_markdown(tag + "\n" + EN) == _markdown_it(tag + "\n" + EN) == tag + "\n--"
        assert _python_markdown(tag + "\n" + EM) == _markdown_it(tag + "\n" + EM) == tag + "\n---"
        text = tag + "\nTitle\n" + EN
        assert _python_markdown(text) == _markdown_it(text) == tag + "\nTitle\n--"
