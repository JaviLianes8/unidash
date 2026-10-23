"""Seeded property tests over hostile text, and linear time on large input."""

from __future__ import annotations

import random
import re
import sys
import time
import unicodedata
from collections.abc import Callable

import pytest

from unidash import (
    DASHES,
    Form,
    dash_table,
    find_dashes,
    fold_dashes,
    iter_fold_dashes,
    to_ascii_punct,
)

FORMS: tuple[Form, ...] = ("ascii", "tex", "typographic")
SOFT, BOM, CR, LF = chr(0xAD), chr(0xFEFF), chr(13), chr(10)
SPECIAL = [*sorted(DASHES), SOFT, BOM, CR, LF, CR + LF, "\x00", chr(0x301), chr(0xD800)]
SPECIAL += [chr(0xDFFF), chr(0x10FFFF), chr(0x1F600), chr(0x2026), chr(0x201C), chr(0xFF5E)]
SEEDS = (11, 23, 2026)


def _text(rng: random.Random) -> str:
    parts = []
    for _ in range(rng.randrange(60)):
        roll = rng.random()
        if roll < 0.5:
            parts.append(rng.choice(SPECIAL))
        elif roll < 0.7:
            parts.append(chr(rng.randrange(sys.maxunicode + 1)))
        else:
            parts.append(chr(rng.randrange(0x20, 0x7F)))
    return "".join(parts)


def _options(rng: random.Random) -> tuple[Form, bool, bool]:
    return rng.choice(FORMS), rng.random() < 0.5, rng.random() < 0.5


@pytest.mark.parametrize("seed", SEEDS)
def test_fold_is_per_character_idempotent_and_never_raises(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(3000):
        text = _text(rng)
        form, script, keep = _options(rng)
        options = {"script_hyphens": script, "keep_soft_hyphens": keep}
        folded = fold_dashes(text, form, **options)
        assert folded == "".join(fold_dashes(char, form, **options) for char in text)
        assert fold_dashes(folded, form, **options) == folded
        assert text.translate(dash_table(form, **options)) == folded


@pytest.mark.parametrize("seed", SEEDS)
def test_ascii_forms_leave_no_foldable_dash_behind(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(3000):
        text = _text(rng)
        form: Form = rng.choice(("ascii", "tex"))
        folded = fold_dashes(text, form, script_hyphens=True)
        assert set(folded) & DASHES <= {"-", chr(0x207B), chr(0x208B)}
        assert SOFT not in folded


def _expected_positions(text: str, changed: set[int]) -> list[tuple[int, int, int]]:
    # An independent count: split on the editor line ends, then walk each line.
    result, offset = [], 0
    for number, line in enumerate(re.split(r"(?:\r\n|\r|\n)", text), start=1):
        for index, _char in enumerate(line):
            if offset + index in changed:
                skip = 1 if number == 1 and text.startswith(BOM) else 0
                result.append((offset + index, number, index + 1 - skip))
        offset += len(line) + (
            2 if text[offset + len(line) : offset + len(line) + 2] == CR + LF else 1
        )
    return result


@pytest.mark.parametrize("seed", SEEDS)
def test_find_dashes_positions_match_an_independent_count(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(2000):
        text = _text(rng)
        form, script, keep = _options(rng)
        changed = {
            i
            for i, char in enumerate(text)
            if fold_dashes(char, form, script_hyphens=script, keep_soft_hyphens=keep) != char
        }
        hits = find_dashes(text, form, script_hyphens=script, keep_soft_hyphens=keep)
        found = [(hit.offset, hit.line, hit.column) for hit in hits]
        assert found == _expected_positions(text, changed), ascii(text)


@pytest.mark.parametrize("seed", SEEDS)
def test_chunks_fold_like_the_whole_text(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(1000):
        text = _text(rng)
        cuts = sorted(rng.randrange(len(text) + 1) for _ in range(rng.randrange(5)))
        chunks = [text[a:b] for a, b in zip([0, *cuts], [*cuts, len(text)], strict=True)]
        form, script, keep = _options(rng)
        options = {"script_hyphens": script, "keep_soft_hyphens": keep}
        assert "".join(iter_fold_dashes(chunks, form, **options)) == fold_dashes(
            text, form, **options
        )


@pytest.mark.parametrize("seed", SEEDS)
def test_to_ascii_punct_is_idempotent(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(3000):
        once = to_ascii_punct(_text(rng))
        assert to_ascii_punct(once) == once


def test_letters_marks_and_digits_are_never_touched() -> None:
    for codepoint in range(sys.maxunicode + 1):
        char = chr(codepoint)
        if unicodedata.category(char)[0] in "LMN":
            assert to_ascii_punct(char) == char, hex(codepoint)
            assert fold_dashes(char, script_hyphens=True) == char, hex(codepoint)


def _best_time(function: Callable[[], object]) -> float:
    best = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        function()
        best = min(best, time.perf_counter() - start)
    return best


@pytest.mark.parametrize(
    "shape",
    [chr(0x2014), SOFT, CR, CR + LF, "a", chr(0x2014) + LF, chr(0x5BE) + SOFT + chr(0x2E3B)],
)
def test_large_input_takes_linear_time(shape: str) -> None:
    small, large = shape * (50_000 // len(shape)), shape * (400_000 // len(shape))
    works: list[Callable[[str], object]] = [
        lambda text: fold_dashes(text, "tex", script_hyphens=True),
        to_ascii_punct,
        lambda text: sum(1 for _ in find_dashes(text)),
    ]
    for work in works:
        ratio = _ratio(work, small, large)
        assert ratio < 24, (ascii(shape), ratio)  # eight times the input; linear is about 8


def _ratio(work: Callable[[str], object], small: str, large: str) -> float:
    return _best_time(lambda: work(large)) / max(_best_time(lambda: work(small)), 1e-6)


def test_a_million_line_breaks_are_counted() -> None:
    text = CR * 1_000_000 + chr(0x2014)
    (hit,) = find_dashes(text)
    assert (hit.line, hit.column, hit.offset) == (1_000_001, 1, 1_000_000)
