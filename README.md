# french-cleaner

Pipeline de nettoyage typographique de textes en français.

## Installation

```bash
pip install -e .
# Avec ftfy pour la correction d'encodage :
pip install -e ".[recommended]"
```

## Utilisation rapide

```python
from french_cleaner import FrenchCleaner

cleaner = FrenchCleaner()
text = cleaner.clean("Bonjour ,comment  vas-tu ?")
# → "Bonjour, comment vas-tu ?"  (avec espace insécable fine avant ?)
```

## Fonctionnalités

### Espaces & ponctuation
- Suppression des espaces avant `,` `.` `)` `]`
- Ajout de l'espace insécable fine (U+202F) avant `: ; ! ?`
- Espace insécable fine autour des guillemets `« »`
- Réduction des espaces multiples
- Normalisation des espaces autour des tirets `—` `–`
- Normalisation des points de suspension `...` → `…`

### Sauts de ligne
- Normalisation CRLF → LF
- Suppression des espaces en fin de ligne
- Réduction des sauts de ligne multiples (max configurable)
- Fusion des sauts de ligne accidentels en milieu de phrase (heuristique)
- Correction des coupures de mot OCR/PDF (`informa-\ntion` → `information`)

### Apostrophes
- Normalisation vers l'apostrophe typographique `'` (U+2019)
- Suppression des espaces autour des apostrophes (`c' est` → `c'est`)
- Correction des élisions manquantes (`le arbre` → `l'arbre`)
- Correction des apostrophes doublées (`l''homme` → `l'homme`)

### Guillemets
- Normalisation des espaces autour des guillemets français `« »`
- Conversion optionnelle des guillemets anglais `"…"` → `«\u202f…\u202f»`
- Conversion optionnelle des guillemets ASCII `"…"` → `«\u202f…\u202f»`

### Encodage & Unicode
- Correction du mojibake via `ftfy` (si installé)
- Normalisation Unicode NFC
- Suppression des caractères de contrôle et de largeur nulle
- Développement des ligatures typographiques rares (ﬁ→fi, ﬂ→fl…)
- Décodage des entités HTML (`&amp;`, `&nbsp;`…)

### Divers (optionnels)
- Suppression des URLs (remplacées par `<URL>`)
- Suppression des e-mails (remplacés par `<EMAIL>`)
- Réduction de la ponctuation répétée (`!!!` → `!`)

## Configuration

```python
from french_cleaner import FrenchCleaner, CleanerConfig

# Via kwargs
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

# Traitement en lot
results = cleaner.clean_batch(["texte 1", "texte 2"])
```

## Utilisation des règles individuellement

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

## Structure du projet

```
french_cleaner/
├── french_cleaner/
│   ├── __init__.py
│   ├── cleaner.py          # FrenchCleaner + CleanerConfig
│   └── rules/
│       ├── spaces.py       # espaces & ponctuation
│       ├── linebreaks.py   # sauts de ligne
│       ├── apostrophes.py  # apostrophes & élisions
│       ├── quotes.py       # guillemets français
│       └── misc.py         # encodage, HTML, URLs, divers
├── tests/
│   ├── test_spaces.py
│   ├── test_linebreaks.py
│   ├── test_apostrophes.py
│   ├── test_quotes.py
│   ├── test_misc.py
│   └── test_cleaner.py     # tests d'intégration
├── pyproject.toml
└── README.md
```

## Références typographiques

- [Lexique des règles typographiques — Imprimerie nationale](https://www.imprimerie-nationale.fr)
- Unicode Character Database : U+202F NARROW NO-BREAK SPACE
- Recommandations AFNOR pour la typographie française
