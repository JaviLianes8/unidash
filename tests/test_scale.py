"""Large input where most characters grow (TeX widths, the ellipsis) still takes linear time,
and a long text folds exactly like its characters one by one."""

from __future__ import annotations

import io
import random
import sys
import time
from collections.abc import Callable

import pytest

from unidash import fold_dashes, iter_fold_dashes, to_ascii_punct
from unidash._cli import main

TWO_EM, THREE_EM, ELLIPSIS = chr(0x2E3A), chr(0x2E3B), chr(0x2026)
SMALL, LARGE = 1_000_000, 4_000_000


def _cli(*args: str) -> Callable[[str], object]:
    def run(text: str) -> object:
        data = text.encode("utf-8")
        saved = sys.stdin, sys.stdout
        out = io.BytesIO()
        sys.stdin, sys.stdout = io.TextIOWrapper(io.BytesIO(data)), io.TextIOWrapper(out)
        try:
            return main(list(args))
        finally:
            sys.stdin, sys.stdout = saved

    return run


WORKS: dict[str, tuple[str, Callable[[str], object]]] = {
    "fold_dashes tex": (THREE_EM, lambda text: fold_dashes(text, "tex")),
    "fold_dashes tex em": (chr(0x2014), lambda text: fold_dashes(text, "tex")),
    "iter_fold_dashes tex": (THREE_EM, lambda text: list(iter_fold_dashes([text], "tex"))),
    "to_ascii_punct": (ELLIPSIS, to_ascii_punct),
    "cli tex": (THREE_EM, _cli("--form", "tex")),
    "cli punct": (ELLIPSIS, _cli("--punct")),
}


def _best_time(function: Callable[[], object]) -> float:
    best = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        function()
        best = min(best, time.perf_counter() - start)
    return best


@pytest.mark.parametrize("name", WORKS)
def test_growing_input_takes_linear_time(name: str) -> None:
    char, work = WORKS[name]
    small, large = char * SMALL, char * LARGE
    ratio = _best_time(lambda: work(large)) / max(_best_time(lambda: work(small)), 1e-6)
    # Four times the input; linear is about 4, quadratic about 16.
    assert ratio < 10, (name, ratio)


def test_a_long_text_folds_like_its_characters() -> None:
    rng = random.Random(7)
    pool = [TWO_EM, THREE_EM, ELLIPSIS, chr(0x2013), chr(0xAD), chr(0x201C), "a", chr(0x1F600)]
    text = "".join(rng.choice(pool) for _ in range(300_000))
    for form in ("ascii", "tex", "typographic"):
        expected = "".join(fold_dashes(char, form) for char in text)
        assert fold_dashes(text, form) == expected
        assert "".join(iter_fold_dashes([text, text], form)) == expected * 2
    assert to_ascii_punct(text) == "".join(to_ascii_punct(char) for char in text)
