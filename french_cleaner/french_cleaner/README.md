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


## Exemple complet

Texte brut issu d'un copier-coller (espaces fautifs, coupure OCR, guillemets mal espacés, apostrophes droites, sauts de ligne multiples, URL, email, ponctuation répétée) :

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

Résultat :

```text
Hier soir, j'ai relu le « Horla » de Maupassant…
C'est l'une de mes nouvelles preferes — avec « La Parure » bien sur !
le style de Maupassant est remarquable : sobre, precis, jamais superflu.

Contacter notre equipe : <EMAIL> ou <URL>
Prix de l'edition collector : 24.90 EUR !
Disponible en librairie ; commandez des maintenant !
```

Ce qui a changé, ligne par ligne :

| Avant | Après | Règle |
|---|---|---|
| `Hier soir ,j' ai` | `Hier soir, j'ai` | espace avant `,` supprimé · espace dans l'apostrophe supprimé |
| `«  Horla  »` | `« Horla »` | espaces multiples → espace insécable fine (U+202F) |
| `Maupassant...` | `Maupassant…` | `...` → `…` (U+2026) |
| `C' est l' une` | `C'est l'une` | espaces autour des apostrophes supprimés |
| `nouvelles—avec` | `nouvelles — avec` | espace autour du tiret cadratin |
| `remar-\nquable` | `remarquable` | coupure de mot OCR/PDF fusionnée |
| `sobre ,precis` | `sobre, precis` | espace avant `,` supprimé · espace après `,` ajouté |
| *(3 lignes vides)* | *(1 ligne vide)* | sauts de ligne multiples réduits |
| `info@example.fr` | `<EMAIL>` | email remplacé par placeholder |
| `https://example.com` | `<URL>` | URL remplacée par placeholder |
| `l' edition` | `l'edition` | espace après apostrophe supprimé |
| `24.90 EUR !!!` | `24.90 EUR !` | ponctuation répétée réduite |
| `librairie  ;  commandez  des  maintenant` | `librairie ; commandez des maintenant` | espaces multiples réduits |

> **Note typographique :** les espaces avant `: ; ! ?` et autour de `« »` sont des espaces insécables fines (U+202F), conformes aux recommandations typographiques françaises. Elles apparaissent comme des espaces normales dans la plupart des éditeurs.


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
