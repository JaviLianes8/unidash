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
| 15 | Gates each exit 0 | PASS: at 31abecc, see Gates |
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

At 6b7d5b6 (round 7 fix) on this PC (CPython 3.13.2) from a fresh clone, each command on its
own, with the fetched Unicode data, the oracle packages and `UNIDASH_E2E=1` (so the wheel e2e,
CLI by subprocess included, runs): `ruff format --check .`, `ruff check .`, `mypy --strict src`,
`mypy --strict src tests` and `pytest` (314 passed, 1 skipped: the POSIX file name test,
which cannot run on Windows) all exit 0; `pytest` without `UNIDASH_E2E` too. 31abecc, daaba06
and 6b7d5b6 change only the GUIDE and the tests, so the interpreter matrix and the mutation
tables stay those of 2bd07b5. The commit that records these runs changes only this report and
CERT-1.0-QA.md, and `pytest` was run again on it before pushing. Earlier runs: daaba06 (312
passed), 31abecc (306 passed), 2bd07b5 (295 passed), 6b342cc (281 passed), d9dc54f (247
passed), 29b10bb and 04fe387.

## QA lenses (item 19) and independent review (item 16)

Rounds 1 to 6 (on bbd84b8, 92a59e7, 6fa3a04, 46ebbae, ef69a71 and 2ab1f9e): every lens but b
in round 2 returned findings; all were fixed, each behaviour bug with a contract test that
failed first, and none was disputed. The tables are in CERT-1.0-QA.md (not shipped).

Round 7, on 99eaeae: lenses a and b confirmed the round 6 fix (a later line over a lone en
dash or an em dash, the first line of a block over touching dashes, 18 render tests passing)
and 9 of the 10 new sweep probes of lens a agreed with the GUIDE. Three more gaps in the GUIDE
block rules, fixed in 6b7d5b6; no library code changed, so the CHANGELOG has nothing to add.

| Finding | Fix | Proof |
| --- | --- | --- |
| a-N4 (low): markdown-it-py keeps the dashes in a list item or a quote only for a lone en dash; touching dashes that fold to three hyphens or more (an em dash, two en dashes, an en and an em dash) end the list or the quote with `<hr />` | GUIDE: markdown-it-py keeps a lone en dash in the item or the quote, and ends the list or the quote with `<hr />` for dashes that fold to three hyphens or more | `tests/test_markdown_blocks.py`: `- item` and `> q` over an em dash, two en dashes, an en and an em dash, and an en dash and a hyphen, full renders through both converters |
| b-H1 (low): a block-level HTML line is a third exception: Python-Markdown never underlines it and starts a new block on the next line, while markdown-it-py takes the next lines into the HTML block as raw text; raw HTML was not named among the places where hyphens stay as written | GUIDE: hyphens inside raw HTML stay as written in both; Python-Markdown underlines only a line that starts a block or follows a block-level HTML line, never the HTML line itself; under such a line Python-Markdown starts a new block while markdown-it-py takes the lines up to the next blank line into the HTML block | full renders of `<div>` and `<p>` holding an en or an em dash (the same as the fold in both), `<div>x</div>` over an en dash, an em dash, `Title` and an en dash, and an indented line, and `<p>x</p>` over an en dash |
| b-H2 (low): a line right after an indented code line also starts a block, so in Python-Markdown an em dash there over an en dash is an `<h2>`, where markdown-it-py gives a thematic break and then an en dash | GUIDE: a line that starts a block starts the text or follows a blank line, a heading, a thematic break or an indented code line, in the block rule sentence and in the underline sentence | full renders of `    code` over an em dash and an en dash, and, through both converters alike, `    code` over an em dash and over `Title` and an en dash, and an indented line after a `#` heading and after a thematic break |

The new GUIDE sentences were checked against more renders than the tests pin: lists and
ordered lists and quotes over each touching pair, `<div>x</div>` and `<!-- c -->` before
every kind of line, and code lines, headings and thematic breaks before an indented line, a
lone en dash, dashes three spaces apart, `Title` and an en dash, and a two-line paragraph.

Disputed findings: none. Next: the five lenses on the round 7 code, then the independent review.
