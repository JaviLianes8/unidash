# unidash guide

The complete contract of the public API. Everything here is kept for every 1.x release.

## The stability promise

- The public names are the nine in `unidash.__all__`: `fold_dashes`, `iter_fold_dashes`,
  `find_dashes`, `DashHit`, `is_dash`, `DASHES`, `dash_table`, `to_ascii_punct` and the
  `Form` type. Anything else, including every module whose name starts with `_`, may change
  in any release.
- Parameter names, defaults, keyword-only options, result types and error types are fixed.
  Error message wording may improve; match on the exception type, not the text.
- The classification follows Unicode 18.0. When a later Unicode version adds a dash, it is
  classified in a minor release (a new character may start folding); a character that is
  already classified never changes class or target within 1.x.
- `is_dash` and `DASHES` use the data built into the library, never the interpreter's
  `unicodedata`, so the answer is the same on every supported Python.

## `fold_dashes(text, form="ascii", *, script_hyphens=False, keep_soft_hyphens=False)`

Returns a new `str`. Every character that is not in the table for the chosen options comes
out unchanged, in order, so letters, digits, ASCII and every other punctuation mark are
never touched.

| Form | General dashes | Wavy dashes | Compatibility forms | Script hyphens (when on) |
| --- | --- | --- | --- | --- |
| `ascii` | `-` | `~` | `-` | `-` |
| `tex` | en `--`; em and bar `---`; two-em and three-em 6 and 9 hyphens; others `-` | `~` | by width | `-` |
| `typographic` | kept | kept | their NFKC character | U+2010 HYPHEN |

The README lists the target of every character. The soft hyphen (U+00AD) is removed in
every form unless `keep_soft_hyphens=True`. The ASCII hyphen-minus and the superscript and
subscript minus are never changed.

The fold works one code point at a time, so it is idempotent (folding twice gives the same
result as folding once) and folding pieces of a text gives the pieces of the folded text.
Time is linear in the length of the text, also when most characters grow (the `tex` widths).

The `tex` form follows the TeX and Markdown convention, so it is one way only where dashes
touch: an en dash followed by an ASCII hyphen gives `---`, which a converter reads as an em
dash. En and em dashes separated by any other character read back exactly through
Python-Markdown (`smarty`), the markdown-it-py typographer, docutils, and smartypants with
old-school dashes (`smartypants.Attr.D`; by default smartypants reads `--` as an em dash); the
tests check this. The other dashes fold many to one: U+2015, U+FE31 and U+FE58 read back as an
em dash and U+FE32 as an en dash. Only docutils and smartypants read the 6 and 9 hyphens of
U+2E3A and U+2E3B as two and three em dashes; Python-Markdown and markdown-it-py leave them
as hyphens.

## `iter_fold_dashes(chunks, form="ascii", *, ...)`

Takes any iterable of `str` and returns an iterator that folds one chunk at a time, with the
same options as `fold_dashes`. The options are checked when it is called; the chunks are
read lazily and each must be a `str`. `"".join(iter_fold_dashes(chunks))` equals
`fold_dashes("".join(chunks))` for every split of the text.

## `find_dashes(text, form="ascii", *, ...)` and `DashHit`

Yields, in text order, a `DashHit` for every character that `fold_dashes` with the same
options would change. Arguments are checked when it is called; the hits are produced lazily.

`DashHit` is a named tuple `(offset, line, column, char, name)`:

- `offset` counts code points from 0, so `text[hit.offset] == hit.char`.
- `line` counts from 1. A line ends at LF, CR or CRLF (one break), as editors count them;
  other separators such as U+2028, vertical tab or form feed do not end a line.
- `column` counts code points from 1 within the line. A byte order mark (U+FEFF) at the
  very start of the text takes no column; anywhere else it is an ordinary character.
- `name` is the Unicode name. For the dashes it comes from the built-in data; for other
  characters (only with the command line `--punct`) from the interpreter, or `U+XXXX`.
- `codepoint` (a property) is `U+XXXX`, with at least four hex digits.

`DashHit` pickles as `unidash.DashHit`.

## `is_dash(char)` and `DASHES`

`DASHES` is a `frozenset` of the 31 characters with the Unicode 18.0 Dash property,
`-` included. `is_dash(char)` is `char in DASHES` for a single character. The soft hyphen is
not a dash in Unicode (it is a format character) and `is_dash` says so, although the folds
remove it.

## `dash_table(form="ascii", *, ...)`

Returns a new `dict` mapping code points to their replacement, the exact table
`fold_dashes` uses with the same options; `None` means delete. It is a fresh copy on every
call, so changing it affects nothing else. Use it to merge the dash fold into your own
`str.translate` table.

## `to_ascii_punct(text)`

Folds the typographic punctuation of a text to ASCII in one pass:

- dashes as in `fold_dashes(text)` (default options), including the soft hyphen removal;
- single quotes and primes U+2018, U+2019, U+201A, U+201B, U+2032, U+2035 to `'`;
- double quotes and double primes U+201C, U+201D, U+201E, U+201F, U+2033, U+2036 to `"`;
- bullets U+2022, U+2023, U+2043, U+2219, U+25E6 to `*`;
- the ellipsis U+2026 to `...`;
- spaces U+00A0, U+1680, U+2000 to U+200A, U+202F, U+205F, U+3000 to a plain space;
- fullwidth punctuation U+FF01 to U+FF5E to its ASCII character, except fullwidth letters
  and digits, which are letters and digits.

Every other character comes out as `fold_dashes(text)` leaves it, so letters, marks and
digits of every script are never changed; the tests check every code point against this
list.

## Errors

| Situation | Error |
| --- | --- |
| `text`, `char` or a chunk is not a `str` | `TypeError` |
| `form` is not a `str` | `TypeError` |
| `form` is a `str` other than `ascii`, `tex`, `typographic` | `ValueError` |
| `script_hyphens` or `keep_soft_hyphens` is not a `bool` | `TypeError` |
| `is_dash` gets a `str` that is not exactly one character | `ValueError` |

Messages name the parameter and the type or value received, and quote at most 40
characters of a value. A `str` subclass is accepted and read as its plain characters; its
own methods are not called.

## What is not a dash

The double hyphens (U+2E40, and U+1400 and U+30A0 among the script hyphens) become `-`,
although UTS #39 lists them as confusable with `=`: they are hyphens in use, and `=` would
change the meaning of the text.

Characters that only look like a hyphen are left alone: letters and marks in other scripts
(such as the spacing marks U+1BF3 BATAK PANONGONAN and U+AA7D MYANMAR SIGN TAI LAING
TONE-5), U+06D4 ARABIC FULL STOP (it ends a sentence), U+2043 HYPHEN BULLET
(`to_ascii_punct` makes it a `*`), U+02D7 MODIFIER LETTER MINUS SIGN (a tone mark), U+10191
ROMAN UNCIA SIGN (a weight unit), and minus-like symbols without the Dash property: U+2052
COMMERCIAL MINUS SIGN, U+2796 HEAVY MINUS SIGN (an emoji), U+2E43 DASH WITH LEFT UPTURN and
U+10D8F GARAY MINUS SIGN. The tests check that every UTS #39 confusable of `-` either folds
or is in this list or is a letter or a mark.

## Command line

```
unidash [--form {ascii,tex,typographic}] [--script-hyphens] [--keep-soft-hyphens]
        [--punct] [--check] [--version] [FILE ...]
```

- Reads each FILE (or stdin for `-` or no FILE) as UTF-8 and writes the folded bytes to
  stdout, byte for byte apart from the fold: line ends and a byte order mark are kept.
- `--punct` uses `to_ascii_punct` and cannot be combined with the dash options.
- `--check` writes nothing but `FILE:LINE:COLUMN: U+XXXX NAME` for each change, with the
  positions of `find_dashes`.
- Stdin is read only for `-`. With no standard input, `-` is reported as an unreadable
  file; with no standard output the tool stops at once with exit 2.
- An invalid `--form` value is quoted to at most 40 characters in the usage error.
- Long input takes linear time.
- Exit codes: 0 when nothing failed (and, with `--check`, nothing would change); 1 when
  `--check` found something or the reader closed stdout early (`unidash big.txt | head`),
  quietly, on every platform; 2 for a file that cannot be read or is not UTF-8 (the other
  files are still processed), for a missing standard input or output, and for usage
  errors, such as reading stdin twice.
- `python -m unidash` runs the same tool.

## Threads

The functions keep no state besides their read-only tables, so they can be called from any
number of threads, including on the free-threaded build of Python.
