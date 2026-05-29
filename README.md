# french-cleaner

> Python pipeline for cleaning and normalizing French text — punctuation spacing, apostrophes, elisions, line breaks, OCR artifacts, mojibake, and more. Zero required dependencies. 194 tests.

*[Lire en français](README.fr.md)*

## Installation

```bash
pip install -e .
# With ftfy for encoding correction:
pip install -e ".[recommended]"
```

## Quick start

```python
from french_cleaner import FrenchCleaner

cleaner = FrenchCleaner()
text = cleaner.clean("Bonjour ,comment  vas-tu ?")
# → "Bonjour, comment vas-tu ?"  (narrow no-break space before ?)
```

## Example

Raw text from a copy-paste (stray spaces, OCR line break, misspaced quotation marks, straight apostrophes, multiple blank lines, URL, email, repeated punctuation):

```text
Hier soir ,j' ai relu le «  Horla  » de Maupassant...
C' est l' une de mes nouvelles preferes—avec «La Parure» bien sur !
le style de Maupassant est remar-
quable : sobre ,precis ,jamais superflu.



Contacter notre equipe : info@example.fr ou https://example.com
Prix de l' edition collector : 24.90 EUR !!!
Disponible en librairie  ;  commandez  des  maintenant !
```

```python
from french_cleaner import FrenchCleaner

cleaner = FrenchCleaner(
    remove_urls=True,
    remove_emails=True,
    fix_repeated_punctuation=True,
)

result = cleaner.clean(raw)
```

Output:

```text
Hier soir, j'ai relu le « Horla » de Maupassant…
C'est l'une de mes nouvelles preferes — avec « La Parure » bien sur !
le style de Maupassant est remarquable : sobre, precis, jamais superflu.

Contacter notre equipe : <EMAIL> ou <URL>
Prix de l'edition collector : 24.90 EUR !
Disponible en librairie ; commandez des maintenant !
```

What changed, line by line:

| Before | After | Rule |
|---|---|---|
| `Hier soir ,j' ai` | `Hier soir, j'ai` | space before `,` removed · space inside apostrophe removed |
| `«  Horla  »` | `« Horla »` | multiple spaces → narrow no-break space (U+202F) |
| `Maupassant...` | `Maupassant…` | `...` → `…` (U+2026) |
| `C' est l' une` | `C'est l'une` | spaces around apostrophes removed |
| `nouvelles—avec` | `nouvelles — avec` | spaces added around em dash |
| `remar-\nquable` | `remarquable` | OCR/PDF word-break hyphen fused |
| `sobre ,precis` | `sobre, precis` | space before `,` removed · space after `,` added |
| *(3 blank lines)* | *(1 blank line)* | consecutive blank lines reduced |
| `info@example.fr` | `<EMAIL>` | email replaced by placeholder |
| `https://example.com` | `<URL>` | URL replaced by placeholder |
| `l' edition` | `l'edition` | space after apostrophe removed |
| `24.90 EUR !!!` | `24.90 EUR !` | repeated punctuation reduced |
| `librairie  ;  commandez  des  maintenant` | `librairie ; commandez des maintenant` | multiple spaces reduced |

> **Typographic note:** spaces before `: ; ! ?` and around `« »` are narrow no-break spaces (U+202F), as recommended by French typographic standards. They render as regular spaces in most editors.

## Features

### Spaces & punctuation
- Removes stray spaces before `,` `.` `)` `]`
- Inserts narrow no-break space (U+202F) before `: ; ! ?`
- Narrow no-break space around French quotation marks `« »`
- Collapses multiple spaces
- Normalizes spaces around em dash `—` and en dash `–`
- Normalizes ellipsis `...` → `…`

### Line breaks
- Normalizes CRLF → LF
- Strips trailing spaces on each line
- Reduces consecutive blank lines (max count configurable)
- Merges accidental mid-sentence line breaks (heuristic)
- Fuses OCR/PDF word-break hyphens (`informa-\ntion` → `information`)

### Apostrophes
- Normalizes to typographic apostrophe `'` (U+2019)
- Removes spaces around apostrophes (`c' est` → `c'est`)
- Fixes missing elisions (`le arbre` → `l'arbre`)
- Collapses double apostrophes (`l''homme` → `l'homme`)

### Quotation marks
- Normalizes spacing around French guillemets `« »`
- Optional: converts typographic English quotes `"…"` → `«\u202f…\u202f»`
- Optional: converts straight ASCII quotes `"…"` → `«\u202f…\u202f»`

### Encoding & Unicode
- Fixes mojibake via `ftfy` (if installed)
- NFC Unicode normalization
- Removes control characters and zero-width characters
- Expands rare typographic ligatures (ﬁ→fi, ﬂ→fl…), preserving `œ` and `æ`
- Decodes HTML entities (`&amp;`, `&nbsp;`…)

### Optional extras
- Removes URLs (replaced by `<URL>`)
- Removes email addresses (replaced by `<EMAIL>`)
- Reduces repeated punctuation (`!!!` → `!`)

## Configuration

```python
from french_cleaner import FrenchCleaner, CleanerConfig

# Via keyword arguments
cleaner = FrenchCleaner(
    remove_urls=True,
    remove_emails=True,
    convert_ascii_quotes=True,
    fix_repeated_punctuation=True,
    max_newlines=1,
    use_typographic_apostrophe=True,   # ' (U+2019)
    fix_elisions=True,
)

# Via CleanerConfig
config = CleanerConfig(remove_urls=True, max_newlines=1)
cleaner = FrenchCleaner(config=config)

# Batch processing
results = cleaner.clean_batch(["texte 1", "texte 2"])
```

## Using individual rules

Each rule is also available as a standalone function:

```python
from french_cleaner.rules.spaces import fix_space_before_punctuation
from french_cleaner.rules.apostrophes import fix_missing_elision
from french_cleaner.rules.linebreaks import fix_accidental_newlines

text = fix_space_before_punctuation("Bonjour ,monde !")
text = fix_missing_elision("le arbre de le ile")
text = fix_accidental_newlines("Le chien\nmangea\nsa croquette.")
```

## Tests

```bash
pip install -e ".[dev]"
pytest
pytest --cov=french_cleaner --cov-report=term-missing
```

## Project structure

```
french_cleaner/
├── french_cleaner/
│   ├── __init__.py
│   ├── cleaner.py          # FrenchCleaner + CleanerConfig
│   └── rules/
│       ├── spaces.py       # spaces & punctuation
│       ├── linebreaks.py   # line breaks
│       ├── apostrophes.py  # apostrophes & elisions
│       ├── quotes.py       # French quotation marks
│       └── misc.py         # encoding, HTML, URLs, misc
├── tests/
│   ├── test_spaces.py
│   ├── test_linebreaks.py
│   ├── test_apostrophes.py
│   ├── test_quotes.py
│   ├── test_misc.py
│   └── test_cleaner.py     # integration tests
├── pyproject.toml
├── README.md
└── README.fr.md
```

## Typographic references

- [Lexique des règles typographiques — Imprimerie nationale](https://www.imprimerie-nationale.fr)
- Unicode Character Database: U+202F NARROW NO-BREAK SPACE
- AFNOR recommendations for French typography
