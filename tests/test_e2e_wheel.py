"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with UNIDASH_E2E=1.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("UNIDASH_E2E") != "1", reason="set UNIDASH_E2E=1 to build"
)

PROGRAM = r"""
import importlib.metadata, importlib.resources
import unidash as u

assert "site-packages" in u.__file__, u.__file__
assert importlib.metadata.version("unidash") == u.__version__
assert importlib.resources.files("unidash").joinpath("py.typed").is_file()
assert len(u.__all__) == 9 and len(u.DASHES) == 31

em, en, soft = chr(0x2014), chr(0x2013), chr(0xAD)
assert u.fold_dashes("a" + em + "b" + soft) == "a-b"
assert u.fold_dashes("1" + en + "2" + em, "tex") == "1--2---"
assert u.fold_dashes(chr(0xFE58) + chr(0xFF0D), "typographic") == em + "-"
assert u.fold_dashes(chr(0x5BE), script_hyphens=True) == "-"
assert u.to_ascii_punct(chr(0x201C) + "x" + chr(0x201D) + chr(0x301C)) == '"x"~'
(hit,) = u.find_dashes("x\n" + em)
assert (hit.line, hit.column, hit.codepoint, hit.name) == (2, 1, "U+2014", "EM DASH")
assert "".join(u.iter_fold_dashes([en, em])) == "--"
assert u.is_dash(chr(0x2212)) and not u.is_dash(soft)
try:
    u.fold_dashes("a", "latex")
except ValueError:
    pass
else:
    raise AssertionError("unknown form accepted")
print("e2e ok")
"""


def _run(*cmd: str | Path, cwd: Path | None = None, stdin: bytes | None = None) -> bytes:
    result = subprocess.run(
        [str(c) for c in cmd], cwd=cwd, input=stdin, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    return result.stdout


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    _run(sys.executable, "-m", "build", "--wheel", "--outdir", dist, ROOT)
    (wheel,) = dist.glob("unidash-*.whl")
    names = zipfile.ZipFile(wheel).namelist()
    assert not [name for name in names if "vectors" in name or name.startswith("tests/")]
    assert "unidash/py.typed" in names

    _run(sys.executable, "-m", "build", "--sdist", "--outdir", dist, ROOT)
    (sdist,) = dist.glob("unidash-*.tar.gz")
    with tarfile.open(sdist) as archive:
        members = archive.getnames()
    data = [name for name in members if "/tests/vectors/" in name]
    assert data == [name for name in data if name.endswith("/MANIFEST.txt")]

    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    _run(python, "-m", "pip", "install", "-q", wheel)

    # Run from an empty folder so the source tree cannot shadow the install.
    work = tmp_path / "work"
    work.mkdir()
    assert _run(python, "-I", "-c", PROGRAM, cwd=work).decode().splitlines() == ["e2e ok"]

    (work / "a.md").write_bytes(("x" + chr(0x2014) + "y\n").encode("utf-8"))
    script = bindir / ("unidash.exe" if sys.platform == "win32" else "unidash")
    assert _run(script, "--form", "tex", "a.md", cwd=work) == b"x---y\n"
    check = subprocess.run(
        [str(script), "--check", "a.md"], cwd=work, capture_output=True, check=False
    )
    assert check.returncode == 1
    assert check.stdout.decode().splitlines() == ["a.md:1:2: U+2014 EM DASH"]
    filtered = _run(python, "-I", "-m", "unidash", "-", cwd=work, stdin="a\u2013b".encode())
    assert filtered == b"a-b"
