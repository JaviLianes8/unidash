# unidash

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

Fold Unicode dashes and punctuation to plain ASCII while leaving letters untouched.

Text pasted from word processors, PDFs, CJK input methods and web pages is full of
characters that look like `-` but are not: en and em dashes, the minus sign, the
non-breaking hyphen, fullwidth and small forms, and the invisible soft hyphen. They break
search, diffs, command lines and parsers. `unidash` knows every character with the Unicode
18.0 Dash property, plus the soft hyphen, and folds them the way you choose.

The full contract of every function is in the
[guide](https://github.com/JaviLianes8/unidash/blob/main/GUIDE.md), and every change is in
the [changelog](https://github.com/JaviLianes8/unidash/blob/main/CHANGELOG.md).

## Install

```
pip install unidash
```

Python 3.10 or newer, no dependencies.

## Dashes

`fold_dashes(text, form="ascii")` has three forms. `ascii` turns every dash into one `-`
(wavy dashes into `~`). `tex` keeps the en and em dash apart the way TeX and Markdown do, as
`--` and `---`. `typographic` keeps the real dashes and only replaces the small, vertical and
fullwidth compatibility forms with their standard counterparts.

```python
from unidash import fold_dashes

text = "Pages 10\u201320 \u2014 see \u22125\uff0d6"
print(fold_dashes(text))
print(fold_dashes(text, "tex"))
print(ascii(fold_dashes("a\ufe58b\uff0dc", "typographic")))
# Pages 10-20 - see -5-6
# Pages 10--20 --- see -5-6
# 'a\u2014b-c'
```

A minus sign is always a single `-` in the `ascii` and `tex` forms (`typographic` keeps
U+2212), so negative numbers stay negative, and characters that are already ASCII are never
touched: `1-2` and a hand-written `--` come out as they went in.

## Soft hyphens, non-breaking hyphens and script hyphens

The soft hyphen (U+00AD) is a hint for where a word may break, not a character, so it is
removed unless you pass `keep_soft_hyphens=True`. The non-breaking hyphen (U+2011) becomes
`-` in the ASCII forms and stays in `typographic`, where its promise matters.

Hyphens that belong to one script (Armenian, the Hebrew maqaf, Canadian syllabics,
Mongolian, the katakana double hyphen, Garay and Yezidi) are left alone, like that script's
letters, unless you pass `script_hyphens=True`.

```python
from unidash import fold_dashes

print(fold_dashes("co\u00adop\u00aderate"))
print(ascii(fold_dashes("co\u00adop", keep_soft_hyphens=True)))
print(ascii(fold_dashes("\u05e2\u05be\u05d1")))
print(ascii(fold_dashes("\u05e2\u05be\u05d1", script_hyphens=True)))
# cooperate
# 'co\xadop'
# '\u05e2\u05be\u05d1'
# '\u05e2-\u05d1'
```

## Finding dashes

`find_dashes` yields a `DashHit` (offset, line, column, character and Unicode name) for
every character `fold_dashes` would change with the same options, which makes a lint or a
pre-commit check a one-liner. Lines end at LF, CR or CRLF, columns count code points from 1,
and a byte order mark at the start of the text takes no column. `is_dash(char)` tells whether
a character has the Unicode Dash property and `DASHES` is that set. `dash_table(...)` returns the `str.translate` table, and
`iter_fold_dashes(chunks, ...)` folds an iterable of strings lazily, for large inputs.

```python
from unidash import find_dashes, is_dash, iter_fold_dashes

for hit in find_dashes("first line\nsecond\u2014line\u00ad"):
    print(hit.line, hit.column, hit.codepoint, hit.name)
print(is_dash("\u2212"), is_dash("\u00ad"))
print("".join(iter_fold_dashes(["a\u2013", "b"])))
# 2 7 U+2014 EM DASH
# 2 12 U+00AD SOFT HYPHEN
# True False
# a-b
```

## All punctuation

`to_ascii_punct(text)` folds the rest of the typographic punctuation too: curly quotes become
`'` and `"`, the ellipsis becomes `...`, non-breaking and other Unicode spaces become a normal
space, bullets become `*`, fullwidth punctuation from CJK input (U+FF01 to U+FF5E, letters and
digits excepted) becomes its ASCII character, and dashes follow the `ascii` form. Accented
letters pass through.

```python
from unidash import to_ascii_punct

print(to_ascii_punct("\u201cCaf\u00e9\u201d\u2014it\u2019s 100\u00a0%\u2026"))
# "Café"-it's 100 %...
```

## Command line

`unidash FILE...` writes the folded text to stdout (`-` or no file reads stdin). It takes
`--form`, `--script-hyphens`, `--keep-soft-hyphens`, and `--punct` for the full punctuation
fold. `--check` lists what would change and exits 1, for pre-commit hooks. Input must be
UTF-8; an unreadable or non UTF-8 file is reported on stderr, the other files are still
processed, and the exit code is 2.

```
$ unidash --check notes.md
notes.md:2:6: U+2014 EM DASH
notes.md:3:3: U+00AD SOFT HYPHEN
$ unidash --form tex notes.md
Draft
Done --- ship it
coop
```

## What counts as a dash

The classes follow the Unicode 18.0 Dash property and General_Category=Pd, and the tests
check them against the Unicode data files and the UTS #39 confusables list.

| Code point | Name | `ascii` | `tex` | `typographic` |
| --- | --- | --- | --- | --- |
| U+2010 | HYPHEN | `-` | `-` | kept |
| U+2011 | NON-BREAKING HYPHEN | `-` | `-` | kept |
| U+2012 | FIGURE DASH | `-` | `-` | kept |
| U+2013 | EN DASH | `-` | `--` | kept |
| U+2014 | EM DASH | `-` | `---` | kept |
| U+2015 | HORIZONTAL BAR | `-` | `---` | kept |
| U+2212 | MINUS SIGN | `-` | `-` | kept |
| U+2E17 | DOUBLE OBLIQUE HYPHEN | `-` | `-` | kept |
| U+2E1A | HYPHEN WITH DIAERESIS | `-` | `-` | kept |
| U+2E3A | TWO-EM DASH | `-` | `------` | kept |
| U+2E3B | THREE-EM DASH | `-` | `---------` | kept |
| U+2E40 | DOUBLE HYPHEN | `-` | `-` | kept |
| U+2E5D | OBLIQUE HYPHEN | `-` | `-` | kept |
| U+FE31 | PRESENTATION FORM FOR VERTICAL EM DASH | `-` | `---` | U+2014 |
| U+FE32 | PRESENTATION FORM FOR VERTICAL EN DASH | `-` | `--` | U+2013 |
| U+FE58 | SMALL EM DASH | `-` | `---` | U+2014 |
| U+FE63 | SMALL HYPHEN-MINUS | `-` | `-` | `-` |
| U+FF0D | FULLWIDTH HYPHEN-MINUS | `-` | `-` | `-` |
| U+2053 | SWUNG DASH | `~` | `~` | kept |
| U+301C | WAVE DASH | `~` | `~` | kept |
| U+3030 | WAVY DASH | `~` | `~` | kept |
| U+00AD | SOFT HYPHEN | removed | removed | removed |

Script hyphens, folded only with `script_hyphens=True` (to `-`, or to U+2010 in
`typographic`): U+058A ARMENIAN HYPHEN, U+05BE HEBREW PUNCTUATION MAQAF, U+1400 CANADIAN
SYLLABICS HYPHEN, U+1806 MONGOLIAN TODO SOFT HYPHEN, U+30A0 KATAKANA-HIRAGANA DOUBLE HYPHEN,
U+10D6E GARAY HYPHEN and U+10EAD YEZIDI HYPHENATION MARK.

Never folded: U+002D HYPHEN-MINUS, and U+207B SUPERSCRIPT MINUS and U+208B SUBSCRIPT MINUS,
which sit next to superscript and subscript digits that stay as they are. Characters that
only look like a hyphen (letters and marks of other scripts, the hyphen bullet, minus-like
symbols without the Dash property) are left alone; the guide gives the reason for each.

## Why

Transliterators fold too much. `unidecode` 1.4.0 and `anyascii` 0.3.3 turn every character
into ASCII, so `café` becomes `cafe` and a Chinese character becomes its romanisation; that
is the wrong tool when you only want to tidy punctuation and keep the words. `unidecode` also
writes an em dash as `--`, which a Markdown converter reads back as an en dash.

Unicode normalization folds too little. NFKC (`unicodedata.normalize`) maps the small,
fullwidth and vertical dash forms, but leaves the en dash, the em dash and the minus sign as
they are, and it changes letters and digits too (the `fi` ligature becomes `fi`, a
superscript two becomes `2`).

Typography converters (Python-Markdown's `smarty`, the markdown-it-py typographer, docutils, and
`smartypants` with old-school dashes, `Attr.D`; by default it reads `--` as an em dash) turn `--`
and `---` into en and em dashes. En and em dashes in the `tex` form read back exactly through all
four, as the tests check, except that markdown-it-py leaves `--` with a space on one side only
as two hyphens; the guide covers this and the rarer dashes. `unidash` folds only punctuation,
classifies every Dash character, leaves letters alone, has no dependencies and is fully typed.

## Development

The Unicode data files are not part of the repository. `python scripts/fetch_vectors.py`
downloads them into `tests/vectors/unicode/` and checks each against the size and SHA-256 in
`MANIFEST.txt`; without them the data tests skip. The comparisons with independent programs
need the packages in `requirements-oracles.txt` and skip without them. The installed-wheel
test runs with `UNIDASH_E2E=1`.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/unidash/blob/main/LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
