"""
FrenchCleaner — classe principale du pipeline de nettoyage de texte français.

Utilisation rapide :
    from french_cleaner import FrenchCleaner

    cleaner = FrenchCleaner()
    text = cleaner.clean("Bonjour ,comment  vas-tu ?")
    # → "Bonjour, comment vas-tu ?"

Utilisation avancée (configuration) :
    cleaner = FrenchCleaner(
        fix_encoding=True,
        fix_linebreaks=True,
        fix_apostrophes=True,
        fix_quotes=True,
        fix_spaces=True,
        remove_urls=False,
        remove_emails=False,
        use_typographic_apostrophe=True,
        convert_english_quotes=False,
        convert_ascii_quotes=False,
        max_newlines=2,
    )
"""

from dataclasses import dataclass, field
from typing import List, Callable

from .rules.misc import (
    fix_encoding as _fix_encoding,
    normalize_unicode,
    remove_control_chars,
    remove_zero_width,
    decode_html_entities,
    remove_html_tags,
    remove_urls as _remove_urls,
    remove_emails as _remove_emails,
    fix_ligatures,
    remove_repeated_punctuation,
)
from .rules.linebreaks import normalize_linebreaks
from .rules.apostrophes import normalize_apostrophes
from .rules.quotes import normalize_quotes
from .rules.spaces import (
    fix_space_before_punctuation,
    fix_space_after_punctuation,
    fix_multiple_spaces,
    fix_space_around_dash,
    fix_ellipsis,
)


@dataclass
class CleanerConfig:
    """Configuration du pipeline FrenchCleaner."""

    # --- Encodage & Unicode ---
    fix_encoding: bool = True
    """Corrige le mojibake via ftfy (si disponible)."""

    remove_zero_width_chars: bool = True
    """Supprime les caractères de largeur nulle (zero-width)."""

    remove_control_characters: bool = True
    """Supprime les caractères de contrôle invisibles."""

    fix_ligatures: bool = True
    """Développe les ligatures rares (ﬁ→fi, etc.) en préservant œ et æ."""

    # --- HTML ---
    decode_html: bool = True
    """Décode les entités HTML (&amp;, &nbsp;, etc.)."""

    strip_html_tags: bool = False
    """Supprime les balises HTML résiduelles."""

    # --- Sauts de ligne ---
    fix_linebreaks: bool = True
    """Normalise les sauts de ligne (CRLF, multiples, accidentels)."""

    max_newlines: int = 2
    """Nombre maximum de sauts de ligne consécutifs autorisés."""

    fix_soft_hyphens: bool = True
    """Corrige les coupures de mot OCR/PDF (ex : informa-\\ntion)."""

    fix_accidental_newlines: bool = True
    """Fusionne les sauts de ligne accidentels en milieu de phrase."""

    # --- Espaces ---
    fix_spaces: bool = True
    """Normalise les espaces (avant/après ponctuation, multiples)."""

    fix_dash_spaces: bool = True
    """Normalise les espaces autour des tirets cadratins et demi-cadratins."""

    fix_ellipsis: bool = True
    """Normalise les points de suspension (... → …)."""

    # --- Apostrophes ---
    fix_apostrophes: bool = True
    """Normalise les apostrophes."""

    use_typographic_apostrophe: bool = True
    """Utilise l'apostrophe typographique ' (U+2019) au lieu de '."""

    fix_elisions: bool = True
    """Corrige les élisions manquantes (le enfant → l'enfant)."""

    # --- Guillemets ---
    fix_quotes: bool = True
    """Normalise les espaces autour des guillemets français « »."""

    convert_english_quotes: bool = False
    """Convertit les guillemets anglais typographiques ("…") en « … »."""

    convert_ascii_quotes: bool = False
    """Convertit les guillemets ASCII droits ("…") en « … »."""

    # --- URLs & emails ---
    remove_urls: bool = False
    """Supprime les URLs (remplacées par <URL>)."""

    url_placeholder: str = "<URL>"
    """Placeholder pour les URLs supprimées."""

    remove_emails: bool = False
    """Supprime les e-mails (remplacés par <EMAIL>)."""

    email_placeholder: str = "<EMAIL>"

    # --- Ponctuation ---
    fix_repeated_punctuation: bool = False
    """Réduit la ponctuation répétée (!!!, ???) à un seul signe."""


class FrenchCleaner:
    """
    Pipeline de nettoyage de texte en français.

    Applique une série de transformations configurables dans le bon ordre
    pour produire un texte normalisé typographiquement correct.

    Exemple
    -------
    >>> from french_cleaner import FrenchCleaner
    >>> cleaner = FrenchCleaner()
    >>> cleaner.clean("Bonjour ,comment  vas-tu ?")
    'Bonjour, comment vas-tu\u202f?'
    """

    def __init__(self, config: CleanerConfig = None, **kwargs):
        """
        Paramètres
        ----------
        config : CleanerConfig, optionnel
            Configuration complète. Si None, utilise les valeurs par défaut.
        **kwargs
            Paramètres de configuration passés directement (surchargent config).
        """
        if config is None:
            config = CleanerConfig()

        # Surcharge avec kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ValueError(f"Paramètre de configuration inconnu : '{key}'")

        self.config = config

    def clean(self, text: str) -> str:
        """
        Nettoie le texte en appliquant le pipeline configuré.

        Paramètres
        ----------
        text : str
            Texte brut à nettoyer.

        Retourne
        --------
        str
            Texte nettoyé et normalisé.
        """
        if not isinstance(text, str):
            raise TypeError(f"Le texte doit être une chaîne, reçu : {type(text)}")

        cfg = self.config

        # 1. Encodage & Unicode (en premier, avant toute autre opération)
        if cfg.fix_encoding:
            text = _fix_encoding(text)
        text = normalize_unicode(text)

        if cfg.remove_zero_width_chars:
            text = remove_zero_width(text)

        if cfg.remove_control_characters:
            text = remove_control_chars(text)

        if cfg.fix_ligatures:
            text = fix_ligatures(text)

        # 2. HTML
        if cfg.decode_html:
            text = decode_html_entities(text)

        if cfg.strip_html_tags:
            text = remove_html_tags(text)

        # 3. URLs & emails (avant les autres transformations pour éviter
        #    que les ponctuation dans les URLs soient modifiées)
        if cfg.remove_urls:
            text = _remove_urls(text, placeholder=cfg.url_placeholder)

        if cfg.remove_emails:
            text = _remove_emails(text, placeholder=cfg.email_placeholder)

        # 4. Sauts de ligne
        if cfg.fix_linebreaks:
            text = normalize_linebreaks(
                text,
                max_newlines=cfg.max_newlines,
                fix_soft=cfg.fix_soft_hyphens,
                fix_accidental=cfg.fix_accidental_newlines,
            )

        # 5. Apostrophes (avant les espaces pour que les élisions
        #    ne créent pas de faux espaces)
        if cfg.fix_apostrophes:
            text = normalize_apostrophes(
                text,
                use_typographic=cfg.use_typographic_apostrophe,
                fix_elisions=cfg.fix_elisions,
            )

        # 6. Guillemets
        if cfg.fix_quotes:
            text = normalize_quotes(
                text,
                convert_english=cfg.convert_english_quotes,
                convert_ascii=cfg.convert_ascii_quotes,
            )

        # 7. Ponctuation répétée — avant les espaces pour éviter que
        #    fix_space_before_punctuation insère des NNBSP entre "!!!" → "! ! !"
        if cfg.fix_repeated_punctuation:
            text = remove_repeated_punctuation(text)

        # 8. Points de suspension
        if cfg.fix_ellipsis:
            text = fix_ellipsis(text)

        # 9. Tirets
        if cfg.fix_dash_spaces:
            text = fix_space_around_dash(text)

        # 10. Espaces autour de la ponctuation (en dernier)
        if cfg.fix_spaces:
            text = fix_space_before_punctuation(text)
            text = fix_space_after_punctuation(text)
            text = fix_multiple_spaces(text)

        return text

    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Nettoie une liste de textes.

        Paramètres
        ----------
        texts : list[str]

        Retourne
        --------
        list[str]
        """
        return [self.clean(t) for t in texts]

    def __repr__(self) -> str:
        active = [
            k for k, v in self.config.__dict__.items()
            if isinstance(v, bool) and v
        ]
        return f"FrenchCleaner(active=[{', '.join(active)}])"
