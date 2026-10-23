"""Command line tool: fold dashes in files or stdin, or report them with ``--check``."""

from __future__ import annotations

import argparse
import errno
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO, NoReturn

from ._checks import quote
from ._hit import scan
from ._mapping import PUNCTUATION_TABLE
from ._tables import FORMS, Table, cached_table, translate_blocks

_STDIN = "-"
# Usage errors and file names may hold whatever the caller typed; past this many characters
# they are cut.
MESSAGE_LIMIT = 200


def _cut(text: str) -> str:
    if len(text) > MESSAGE_LIMIT:
        return f"{text[:MESSAGE_LIMIT]}... ({len(text)} characters)"
    return text


def _short_name(name: str) -> str:
    # A long path keeps both ends: where it starts and the file it names.
    if len(name) > MESSAGE_LIMIT:
        half = MESSAGE_LIMIT // 2
        return f"{name[:half]}...{name[-half:]} ({len(name)} characters)"
    return name


def _report(message: str) -> None:
    # With stderr closed Python sets sys.stderr to None, and print would then write to stdout,
    # into the folded data. The message is dropped instead.
    if sys.stderr is not None:
        print(message, file=sys.stderr)


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        message = _cut(message)
        if sys.stderr is None:
            self.exit(2)
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n")


def _form(value: str) -> str:
    # argparse's own choices error would echo a huge value whole; quote it like the library.
    if value not in FORMS:
        choices = ", ".join(FORMS)
        raise argparse.ArgumentTypeError(f"invalid choice: {quote(value)} (choose from {choices})")
    return value


def _parser() -> argparse.ArgumentParser:
    from . import __version__

    parser = _Parser(
        prog="unidash",
        description="Fold Unicode dashes to ASCII or tidy typographic dashes. Reads UTF-8.",
    )
    parser.add_argument("files", nargs="*", metavar="FILE", help="files to read; - is stdin")
    parser.add_argument(
        "--form",
        type=_form,
        default=None,
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
        # --form defaults to None, so an explicit --form ascii is refused like any other.
        if args.form is not None or args.script_hyphens or args.keep_soft_hyphens:
            parser.error(
                "--punct cannot be combined with --form, --script-hyphens or --keep-soft-hyphens"
            )
        return PUNCTUATION_TABLE
    form = "ascii" if args.form is None else args.form
    return cached_table(form, args.script_hyphens, args.keep_soft_hyphens)


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
        # ValueError covers text that is not UTF-8 and, on POSIX, a name the system cannot
        # encode (a lone surrogate).
        except (OSError, ValueError) as error:
            _report(f"unidash: {_short_name(label)}: {_reason(error)}")
            status = 2
            continue
        if not args.check:
            for block in translate_blocks(text, table):
                stdout.write(block.encode("utf-8"))
            continue
        prefix = _name_bytes(label)
        for hit in scan(text, table):
            line = f":{hit.line}:{hit.column}: {hit.codepoint} {hit.name}\n"
            stdout.write(prefix + line.encode("utf-8"))
            status = max(status, 1)
    stdout.flush()
    return status


def _reason(error: Exception) -> str:
    # An OSError's own text repeats the file name, which the message already holds.
    if isinstance(error, OSError) and error.strerror:
        return error.strerror
    return str(error)


def _name_bytes(label: str) -> bytes:
    # File names on POSIX may hold undecodable bytes; give them back as they were. Other lone
    # surrogates (Windows names may hold any) are written as backslash escapes.
    try:
        return label.encode("utf-8", "surrogateescape")
    except UnicodeEncodeError:
        return label.encode("utf-8", "backslashreplace")


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
        _report("unidash: no standard output")
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
