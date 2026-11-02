"""Compare real installed releases across an in-place upgrade, from an empty directory."""

from __future__ import annotations

import hashlib
import json
import pickle
import random
import subprocess
import sys
from pathlib import Path

import unidash as u


def snapshot() -> str:
    rng = random.Random(20261102)
    alphabet = sorted(u.DASHES) + list("abc 123\r\n\ufeff\u00ad\u201c\u2026\ud800")
    digest = hashlib.sha256()
    for _ in range(200):
        text = "".join(rng.choices(alphabet, k=rng.randrange(80)))
        for form in ("ascii", "tex", "typographic"):
            for scripts in (False, True):
                for soft in (False, True):
                    options = {"script_hyphens": scripts, "keep_soft_hyphens": soft}
                    folded = u.fold_dashes(text, form, **options)
                    chunks = u.iter_fold_dashes([text[:10], text[10:]], form, **options)
                    assert "".join(chunks) == folded
                    table = u.dash_table(form, **options)
                    assert text.translate(table) == folded
                    hits = list(u.find_dashes(text, form, **options))
                    row = [folded, hits, u.to_ascii_punct(text), [u.is_dash(c) for c in text]]
                    digest.update(json.dumps(row, ensure_ascii=True).encode("ascii"))
    return digest.hexdigest()


def changed_contracts() -> None:
    old = u.__version__ == "0.2.0"
    assert u.__version__ in {"0.2.0", "1.0.0"}
    try:
        u.fold_dashes("x", [])  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        assert type(error) is (ValueError if old else TypeError)
    else:
        raise AssertionError("invalid form accepted")
    try:
        u.fold_dashes("x", "x" * 1000)  # type: ignore[arg-type]
    except ValueError as error:
        assert (len(str(error)) > 1000) is old
    else:
        raise AssertionError("unknown form accepted")

    class Override(str):
        def translate(self, table: object) -> str:
            return "overridden"

    assert u.fold_dashes(Override("x")) == ("overridden" if old else "x")
    hit = next(u.find_dashes("a\u2014b"))
    path = Path("old-hit.pickle")
    if old:
        path.write_bytes(pickle.dumps(hit))
    else:
        assert pickle.loads(path.read_bytes()) == hit
        assert u.DashHit.__module__ == "unidash"
    result = subprocess.run(
        [sys.executable, "-I", "-m", "unidash", "--punct", "--form", "ascii"],
        input=b"text",
        capture_output=True,
        check=False,
    )
    assert result.returncode == (0 if old else 2)
    common = subprocess.run(
        [sys.executable, "-I", "-m", "unidash", "--form", "tex"],
        input="x\u2014y".encode(),
        capture_output=True,
        check=True,
    )
    assert common.stdout == b"x---y"


if __name__ == "__main__":
    changed_contracts()
    print(snapshot())
