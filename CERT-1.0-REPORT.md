# unidash 1.0.0 certification report

Preparation resumed on 2026-11-02 from 6f49665. Earlier commits and evidence are retained.
No library implementation changed in this preparation update.

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
Tests derive Dash membership, Pd membership, names, compatibility decompositions and
confusable targets from those fetched files. The sources are not invented test vectors.
Hand-written boundary expectations and generated random inputs are separate contracts.

Independent reference programs pinned in `requirements-oracles.txt` run in this session:
regex 2026.9.29 scans all code points for Dash and Pd; Markdown 3.11.2, markdown-it-py 4.2.0,
docutils 0.23 and smartypants 2.0.2 check TeX conventions on seeded texts. Full render tests
pin the documented Markdown block exceptions. Prior source/reference evidence and its
limitations remain recorded in the earlier commits and CERT-1.0-QA.md.

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

Skips: the opt-in build test (run separately), POSIX byte filenames, and a readable
210-character filename whose full temporary path this Windows configuration refuses.
Embedded builds omit `venv`; moving that import inside the opt-in build test fixed test
collection, and all four embedded suites then passed. No library change was needed.
The launcher also lists deleted installations: 3.10.19, 3.11.5, 3.11.14, 3.11.17,
3.12.12, 3.12.15, 3.13.16, 3.14.2/3.14.2t and 3.14.8/3.14.8t. Those paths cannot run;
the table covers every available build found by the filesystem inventory.

## Gates (item 15)

On CPython 3.14.6, each final command exits 0 independently: `ruff format --check .`,
`ruff check .`, `mypy --strict src`, `mypy --strict src tests`, and `pytest`.
The final source-tree suite includes fetched sources, all reference programs,
`UNIDASH_E2E=1` and `UNIDASH_E2E_PYPI=1`: **330 passed, 2 skipped** in 116.37 seconds.
The skips are POSIX byte filenames and the Windows long-path case described above.
The final wheel and sdist both pass `twine check --strict`. Without optional fetched
files and build tests, the earlier source-tree run passed 320 tests with 12 skips.
The installed suite with fetched sources passes 320 tests plus nine doctests on every
available build above. All preparation items (1 to 15 and 18) are complete.

## Mutation round (item 18)

On 2026-11-02, twelve mutations were applied one at a time to a scratch copy. The API,
tools, dash, punctuation and CLI contract tests ran with `-x` and bytecode disabled.
Every mutant returned pytest exit 1 with an assertion failure. Baseline and restored
source passed the same selection (149 passed, one POSIX filename skip). No mutant survived. The additional round is below;
earlier rounds (37, 15, 14 and 6 killed mutants) remain in CERT-1.0-MUTATIONS.md.

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

The eight earlier QA rounds and their fixes are preserved in CERT-1.0-QA.md. They did
not finish with five passing lenses. The round-2 lens b PASS predates later code changes
and subsequent findings, so it is not a current approval. No independent reviewer has
passed the final commit. These checks remain for the next stage.

### QA lenses, round 1 fixes (2026-11-02)

Base: `5da447254e0739a9c6014b171baed37bc8b36ce9`. Fix commit: the commit containing this
section, identified by Git revision `:/^fix round one qa findings$` on `release/1.0.0`.
All seven reported findings are addressed; no finding is disputed. Independent lens
re-verification remains pending. Public signatures, defaults and exception types are unchanged.

| Finding | Change and verification |
| --- | --- |
| B-001 | GUIDE distinguishes HTML blocks and attributes from inline HTML text. Six new converter cases pass with Markdown 3.11.2 and markdown-it-py 4.2.0. |
| C-01 | API and CLI form errors omit rejected values and list allowed forms. Short and long synthetic secret markers are covered across all four form-taking APIs and CLI subprocesses. |
| C-02 | Type errors omit received class names for text, char, chunk, form and both flags. Million-character and control-character class names produce fixed diagnostics. |
| E-01 | The hostile str subclass now raises from `__str__`; the existing character and form contracts still pass. M16 fails `test_str_subclasses_are_read_as_their_characters`. |
| E-02 | Complete chunk sequences include empty inputs and chunks emptied by folding. M19 fails `test_stream_preserves_every_empty_chunk`. |
| E-03 | No hits are constructed before iteration, and each next call constructs one. M20 fails `test_find_constructs_only_the_hit_requested`. |
| E-04 | Subprocess tests preserve repeated filenames and order in filter and check modes. M35 fails `test_repeated_files_preserve_multiplicity_and_order`. |

Diagnostic contracts were added first: the original implementation produced 24 failures
and four passes. After fixing diagnostics, the focused contracts and HTML tests pass
(74 passed). Each of M16, M19, M20 and M35 was injected separately in a scratch copy:
pytest exited 1 on the named contract; restoring each original file made its test pass.
The four coverage findings required no production behavior change. CHANGELOG records
both diagnostic changes and the documentation and contract corrections.

Final local gates: `ruff format --check .`, `ruff check .`, `mypy --strict src`,
`mypy --strict src tests` and the full pytest suite exit 0 on CPython 3.14.6:
**351 passed, 11 skipped** in 123.05 seconds.
Pytest includes the wheel build, installed API/CLI checks and PyPI 0.2.0 upgrade, with a
300-second per-test timeout. Optional Unicode source files are absent in this checkout;
their nine tests skip, along with the two platform/path skips documented above.
Closed-reader tests use an ordinary scratch sink via a startup hook instead of a device.
Logs and mutation repros are under `C:/lianes8-build/codex-pylib/scratch/unidash-cert/fix-r1/`.
An initial full run found the guide over its line limit; the shortened guide is rechecked.

## Release status (item 17)

PR #3 targets main from release/1.0.0. Merge and publication remain pending.
