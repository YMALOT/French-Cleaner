"""Tests pour french_cleaner.rules.linebreaks"""

import pytest
from french_cleaner.rules.linebreaks import (
    fix_crlf,
    fix_trailing_spaces,
    fix_multiple_newlines,
    fix_soft_hyphens,
    fix_accidental_newlines,
    normalize_linebreaks,
)


class TestFixCrlf:

    def test_crlf_to_lf(self):
        assert fix_crlf("ligne1\r\nligne2") == "ligne1\nligne2"

    def test_cr_only_to_lf(self):
        assert fix_crlf("ligne1\rligne2") == "ligne1\nligne2"

    def test_lf_unchanged(self):
        assert fix_crlf("ligne1\nligne2") == "ligne1\nligne2"

    def test_mixed_endings(self):
        result = fix_crlf("a\r\nb\rc\nd")
        assert result == "a\nb\nc\nd"


class TestFixTrailingSpaces:

    def test_trailing_space_removed(self):
        assert fix_trailing_spaces("Bonjour   \n") == "Bonjour\n"

    def test_trailing_tab_removed(self):
        assert fix_trailing_spaces("Bonjour\t\n") == "Bonjour\n"

    def test_leading_space_preserved(self):
        assert fix_trailing_spaces("  Bonjour\n") == "  Bonjour\n"

    def test_multiple_lines(self):
        result = fix_trailing_spaces("ligne1  \nligne2 \nligne3")
        assert result == "ligne1\nligne2\nligne3"


class TestFixMultipleNewlines:

    def test_three_newlines_reduced_to_two(self):
        result = fix_multiple_newlines("a\n\n\nb")
        assert result == "a\n\nb"

    def test_many_newlines_reduced(self):
        result = fix_multiple_newlines("a\n\n\n\n\nb")
        assert result == "a\n\nb"

    def test_two_newlines_preserved(self):
        result = fix_multiple_newlines("a\n\nb")
        assert result == "a\n\nb"

    def test_single_newline_preserved(self):
        result = fix_multiple_newlines("a\nb")
        assert result == "a\nb"

    def test_custom_max(self):
        result = fix_multiple_newlines("a\n\n\nb", max_newlines=1)
        assert result == "a\nb"


class TestFixSoftHyphens:

    def test_ocr_hyphen_fused(self):
        result = fix_soft_hyphens("informa-\ntion")
        assert result == "information"

    def test_hyphen_composition_preserved(self):
        """
        Si la lettre suivante est une majuscule, le trait d'union
        est un tiret de composition (ex: franco-\nBritannique) → préservé.
        """
        result = fix_soft_hyphens("franco-\nBritannique")
        assert "-\n" in result

    def test_word_continuation(self):
        result = fix_soft_hyphens("re-\nprendre")
        assert result == "reprendre"

    def test_no_hyphen_unchanged(self):
        assert fix_soft_hyphens("bonjour\nmonde") == "bonjour\nmonde"


class TestFixAccidentalNewlines:

    def test_newline_mid_sentence_fused(self):
        """Saut de ligne accidentel devant une minuscule → espace."""
        result = fix_accidental_newlines("Bonjour\nmonde")
        assert result == "Bonjour monde"

    def test_newline_before_uppercase_preserved(self):
        """Saut de ligne avant une majuscule → conservé (nouveau paragraphe)."""
        result = fix_accidental_newlines("Bonjour.\nMonde")
        assert "\n" in result

    def test_newline_after_period_preserved(self):
        """Saut de ligne après un point → conservé (fin de phrase)."""
        result = fix_accidental_newlines("Fin de phrase.\nmonde")
        assert "\n" in result

    def test_newline_after_exclamation_preserved(self):
        result = fix_accidental_newlines("Super !\nmonde")
        assert "\n" in result

    def test_newline_before_digit_fused(self):
        """Saut de ligne devant un chiffre en milieu de phrase → espace."""
        result = fix_accidental_newlines("Il y a\n3 pommes")
        assert result == "Il y a 3 pommes"

    def test_intentional_paragraph_preserved(self):
        result = fix_accidental_newlines("Paragraphe 1.\n\nParagraphe 2.")
        assert "\n\n" in result


class TestNormalizeLinebreaks:

    def test_full_pipeline(self):
        text = "Bonjour  \r\ncomment\nvas-tu ?\n\n\n\nBien merci."
        result = normalize_linebreaks(text)
        assert "\r" not in result
        assert "\n\n\n" not in result
        assert "Bonjour" in result
        assert "Bien merci." in result

    def test_soft_hyphen_pipeline(self):
        result = normalize_linebreaks("informa-\ntion", fix_soft=True)
        assert "information" in result

    def test_accidental_newline_pipeline(self):
        result = normalize_linebreaks(
            "Le chien\nmangea sa\ncroquette.",
            fix_accidental=True,
        )
        assert "\n" not in result
        assert "Le chien mangea sa croquette." == result
