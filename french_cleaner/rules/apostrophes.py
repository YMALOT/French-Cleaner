"""
Règles de gestion des apostrophes en français.

Cas couverts :
- Remplacement de l'apostrophe droite (') par l'apostrophe typographique (')
- Suppression des espaces autour de l'apostrophe
- Détection des apostrophes manquantes dans les élisions courantes
- Normalisation des apostrophes doubles ou mal placées
"""

import re

# Apostrophe typographique (courbe, recommandée) vs droite (dactylographique)
APOS_TYPO = "\u2019"   # '  RIGHT SINGLE QUOTATION MARK
APOS_DROIT = "'"       # '  APOSTROPHE (ASCII)
APOS_GRAVE = "\u0060"  # `  GRAVE ACCENT (parfois utilisé par erreur)
APOS_AIGU = "\u00b4"   # ´  ACUTE ACCENT (idem)

# Mots qui déclenchent une élision obligatoire en français
# (liste non exhaustive mais couvrant les cas les plus fréquents)
ELISION_WORDS = [
    "le", "la", "les",
    "de", "du", "des",
    "je", "me", "te", "se", "ne",
    "que", "qu",
    "ce",
    "si",  # seulement devant il/ils
    "lorsque", "puisque", "quoique", "jusque",
]

# Prépositions / articles déclenchant élision devant voyelle ou h muet
ELISION_BEFORE_VOWEL = re.compile(
    r"\b(le|la|de|je|me|te|se|ne|que|ce|si)\s+([aeéèêëhiîïoôuùûüœ])",
    re.IGNORECASE,
)


def normalize_apostrophe_char(text: str, use_typographic: bool = True) -> str:
    """
    Normalise tous les caractères apostrophe vers la forme choisie.

    Paramètres
    ----------
    text : str
    use_typographic : bool
        Si True  → apostrophe typographique ' (U+2019)  [défaut]
        Si False → apostrophe droite ' (U+0027)
    """
    target = APOS_TYPO if use_typographic else APOS_DROIT

    # Remplace les variantes fautives
    for wrong in [APOS_GRAVE, APOS_AIGU, "\u02bc", "\u02b9", "\u0060"]:
        text = text.replace(wrong, target)

    # Normalise l'une vers l'autre selon le mode
    if use_typographic:
        text = text.replace(APOS_DROIT, APOS_TYPO)
    else:
        text = text.replace(APOS_TYPO, APOS_DROIT)

    return text


def fix_space_around_apostrophe(text: str) -> str:
    """
    Supprime les espaces accidentels autour des apostrophes.

    Exemples :
        "c' est"    → "c'est"
        "l 'homme"  → "l'homme"
        "j' ai"     → "j'ai"
    """
    # Espace après l'apostrophe (ex : "c' est")
    text = re.sub(r"(['\u2019])\s+", r"\1", text)
    # Espace avant l'apostrophe (ex : "l 'homme")
    text = re.sub(r"\s+(['\u2019])(?=\w)", r"\1", text)
    return text


def fix_missing_elision(text: str) -> str:
    """
    Détecte et corrige les élisions manquantes devant voyelle ou h muet.

    Exemples :
        "le enfant"  → "l'enfant"
        "de avoir"   → "d'avoir"
        "je arrive"  → "j'arrive"
        "ce est"     → "c'est"
        "me a dit"   → "m'a dit"

    Note : cette règle est conservative et n'agit que sur les cas
    sans ambiguïté (pas d'élision optionnelle).
    """
    # Map des formes élidées
    elision_map = {
        "le": "l",
        "la": "l",
        "de": "d",
        "je": "j",
        "me": "m",
        "te": "t",
        "se": "s",
        "ne": "n",
        "que": "qu",
        "ce": "c",
    }

    vowels = "aeéèêëhiîïoôuùûüœ"

    def replace_elision(m: re.Match) -> str:
        word = m.group(1).lower()
        next_char = m.group(2)
        if word in elision_map:
            elided = elision_map[word]
            # Préserve la casse du mot original
            if m.group(1)[0].isupper():
                elided = elided.capitalize()
            return f"{elided}'{next_char}"
        return m.group(0)

    pattern = re.compile(
        r"\b(le|la|de|je|me|te|se|ne|que|ce)\s+([" + vowels + r"])",
        re.IGNORECASE,
    )
    text = pattern.sub(replace_elision, text)
    return text


def fix_double_apostrophe(text: str) -> str:
    """
    Réduit les apostrophes doublées à une seule.
    Ex : "l''homme" → "l'homme"
    """
    text = re.sub(r"['\u2019]{2,}", APOS_TYPO, text)
    return text


def normalize_apostrophes(
    text: str,
    use_typographic: bool = True,
    fix_elisions: bool = True,
) -> str:
    """
    Pipeline complet de normalisation des apostrophes.

    Paramètres
    ----------
    text : str
    use_typographic : bool
        Utiliser l'apostrophe typographique ' (U+2019).
    fix_elisions : bool
        Corriger les élisions manquantes.
    """
    text = normalize_apostrophe_char(text, use_typographic=use_typographic)
    text = fix_double_apostrophe(text)
    text = fix_space_around_apostrophe(text)
    if fix_elisions:
        text = fix_missing_elision(text)
    return text
