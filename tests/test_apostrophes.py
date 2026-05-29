"""Tests pour french_cleaner.rules.apostrophes"""

import pytest
from french_cleaner.rules.apostrophes import (
    normalize_apostrophe_char,
    fix_space_around_apostrophe,
    fix_missing_elision,
    fix_double_apostrophe,
    normalize_apostrophes,
)

APOS_TYPO = "\u2019"  # '
APOS_DROIT = "'"


class TestNormalizeApostropheChar:

    def test_straight_to_typographic(self):
        result = normalize_apostrophe_char("l'homme", use_typographic=True)
        assert result == "l\u2019homme"

    def test_typographic_to_straight(self):
        result = normalize_apostrophe_char("l\u2019homme", use_typographic=False)
        assert result == "l'homme"

    def test_grave_accent_replaced(self):
        result = normalize_apostrophe_char("l`homme", use_typographic=True)
        assert APOS_TYPO in result

    def test_acute_accent_replaced(self):
        result = normalize_apostrophe_char("l\u00b4homme", use_typographic=True)
        assert APOS_TYPO in result


class TestFixSpaceAroundApostrophe:

    def test_space_after_apostrophe_removed(self):
        result = fix_space_around_apostrophe("c' est")
        assert result == "c'est"

    def test_space_before_apostrophe_removed(self):
        result = fix_space_around_apostrophe("l 'homme")
        assert result == "l'homme"

    def test_both_spaces_removed(self):
        result = fix_space_around_apostrophe("j' ai")
        assert result == "j'ai"

    def test_multiple_spaces_around_apos(self):
        result = fix_space_around_apostrophe("c'  est")
        assert result == "c'est"

    def test_no_space_unchanged(self):
        result = fix_space_around_apostrophe("l'homme")
        assert result == "l'homme"

    def test_typographic_apostrophe_spaces(self):
        result = fix_space_around_apostrophe("c\u2019 est")
        assert result == "c\u2019est"


class TestFixMissingElision:

    def test_le_before_vowel(self):
        result = fix_missing_elision("le arbre")
        assert "l'arbre" in result or "l\u2019arbre" in result

    def test_la_before_vowel(self):
        result = fix_missing_elision("la armoire")
        assert "l'armoire" in result or "l\u2019armoire" in result

    def test_de_before_vowel(self):
        result = fix_missing_elision("de eau")
        assert "d'eau" in result or "d\u2019eau" in result

    def test_je_before_vowel(self):
        result = fix_missing_elision("je arrive")
        assert "j'arrive" in result or "j\u2019arrive" in result

    def test_ce_before_e(self):
        result = fix_missing_elision("ce est")
        assert "c'est" in result or "c\u2019est" in result

    def test_ne_before_vowel(self):
        result = fix_missing_elision("il ne arrive pas")
        assert "n'arrive" in result or "n\u2019arrive" in result

    def test_que_before_vowel(self):
        result = fix_missing_elision("parce que il")
        assert "qu'il" in result or "qu\u2019il" in result

    def test_no_elision_before_consonant(self):
        """Pas d'élision devant une consonne."""
        result = fix_missing_elision("le chat")
        assert result == "le chat"

    def test_uppercase_preserved(self):
        """La casse du mot élidé doit être préservée."""
        result = fix_missing_elision("Le arbre")
        assert result[0].isupper() or result.startswith("L'")

    def test_h_mute_elision(self):
        result = fix_missing_elision("le homme")
        assert "l'homme" in result or "l\u2019homme" in result


class TestFixDoubleApostrophe:

    def test_double_straight_reduced(self):
        result = fix_double_apostrophe("l''homme")
        assert result.count("'") + result.count(APOS_TYPO) == 1

    def test_triple_reduced(self):
        result = fix_double_apostrophe("l'''homme")
        assert result.count(APOS_TYPO) == 1

    def test_single_unchanged(self):
        result = fix_double_apostrophe("l'homme")
        assert result == "l'homme" or result == "l\u2019homme"


class TestNormalizeApostrophes:

    def test_full_pipeline(self):
        result = normalize_apostrophes("c' est l 'homme de le epoque")
        # c'est, l'homme
        assert "c\u2019est" in result
        assert "l\u2019homme" in result

    def test_pipeline_no_elision(self):
        result = normalize_apostrophes("le arbre", fix_elisions=False)
        # Sans correction d'élision, "le arbre" reste intact
        assert "le arbre" in result

    def test_pipeline_straight_apostrophe(self):
        result = normalize_apostrophes(
            "c'est", use_typographic=False
        )
        assert "'" in result
        assert APOS_TYPO not in result
