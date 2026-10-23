# unidash 1.0.0 QA rounds 1 to 4 (item 19)

The findings of the first four QA rounds and how each was fixed; the summary and the
latest round are in CERT-1.0-REPORT.md.

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

Round 3, on 6fa3a04: every lens returned at least one finding. All are fixed in 931adf3,
d027888 and 6b342cc, each behaviour bug with a contract test that failed on 6fa3a04 first;
the behaviour changes are in the CHANGELOG. No finding is disputed.

| Finding | Fix | Proof |
| --- | --- | --- |
| a-F1, d-D1, e-F1 (high, high, medium): `pytest` red at 6fa3a04, this report had 234 lines and its gate runs were of d9dc54f | mutation tables moved to CERT-1.0-MUTATIONS.md (also excluded from the sdist); gates and matrix rerun on the round 3 code and recorded above | `test_every_source_file_stays_under_two_hundred_lines` passes |
| a-F2 (low): `DashHit` fields annotated with `ForwardRef('int')` at runtime | no `__future__` import in `_hit.py` | `test_contract.py::test_dash_hit_fields_carry_their_real_types` (failed before) |
| a-F3 (low): `--punct --form ascii` accepted, exit 0 | `--form` defaults to None, so any explicit `--form` is refused with `--punct` | `test_cli_names.py::test_punct_refuses_any_explicit_form` (`ascii` failed before) |
| b-F1 (low): the `tex` read-back promise covered "any other character" | README and GUIDE promise letters, digits, spaces and `. , ; : ? ! ( )`, and name the backslash escape, the markdown-it-py `+-` rule and code spans | oracle texts now mix CJK, accented words and that punctuation around the dashes (over 50 texts with a dash touching it); each named exception pinned by a test |
| c2-F1 (medium): `--check` crashes when a Windows file name holds a lone surrogate | report names written with surrogateescape, else backslash escapes; reading errors include `ValueError`, so a name POSIX cannot encode, or one with a NUL, is an unreadable file | in process and by subprocess on Windows (both failed before); a missing such name and a NUL name in both modes (the NUL one failed before) |
| c2-F2 (low): a huge file name echoed twice in a read error | only the system's reason is printed, and a name over 200 characters keeps its first and last 100 | 30,000-character name: under 500 bytes of stderr; names of 200 and 201 characters (failed before) |
| e-F2 (low): mutant N07, U+2028 ends a line, survives | test of VT, FF, U+001C to U+001E, U+0085, U+2028 and U+2029 before a dash; the fuzz pool gains five of them | N07 applied: the new test and all three fuzz seeds fail |
| e-F3 (low): mutant N13, `>=` at the usage error limit, survives | messages of 199, 200 and 201 characters through the parser's `error` | N13 applied: the 200 case fails |

Disputed findings: none.

Round 4, on 46ebbae: all five lenses confirmed the round 3 fixes. Lens c found nothing else
in 32 probes and 6,000 fuzzed names, lens d reran the six interpreters and the external
consumer, and each lens reported what follows. All of it is fixed in 2bd07b5; the behaviour
change is in the CHANGELOG.

| Finding | Fix | Proof |
| --- | --- | --- |
| a-N1, b-N1, c3-F1, d-F1, e-G1 (low): on Windows `--check` wrote a lone surrogate from U+DC80 to U+DCFF in a file name as a raw byte, so the report was not UTF-8, against the GUIDE | `_name_bytes` uses surrogateescape only where the file system error handler is surrogateescape (POSIX names are bytes); elsewhere every lone surrogate is a backslash escape | `test_cli_names.py`: in process for U+D800, U+DBFF, U+DC00, U+DC7F, U+DC80, U+DCFF, U+DD00 and U+DFFF, by subprocess for U+D800, U+DC80 and U+DCFF (U+DC80 and U+DCFF failed on 46ebbae in both); the handler test runs the POSIX branch on every platform |
| e-G1 (low): mutant P21, backslash escapes for POSIX bytes too, survived on Windows | the handler test above | M68 killed |
| e-G2 (low): mutant P30, the `--check` prefix shortened like the error name, survived | contract: a readable 210-character name is written whole while a missing one of the same length is shortened | M69 killed (the new test fails with it) |
| b-F1b (low): the `tex` read-back promise ignored Markdown block rules (a line indented four spaces is code; a line of only dashes and spaces is a thematic break) | GUIDE names both rules among the exceptions | full renders through Python-Markdown and markdown-it-py (now `tests/test_markdown_blocks.py`, reworded in round 5) |

Disputed findings: none.
