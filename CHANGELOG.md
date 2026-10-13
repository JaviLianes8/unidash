# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

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

## [0.1.0]

- First release.
- `to_ascii_punct(text)` folds Unicode punctuation to ASCII: curly quotes to `'` and `"`,
  en and em dashes and the minus sign to `-`, the ellipsis to `...`, non-breaking and
  other spaces to a normal space, and bullets to `*`.
- Letters, including accented ones, pass through untouched, unlike `unidecode` and
  `anyascii`, which transliterate every character.
- Zero runtime dependencies, with the mapping vendored in.
