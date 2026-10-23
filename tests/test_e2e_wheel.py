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
assert sorted(u.__all__) == sorted(n for n in vars(u) if not n.startswith("_"))
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
for bad, error in (("latex", ValueError), (["ascii"], TypeError), ("x" * 10**6, ValueError)):
    try:
        u.fold_dashes("a", bad)
    except error as caught:
        assert len(str(caught)) < 120
    else:
        raise AssertionError("bad form accepted")
import pickle
assert u.DashHit.__module__ == "unidash"
assert pickle.loads(pickle.dumps(hit)) == hit
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
    top = {name.split("/", 1)[1] for name in members if "/" in name}
    assert {"LICENSE", "README.md", "CHANGELOG.md", "GUIDE.md", "pyproject.toml"} <= top
    assert not [name for name in top if name.startswith(("CERT-1.0", "IMPROVEMENTS"))]
    assert not [name for name in members if "__pycache__" in name or name.endswith(".pyc")]
    assert [name for name in names if name.endswith(".dist-info/licenses/LICENSE")]
    assert not [name for name in names if not name.startswith("unidash")]

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
    version = _run(script, "--version", cwd=work).decode().strip()
    assert version == "unidash " + _pyproject_version()
    quotes = (chr(0x201C) + "q" + chr(0x201D) + chr(0x5BE)).encode()
    assert _run(script, "--punct", cwd=work, stdin=quotes) == b'"q"' + chr(0x5BE).encode()
    hebrew = _run(script, "--script-hyphens", "--form", "typographic", cwd=work, stdin=quotes)
    assert hebrew.decode() == chr(0x201C) + "q" + chr(0x201D) + chr(0x2010)
    stdin_check = subprocess.run(
        [str(script), "--check", "--keep-soft-hyphens"],
        cwd=work,
        input=("a" + chr(0xAD) + chr(10) + chr(0x2212)).encode(),
        capture_output=True,
        check=False,
    )
    assert (stdin_check.returncode, stdin_check.stdout) == (1, b"<stdin>:2:1: U+2212 MINUS SIGN\n")
    broken = subprocess.run([str(script)], cwd=work, input=b"caf\xe9", capture_output=True)
    assert broken.returncode == 2
    assert broken.stdout == b""
    assert broken.stderr.decode().startswith("unidash: <stdin>: ")


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    return text.split('version = "', 1)[1].split('"', 1)[0]
