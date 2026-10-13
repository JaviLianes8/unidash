"""The public surface: names, version and type information."""

from __future__ import annotations

import importlib.resources

import unidash

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "DASHES",
    "DashHit",
    "Form",
    "dash_table",
    "find_dashes",
    "fold_dashes",
    "is_dash",
    "iter_fold_dashes",
    "to_ascii_punct",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(unidash.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in unidash.__all__:
        assert hasattr(unidash, name)


def test_version_is_a_three_part_string() -> None:
    parts = unidash.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("unidash").joinpath("py.typed").is_file()
