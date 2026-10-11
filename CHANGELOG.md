# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

- First release.
- `to_ascii_punct(text)` folds Unicode punctuation to ASCII: curly quotes to `'` and `"`,
  en and em dashes and the minus sign to `-`, the ellipsis to `...`, non-breaking and
  other spaces to a normal space, and bullets to `*`.
- Letters, including accented ones, pass through untouched, unlike `unidecode` and
  `anyascii`, which transliterate every character.
- Zero runtime dependencies, with the mapping vendored in.
