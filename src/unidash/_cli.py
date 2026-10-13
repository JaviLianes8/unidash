"""Command line tool: fold dashes in files or stdin, or report them with ``--check``."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO

from ._dashes import scan
from ._mapping import PUNCTUATION_TABLE
from ._tables import FORMS, Table, cached_table

_STDIN = "-"


def _parser() -> argparse.ArgumentParser:
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="unidash",
        description="Fold Unicode dashes to ASCII or tidy typographic dashes. Reads UTF-8.",
    )
    parser.add_argument("files", nargs="*", metavar="FILE", help="files to read; - is stdin")
    parser.add_argument("--form", choices=FORMS, default="ascii", help="target (default ascii)")
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


def _read(name: str, stdin: BinaryIO) -> str:
    data = stdin.read() if name == _STDIN else Path(name).read_bytes()
    return data.decode("utf-8")


def _run(args: argparse.Namespace, table: Table, names: list[str], stdout: BinaryIO) -> int:
    status = 0
    for name in names:
        label = "<stdin>" if name == _STDIN else name
        try:
            text = _read(name, sys.stdin.buffer)
        except (OSError, UnicodeDecodeError) as error:
            print(f"unidash: {label}: {error}", file=sys.stderr)
            status = 2
            continue
        if not args.check:
            stdout.write(text.translate(table).encode("utf-8"))
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
    try:
        return _run(args, table, names, sys.stdout.buffer)
    except BrokenPipeError:
        # The reader went away (``unidash big.txt | head``): stop quietly, like other filters.
        devnull = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(devnull, sys.stdout.fileno())
        except (OSError, ValueError):
            pass
        finally:
            os.close(devnull)
        return 1
