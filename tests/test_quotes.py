"""Tests pour french_cleaner.rules.quotes"""

import pytest
from french_cleaner.rules.quotes import (
    fix_guillemet_spaces,
    convert_english_quotes_to_french,
    convert_ascii_quotes_to_french,
    fix_missing_guillemet_space,
    normalize_quotes,
)

NNBSP = "\u202f"
NBSP = "\u00a0"


class TestFixGuillemetsSpaces:

    def test_nnbsp_after_opening_guillemet(self):
        result = fix_guillemet_spaces("«bonjour»")
        assert result == "«" + NNBSP + "bonjour" + NNBSP + "»"

    def test_nnbsp_replaces_normal_space(self):
        result = fix_guillemet_spaces("« bonjour »")
        assert result == "«" + NNBSP + "bonjour" + NNBSP + "»"

    def test_nnbsp_replaces_nbsp(self):
        result = fix_guillemet_spaces("«" + NBSP + "bonjour" + NBSP + "»")
        assert result == "«" + NNBSP + "bonjour" + NNBSP + "»"

    def test_multiple_spaces_normalized(self):
        result = fix_guillemet_spaces("«   bonjour   »")
        assert result == "«" + NNBSP + "bonjour" + NNBSP + "»"

    def test_already_correct_unchanged(self):
        correct = "«" + NNBSP + "bonjour" + NNBSP + "»"
        assert fix_guillemet_spaces(correct) == correct


class TestConvertEnglishQuotes:

    def test_typographic_double_to_french(self):
        result = convert_english_quotes_to_french("\u201cBonjour\u201d")
        assert "«" in result
        assert "»" in result
        assert "Bonjour" in result

    def test_content_preserved(self):
        result = convert_english_quotes_to_french("\u201cle chat\u201d")
        assert "le chat" in result


class TestConvertAsciiQuotes:

    def test_ascii_double_to_french(self):
        result = convert_ascii_quotes_to_french('"Bonjour"')
        assert "«" in result
        assert "»" in result
        assert "Bonjour" in result

    def test_spaces_stripped_around_content(self):
        result = convert_ascii_quotes_to_french('"  Bonjour  "')
        assert NNBSP + "Bonjour" + NNBSP in result

    def test_unmatched_quote_not_converted(self):
        """Un guillemet ASCII seul ne doit pas être transformé."""
        result = convert_ascii_quotes_to_french('Il a dit "oui" et "non"')
        assert result.count("«") == 2
        assert result.count("»") == 2


class TestFixMissingGuillemetsSpace:

    def test_adds_nnbsp_after_opening(self):
        result = fix_missing_guillemet_space("«bonjour»")
        assert "«" + NNBSP in result

    def test_adds_nnbsp_before_closing(self):
        result = fix_missing_guillemet_space("«bonjour»")
        assert NNBSP + "»" in result

    def test_normal_space_to_nnbsp(self):
        result = fix_missing_guillemet_space("« bonjour »")
        assert "«" + NNBSP in result
        assert NNBSP + "»" in result

    def test_nbsp_to_nnbsp(self):
        result = fix_missing_guillemet_space("«\u00a0bonjour\u00a0»")
        assert "«" + NNBSP in result
        assert NNBSP + "»" in result


class TestNormalizeQuotes:

    def test_guillemet_spaces_normalized(self):
        result = normalize_quotes("Il dit «bonjour»")
        assert "«" + NNBSP + "bonjour" + NNBSP + "»" in result

    def test_convert_english_off_by_default(self):
        """La conversion des guillemets anglais est désactivée par défaut."""
        result = normalize_quotes("\u201cBonjour\u201d")
        assert "\u201c" in result  # conservé

    def test_convert_english_on(self):
        result = normalize_quotes("\u201cBonjour\u201d", convert_english=True)
        assert "«" in result
        assert "»" in result

    def test_convert_ascii_on(self):
        result = normalize_quotes('"Bonjour"', convert_ascii=True)
        assert "«" in result
        assert "»" in result

    def test_sentence_with_guillemets(self):
        result = normalize_quotes('Il a dit « Bonjour monde ».')
        assert "«" + NNBSP + "Bonjour monde" + NNBSP + "»" in result
