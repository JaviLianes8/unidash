# unidash 1.0.0 certification report

The 1.0.0 certification bar applied to unidash. PyPI has no `unidash` release
(`https://pypi.org/pypi/unidash/json` answered 404 on 2026-10-23), so there is no upgrade
path to check; every change since 0.2.0 is still listed in the CHANGELOG.

Progress:
- [x] Branch `release/1.0.0` created from `main` (a7a06bb, 0.2.0)
- [x] Baseline gates on 0.2.0
- [x] API review and 1.0.0 changes (item 1)
- [x] Errors, typing, docstrings and doctests (items 2 to 5)
- [x] Ground truth: Unicode data fetched live, independent oracles (item 7)
- [x] Contract, fuzz and author mutation round (items 6, 9, 18)
- [x] Docs: README, GUIDE, CHANGELOG (items 11, 12)
- [x] Packaging, e2e, every Python (items 8, 10, 13, 14)
- [x] Gates (item 15)
- [x] PR and trace guard
- [x] QA rounds 1 and 2: every finding fixed
- [x] Second author mutation round on the fix code, final matrix and gates at d9dc54f
- [x] QA round 3 (five lenses on 6fa3a04): every finding fixed
- [x] Third mutation round, matrix and gates on the round 3 code (6b342cc)
- [x] QA round 4 (five lenses on 46ebbae): every finding fixed, fourth mutation round,
  matrix and gates on the fix (2bd07b5)
- [x] QA round 5 (lenses on ef69a71): every finding fixed in the GUIDE, gates on the
  fix (31abecc)
- [x] QA round 6 (lenses on 2ab1f9e): every finding fixed in the GUIDE, gates on the
  fix (daaba06)
- [x] QA round 7 (lenses on 99eaeae): every finding fixed in the GUIDE, gates on the
  fix (6b7d5b6)
- [x] QA round 8 (lenses on 3b85a49): every finding fixed in the GUIDE, gates on the
  fix (01694d2)
- [ ] Five QA lenses passing on the final code (item 19)
- [ ] Independent reviewer (item 16)

## Scorecard

| # | Item | Result |
| --- | --- | --- |
| 1 | Public API reviewed for stability | PASS: the nine names of 0.2.0 kept, signatures pinned; changes in CHANGELOG and GUIDE |
| 2 | `__all__` exact, no private imports in docs | PASS: the package namespace equals `__all__` (stray `annotations` removed) |
| 3 | Docstrings with runnable examples, doctests | PASS: 9 doctests cover every public name; the 4 README blocks run as tests |
| 4 | Typed end to end | PASS: `mypy --strict src tests`, `py.typed`, typing checked from a consumer snippet |
| 5 | Typed, documented, bounded errors | PASS: `TypeError` and `ValueError` as in the GUIDE table, at most 40 quoted characters |
| 6 | Contract tests of every public name | PASS: `tests/test_contract_api.py` and the per-area tests |
| 7 | Real ground truth | PASS: Unicode 18.0 files fetched 2026-10-23, regex, four typography converters |
| 8 | Real e2e from the wheel | PASS: wheel in a fresh venv, API and CLI by subprocess; no PyPI release to upgrade from |
| 9 | Seeded fuzz, no crash, hang or blowup | PASS: `tests/test_fuzz.py`; linear on growing input since QA round 1 (`tests/test_scale.py`) |
| 10 | Supported Pythons | PASS: CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2, 3.14.2t, at 2bd07b5 |
| 11 | README and `twine check` | PASS: `twine check --strict` on wheel and sdist, absolute links |
| 12 | Dated CHANGELOG section | PASS: 1.0.0, 2026-10-23 |
| 13 | pyproject 1.0.0, Production/Stable | PASS |
| 14 | sdist and wheel contents | PASS |
| 15 | Gates each exit 0 | PASS: at 01694d2, see Gates |
| 16 | Independent reviewer | pending (next stage) |
| 17 | PR and trace guard | PR from `release/1.0.0`, trace guard CLEAN; merge and publish left to the maintainer |
| 18 | Contracts bite (mutations) | PASS: four author rounds, all killed (CERT-1.0-MUTATIONS.md) |
| 19 | Five independent QA lenses | pending (next stage) |

## Baseline on 0.2.0 (before any change)

On this PC, CPython 3.13.2, with the Unicode data fetched: `ruff format --check .`,
`ruff check .` and `mypy --strict src tests` exit 0; `pytest` 126 passed, 2 skipped (the
installed-wheel test, which needs `UNIDASH_E2E=1`, and the POSIX file name test); no
doctests existed.

Defects found in 0.2.0 by reading and then reproducing: `fold_dashes("a", "x" * 100000)`
raised a `ValueError` holding the whole string (100,051 characters); a `str` subclass that
overrides `translate` changed what `fold_dashes` returned, one that overrides `__iter__` hid
every `find_dashes` hit, and one whose `__eq__` matches anything passed as a form; a list as
`form` raised `ValueError`; `DashHit` pickled as a private module; no public docstring had a
runnable example; `scripts/release.ps1` could publish only one version and built from a dirty
tree.

## API review (item 1)

Kept: the nine public names of 0.2.0 with their parameter names, defaults and keyword-only
options, now pinned by `tests/test_contract_api.py`. Changed, all in the CHANGELOG: a
non-str `form` raises `TypeError`; messages quote at most 40 characters; a `str` subclass is
read as its plain characters (its `translate`, `__iter__` and `__eq__` are never called);
the chunk error names `chunk`; `DashHit` pickles as `unidash.DashHit`; `python -m unidash`
runs only as a program. Internal: argument checks moved to `_checks.py` and the position
scan to `_hit.py`, so every file stays under 200 lines with its examples. The GUIDE states
the versioning promise, including how a later Unicode version is taken in.

## Ground truth (item 7)

Fetched on 2026-10-23 by `scripts/fetch_vectors.py` into the ignored
`tests/vectors/unicode` folder; size and SHA-256 match `MANIFEST.txt`. Nothing fetched is
committed or shipped.

- UnicodeData.txt and PropList.txt 18.0.0 (https://www.unicode.org/Public/18.0.0/ucd/):
  the three classes are exactly the Dash property, cover the 27 Pd code points, the stored
  names match, and the `typographic` targets are exactly the `<small>`, `<vertical>` and
  `<wide>` decompositions in the file (U+2011 `<noBreak>` kept on purpose, asserted).
- confusables.txt 18.0.0 (https://www.unicode.org/Public/18.0.0/security/confusables.txt):
  every confusable of `-` folds, is a letter or a mark, or is a listed non-dash; ASCII targets agree.
- regex 2026.9.29, an independent implementation of the Unicode properties: `\p{Dash}` over
  every code point equals `DASHES` (31), and the 27 `\p{Pd}` code points are all classified.
- Four typography converters, 600 seeded texts each of words (letters, digits, CJK) with
  sentence punctuation, joined by dashes and spaces: Python-Markdown 3.11.2 `smarty` (3.9 on
  Python 3.10), the markdown-it-py 4.2.0 typographer, docutils 0.23 smartquotes and
  smartypants 2.0.2 (`Attr.D`) read the `tex` form back as the original en and em dashes; docutils and
  smartypants read the two-em and three-em widths as two and three em dashes.
- The README comparison, run on 2026-10-23: unidecode 1.4.0 and anyascii 0.3.3 turn `café`
  into `cafe`, unidecode writes the em dash as `--`, and NFKC on CPython 3.13.2 keeps U+2013,
  U+2014 and U+2212 while mapping U+FB01 to `fi` and U+00B2 to `2`.

## Fuzz and hostile input (item 9)

`tests/test_fuzz.py`, three seeds over text mixing every dash, CR, LF, CRLF, BOM, NUL, lone
surrogates, the separators that do not end a line (VT, FF, U+0085, U+2028 and U+2029),
astral and random code points: the fold is per character, idempotent and equal
to `str.translate` with `dash_table`; the ASCII forms leave no foldable dash; every
`find_dashes` position equals an independent count (split on line ends); chunked folding
equals whole folding; `to_ascii_punct` is idempotent; no letter, mark or digit of any code
point changes; seven input shapes scale linearly from 50,000 to 400,000 characters; a
million CRs are counted; four threads agree with the serial results. `test_cli.py` checks
100,000 hits on stdin; a 1,000,000 character form string gives a short message.

## Author mutation rounds (item 18)

Each mutant applied alone to a copy of the tree with the fetched data and the oracle packages,
full suite with `-x`; the unmutated tree passed first. The tables, with the first test that
failed for each mutant, are in CERT-1.0-MUTATIONS.md (not shipped).

- First round, 37 mutants of the library and the CLI at c76b0e7: all killed.
- Second round, 15 mutants of the QA round 1 and 2 fixes at d9dc54f: all killed.
- Third round, 14 mutants of the QA round 3 fixes at 6b342cc, including the two that QA lens e
  found surviving at 6fa3a04: all killed.
- Fourth round, 6 mutants of the QA round 4 fix at 2bd07b5, including the two that lens e
  found surviving at 46ebbae (P21, P30): all killed.

## Packaging, e2e and Pythons (items 8, 10, 13, 14)

- At 6101860 on another machine (CPython 3.14.2), fresh clone, `UNIDASH_E2E=1`: the e2e
  test builds the wheel and the sdist, inspects both, installs the wheel in a fresh venv,
  drives the API from an empty folder with `-I`, and runs the `unidash` script and
  `python -m unidash` by subprocess (filter, `--form`, `--punct`, `--script-hyphens`,
  `--check` on a file and on stdin, `--version`, non UTF-8 input exits 2).
- At 2bd07b5 (round 4 code) on this PC, as at 6b342cc, d9dc54f and 25a6b63 before: wheel and sdist
  built from a fresh clone, `twine check --strict` passed for both; for each of CPython
  3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2 free-threaded, the wheel in a fresh venv
  and the sdist's own suite with `src` removed (fetched data, oracles and mypy present): 287
  collected, all passed except the opt-in e2e and the POSIX file name test, plus the 9
  doctests of the installed package. 3.8 and 3.9 are below `requires-python`.
- Wheel: the ten modules, `py.typed`, METADATA, the entry point
  `unidash = unidash._cli:main` and `licenses/LICENSE`. Sdist: sources, tests, scripts,
  docs, LICENSE and the data manifest; no fetched data, no report files, no caches. The only
  Unicode content in the code is character names and property membership, which are facts.
- No PyPI release exists, so there is no upgrade path to check.

## Gates (item 15)

At 01694d2 (round 8 fix) on this PC (CPython 3.13.2) from a fresh clone, each command on its
own, with the fetched Unicode data, the oracle packages and `UNIDASH_E2E=1` (so the wheel e2e,
CLI by subprocess included, runs): `ruff format --check .`, `ruff check .`, `mypy --strict src`,
`mypy --strict src tests` and `pytest` (331 passed, 1 skipped: the POSIX file name test,
which cannot run on Windows) all exit 0; `pytest` without `UNIDASH_E2E` too. 31abecc, daaba06,
6b7d5b6 and 01694d2 change only the GUIDE and the tests, so the interpreter matrix and the
mutation tables stay those of 2bd07b5. The commit that records these runs changes only this
report and CERT-1.0-QA.md, and `pytest` was run again on it before pushing. Earlier runs:
6b7d5b6 (314 passed), daaba06 (312 passed), 31abecc (306 passed), 2bd07b5 (295 passed),
6b342cc (281 passed), d9dc54f (247 passed), 29b10bb and 04fe387.

## QA lenses (item 19) and independent review (item 16)

Rounds 1 to 7 (on bbd84b8, 92a59e7, 6fa3a04, 46ebbae, ef69a71, 2ab1f9e and 99eaeae): every
lens but b in round 2 returned findings; all were fixed, each behaviour bug with a contract
test that failed first, and none was disputed. The tables are in CERT-1.0-QA.md (not shipped).

Round 8, on 3b85a49: lenses a and b confirmed the round 7 fix (`<div>` and `<p>` lines, the
code line that starts a block, 20 render tests passing) and lens b found 7 of its 10 new
probes in line with the GUIDE. Two more gaps in the GUIDE block rules, fixed in 01694d2; no
library code changed, so the CHANGELOG has nothing to add.

| Finding | Fix | Proof |
| --- | --- | --- |
| a-N5, b-I1 (low, medium): markdown-it-py takes the next lines into the HTML block only for HTML that ends at a blank line (CommonMark types 6 and 7, such as `<div>`, `<p>`, `<hr>`); a comment and a `<pre>`, `<script>`, `<style>` or `<textarea>` element end on their closing line, so there both converters start a new block on the next line | GUIDE: after a line of only HTML, both start a new block if it closes a comment, a `<pre>`, `<script>`, `<style>` or `<textarea>` element, a `<?` instruction, a `<!DOCTYPE` or a CDATA section; only Python-Markdown does after block-level HTML that closes what it opens (`<div>x</div>`, `<hr>`). Found while checking the fix: under a tag left open (`<div>`) both take the next lines into the HTML block, and `<!ELEMENT` or text after the closing tag behave otherwise in Python-Markdown, so the GUIDE names only the cases checked | new `tests/test_markdown_html.py` (the raw HTML test moved there so both files stay under 200 lines): thirteen such blocks, on one line and over several, each over an en dash, an em dash, `Title` and an en dash, and an indented line, the same full render in both converters; `<hr>`, `<hr />`, `<section>` and a nested `<div>` added to the markdown-it-py raw case; `<div>`, `<p>` and `<div>x` left open |
| a-N6 (low): in markdown-it-py dashes indented to the text of a list item belong to the item, so `- item` over two spaces and an em dash gives `<h2>item</h2>` inside the item, not the list and `<hr />` | GUIDE: the list and quote heading sentence holds for dashes at the start of the line; markdown-it-py puts dashes indented to the item text in the item (touching ones make its text an `<h2>`, others that fold to three hyphens or more an `<hr />`, both inside the item); Python-Markdown applies the thematic break rule to dashes indented one to three spaces under an item or a quote | `tests/test_markdown_blocks.py`: `- item` over two, three and five spaces and a lone en dash, an em dash, two en dashes or an en and an em dash; `1. item` over three spaces and an em dash; two spaced en dashes inside the item; one space (less than the item text); in Python-Markdown, one to three spaces under `- item` and `> q`, with the quote case through both converters |

To keep the GUIDE at 200 lines the Threads paragraph became a bullet of the stability promise
and the `DashHit` pickle sentence joined the named tuple line; their content is unchanged. The
new sentences were checked against more renders than the tests pin: `- item`, `* item`,
`1. item` and `> q` over zero to six spaces and four dash lines, and over 25 kinds of HTML
line over an en dash and an em dash, most also over `Title` and an en dash.

Disputed findings: none. Next: the five lenses on the round 8 code, then the independent review.
