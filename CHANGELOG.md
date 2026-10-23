# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-23

The first release published on PyPI; 0.1.0 and 0.2.0 were development versions. The public
API is now stable: the nine names in `unidash.__all__`, their parameter names, defaults,
results and error types are kept for every 1.x release. The dash classification follows
Unicode 18.0; a later Unicode version that adds dashes is taken in a minor release and never
moves a character that is already classified.

### Changed

- A `form` that is not a str now raises `TypeError` (`form must be a str, not list`); an
  unknown str still raises `ValueError`.
- Error messages quote at most 40 characters of the value passed, so a huge `form` string
  no longer ends up whole in the message.
- A `str` subclass is read as its plain characters: an overridden `translate` or `__iter__`
  can no longer change what `fold_dashes`, `find_dashes`, `iter_fold_dashes`, `is_dash` or
  `to_ascii_punct` return, and a subclass whose `__eq__` matches anything is no longer
  taken for a valid form.
- A non-str chunk in `iter_fold_dashes` is reported as `chunk must be a str`.
- `is_dash` says how many characters it was given (`not 2 characters`).
- `DashHit` reports and pickles as `unidash.DashHit`, not as a private module.
- `python -m unidash` no longer runs the tool when the module is only imported.
- The command line reads stdin only for `-`, so files are processed when there is no
  standard input. A missing stdin (for `-`) or stdout is reported on stderr with exit 2
  instead of a traceback.
- An invalid `--form` value is quoted to at most 40 characters in the usage error, and any
  usage error message longer than 200 characters (such as one naming a huge unknown option)
  is cut there.
- With no standard error, the command line drops its diagnostics instead of writing them
  into the folded output or the `--check` report.
- `--punct` refuses any explicit `--form`, `--form ascii` included; before, only a form
  other than the default was refused.
- A file the command line cannot read is reported with the system's reason only (the name is
  no longer repeated), and a file name longer than 200 characters is shortened to its first
  and last 100 characters there.

### Fixed

- `fold_dashes` and `iter_fold_dashes` with the `tex` form, `to_ascii_punct` and the command
  line take linear time on long text where most characters grow (the two-em and three-em
  dashes, the ellipsis); they were quadratic.
- On Windows, the command line stops quietly with exit 1 when the reader closes stdout early
  (`unidash --check big.txt | head`), as it already did elsewhere, instead of printing a
  traceback and exiting 120.
- `unidash --check` no longer crashes when a file name holds a lone surrogate (possible on
  Windows): the name is written with backslash escapes. A name the system refuses (one with
  a NUL character, or on POSIX a lone surrogate) is reported as an unreadable file (exit 2)
  instead of a traceback.
- The `DashHit` fields are annotated with `int` and `str` at runtime, so `help()` and
  `inspect.signature` show real types instead of `ForwardRef` strings.

### Added

- Runnable examples in the docstring of every public name, run as doctests.
- A guide (GUIDE.md) with the full contract of each function and the versioning promise.

## [0.2.0] - 2026-10-13

Development version, not published to PyPI.

### Added

- `fold_dashes(text, form="ascii")` with three forms: `ascii` (every dash to one `-`, wavy
  dashes to `~`), `tex` (en dash `--`, em dash `---`) and `typographic` (real dashes kept,
  small, vertical and fullwidth forms replaced by their standard counterparts).
- Every code point with the Unicode 18.0 Dash property is classified: general dashes fold by
  default, script hyphens only with `script_hyphens=True`, and the superscript and subscript
  minus are never folded.
- Soft hyphens are removed unless `keep_soft_hyphens=True`.
- `find_dashes` and `DashHit` report line, column and name of each character a fold would
  change; `is_dash`, `DASHES`, `dash_table` and the streaming `iter_fold_dashes`.
- Command line tool `unidash` (also `python -m unidash`) with `--check` for pre-commit use.
- Tests against the Unicode data files and the UTS #39 confusables, fetched by
  `scripts/fetch_vectors.py` and pinned by size and SHA-256, plus an installed-wheel test.

### Changed

- `to_ascii_punct` now folds every general dash (fullwidth, small, vertical, two-em and
  three-em dashes, wave dashes to `~`) and removes soft hyphens.
- Type errors name the type that was passed.
- `to_ascii_punct` folds fullwidth punctuation (U+FF01 to U+FF5E, not letters or digits) to
  ASCII, so the Japanese wave dash from CP932 text (U+FF5E) becomes `~`.

## [0.1.0] - 2026-10-12

Development version, not published to PyPI.

- `to_ascii_punct(text)` folds Unicode punctuation to ASCII: curly quotes to `'` and `"`,
  en and em dashes and the minus sign to `-`, the ellipsis to `...`, non-breaking and
  other spaces to a normal space, and bullets to `*`.
- Letters, including accented ones, pass through untouched, unlike `unidecode` and
  `anyascii`, which transliterate every character.
- Zero runtime dependencies, with the mapping vendored in.
