"""Every dash-like code point the library knows, sorted into classes with a reason each.

The classes follow the Unicode 18.0 Dash property (PropList.txt) and General_Category=Pd
(UnicodeData.txt); the tests check them against both files. Names are the Unicode character
names, kept here so messages read the same on interpreters with older Unicode tables.
"""

from __future__ import annotations

# Dashes and hyphens used in running text of any script: folded by default. The value is
# the single ASCII character each one becomes in the ``ascii`` form.
GENERAL: dict[int, tuple[str, str]] = {
    0x2010: ("-", "HYPHEN"),
    0x2011: ("-", "NON-BREAKING HYPHEN"),
    0x2012: ("-", "FIGURE DASH"),
    0x2013: ("-", "EN DASH"),
    0x2014: ("-", "EM DASH"),
    0x2015: ("-", "HORIZONTAL BAR"),
    0x2212: ("-", "MINUS SIGN"),
    0x2E17: ("-", "DOUBLE OBLIQUE HYPHEN"),
    0x2E1A: ("-", "HYPHEN WITH DIAERESIS"),
    0x2E3A: ("-", "TWO-EM DASH"),
    0x2E3B: ("-", "THREE-EM DASH"),
    0x2E40: ("-", "DOUBLE HYPHEN"),
    0x2E5D: ("-", "OBLIQUE HYPHEN"),
    0xFE31: ("-", "PRESENTATION FORM FOR VERTICAL EM DASH"),
    0xFE32: ("-", "PRESENTATION FORM FOR VERTICAL EN DASH"),
    0xFE58: ("-", "SMALL EM DASH"),
    0xFE63: ("-", "SMALL HYPHEN-MINUS"),
    0xFF0D: ("-", "FULLWIDTH HYPHEN-MINUS"),
    # Wavy dashes read as a tilde in ASCII; UTS #39 lists them as confusable with it too.
    0x2053: ("~", "SWUNG DASH"),
    0x301C: ("~", "WAVE DASH"),
    0x3030: ("~", "WAVY DASH"),
}

# Hyphens that belong to one script, the way its letters do. Folding them is a choice about
# that script's text, so it happens only on request.
SCRIPT_HYPHENS: dict[int, str] = {
    0x058A: "ARMENIAN HYPHEN",
    0x05BE: "HEBREW PUNCTUATION MAQAF",
    0x1400: "CANADIAN SYLLABICS HYPHEN",
    0x1806: "MONGOLIAN TODO SOFT HYPHEN",
    0x30A0: "KATAKANA-HIRAGANA DOUBLE HYPHEN",
    0x10D6E: "GARAY HYPHEN",
    0x10EAD: "YEZIDI HYPHENATION MARK",
}

# Dash property members that are never folded: the ASCII hyphen-minus itself, and the
# superscript and subscript minus, which sit beside superscript digits that stay as they are.
KEPT: dict[int, str] = {
    0x002D: "HYPHEN-MINUS",
    0x207B: "SUPERSCRIPT MINUS",
    0x208B: "SUBSCRIPT MINUS",
}

SOFT_HYPHEN = 0x00AD

# The TeX and Markdown convention: an en dash is two hyphens, an em dash three.
TEX_WIDTHS: dict[int, int] = {
    0x2013: 2,
    0xFE32: 2,
    0x2014: 3,
    0x2015: 3,
    0xFE31: 3,
    0xFE58: 3,
    0x2E3A: 6,
    0x2E3B: 9,
}

# Compatibility forms and their canonical counterparts (their NFKC mapping).
COMPATIBILITY: dict[int, str] = {
    0xFE31: chr(0x2014),
    0xFE32: chr(0x2013),
    0xFE58: chr(0x2014),
    0xFE63: "-",
    0xFF0D: "-",
}

TYPOGRAPHIC_HYPHEN = chr(0x2010)

NAMES: dict[int, str] = {
    **{cp: name for cp, (_, name) in GENERAL.items()},
    **SCRIPT_HYPHENS,
    **KEPT,
    SOFT_HYPHEN: "SOFT HYPHEN",
}

DASH_CODEPOINTS = frozenset(GENERAL) | frozenset(SCRIPT_HYPHENS) | frozenset(KEPT)
