# unidash improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [ ] Dash classification from the Unicode data: general dashes, script hyphens, kept marks
- [ ] `fold_dashes` with the `ascii`, `tex` and `typographic` forms and soft hyphen control
- [ ] `to_ascii_punct` covers every general dash and drops soft hyphens
- [ ] `find_dashes`, `is_dash`, `DASHES`, `dash_table`, streaming `iter_fold_dashes`
- [ ] Command line tool (`unidash`, `python -m unidash`) with `--check`
- [ ] Contracts: UCD and UTS #39 data, interpreter scan, typing, README, wheel e2e
- [ ] Mutation run (guards removed one at a time, each must fail the suite)
- [ ] Docs: README, CHANGELOG, docstrings, packaging metadata
- [ ] Gates: ruff format, ruff check, mypy --strict, pytest
- [ ] Independent review findings fixed with regression tests
- [ ] Pull request opened, guard clean

## Starting point

`0.1.0` (not on PyPI) ships one function, `to_ascii_punct`, which folds a hand-picked set of
quotes, seven dashes, bullets, spaces and the ellipsis. Read as a user who cleans text pasted
from word processors, PDFs, CJK input methods and web pages:

- Only U+2010..U+2015 and U+2212 fold. The fullwidth hyphen-minus from a Japanese keyboard,
  the small and vertical presentation forms, the two-em and three-em dashes and the wave dash
  pass through, so "ASCII punctuation" output still holds non-ASCII dashes.
- The soft hyphen (U+00AD) is kept. It is invisible, breaks search and diffing, and is the most
  common stray character in text copied from PDFs and hyphenating renderers.
- There is no choice of target. Everything becomes one `-`, which loses the en and em dash
  distinction that Markdown and TeX users keep as `--` and `---`, and there is no way to only
  tidy lookalike forms while keeping real typographic dashes.
- Nothing says which characters were chosen or why; nothing is checked against the Unicode
  data, so the next Unicode version silently adds dashes the table never heard of.
- No way to find dashes (a lint or a pre-commit check), no streaming, no command line tool.
- Packaging: README example is not executed, no Python classifiers, no wheel test.

## Sources (fetched 2026-10-13)

- UnicodeData.txt 18.0.0, https://www.unicode.org/Public/18.0.0/ucd/UnicodeData.txt: 27 code
  points have General_Category=Pd (U+002D, U+058A, U+05BE, U+1400, U+1806, U+2010..U+2015,
  U+2E17, U+2E1A, U+2E3A, U+2E3B, U+2E40, U+2E5D, U+301C, U+3030, U+30A0, U+FE31, U+FE32,
  U+FE58, U+FE63, U+FF0D, U+10D6E, U+10EAD).
- PropList.txt 18.0.0, https://www.unicode.org/Public/18.0.0/ucd/PropList.txt: the Dash
  property is every Pd code point plus U+2053 SWUNG DASH (Po) and three math signs, U+207B,
  U+208B and U+2212 (Sm).
- confusables.txt 18.0.0 (UTS #39), https://www.unicode.org/Public/18.0.0/security/confusables.txt:
  maps to U+002D the hyphen, non-breaking hyphen, figure dash, en dash, minus sign, small em
  dash and small hyphen-minus, and also non-dashes (letters in Coptic, Buhid and Myanmar, a
  modifier letter, the Arabic full stop, the hyphen bullet, an emoji, a Roman weight sign).
  The em dash, horizontal bar and fullwidth hyphen-minus map to U+30FC instead; the wave dash
  and swung dash to `~`; the double hyphens to `=`.
- The three files are third-party and not committed: `scripts/fetch_vectors.py` fetches them
  into a gitignored folder checked against a tracked MANIFEST; the tests that read them skip
  when the folder is absent. The running interpreter's `unicodedata` gives a second, always-on
  check for General_Category and NFKC.

## Ranked improvements

1. **Every dash is classified, on purpose.** Three tables built from code points, each with a
   reason: general dashes (fold by default), script hyphens (Armenian, Hebrew maqaf, Canadian
   syllabics, Mongolian, katakana double hyphen, Garay, Yezidi: they belong to a script, like
   letters, so they fold only on request) and kept marks (superscript and subscript minus,
   which sit next to superscript digits that stay). A contract checks that every Pd and Dash
   code point in the fetched data lands in exactly one table, and every UTS #39 confusable of
   `-` is either folded or excluded for a stated reason (letter, emoji, bullet, sentence stop).
2. **`fold_dashes(text, form=...)`.** `ascii` (default): every general dash becomes `-`, the
   wave and swung dashes become `~`. `tex`: en dash `--`, em dash and horizontal bar `---`,
   two-em and three-em dashes six and nine hyphens, the rest as `ascii`. `typographic`: real
   dashes stay; only compatibility forms (small, vertical, fullwidth) become their NFKC
   counterparts. `script_hyphens=True` folds the script hyphens too.
3. **Soft and non-breaking hyphens.** The soft hyphen is dropped by default (it is a line
   break hint, not a character), `keep_soft_hyphens=True` keeps it. The non-breaking hyphen
   folds to `-` in the ASCII forms and stays in `typographic`, where it carries meaning.
4. **Numbers and ranges preserved.** A minus sign is always a single `-`, in every form, so
   `-5` stays a negative number; the TeX form never touches characters that are already ASCII,
   so `1-2` and `--` written by hand come out unchanged.
5. **`to_ascii_punct` follows suit.** It folds every general dash and drops soft hyphens, so
   its output is ASCII for every dash the Unicode data knows.
6. **Find, test and build.** `find_dashes(text)` yields position, character and Unicode name
   for each non-ASCII dash (for linting); `is_dash(char)`; `DASHES` is the Dash property as a
   frozenset; `dash_table(...)` returns the `str.translate` table for callers with their own
   pipeline.
7. **Streaming.** `iter_fold_dashes(chunks, ...)` folds an iterable of strings lazily. The fold
   is per code point, so a chunked result equals the whole-text result (property test).
8. **Command line tool.** `unidash [FILE...]` writes folded text to stdout (`-` is stdin),
   `--form`, `--script-hyphens`, `--keep-soft-hyphens`, `--punct` for the full punctuation fold,
   and `--check` lists `file:line:col: U+2014 EM DASH` and exits 1 (pre-commit style). Exit 2
   on unreadable or non UTF-8 input.
9. **Contracts that bite.** UCD and UTS #39 data checks, an interpreter scan, chunking
   properties, a mypy snippet over the typed API, executed README examples, an installed-wheel
   e2e and a mutation run.
10. **Docs and packaging.** README with runnable examples and the full classification, CHANGELOG
    0.2.0, classifiers and keywords.

Left out on purpose: turning ASCII hyphens into typographic dashes (the opposite direction,
`smartypants` owns it), context rules such as "en dash between digits" (guesswork that breaks
code and identifiers), in-place file rewriting (shell redirection and editors already do this
safely), and folding letters that look like hyphens (the library never touches letters).
