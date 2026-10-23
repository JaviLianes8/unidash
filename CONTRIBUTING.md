# Contributing

Thanks for taking the time. This project keeps a small, predictable shape.

## Setup

```
pip install -r requirements-dev.txt
```

## Before you open a pull request

- Keep public API in `src/unidash/__init__.py`; internals live in `_`-prefixed modules.
- Add a test for the behaviour you change. Tests write only to pytest's temporary folders.
  They read the repository's own files (the docs tests check README, GUIDE and CHANGELOG)
  and the Unicode data in `tests/vectors/unicode/`, skipping when it has not been fetched.
  Command line tests also start the tool as a subprocess. Only the opt-in installed-wheel
  test (`UNIDASH_E2E=1`) may need the network: it builds the package, and the isolated
  build downloads the build backend.
- Run `scripts/check.ps1` (format, lint, types, tests) and make sure it passes.
- One logical change per commit, imperative subject line.

Open an issue first if the change is large or shifts the public API.
