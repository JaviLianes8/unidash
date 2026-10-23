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
- [ ] Five QA lenses (item 19)
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
| 10 | Supported Pythons | PASS: CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2, 3.14.2t |
| 11 | README and `twine check` | PASS: `twine check --strict` on wheel and sdist, absolute links |
| 12 | Dated CHANGELOG section | PASS: 1.0.0, 2026-10-23 |
| 13 | pyproject 1.0.0, Production/Stable | PASS |
| 14 | sdist and wheel contents | PASS |
| 15 | Gates each exit 0 | PASS: see Gates |
| 16 | Independent reviewer | pending (next stage) |
| 17 | PR and trace guard | PR from `release/1.0.0`, trace guard CLEAN; merge and publish left to the maintainer |
| 18 | Contracts bite (mutations) | PASS: author round of 37 mutants, all killed |
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
- Four typography converters, 600 seeded texts each: Python-Markdown 3.11.2 `smarty` (3.9 on
  Python 3.10), the markdown-it-py 4.2.0 typographer, docutils 0.23 smartquotes and
  smartypants 2.0.2 (`Attr.D`) read the `tex` form back as the original en and em dashes; docutils and
  smartypants read the two-em and three-em widths as two and three em dashes.
- The README comparison, run on 2026-10-23: unidecode 1.4.0 and anyascii 0.3.3 turn `café`
  into `cafe`, unidecode writes the em dash as `--`, and NFKC on CPython 3.13.2 keeps U+2013,
  U+2014 and U+2212 while mapping U+FB01 to `fi` and U+00B2 to `2`.

## Fuzz and hostile input (item 9)

`tests/test_fuzz.py`, three seeds over text mixing every dash, CR, LF, CRLF, BOM, NUL, lone
surrogates, astral and random code points: the fold is per character, idempotent and equal
to `str.translate` with `dash_table`; the ASCII forms leave no foldable dash; every
`find_dashes` position equals an independent count (split on line ends); chunked folding
equals whole folding; `to_ascii_punct` is idempotent; no letter, mark or digit of any code
point changes; seven input shapes scale linearly from 50,000 to 400,000 characters; a
million CRs are counted; four threads agree with the serial results. `test_cli.py` checks
100,000 hits on stdin; a 1,000,000 character form string gives a short message.

## Author mutation round (item 18)

Each mutant applied alone to a copy of the tree at c76b0e7 (fetched Unicode data and the
oracle packages present), full suite with `-x` and bytecode off, on another machine with
CPython 3.14.2; the unmutated tree passed first. All 37 killed; the last column is the first
test that failed. M37 came with its test at 6101860 and was run alone on this PC.

| Mutant | Change | First failing test |
| --- | --- | --- |
| M01 | message quote limit ten times larger | `test_contract_api.py::test_messages_quote_at_most_forty_characters[41]` |
| M02 | off by one at the quote limit | `test_contract_api.py::test_a_forty_character_form_is_quoted_whole` |
| M03 | str subclass kept as given | `test_contract_api.py::test_str_subclasses_are_read_as_their_characters` |
| M04 | form compared through the subclass __eq__ | `test_contract_api.py::test_a_str_subclass_form_must_spell_a_form` |
| M05 | flags accept any truthy value | `test_contract_api.py::test_every_folder_checks_its_options_the_same_way[fold_dashes]` |
| M06 | wrong parameter name in the chunk error | `test_contract_api.py::test_a_bad_chunk_is_named_when_it_is_read` |
| M07 | three-em dash as wide as two-em in tex | `test_dashes.py::test_tex_widens_the_long_dashes` |
| M08 | script hyphen switch inverted | `test_cli.py::test_dash_options_reach_the_fold` |
| M09 | soft hyphen switch inverted | `_dashes.py::unidash._dashes.dash_table` |
| M10 | typographic script hyphens to ASCII | `test_cli.py::test_dash_options_reach_the_fold` |
| M11 | typographic drops the compatibility forms | `_dashes.py::unidash._dashes.fold_dashes` |
| M12 | swung dash to hyphen instead of tilde | `test_dashes.py::test_wavy_dashes_become_a_tilde` |
| M13 | Unicode 14 oblique hyphen dropped | `__init__.py::unidash` |
| M14 | vertical en dash target swapped with em | `test_dashes.py::test_typographic_unifies_the_compatibility_forms` |
| M15 | astral script hyphen dropped | `__init__.py::unidash` |
| M16 | subscript minus missing from the kept marks | `__init__.py::unidash` |
| M17 | leading BOM takes a column | `test_cli.py::test_a_bom_survives_filtering_and_takes_no_column` |
| M18 | CRLF counted as two line ends | `test_fuzz.py::test_find_dashes_positions_match_an_independent_count[11]` |
| M19 | columns counted from 0 | `__init__.py::unidash.DashHit` |
| M20 | code point not padded to four digits | `_dashes.py::unidash._dashes.find_dashes` |
| M21 | names taken from the interpreter only | `test_tools.py::test_find_names_do_not_depend_on_the_interpreter_tables` |
| M22 | a lone CR does not end a line | `test_fuzz.py::test_find_dashes_positions_match_an_independent_count[11]` |
| M23 | is_dash accepts the empty string | `test_contract_api.py::test_is_dash_errors` |
| M24 | streaming reads every chunk at once | `test_contract_api.py::test_a_bad_chunk_is_named_when_it_is_read` |
| M25 | dash_table hands out the shared cached table | `test_contract_api.py::test_dash_table_is_fresh_and_equals_what_fold_uses` |
| M26 | fullwidth offset off by one | `_fold.py::unidash._fold.to_ascii_punct` |
| M27 | fullwidth tilde (CP932 wave dash) dropped | `test_fold.py::test_fullwidth_punctuation_folds_to_its_nfkc_ascii_form` |
| M28 | ellipsis to two dots | `test_docs.py::test_each_example_prints_what_its_comments_say[3]` |
| M29 | a finding hides an earlier read error | `test_cli.py::test_errors_win_over_findings_in_check` |
| M30 | stdin may be named twice | `test_cli.py::test_stdin_twice_is_refused` |
| M31 | closed pipe reported as success | `test_cli.py::test_a_closed_pipe_stops_quietly` |
| M32 | --punct accepts --keep-soft-hyphens | `test_cli.py::test_punct_refuses_dash_options` |
| M33 | DashHit pickles through the private module | `test_contract_api.py::test_dash_hit_is_a_named_tuple_that_pickles_as_public` |
| M34 | to_ascii_punct takes any object | `test_contract_api.py::test_text_must_be_a_str[to_ascii_punct]` |
| M35 | wrong error type for a non-str | `test_contract_api.py::test_every_folder_checks_its_options_the_same_way[fold_dashes]` |
| M36 | filter rewrites CRLF line ends | `test_cli.py::test_stdin_is_filtered_to_stdout_byte_exactly` |
| M37 | `python -m unidash` guard removed | `test_cli.py::test_importing_the_main_module_does_not_run_the_tool` |

## Packaging, e2e and Pythons (items 8, 10, 13, 14)

- At 6101860 on another machine (CPython 3.14.2), fresh clone, `UNIDASH_E2E=1`: the e2e
  test builds the wheel and the sdist, inspects both, installs the wheel in a fresh venv,
  drives the API from an empty folder with `-I`, and runs the `unidash` script and
  `python -m unidash` by subprocess (filter, `--form`, `--punct`, `--script-hyphens`,
  `--check` on a file and on stdin, `--version`, non UTF-8 input exits 2).
- At 25a6b63 on this PC: wheel and sdist built from a fresh clone, `twine check --strict`
  passed for both; for each of CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2
  free-threaded, the wheel in a fresh venv and the sdist's own suite with `src` removed
  (fetched data and oracles present): 191 passed, 2 skipped (the opt-in e2e and the POSIX
  file name test), plus the 9 doctests of the installed package. 3.8 and 3.9 are below
  `requires-python`. The thread test added after was run on 3.14.2t and 3.13.2.
- Wheel: the ten modules, `py.typed`, METADATA, the entry point
  `unidash = unidash._cli:main` and `licenses/LICENSE`. Sdist: sources, tests, scripts,
  docs, LICENSE and the data manifest; no fetched data, no report files, no caches. The only
  Unicode content in the code is character names and property membership, which are facts.
- No PyPI release exists, so there is no upgrade path to check.

## Gates (item 15)

At 29b10bb on another machine (CPython 3.14.2) from a fresh clone, each command on its own,
with the fetched Unicode data, the oracle packages and `UNIDASH_E2E=1`: `ruff format --check .`,
`ruff check .`, `mypy --strict src`, `mypy --strict src tests` and `pytest` (202 passed,
1 skipped: the POSIX file name test, which cannot run on Windows) all exit 0. QA round 1
changed code after this; its gate run is below.

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

Gates at 04fe387 on Elena's PC (CPython 3.14.2, fresh clone with the Unicode data, the oracles and
`UNIDASH_E2E=1`): `ruff format --check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src
tests` exit 0, `pytest` 225 passed, 1 skipped (POSIX file names).

Disputed findings: none. Next: round 2 by the same lenses, then the independent review.
