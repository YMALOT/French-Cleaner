"""
french_cleaner — Nettoyage typographique de textes en français.
"""

from .cleaner import FrenchCleaner, CleanerConfig
from .rules import (
    fix_space_before_punctuation,
    fix_space_after_punctuation,
    fix_multiple_spaces,
    fix_space_around_dash,
    fix_ellipsis,
    normalize_linebreaks,
    normalize_apostrophes,
    normalize_quotes,
    fix_encoding,
    normalize_unicode,
    remove_control_chars,
    remove_zero_width,
    decode_html_entities,
    remove_html_tags,
    remove_urls,
    remove_emails,
    fix_ligatures,
    remove_repeated_punctuation,
)

__version__ = "0.1.0"
__author__ = "french_cleaner"

__all__ = [
    "FrenchCleaner",
    "CleanerConfig",
    # règles individuelles
    "fix_space_before_punctuation",
    "fix_space_after_punctuation",
    "fix_multiple_spaces",
    "fix_space_around_dash",
    "fix_ellipsis",
    "normalize_linebreaks",
    "normalize_apostrophes",
    "normalize_quotes",
    "fix_encoding",
    "normalize_unicode",
    "remove_control_chars",
    "remove_zero_width",
    "decode_html_entities",
    "remove_html_tags",
    "remove_urls",
    "remove_emails",
    "fix_ligatures",
    "remove_repeated_punctuation",
]
