"""Where a dash sits in a text: the ``DashHit`` record and the line and column scan."""

# No __future__ import here: on a NamedTuple it would leave the public fields annotated with
# ForwardRef strings instead of int and str.
import unicodedata
from collections.abc import Iterator
from typing import NamedTuple

from ._classes import NAMES
from ._tables import Table

BOM, CR, LF = chr(0xFEFF), chr(13), chr(10)


class DashHit(NamedTuple):
    r"""One character that a fold would change, with its place in the text.

    ``offset`` counts code points from 0; ``line`` and ``column`` count from 1, lines end
    at LF, CR or CRLF, and a byte order mark at the very start takes no column. ``name`` is
    the Unicode character name.

    >>> from unidash import find_dashes
    >>> hit = next(find_dashes("one\ntwo\u2013three"))
    >>> print(ascii(hit))
    DashHit(offset=7, line=2, column=4, char='\u2013', name='EN DASH')
    >>> hit.codepoint
    'U+2013'
    """

    offset: int
    line: int
    column: int
    char: str
    name: str

    @property
    def codepoint(self) -> str:
        r"""The code point in ``U+XXXX`` notation.

        >>> from unidash import DashHit
        >>> DashHit(0, 1, 1, "\U00010ead", "YEZIDI HYPHENATION MARK").codepoint
        'U+10EAD'
        """
        return f"U+{ord(self.char):04X}"


def char_name(char: str) -> str:
    known = NAMES.get(ord(char))
    if known is not None:
        return known
    fallback = f"U+{ord(char):04X}"
    return unicodedata.name(char, fallback)


def scan(text: str, table: Table) -> Iterator[DashHit]:
    # Lines end at LF, CR or CRLF, as editors count them; a leading BOM takes no column.
    line, line_start = 1, 1 if text.startswith(BOM) else 0
    previous = ""
    for offset, char in enumerate(text):
        if char == LF and previous == CR:
            line_start = offset + 1
        elif char in (CR, LF):
            line, line_start = line + 1, offset + 1
        elif ord(char) in table:
            yield DashHit(offset, line, offset - line_start + 1, char, char_name(char))
        previous = char
