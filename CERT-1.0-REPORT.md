# unidash 1.0.0 certification report

The 1.0.0 certification bar applied to unidash. PyPI has no `unidash` release
(`https://pypi.org/pypi/unidash/json` answered 404 on 2026-10-23), so there is no upgrade
path to check; every change since 0.2.0 is still listed in the CHANGELOG.

Progress:
- [x] Branch `release/1.0.0` created from `main` (a7a06bb, 0.2.0)
- [x] Baseline gates on 0.2.0
- [x] API review and 1.0.0 changes (item 1)
- [x] Errors, typing, docstrings and doctests (items 2 to 5)
- [ ] Ground truth: Unicode data fetched live, independent oracles (item 7)
- [ ] Contract, fuzz and author mutation round (items 6, 9, 18)
- [ ] Docs: README, GUIDE, CHANGELOG (items 11, 12)
- [ ] Packaging, e2e, every Python (items 8, 10, 13, 14)
- [ ] Gates (item 15)
- [ ] PR and trace guard
- [ ] Five QA lenses (item 19)
- [ ] Independent reviewer (item 16)

## Baseline on 0.2.0 (before any change)

On this PC, CPython 3.13.2, with the Unicode data fetched: `ruff format --check .`,
`ruff check .` and `mypy --strict src tests` exit 0; `pytest` 126 passed, 2 skipped (the
installed-wheel test, which needs `UNIDASH_E2E=1`, and the POSIX file name test); no
doctests existed.

Defects found in 0.2.0 by reading and then reproducing:

- `fold_dashes("a", "x" * 100000)` raised a `ValueError` whose message held the whole
  100,000 character string (100,051 characters).
- A `str` subclass that overrides `translate` made `fold_dashes` return the override's
  result; one that overrides `__iter__` made `find_dashes` report nothing.
- A `str` subclass whose `__eq__` matches anything was accepted as a form.
- A list as `form` raised `ValueError`, although it is a wrong type.
- `DashHit` reported and pickled as `unidash._dashes.DashHit`, a private module.
- No public docstring had a runnable example.
- `scripts/release.ps1` refused to upload once the name existed on PyPI, so it could only
  ever publish one version, and it built from a dirty tree.
