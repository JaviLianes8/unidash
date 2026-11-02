"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with UNIDASH_E2E=1.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("UNIDASH_E2E") != "1", reason="set UNIDASH_E2E=1 to build"
)


def _run(*cmd: str | Path, cwd: Path | None = None, stdin: bytes | None = None) -> bytes:
    result = subprocess.run(
        [str(c) for c in cmd], cwd=cwd, input=stdin, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    return result.stdout


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    import venv

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
    work = tmp_path / "work"
    work.mkdir()
    previous = None
    consumer = ROOT / "tests" / "upgrade_consumer.py"
    if os.environ.get("UNIDASH_E2E_PYPI") == "1":
        _run(python, "-m", "pip", "install", "-q", "unidash==0.2.0")
        previous = _run(python, "-I", consumer, cwd=work)
    _run(python, "-m", "pip", "install", "-q", wheel)
    if previous is not None:
        assert _run(python, "-I", consumer, cwd=work) == previous

    # Run from an empty folder so the source tree cannot shadow the install.
    output = _run(python, "-I", ROOT / "tests" / "wheel_consumer.py", cwd=work)
    assert output.decode().splitlines() == ["e2e ok"]

    (work / "a.md").write_bytes(("x" + chr(0x2014) + "y\n").encode("utf-8"))
    script = bindir / ("unidash.exe" if sys.platform == "win32" else "unidash")
    compatibility_forms = [
        "".join(chr(start + ord(char) - ord("a")) for char in form)
        for start in (0xFF41, 0x24D0, 0x1D41A)
        for form in ("ascii", "tex", "typographic")
    ]
    nonascii_forms = [
        form[:position] + addition + form[position:]
        for form in ("ascii", "tex", "typographic")
        for addition in ("\u200b", "\u00e9", "\u0301", "\U0001f600")
        for position in (0, 1, len(form))
    ]
    for bad in (
        " ascii",
        "tex ",
        " typographic ",
        "\ttex\n",
        "as",
        "te",
        "typo",
        "",
        *compatibility_forms,
        *nonascii_forms,
    ):
        for mode in ([], ["--check"]):
            rejected = subprocess.run(
                [str(script), *mode, "--form", bad],
                cwd=work,
                input="x\u2014".encode(),
                capture_output=True,
                timeout=300,
            )
            assert (rejected.returncode, rejected.stdout) == (2, b"")
            assert b"form must be one of ascii, tex, typographic" in rejected.stderr
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
    (work / "big.txt").write_bytes(("x" + chr(0x2014) + chr(10)).encode() * 400_000)
    for args in (["--check", "big.txt"], ["--form", "tex", *["big.txt"] * 5]):
        assert _close_early([str(script), *args], work) == (1, b"")


def _close_early(cmd: list[str], cwd: Path) -> tuple[int, bytes]:
    # The reader takes a little output, then goes away, like ``unidash big.txt | head``.
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None and process.stderr is not None
    assert process.stdout.read(64)
    process.stdout.close()
    errors = process.stderr.read()
    process.stderr.close()
    return process.wait(timeout=120), errors


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    return text.split('version = "', 1)[1].split('"', 1)[0]
