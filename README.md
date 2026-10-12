# unidash

Fold Unicode punctuation to plain ASCII while leaving letters untouched

## Install

```
pip install unidash
```

## Usage

```python
from unidash import to_ascii_punct

to_ascii_punct("“Café”—it’s 100 %…")
# '"Café"-it\'s 100 %...'
```

Curly quotes become `'` and `"`, en and em dashes and the minus sign become `-`, the
ellipsis character becomes `...`, non-breaking and other Unicode spaces become a normal
space, and bullets become `*`. Accented letters such as `é` and `ñ` pass through
untouched, and so does any text that is already plain ASCII.

## Why

Tools like `unidecode` and `anyascii` transliterate every character, so `café` turns into
`cafe` and `naïve` into `naive`. That is the wrong tool when you only want to tidy
typographic punctuation and keep the words exactly as written. `smartypants` goes the
opposite way, turning ASCII into fancy quotes, and `normality` is broader and strips
punctuation entirely. `unidash` does one thing: it folds punctuation to ASCII and leaves
letters alone. It is zero dependency, typed, and ships a small vendored mapping.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
