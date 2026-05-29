"""
Règles diverses de nettoyage de texte français.

Cas couverts :
- Correction de l'encodage cassé (mojibake) via ftfy
- Suppression/remplacement des entités HTML (&amp; &nbsp; etc.)
- Normalisation Unicode (NFC)
- Suppression des caractères de contrôle invisibles
- Suppression / remplacement des URLs et emails
- Normalisation des nombres (séparateur décimal, milliers)
- Suppression des marqueurs de mise en forme résiduels
"""

import html
import re
import unicodedata

try:
    import ftfy  # type: ignore
    HAS_FTFY = True
except ImportError:
    HAS_FTFY = False


# ---- Encodage / Unicode -------------------------------------------------- #

def fix_encoding(text: str) -> str:
    """
    Corrige le mojibake (encodage cassé) si ftfy est disponible.
    Ex : "lÃ©gume" → "légume"
    Si ftfy n'est pas installé, applique une normalisation Unicode basique.
    """
    if HAS_FTFY:
        return ftfy.fix_text(text)
    return unicodedata.normalize("NFC", text)


def normalize_unicode(text: str) -> str:
    """
    Applique la forme normale NFC (composition canonique).
    Utile pour uniformiser les caractères accentués.
    """
    return unicodedata.normalize("NFC", text)


def remove_control_chars(text: str) -> str:
    """
    Supprime les caractères de contrôle Unicode invisibles
    (sauf tabulation \\t, saut de ligne \\n, retour chariot \\r).
    """
    return re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b\u200c\u200d\ufeff]",
        "",
        text,
    )


def remove_zero_width(text: str) -> str:
    """
    Supprime les espaces et jointures de largeur nulle (zero-width).
    U+200B ZERO WIDTH SPACE
    U+200C ZERO WIDTH NON-JOINER
    U+200D ZERO WIDTH JOINER
    U+FEFF BOM / ZERO WIDTH NO-BREAK SPACE
    """
    return re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)


# ---- HTML ----------------------------------------------------------------- #

def decode_html_entities(text: str) -> str:
    """
    Décode les entités HTML : &amp; → &, &nbsp; → espace, &lt; → <, etc.
    """
    return html.unescape(text)


def remove_html_tags(text: str) -> str:
    """
    Supprime les balises HTML résiduelles.
    Ex : "<b>Bonjour</b>" → "Bonjour"
    """
    return re.sub(r"<[^>]+>", "", text)


def replace_html_nbsp(text: str) -> str:
    """
    Remplace les entités &nbsp; (et leur équivalent Unicode U+00A0)
    par une espace normale dans les contextes non-typographiques.
    """
    text = text.replace("&nbsp;", " ")
    text = text.replace("\u00a0", " ")
    return text


# ---- URLs & emails -------------------------------------------------------- #

_URL_PATTERN = re.compile(
    r"https?://\S+|www\.\S+",
    re.IGNORECASE,
)

_EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)


def remove_urls(text: str, placeholder: str = "<URL>") -> str:
    """Supprime les URLs et les remplace par un placeholder."""
    return _URL_PATTERN.sub(placeholder, text)


def remove_emails(text: str, placeholder: str = "<EMAIL>") -> str:
    """Supprime les adresses e-mail et les remplace par un placeholder."""
    return _EMAIL_PATTERN.sub(placeholder, text)


# ---- Nombres & formats français ------------------------------------------ #

def normalize_decimal_separator(text: str) -> str:
    """
    Normalise le séparateur décimal : remplace le point par une virgule
    dans les nombres décimaux (convention française).

    Ex : "3.14" → "3,14"   (mais pas "v3.14" ni "www.site.fr")
    """
    return re.sub(
        r"(?<!\w)(\d+)\.(\d+)(?!\w)",
        r"\1,\2",
        text,
    )


def normalize_number_separator(text: str) -> str:
    """
    Normalise le séparateur de milliers :
    remplace la virgule anglaise dans les grands nombres par une espace insécable fine.

    Ex : "1,000,000" → "1 000 000"
    """
    NNBSP = "\u202f"

    def replace_thousands(m: re.Match) -> str:
        num = m.group(0).replace(",", NNBSP)
        return num

    return re.sub(r"\d{1,3}(?:,\d{3})+", replace_thousands, text)


# ---- Caractères spéciaux divers ------------------------------------------ #

def fix_ligatures(text: str) -> str:
    """
    Développe les ligatures typographiques rares en leurs composantes.
    Les ligatures françaises courantes (œ, æ) sont PRESERVÉES.

    Ligatures développées : ﬁ→fi  ﬂ→fl  ﬀ→ff  ﬃ→ffi  ﬄ→ffl
    """
    replacements = {
        "\ufb01": "fi",  # ﬁ
        "\ufb02": "fl",  # ﬂ
        "\ufb00": "ff",  # ﬀ
        "\ufb03": "ffi", # ﬃ
        "\ufb04": "ffl", # ﬄ
    }
    for lig, expanded in replacements.items():
        text = text.replace(lig, expanded)
    return text


def fix_roman_quotes(text: str) -> str:
    """
    Remplace les guillemets doubles droits par des guillemets français
    lorsqu'ils encadrent un texte (version conservative).
    """
    # Déjà géré dans quotes.py — ici pour usage autonome
    NNBSP = "\u202f"
    text = re.sub(
        r'"([^"]+)"',
        lambda m: f"«{NNBSP}{m.group(1).strip()}{NNBSP}»",
        text,
    )
    return text


def remove_repeated_punctuation(text: str) -> str:
    """
    Réduit les signes de ponctuation répétés abusivement.

    Ex : "vraiment !!!" → "vraiment !"
         "quoi ???"     → "quoi ?"
         "ah..."        → conservé (traité dans fix_ellipsis)
    """
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"\?{2,}", "?", text)
    # Combinaisons !? ou ?! → ?
    text = re.sub(r"[!?]{2,}", "?", text)
    return text
