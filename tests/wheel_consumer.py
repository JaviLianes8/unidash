"""External installed-wheel API contracts with hand-written inputs."""

from __future__ import annotations

PROGRAM = r"""
from __future__ import annotations

import importlib.metadata
import importlib.resources
import pickle
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
nul_forms = [
    value
    for form in ("ascii", "tex", "typographic")
    for value in (
        f"\x00{form}", f"{form[:1]}\x00{form[1:]}", f"{form}\x00", f"{form}\x00ignored",
    )
]
import sys, unicodedata
droppable = [
    c for c in map(chr, range(sys.maxunicode + 1))
    if c.isspace() or unicodedata.category(c) in {"Cc", "Cf", "Mn", "Me", "Zs", "Zl", "Zp"}
]
assert set("\v\f\x1c\x1d\x1e\x1f\x85\xa0\u2028\u3000") <= set(droppable)
padded_forms = [
    value
    for form in ("ascii", "tex", "typographic")
    for pad in (*droppable, "\r\n")
    for value in (pad + form, form + pad, pad + form + pad, form[:1] + pad + form[1:])
]
near_forms = [
    variant
    for form in ("ascii", "tex", "typographic")
    for variant in (
        form.upper(), form.title(), form + "s", "x" + form, form[1:], form[:-1] + "x",
        form[1] + form[0] + form[2:], form.replace("s", "\u017f"), form.replace("a", "\u0430"),
    )
    if variant != form
]
for bad in (
    " ascii", "tex ", " typographic ", "\ttex\n", "as", "te", "typo", "", "latex", "0",
    *compatibility_forms, *nonascii_forms, *nul_forms, *padded_forms, *near_forms,
):
    for function, args in (
        (u.fold_dashes, (em,)), (u.iter_fold_dashes, ([em],)),
        (u.find_dashes, (em,)), (u.dash_table, ()),
    ):
        try:
            function(*args, form=bad)
        except ValueError as caught:
            assert str(caught) == "form must be one of ascii, tex, typographic"
        else:
            raise AssertionError((function.__name__, bad))
import array, collections, pathlib
for bad_bytes in (
    *(
        kind(form)
        for form in (b"ascii", b"tex", b"typographic")
        for kind in (
            bytes, bytearray, memoryview, lambda raw: memoryview(bytearray(raw)),
            lambda raw: array.array("B", raw), lambda raw: raw.decode().encode("utf-16"),
            lambda raw: collections.UserString(raw.decode()),
            lambda raw: pathlib.PurePosixPath(raw.decode()),
            lambda raw: list(raw.decode()), lambda raw: [raw.decode()],
        )
    ),
    0, 1, 2, True, None,
):
    for function, args in (
        (u.fold_dashes, (em,)), (u.iter_fold_dashes, ([em],)),
        (u.find_dashes, (em,)), (u.dash_table, ()),
    ):
        try:
            function(*args, form=bad_bytes)
        except TypeError as caught:
            assert str(caught) == "form must be a str"
        else:
            raise AssertionError((function.__name__, bad_bytes))
for bad, error in (("latex", ValueError), (["ascii"], TypeError), ("x" * 10**6, ValueError)):
    try:
        u.fold_dashes("a", bad)
    except error as caught:
        assert len(str(caught)) < 120
    else:
        raise AssertionError("bad form accepted")
assert u.DashHit.__module__ == "unidash"
assert pickle.loads(pickle.dumps(hit)) == hit
print("e2e ok")
"""


if __name__ == "__main__":
    exec(PROGRAM)
