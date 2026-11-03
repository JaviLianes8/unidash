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
- [x] Five QA lenses (item 19) and independent reviewer (item 16)
- [ ] Merge and publish (item 17)

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

Review round 1 full suite at `5e6d35e`, from source, 300 s timeout, on every CPython on this
PC (no 3.11 here). Skips: optional oracle/typing packages absent there, POSIX names, long paths.

| CPython build | Suite |
| --- | --- |
| 3.10.19, 3.12.12, 3.14.2 | 996 passed, 2 skipped each |
| 3.13.2 | 954 passed, 44 skipped |
| 3.14.2 free-threaded | 921 passed, 66 skipped |

Earlier the installed-wheel suite (320 tests) passed on eleven builds, 3.11 included.

## Gates (item 15)

The initial CPython 3.14.6 gates passed: format, lint, strict src/tests typing and
pytest. With fetched Unicode sources, reference programs, wheel and PyPI upgrade:
**330 passed, 2 skipped** (116.37 s). Skips were POSIX filenames and Windows long paths.
Both archives passed `twine check --strict`. Later gate results are with each round below.

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
| N12 | unreadable input exits success | `test_cli.py::test_missing_file_is_an_error_but_others_still_## Independent QA and review (items 16, 19)

All five lenses passed on their final round. Reports stay in the build scratch folder
`unidash-cert/`; fixes of every round are in CERT-1.0-QA.md.

| Lens | Rounds | Final verdict | Report | Commit |
| --- | --- | --- | --- | --- |
| a, API and docs | 1 | PASS, no findings | laptop evidence, `lens-a-r1/REPORT.md` | `5da4472` |
| b, ground truth | 2 | PASS, no findings | laptop evidence, `lens-b-r2/REPORT.md` | `89a252e` |
| c, adversarial | 2 | PASS, no findings | laptop evidence, `lens-c-r2/REPORT.md` | `89a252e` |
| d, packaging and e2e | 1 | PASS, no findings | laptop evidence, `lens-d-r1/REPORT.md` | `5da4472` |
| e, contract strength | 7 | PASS, no findings | build scratch, `lens-e-r7/REPORT.md` | `da63442` |

Independent reviewer: round 1 FAIL on item 10 (`--form=--` on 3.10) and three evidence
paths, fixed in `5e6d35e` and `8d27cca`. Round 2 PASS at `8d27cca`
(`review-r2/REPORT.md` in build scratch): suites green on 3.10.19, 3.12.12, 3.13.2 and
3.14.2, fixtures matching the MANIFEST hashes, four gates exit 0.

| Item | Score | Item | Score |
| --- | --- | --- | --- |
| 1 API retained | PASS | 11 README | PASS |
| 2 contracts | PASS | 12 dated changelog | PASS |
| 3 examples | PASS | 13 metadata | PASS |
| 4 typing | PASS | 14 archives | PASS |
| 5 errors | PASS | 15 gates | PASS |
| 6 CLI | PASS | 16 independent review | PASS |
| 7 ground truth | PASS | 17 PR, trace guard | ready; merge pending |
| 8 wheel and upgrade | PASS | 18 mutations | PASS |
| 9 fuzz and scale | PASS | 19 five QA lenses | PASS |
| 10 interpreters | PASS | | |

ratch.

## Release status (item 17)

PR #3 targets main from release/1.0.0. Merge and publication remain pending.
