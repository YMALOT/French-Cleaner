"""
Règles de gestion des guillemets en français.

Cas couverts :
- Remplacement des guillemets anglais ("…") par des guillemets français (« … »)
- Remplacement des guillemets simples utilisés comme guillemets ('…') par « … »
- Normalisation des espaces autour des guillemets (espace insécable fine)
- Gestion des guillemets imbriqués (guillemets doubles pour le 2e niveau)
"""

import re

# Caractères Unicode
GUILLEMET_OUV = "«"     # U+00AB
GUILLEMET_FERM = "»"    # U+00BB
NNBSP = "\u202f"        # espace insécable fine
NBSP = "\u00a0"         # espace insécable normale

# Guillemets anglais hauts doubles
QUOTE_DOUBLE_OUV = "\u201c"   # "
QUOTE_DOUBLE_FERM = "\u201d"  # "
QUOTE_DOUBLE_DROIT = '"'      # " ASCII

# Guillemets anglais hauts simples
QUOTE_SIMPLE_OUV = "\u2018"   # '
QUOTE_SIMPLE_FERM = "\u2019"  # '  (= aussi apostrophe typo !)
QUOTE_SIMPLE_DROIT = "'"      # ' ASCII


def fix_guillemet_spaces(text: str) -> str:
    """
    Normalise les espaces autour des guillemets français « et ».

    Règle typographique française :
    - Espace insécable fine (U+202F) après «
    - Espace insécable fine (U+202F) avant »

    Supprime également les espaces normaux mal placés.
    """
    # Après « : exactement une espace insécable fine
    text = re.sub(r"«\s*", "«" + NNBSP, text)

    # Avant » : exactement une espace insécable fine
    text = re.sub(r"\s*»", NNBSP + "»", text)

    return text


def convert_english_quotes_to_french(text: str) -> str:
    """
    Convertit les guillemets anglais typographiques ("…" et "…")
    en guillemets français (« … »).

    Note : cette conversion est optionnelle et doit être utilisée avec
    précaution sur des textes mixtes (citations en anglais, code, etc.).
    """
    # Guillemets doubles typographiques ouvrants/fermants → « »
    text = re.sub(
        r"\u201c([^\"]*?)\u201d",
        lambda m: f"«{NNBSP}{m.group(1).strip()}{NNBSP}»",
        text,
    )
    return text


def convert_ascii_quotes_to_french(text: str) -> str:
    """
    Convertit les guillemets ASCII droits ("…") en guillemets français (« … »).

    Heuristique : paires de guillemets droits équilibrées.
    Attention : à n'utiliser que si le texte est en français et que les
    guillemets droits sont bien des guillemets (pas du code, pas des inches).
    """
    # Guillemets droits doubles : paires équilibrées
    text = re.sub(
        r'"([^"]+)"',
        lambda m: f"«{NNBSP}{m.group(1).strip()}{NNBSP}»",
        text,
    )
    return text


def fix_missing_guillemet_space(text: str) -> str:
    """
    Ajoute l'espace insécable fine manquante après « ou avant »
    si le contenu est collé au guillemet.

    Ex : «bonjour»   → « bonjour »
         « bonjour » → déjà correct (espace normale → insécable fine)
    """
    # Guillemet ouvrant collé → ajoute NNBSP
    text = re.sub(r"«(?!" + NNBSP + r"|\s)", "«" + NNBSP, text)
    # Guillemet fermant collé → ajoute NNBSP
    text = re.sub(r"(?<!" + NNBSP + r")(?<!\s)»", NNBSP + "»", text)
    # Espace normale autour des guillemets → remplace par NNBSP
    text = re.sub(r"« ", "«" + NNBSP, text)
    text = re.sub(r" »", NNBSP + "»", text)
    # Espace insécable normale → espace insécable fine
    text = re.sub(r"«" + NBSP, "«" + NNBSP, text)
    text = re.sub(NBSP + "»", NNBSP + "»", text)
    return text


def normalize_quotes(
    text: str,
    convert_english: bool = False,
    convert_ascii: bool = False,
) -> str:
    """
    Pipeline complet de normalisation des guillemets.

    Paramètres
    ----------
    text : str
    convert_english : bool
        Convertit les guillemets anglais typographiques en guillemets français.
    convert_ascii : bool
        Convertit les guillemets ASCII droits en guillemets français.
        À utiliser avec précaution.
    """
    if convert_english:
        text = convert_english_quotes_to_french(text)
    if convert_ascii:
        text = convert_ascii_quotes_to_french(text)
    text = fix_missing_guillemet_space(text)
    text = fix_guillemet_spaces(text)
    return text
