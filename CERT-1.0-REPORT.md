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
- [ ] Third mutation round, matrix and gates on the round 3 code
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
| 10 | Supported Pythons | PASS: CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2, 3.14.2t, at d9dc54f |
| 11 | README and `twine check` | PASS: `twine check --strict` on wheel and sdist, absolute links |
| 12 | Dated CHANGELOG section | PASS: 1.0.0, 2026-10-23 |
| 13 | pyproject 1.0.0, Production/Stable | PASS |
| 14 | sdist and wheel contents | PASS |
| 15 | Gates each exit 0 | PASS: at d9dc54f, see Gates |
| 16 | Independent reviewer | pending (next stage) |
| 17 | PR and trace guard | PR from `release/1.0.0`, trace guard CLEAN; merge and publish left to the maintainer |
| 18 | Contracts bite (mutations) | PASS: three author rounds, all killed (CERT-1.0-MUTATIONS.md) |
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
- Third round, mutants of the QA round 3 fixes: RESULT3.

## Packaging, e2e and Pythons (items 8, 10, 13, 14)

- At 6101860 on another machine (CPython 3.14.2), fresh clone, `UNIDASH_E2E=1`: the e2e
  test builds the wheel and the sdist, inspects both, installs the wheel in a fresh venv,
  drives the API from an empty folder with `-I`, and runs the `unidash` script and
  `python -m unidash` by subprocess (filter, `--form`, `--punct`, `--script-hyphens`,
  `--check` on a file and on stdin, `--version`, non UTF-8 input exits 2).
- At d9dc54f (final code) on this PC, as at 25a6b63 before the QA fixes: wheel and sdist
  built from a fresh clone, `twine check --strict` passed for both; for each of CPython
  3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2 free-threaded, the wheel in a fresh venv
  and the sdist's own suite with `src` removed (fetched data, oracles and mypy present): 239
  collected, all passed except the opt-in e2e and the POSIX file name test, plus the 9
  doctests of the installed package. 3.8 and 3.9 are below `requires-python`.
- Wheel: the ten modules, `py.typed`, METADATA, the entry point
  `unidash = unidash._cli:main` and `licenses/LICENSE`. Sdist: sources, tests, scripts,
  docs, LICENSE and the data manifest; no fetched data, no report files, no caches. The only
  Unicode content in the code is character names and property membership, which are facts.
- No PyPI release exists, so there is no upgrade path to check.

## Gates (item 15)

At d9dc54f (final code) on this PC (CPython 3.13.2) from a fresh clone, each command on its
own, with the fetched Unicode data, the oracle packages and `UNIDASH_E2E=1` (so the wheel e2e,
CLI by subprocess included, runs): `ruff format --check .`, `ruff check .`, `mypy --strict src`,
`mypy --strict src tests` and `pytest` (247 passed, 1 skipped: the POSIX file name test,
which cannot run on Windows) all exit 0. Earlier runs: 29b10bb (202 passed) and 04fe387
(225 passed), both on another machine with CPython 3.14.2.

## QA lenses (item 19) and independent review (item 16)

Round 1, on bbd84b8: lenses a (API and docs), b (ground truth), c (adversarial), d (packaging and
e2e) and e (contract strength, 79 mutants of its own) all returned FAIL. Every finding is fixed in
04fe387, each behaviour bug with a test that failed first; behaviour changes are in the CHANGELOG.

| Findings | Fix | Proof |
| --- | --- | --- |
| a-A1, c-F2, d-D1 (medium): on Windows a reader closing stdout early gives a traceback, exit 120 (EINVAL) | EPIPE, and EINVAL on Windows, handled like `BrokenPipeError`: devnull, exit 1 | `test_cli_edges.py` closes a real pipe in `--check` and fold mode (before: 120 and a traceback); the e2e test repeats it with the installed script |
| c-F1 (high): quadratic `tex` fold, `to_ascii_punct` and CLI on growing input | translate in blocks of 65,536 code points | `test_scale.py`, 1M vs 4M characters, six workloads, CPython 3.13.2: ratio 14.7 and 12.1 before, 3.4 to 4.2 after; a long text equals its per-character fold |
| c-F3 (medium): missing stdin or stdout crashes | stdin read only for `-`; a missing stream is reported, exit 2 | `test_cli_edges.py` (before: AttributeError) |
| c-F4 (low): the CLI echoes a huge `--form` | `type=` check quoting at most 40 characters | 20,000 characters: 20,257 bytes of stderr before, under 500 after |
| e-F1 (medium): 8 punctuation table mutants survive | `test_fold.py` checks every code point against the GUIDE list, written out in the test | U+25E6 dropped and U+00B7 added now fail |
| e-F2 (low): swapped CLI dash flags survive the default gate | each flag tested on its own | the swap fails both cases |
| a-A2, b-F2, b-F1 (low, low, medium): `tex` read-back overstated; smartypants needs `Attr.D` | README and GUIDE: en and em exact through all four (smartypants with `Attr.D`), other dashes many to one, long dashes only in docutils and smartypants | oracle tests for the many-to-one targets and the smartypants default |
| b-F3 (low): two spacing marks are confusables of `-` | "letters and marks", U+1BF3 and U+AA7D named | data test asserts both are marks |
| b-F4, a-A3, a-A4 (low): U+3030 comment; undated 0.x sections; CONTRIBUTING | comment names the two listed wavy dashes; 0.1.0 and 0.2.0 dated and marked unpublished; CONTRIBUTING says what tests read, write and run | |

Round 2, on 92a59e7: lens b (ground truth) PASS, 40 new probes on the changed code and no
finding. The other lenses' findings, all fixed in 4d98934 and d9dc54f:

| Finding | Fix | Proof |
| --- | --- | --- |
| With stderr closed, `print(file=None)` wrote diagnostics into the folded output or the `--check` report | `_report` and the parser drop them when `sys.stderr` is None | `test_cli_io.py`: in process and a real child with stderr closed write only data (M38, M41) |
| A usage error naming a huge unknown option echoed it whole | usage errors cut at 200 characters | `test_a_huge_unknown_argument_is_cut_short` (M39, M40) |
| markdown-it-py reads `--` as an en dash only with whitespace on both sides or on neither; the docs claimed exact read-back | README and GUIDE state the exception; the oracle texts pick the space on each side apart | oracle test expects hyphens for lopsided en dashes (over 50 cases), plus a direct test |
| Mutants surviving the suite: CLI writing only the first block or stopping after it, forms in any case, non UTF-8 replaced, stdin BOM lost, any write error swallowed | new CLI contracts in `tests/test_cli_io.py` | the second author round kills each of these shapes |
| The close-early test passed 300 full temporary paths, near the Windows command line limit | bare names with the folder as cwd | test unchanged in intent |
| The linear time test could fail on a loaded machine | sizes of 200,000 and 1,600,000 characters, bound 40 (linear about 8, quadratic 64) | steady on the final runs |
| GUIDE silent on other write errors and on case in form names | a full disk raises with a traceback; form names are exact | M45, M48 |

Round 3, on 6fa3a04: every lens returned at least one finding. All are fixed in 931adf3 and
d027888, each behaviour bug with a contract test that failed on 6fa3a04 first; the behaviour
changes are in the CHANGELOG. No finding is disputed.

| Finding | Fix | Proof |
| --- | --- | --- |
| a-F1, d-D1, e-F1 (high, high, medium): `pytest` red at 6fa3a04, this report had 234 lines and its gate runs were of d9dc54f | mutation tables moved to CERT-1.0-MUTATIONS.md (also excluded from the sdist); gates and matrix rerun on the round 3 code and recorded below | `test_every_source_file_stays_under_two_hundred_lines` passes |
| a-F2 (low): `DashHit` fields annotated with `ForwardRef('int')` at runtime | no `__future__` import in `_hit.py` | `test_contract.py::test_dash_hit_fields_carry_their_real_types` (failed before) |
| a-F3 (low): `--punct --form ascii` accepted, exit 0 | `--form` defaults to None, so any explicit `--form` is refused with `--punct` | `test_cli_names.py::test_punct_refuses_any_explicit_form` (`ascii` failed before) |
| b-F1 (low): the `tex` read-back promise covered "any other character" | README and GUIDE promise letters, digits, spaces and `. , ; : ? ! ( )`, and name the backslash escape, the markdown-it-py `+-` rule and code spans | oracle texts now mix CJK, accented words and that punctuation around the dashes (over 50 texts with a dash touching it); each named exception pinned by a test |
| c2-F1 (medium): `--check` crashes when a Windows file name holds a lone surrogate | report names written with surrogateescape, else backslash escapes; reading errors include `ValueError`, so a name POSIX cannot encode, or one with a NUL, is an unreadable file | in process and by subprocess on Windows (both failed before); a missing such name and a NUL name in both modes (the NUL one failed before) |
| c2-F2 (low): a huge file name echoed twice in a read error | only the system's reason is printed, and a name over 200 characters keeps its first and last 100 | 30,000-character name: under 500 bytes of stderr; names of 200 and 201 characters (failed before) |
| e-F2 (low): mutant N07, U+2028 ends a line, survives | test of VT, FF, U+001C to U+001E, U+0085, U+2028 and U+2029 before a dash; the fuzz pool gains five of them | N07 applied: the new test and all three fuzz seeds fail |
| e-F3 (low): mutant N13, `>=` at the usage error limit, survives | messages of 199, 200 and 201 characters through the parser's `error` | N13 applied: the 200 case fails |

Disputed findings: none. Next: the five lenses on the round 3 code, then the independent review.
