"""Command line tool: fold dashes in files or stdin, or report them with ``--check``."""

from __future__ import annotations

import argparse
import errno
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO

from ._checks import quote
from ._hit import scan
from ._mapping import PUNCTUATION_TABLE
from ._tables import FORMS, Table, cached_table, translate_blocks

_STDIN = "-"


def _form(value: str) -> str:
    # argparse's own choices error would echo a huge value whole; quote it like the library.
    if value not in FORMS:
        choices = ", ".join(FORMS)
        raise argparse.ArgumentTypeError(f"invalid choice: {quote(value)} (choose from {choices})")
    return value


def _parser() -> argparse.ArgumentParser:
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="unidash",
        description="Fold Unicode dashes to ASCII or tidy typographic dashes. Reads UTF-8.",
    )
    parser.add_argument("files", nargs="*", metavar="FILE", help="files to read; - is stdin")
    parser.add_argument(
        "--form",
        type=_form,
        default="ascii",
        metavar="{" + ",".join(FORMS) + "}",
        help="target (default ascii)",
    )
    parser.add_argument("--script-hyphens", action="store_true", help="fold script hyphens too")
    parser.add_argument("--keep-soft-hyphens", action="store_true", help="do not drop U+00AD")
    parser.add_argument(
        "--punct", action="store_true", help="fold all punctuation (to_ascii_punct)"
    )
    parser.add_argument(
        "--check", action="store_true", help="list what would change, exit 1 if anything"
    )
    parser.add_argument("--version", action="version", version=f"unidash {__version__}")
    return parser


def _table(args: argparse.Namespace, parser: argparse.ArgumentParser) -> Table:
    if args.punct:
        if args.form != "ascii" or args.script_hyphens or args.keep_soft_hyphens:
            parser.error("--punct cannot be combined with the dash options")
        return PUNCTUATION_TABLE
    return cached_table(args.form, args.script_hyphens, args.keep_soft_hyphens)


def _read(name: str) -> str:
    if name != _STDIN:
        return Path(name).read_bytes().decode("utf-8")
    # Started with stdin closed (or under pythonw), Python sets sys.stdin to None.
    stdin = getattr(sys.stdin, "buffer", None)
    if stdin is None:
        raise OSError("no standard input")
    data: bytes = stdin.read()
    return data.decode("utf-8")


def _run(args: argparse.Namespace, table: Table, names: list[str], stdout: BinaryIO) -> int:
    status = 0
    for name in names:
        label = "<stdin>" if name == _STDIN else name
        try:
            text = _read(name)
        except (OSError, UnicodeDecodeError) as error:
            print(f"unidash: {label}: {error}", file=sys.stderr)
            status = 2
            continue
        if not args.check:
            for block in translate_blocks(text, table):
                stdout.write(block.encode("utf-8"))
            continue
        for hit in scan(text, table):
            line = f"{label}:{hit.line}:{hit.column}: {hit.codepoint} {hit.name}\n"
            # File names on POSIX may hold undecodable bytes; give them back as they were.
            stdout.write(line.encode("utf-8", "surrogateescape"))
            status = max(status, 1)
    stdout.flush()
    return status


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool and return its exit code: 0 clean, 1 changes found by --check, 2 error."""
    parser = _parser()
    args = parser.parse_args(argv)
    table = _table(args, parser)
    names = args.files or [_STDIN]
    if names.count(_STDIN) > 1:
        parser.error("stdin (-) can be read only once")
    stdout = getattr(sys.stdout, "buffer", None)
    if stdout is None:
        print("unidash: no standard output", file=sys.stderr)
        return 2
    try:
        return _run(args, table, names, stdout)
    except OSError as error:
        if not _reader_left(error):
            raise
        # The reader went away (``unidash big.txt | head``): stop quietly, like other filters.
        _silence_stdout()
        return 1


def _reader_left(error: OSError) -> bool:
    # Windows reports a write to a pipe whose reader has gone as EINVAL, not EPIPE.
    if isinstance(error, BrokenPipeError) or error.errno == errno.EPIPE:
        return True
    return sys.platform == "win32" and error.errno == errno.EINVAL


def _silence_stdout() -> None:
    # Whatever is still buffered goes to devnull at exit instead of failing again.
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, sys.stdout.fileno())
    except (OSError, ValueError):
        pass
    finally:
        os.close(devnull)
