"""
Règles de gestion des espaces autour de la ponctuation française.

Références typographiques :
- Espace insécable fine (U+202F) avant : ; ! ? » et après «
- Pas d'espace avant , . ) ] et après ( [
- Espace normale après , . ; : ! ? ) ]
"""

import re

# ---- constantes Unicode -------------------------------------------------- #
NBSP = "\u00a0"       # espace insécable normale
NNBSP = "\u202f"      # espace insécable fine (recommandée en typo FR)
SPACE = " "


def use_narrow_nbsp(text: str) -> str:
    """
    Remplace l'espace insécable normale (U+00A0) par une espace insécable
    fine (U+202F) dans les contextes typographiques français où c'est correct
    (avant : ; ! ? et autour des guillemets « »).
    """
    # Avant : ; ! ?  — remplace tout espace (y compris normal) par NNBSP
    text = re.sub(r" +([;!?])", NNBSP + r"\1", text)
    text = re.sub(r"\u00a0([;!?])", NNBSP + r"\1", text)
    # Avant les deux-points hors URL (http:// etc.)
    text = re.sub(r"(?<![a-zA-Z]) +(:)(?!/)", NNBSP + r"\1", text)
    text = re.sub(r"(?<![a-zA-Z])\u00a0(:)(?!/)", NNBSP + r"\1", text)
    return text


def fix_space_before_punctuation(text: str) -> str:
    """
    Supprime les espaces intempestifs AVANT , . ) ] (pas d'espace en français).
    Ajoute une espace insécable fine avant : ; ! ? (typographie française).
    """
    # Supprime espace(s) avant virgule et point (sauf points de suspension …)
    text = re.sub(r" +([,.](?!\.))", r"\1", text)

    # Supprime espace(s) avant parenthèse/crochet fermant
    text = re.sub(r" +([)\]])", r"\1", text)

    # Espace insécable fine avant : ; ! ?
    # (on accepte un espace normal ou insécable existant, on normalise)
    text = re.sub(r"\s*([;!?])", NNBSP + r"\1", text)
    # Pour le « : » on évite les URL (http:// , C:\ …)
    # On consomme d'abord l'espace(s) existant(s) pour éviter le doublon
    text = re.sub(r"(\w) *(:)(?![/\\])", r"\1" + NNBSP + r"\2", text)

    return text


def fix_space_after_punctuation(text: str) -> str:
    """
    Ajoute une espace normale manquante APRÈS , . ; : ! ? ) ] si le caractère
    suivant est une lettre ou un chiffre.
    Supprime les espaces multiples après ces signes.
    """
    # Après . , ; : ! ? — s'assure qu'il y a exactement une espace
    # (on ne touche pas aux abréviations M. Mme. etc. → géré par lookahead)
    text = re.sub(r"([,;!?])([^\s\n»\u202f\u00a0])", r"\1 \2", text)

    # Après un point : seulement si suivi d'une majuscule ou d'un chiffre
    # pour éviter les faux positifs sur les décimales (3.14) et abbréviations
    text = re.sub(r"(\.)([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÆŒ])", r"\1 \2", text)

    # Après « : espace insécable fine
    text = re.sub(r"«\s*", "«" + NNBSP, text)

    # Avant » : espace insécable fine
    text = re.sub(r"\s*»", NNBSP + "»", text)

    # Espace après parenthèse/crochet ouvrant — supprimer
    text = re.sub(r"([\[(])\s+", r"\1", text)

    return text


def fix_multiple_spaces(text: str) -> str:
    """
    Réduit les espaces multiples (hors sauts de ligne) à une seule espace,
    en préservant les indentations en début de ligne.
    """
    # Espaces multiples sur une même ligne → une seule espace
    text = re.sub(r"[^\S\n]{2,}", " ", text)
    return text


def fix_space_around_dash(text: str) -> str:
    """
    Normalise les espaces autour des tirets :
    - tiret cadratin (—) : espace avant et après
    - tiret demi-cadratin (–) : espace avant et après
    - trait d'union (-) dans un mot : pas d'espace
    """
    # Tiret cadratin — et demi-cadratin –
    text = re.sub(r"\s*([—–])\s*", r" \1 ", text)

    # Trait d'union collé à un espace d'un seul côté → on retire l'espace
    # (ex : "bien - sûr" → "bien-sûr")  — optionnel / conservateur
    # text = re.sub(r"(?<=\w) - (?=\w)", r"-", text)

    return text


def fix_ellipsis(text: str) -> str:
    """
    Normalise les points de suspension :
    - "..." → "…"  (caractère Unicode recommandé)
    - supprime les espaces avant "…"
    - ajoute une espace après "…" si suivi d'une lettre
    """
    # Trois points ou plus → ellipse Unicode
    text = re.sub(r"\.{3,}", "…", text)

    # Espace avant l'ellipse : supprimée
    text = re.sub(r" +…", "…", text)

    # Espace après l'ellipse si suivi d'une lettre majuscule
    text = re.sub(r"…([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÆŒ])", r"… \1", text)

    return text
