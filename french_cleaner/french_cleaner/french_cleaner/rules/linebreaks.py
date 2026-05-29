"""
Règles de gestion des sauts de ligne dans le texte français.

Cas couverts :
- Sauts de ligne intempestifs au milieu d'une phrase (coupures de paragraphe OCR/PDF/copier-coller)
- Sauts de ligne multiples → maximum 2 (séparation de paragraphe)
- Normalisation des fins de ligne Windows (CRLF → LF)
- Suppression des espaces en fin de ligne
"""

import re


def fix_crlf(text: str) -> str:
    """Normalise les fins de ligne Windows (\\r\\n) et les \\r seuls en \\n."""
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    return text


def fix_trailing_spaces(text: str) -> str:
    """Supprime les espaces et tabulations en fin de chaque ligne."""
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    return text


def fix_multiple_newlines(text: str, max_newlines: int = 2) -> str:
    """
    Réduit les séquences de sauts de ligne excessifs.
    Par défaut, on tolère au maximum 2 sauts de ligne consécutifs
    (= une ligne vide entre deux paragraphes).
    """
    pattern = r"\n{" + str(max_newlines + 1) + r",}"
    replacement = "\n" * max_newlines
    text = re.sub(pattern, replacement, text)
    return text


def fix_soft_hyphens(text: str) -> str:
    """
    Supprime les coupures de mot avec trait d'union en fin de ligne
    introduites par les PDF ou traitements de texte.

    Exemple :
        "informa-\\ntion"  →  "information"
        "avant-\\ngarde"   →  "avant-garde"  (tiret de composition préservé)
    """
    # Trait d'union en fin de ligne suivi d'un mot en minuscule → fusion
    text = re.sub(
        r"(\w)-\n(\w)",
        lambda m: (
            m.group(1) + m.group(2)          # fusionne si minuscule suivante
            if m.group(2).islower()
            else m.group(1) + "-\n" + m.group(2)
        ),
        text,
    )
    return text


def fix_accidental_newlines(text: str) -> str:
    """
    Supprime les sauts de ligne accidentels AU MILIEU d'une phrase.

    Heuristique : un saut de ligne est "accidentel" si :
    - la ligne précédente ne se termine pas par un signe de fin de phrase
      (. ! ? : … ou guillemet fermant »)
    - ET la ligne suivante commence par une lettre minuscule ou un chiffre
      (pas un début de nouveau paragraphe)

    Cette règle est conservative : elle ne fusionne pas si la ligne suivante
    commence par une majuscule (possible début de phrase ou titre).
    """
    text = re.sub(
        r"(?<![.!?:…»\n])\n(?=[a-zàâäéèêëîïôöùûüÿæœ0-9])",
        " ",
        text,
    )
    return text


def fix_newline_after_hyphen(text: str) -> str:
    """
    Gère le cas particulier où une coupure de ligne intervient après un tiret
    de liste ou de dialogue (— ou -) en début de ligne suivante.
    Ces sauts de ligne sont intentionnels, on les préserve.
    """
    # Ne rien faire — cette fonction est un point d'extension documenté.
    return text


def normalize_linebreaks(
    text: str,
    max_newlines: int = 2,
    fix_soft: bool = True,
    fix_accidental: bool = True,
) -> str:
    """
    Pipeline complet de normalisation des sauts de ligne.

    Paramètres
    ----------
    text : str
        Texte à nettoyer.
    max_newlines : int
        Nombre maximum de sauts de ligne consécutifs autorisés (défaut : 2).
    fix_soft : bool
        Si True, supprime les coupures de mot OCR/PDF (ex : "informa-\\ntion").
    fix_accidental : bool
        Si True, fusionne les sauts de ligne accidentels en milieu de phrase.
    """
    text = fix_crlf(text)
    text = fix_trailing_spaces(text)
    if fix_soft:
        text = fix_soft_hyphens(text)
    if fix_accidental:
        text = fix_accidental_newlines(text)
    text = fix_multiple_newlines(text, max_newlines=max_newlines)
    return text
