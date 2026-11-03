"""Chunk boundaries and lazy hit construction are observable API contracts."""

from __future__ import annotations

import pytest

from unidash import DashHit, _hit, find_dashes, iter_fold_dashes


def test_stream_preserves_every_empty_chunk() -> None:
    assert list(iter_fold_dashes(["", "a\u2014", "", "\u00ad", ""])) == ["", "a-", "", "", ""]
    assert list(iter_fold_dashes(["", ""])) == ["", ""]
    assert list(iter_fold_dashes([])) == []


def test_find_constructs_only_the_hit_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    constructed = 0

    def hit(offset: int, line: int, column: int, char: str, name: str) -> DashHit:
        nonlocal constructed
        constructed += 1
        return DashHit(offset, line, column, char, name)

    monkeypatch.setattr(_hit, "DashHit", hit)
    hits = find_dashes("\u2014" * 2000)
    assert constructed == 0
    assert next(hits) == DashHit(0, 1, 1, "\u2014", "EM DASH")
    assert constructed == 1
    assert next(hits) == DashHit(1, 1, 2, "\u2014", "EM DASH")
    assert constructed == 2
