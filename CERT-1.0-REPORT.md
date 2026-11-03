# unidash 1.0.0 certification report

Progress:
- [x] Public API, errors, typing, examples and contracts (items 1 to 6)
- [x] Fresh Unicode sources and reference programs (item 7)
- [x] Built-wheel API, CLI and real PyPI 0.2.0 upgrade (item 8)
- [x] Seeded fuzz and scaling contracts (item 9)
- [x] Available interpreter inventory and installed-wheel suite (item 10)
- [x] README, dated changelog, metadata and archive inspection (items 11 to 14)
- [x] Four gates and strict typing of tests (item 15)
- [x] Twelve additional mutations, all killed (item 18)
- [ ] Independent reviewer (item 16), merge and publish (item 17), five QA lenses (item 19)

## API and contracts (items 1 to 6)

The nine public names of 0.2.0 are retained with their signatures and defaults:
`DASHES`, `DashHit`, `Form`, `dash_table`, `find_dashes`, `fold_dashes`, `is_dash`,
`iter_fold_dashes` and `to_ascii_punct`. `__all__` matches the package namespace exactly.
`tests/test_contract.py` and `tests/test_contract_api.py` pin that surface, field types,
pickling, input checks, exact form names, eager option checking and lazy chunk iteration.
The per-area tests pin mapping values, every switch, text positions and CLI exit codes.

Every public name has a runnable example; nine doctests cover the package and its public
objects. The four README examples and its CLI transcript execute in `tests/test_docs.py`.
`mypy --strict src tests` passes, the installed package includes `py.typed`, and consumer
snippets verify inferred results and rejected calls. No public result leaks `Any`.

Errors retain the documented `TypeError` and `ValueError` families. A non-string form now
raises `TypeError`, rejected form values and class names are omitted, subclass overrides
do not change string interpretation, and chunk errors name the chunk. All changes from the
published 0.2.0 release, including CLI fixes, are in CHANGELOG and GUIDE.

## Ground truth (item 7)

On 2026-11-02, `scripts/fetch_vectors.py` fetched these files into a scratch copy of the
source tree and verified their sizes and SHA-256 against the tracked manifest:

- https://www.unicode.org/Public/18.0.0/ucd/UnicodeData.txt
- https://www.unicode.org/Public/18.0.0/ucd/PropList.txt
- https://www.unicode.org/Public/18.0.0/security/confusables.txt

`tests/vectors/unicode/MANIFEST.txt` records revision, URLs, sizes, hashes and Unicode
License v3. Third-party contents remain outside the repository and distribution archives.
Tests derive membership, names, compatibility decompositions and confusable targets
from those fetched files. Hand-written and random boundary inputs are separate contracts.

Reference programs in requirements-oracles.txt ran: regex 2026.9.29 scans all code
points for Dash/Pd; Markdown 3.11.2, markdown-it-py 4.2.0, docutils 0.23 and smartypants
2.0.2 check seeded TeX conventions and Markdown block exceptions. Earlier evidence
and limitations remain in CERT-1.0-QA.md.

## Fuzz and robustness (item 9)

`tests/test_fuzz.py` exercises seeded mixed Unicode, dashes, CR/LF/CRLF, BOM, NUL,
surrogates and astral characters: translation agreement, idempotence, ASCII targets,
chunk equivalence, independent positions and preservation of letters, marks and digits.
`tests/test_scale.py` checks growing input shapes and a million CR characters; contracts
also cover threads, huge invalid forms, 100,000 CLI hits and closed or missing streams.
All pytest runs use pytest-timeout with a 300-second per-test limit and scratch basetemps.

## Packaging and upgrade (items 8, 11 to 14)

https://pypi.org/pypi/unidash/json returned HTTP 200 on 2026-11-02. Its current version is
0.2.0, uploaded on 2026-10-26. This supersedes the earlier report's 2026-10-23 HTTP 404.
The 1.0.0 CHANGELOG is dated 2026-11-02 and corrects that publication history.

With `UNIDASH_E2E=1` and `UNIDASH_E2E_PYPI=1`, `tests/test_e2e_wheel.py` builds the wheel
and sdist, creates a fresh venv, installs the actual PyPI 0.2.0, then upgrades that same
venv to the built 1.0.0 wheel. The external consumer runs with `-I` from an empty folder.
`tests/upgrade_consumer.py` compares 2,400 seeded combinations (200 texts, three forms,
four flag combinations), including fold, chunk, table, hit, punctuation and membership
results. Both releases produce the same digest. A pickle written by 0.2.0 loads after
upgrade. Non-string forms, bounded messages, string subclasses and explicit `--punct
--form ascii` show exactly the documented changes. Common CLI output remains identical.

The installed-wheel e2e passes: API, type marker, exports, pickles, errors, console script,
module invocation, stdin, files, all switches, check reports, invalid UTF-8 and early pipe
closure. `twine check --strict` passes for both built archives.

Archive names were inspected in this session. Wheel: ten package modules, `py.typed`,
metadata, entry point and LICENSE. Sdist: source, tests, scripts, docs, manifest and
LICENSE; no fetched files, report files, bytecode, cache or scratch files. Test sources
ship in the sdist for reproducibility, never in the wheel.

README states the problem, alternatives and limitations, installation and usage; links
are absolute, including GUIDE and CHANGELOG. Its certification badge matches the supplied
reference. Metadata is 1.0.0, Production/Stable, Python >=3.10 with classifiers through
3.14, MIT, project URLs and keywords, and no runtime dependencies.

## Supported interpreters (item 10)

All eleven distinct available builds passed the installed-wheel suite: 320 tests and
nine doctests each. Each used a fresh venv or an isolated copy of the embedded runtime,
tests extracted from the sdist with its `src` removed, and the fetched Unicode data.

| CPython build | Suite | Doctests |
| --- | --- | --- |
| 3.10.11 (embedded), 3.10.22 | 320 passed, 3 skipped each | 9 passed each |
| 3.11.9 (embedded), 3.11.18 | 320 passed, 3 skipped each | 9 passed each |
| 3.12.10 (embedded), 3.12.16 | 320 passed, 3 skipped each | 9 passed each |
| 3.13.2 (embedded), 3.13.18 | 320 passed, 3 skipped each | 9 passed each |
| 3.14.6, 3.14.10, 3.14.10 free-threaded | 320 passed, 3 skipped each | 9 passed each |

Skips: opt-in build, POSIX byte filenames and Windows long paths. Embedded builds
passed with the venv import inside the opt-in test; deleted launcher entries were excluded.

## Gates (item 15)

The initial CPython 3.14.6 gates passed: format, lint, strict src/tests typing and
pytest. With fetched Unicode sources, reference programs, wheel and PyPI upgrade:
**330 passed, 2 skipped** (116.37 s). Skips were POSIX filenames and Windows long paths.
Both archives passed `twine check --strict`. Without optional data/build checks:
320 passed, 12 skipped. Installed suites passed on all builds listed above.
Later QA gate results are recorded with each round below.

## Mutation round (item 18)

Twelve mutations applied separately to a scratch copy on 2026-11-02 all failed
contracts with pytest exit 1. Baseline/restored: 149 passed, one POSIX skip.
Earlier rounds (37, 15, 14 and 6 killed mutants) remain in CERT-1.0-MUTATIONS.md.

| ID | Mutation | First failing contract |
| --- | --- | --- |
| N01 | quote bound widened | `test_contract_api.py::test_messages_quote_at_most_forty_characters[41]` |
| N02 | str override honored | `test_contract_api.py::test_str_subclasses_are_read_as_their_characters` |
| N03 | script switch inverted | `test_tools.py::test_find_follows_the_fold_options` |
| N04 | soft hyphen switch inverted | `test_contract_api.py::test_str_subclasses_are_read_as_their_characters` |
| N05 | typographic script target wrong | `test_dashes.py::test_typographic_script_hyphens_become_the_unicode_hyphen` |
| N06 | TeX width off by one | `test_contract_api.py::test_str_subclasses_are_read_as_their_characters` |
| N07 | leading BOM occupies a column | `test_tools.py::test_a_leading_bom_takes_no_column` |
| N08 | column starts at zero | `test_tools.py::test_find_reports_line_column_and_name` |
| N09 | ellipsis loses two stops | `test_fold.py::test_ellipsis_char_becomes_three_dots` |
| N10 | bullet becomes hyphen | `test_fold.py::test_bullet_becomes_asterisk` |
| N11 | check exits success on changes | `test_cli.py::test_check_lists_each_change_and_exits_one` |
| N12 | unreadable input exits success | `test_cli.py::test_missing_file_is_an_error_but_others_still_run` |

## Independent QA and review (items 16, 19)

Earlier QA evidence is in CERT-1.0-QA.md. Five current lens approvals and an
independent reviewer PASS remain pending; earlier approvals predate later findings.

Fixes of QA lens rounds 1 to 4 are in CERT-1.0-QA.md.

### QA lenses, round 5 fixes (2026-11-03)

Base: `c10b6824da1e6f0cf1e5cfd60c82c8d91e5f2e70`.
Fix commit: this commit, `test rejection of bytearray and nul forms`.
E-11 covers immediate TypeError for all three valid form names as bytearrays.
E-12 covers immediate ValueError for all three forms with NUL at the start, middle
or end, including a suffix after NUL. Both cover all four APIs without consuming
iterators and the installed-wheel consumer. NUL is excluded from subprocess argv.
Production behavior is unchanged; CHANGELOG records the coverage fixes. Neither
finding is disputed; independent re-verification remains pending.
Baseline/restored source passes 368 API cases. Bytearray coercion fails 12 new cases;
NUL truncation fails 24 (trailing NUL, with/without suffix). Both mutated wheels fail
their external consumers. Scratch mutations are restored.
Final format, lint, strict src/tests typing and pytest pass: **867 passed, 11 skipped**
with wheel and PyPI upgrade (182.67 s). Skips: nine missing fixtures, two platform/path.
Initial run: report length and one timing ratio failed; report condensed, serial rerun passed.
Per-test timeout: 300 s; basetemps and evidence remain in scratch.
Evidence: `C:/lianes8-build/codex-pylib/scratch/unidash-cert/fix-r5/`.

### QA lenses, round 6 fixes (2026-11-03)

Base `ec7a43c535a8bb4aa3785055d82a5051628747c0`; fix commit
`925ab7cb135113357e2eaba79d83372adef3e8f4`. Lens e mutants surviving in `check_form`: E-13
memoryview forms decoded as ASCII, E-14 trailing CR/LF stripped, E-15 VT, FF, U+001C to
U+001F, U+0085 and U+00A0 stripped. All are contract gaps; behavior is unchanged.
Disputed findings: none. The round closes the whole class, not just three spellings:
- `test_contract_forms.py`: only-leading and only-trailing `\n`, `\r\n` and `\r` forms join
  `INVALID_FORMS` for the four APIs and both CLI subprocess modes (108 new cases).
- `test_contract_form_class.py` (new): 30,727 str spellings get the exact `ValueError` from
  the four APIs (iterators not consumed) and the CLI in process: each form with any of 2,252
  characters (every `str.isspace()` one and categories Cc, Cf, Mn, Me, Zs, Zl, Zp), ASCII
  punctuation or `\r\n` before, after, around and inside it; every case mix, substrings,
  deletions, swaps, substitutions, additions, Cyrillic and Greek lookalikes, long s, aliases.
  68 non-str values (memoryview, array, UTF-16/32 bytes, `UserString`, paths, `__str__` and
  `__fspath__` objects, a non-str enum member, containers, iterators, numbers, None) get the
  exact `TypeError` at call time.
- `wheel_consumer.py` checks the padded set, near misses, lookalikes, memoryview, array,
  path and number forms on the installed wheel; `test_e2e_wheel.py` drives the installed CLI
  with newline, CR/LF, VT and NBSP padded forms.

On a scratch copy restored after each run, 24 `check_form` mutants (the three survivors,
strip, collapse, casefold, punctuation, format or combining mark removal, fuzzy, prefix,
suffix and anagram matching, transliteration, long s, `os.fspath`, `str()`, int index, enum
value, UTF-16, array, sequence join, None as default) and one CLI-only strip are all killed;
ten of them, the survivors included, also fail the installed consumer program.
Gates, Elena's PC, CPython 3.14.2, clean clone of the fix commit: format, lint and
`mypy --strict src` exit 0; pytest with `UNIDASH_E2E=1` and `UNIDASH_E2E_PYPI=1` (wheel,
installed consumer and CLI, upgrade from PyPI 0.2.0): **942 passed, 54 skipped** (84.74 s).
Skips: optional oracle packages, unfetched Unicode fixtures, POSIX names. Strict test typing
passes on CPython 3.13.2. Timeout 300 s. Lens e re-verification pending.
Evidence: `D:/pylib-scratch/unidash-cert/fix-r6/`.

## Release status (item 17)

PR #3 targets main from release/1.0.0. Merge and publication remain pending.
