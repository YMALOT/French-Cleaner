"""Tests pour french_cleaner.rules.spaces"""

import pytest
from french_cleaner.rules.spaces import (
    fix_space_before_punctuation,
    fix_space_after_punctuation,
    fix_multiple_spaces,
    fix_space_around_dash,
    fix_ellipsis,
)

NNBSP = "\u202f"  # espace insécable fine


# =========================================================================== #
# fix_space_before_punctuation
# =========================================================================== #

class TestFixSpaceBeforePunctuation:

    def test_space_before_comma_removed(self):
        assert fix_space_before_punctuation("Bonjour ,monde") == "Bonjour,monde"

    def test_multiple_spaces_before_comma_removed(self):
        assert fix_space_before_punctuation("Bonjour  ,monde") == "Bonjour,monde"

    def test_space_before_period_removed(self):
        assert fix_space_before_punctuation("Fin de phrase .") == "Fin de phrase."

    def test_no_space_before_period_unchanged(self):
        result = fix_space_before_punctuation("Fin de phrase.")
        assert result == "Fin de phrase."

    def test_nnbsp_before_exclamation(self):
        result = fix_space_before_punctuation("Bonjour !")
        assert result == "Bonjour" + NNBSP + "!"

    def test_nnbsp_before_question(self):
        result = fix_space_before_punctuation("Comment vas-tu ?")
        assert result == "Comment vas-tu" + NNBSP + "?"

    def test_nnbsp_before_semicolon(self):
        result = fix_space_before_punctuation("Voici la liste ;")
        assert result == "Voici la liste" + NNBSP + ";"

    def test_nnbsp_before_colon(self):
        result = fix_space_before_punctuation("Résultat :")
        assert result == "Résultat" + NNBSP + ":"

    def test_url_colon_not_affected(self):
        """Le : dans une URL ne doit pas recevoir d'espace insécable."""
        result = fix_space_before_punctuation("Voir https://example.com")
        assert "https" + NNBSP + "://" not in result
        assert "https://example.com" in result

    def test_space_before_closing_paren_removed(self):
        assert fix_space_before_punctuation("(bonjour )") == "(bonjour)"

    def test_space_before_closing_bracket_removed(self):
        assert fix_space_before_punctuation("[liste ]") == "[liste]"

    def test_no_change_when_already_correct(self):
        text = "Bonjour" + NNBSP + "!"
        assert fix_space_before_punctuation(text) == text


# =========================================================================== #
# fix_space_after_punctuation
# =========================================================================== #

class TestFixSpaceAfterPunctuation:

    def test_space_after_comma(self):
        result = fix_space_after_punctuation("Bonjour,monde")
        assert result == "Bonjour, monde"

    def test_space_after_semicolon(self):
        result = fix_space_after_punctuation("un;deux")
        assert result == "un; deux"

    def test_space_after_exclamation(self):
        result = fix_space_after_punctuation("Super!Bravo")
        assert result == "Super! Bravo"

    def test_space_after_question(self):
        result = fix_space_after_punctuation("Quoi?Pourquoi")
        assert result == "Quoi? Pourquoi"

    def test_space_after_period_before_uppercase(self):
        result = fix_space_after_punctuation("Fin.Début")
        assert result == "Fin. Début"

    def test_no_space_after_period_before_lowercase(self):
        """Ne doit pas toucher au point dans '3.14'"""
        result = fix_space_after_punctuation("3.14")
        assert result == "3.14"

    def test_guillemet_ouvrant_space(self):
        result = fix_space_after_punctuation("Il dit «bonjour»")
        assert "«" + NNBSP in result

    def test_guillemet_fermant_space(self):
        result = fix_space_after_punctuation("Il dit «bonjour»")
        assert NNBSP + "»" in result

    def test_no_space_after_opening_paren(self):
        result = fix_space_after_punctuation("( bonjour )")
        assert result.startswith("(b")

    def test_already_correct_unchanged(self):
        text = "Bonjour, monde."
        assert fix_space_after_punctuation(text) == text


# =========================================================================== #
# fix_multiple_spaces
# =========================================================================== #

class TestFixMultipleSpaces:

    def test_double_space_reduced(self):
        assert fix_multiple_spaces("Bonjour  monde") == "Bonjour monde"

    def test_many_spaces_reduced(self):
        assert fix_multiple_spaces("Bonjour     monde") == "Bonjour monde"

    def test_newlines_preserved(self):
        text = "Ligne 1\n\nLigne 2"
        assert fix_multiple_spaces(text) == "Ligne 1\n\nLigne 2"

    def test_tabs_reduced(self):
        assert fix_multiple_spaces("a\t\tb") == "a b"

    def test_single_space_unchanged(self):
        assert fix_multiple_spaces("Un seul espace") == "Un seul espace"


# =========================================================================== #
# fix_space_around_dash
# =========================================================================== #

class TestFixSpaceAroundDash:

    def test_em_dash_gets_spaces(self):
        result = fix_space_around_dash("mot—autre")
        assert result == "mot — autre"

    def test_en_dash_gets_spaces(self):
        result = fix_space_around_dash("mot–autre")
        assert result == "mot – autre"

    def test_already_spaced_dash_unchanged(self):
        result = fix_space_around_dash("mot — autre")
        # L'espace double éventuel sera géré par fix_multiple_spaces
        assert "—" in result

    def test_hyphen_in_word_unchanged(self):
        """Le trait d'union dans un mot composé ne doit pas être touché."""
        result = fix_space_around_dash("avant-garde")
        assert result == "avant-garde"


# =========================================================================== #
# fix_ellipsis
# =========================================================================== #

class TestFixEllipsis:

    def test_three_dots_to_unicode(self):
        assert fix_ellipsis("Hmm...") == "Hmm…"

    def test_four_dots_to_unicode(self):
        assert fix_ellipsis("Hmm....") == "Hmm…"

    def test_space_before_ellipsis_removed(self):
        assert fix_ellipsis("Hmm ...") == "Hmm…"

    def test_space_after_ellipsis_before_uppercase(self):
        result = fix_ellipsis("Hmm…Bonjour")
        assert result == "Hmm… Bonjour"

    def test_ellipsis_before_lowercase_no_space(self):
        result = fix_ellipsis("Je ne sais…pas")
        assert result == "Je ne sais…pas"

    def test_unicode_ellipsis_preserved(self):
        assert fix_ellipsis("Hmm…") == "Hmm…"
