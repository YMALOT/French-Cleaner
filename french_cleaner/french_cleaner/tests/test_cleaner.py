"""
Tests d'intégration pour FrenchCleaner.

Ces tests vérifient le comportement du pipeline complet sur des cas réels
rencontrés dans la pratique (scraping, OCR, copier-coller, etc.).
"""

import pytest
from french_cleaner import FrenchCleaner, CleanerConfig

NNBSP = "\u202f"


# =========================================================================== #
# Fixtures
# =========================================================================== #

@pytest.fixture
def cleaner():
    return FrenchCleaner()


@pytest.fixture
def cleaner_full():
    """Cleaner avec toutes les options activées."""
    return FrenchCleaner(
        remove_urls=True,
        remove_emails=True,
        convert_ascii_quotes=True,
        fix_repeated_punctuation=True,
    )


@pytest.fixture
def cleaner_minimal():
    """Cleaner avec toutes les transformations optionnelles désactivées."""
    return FrenchCleaner(
        fix_encoding=False,
        fix_linebreaks=False,
        fix_apostrophes=False,
        fix_quotes=False,
        fix_spaces=False,
        fix_ellipsis=False,
        fix_dash_spaces=False,
    )


# =========================================================================== #
# Tests de base
# =========================================================================== #

class TestCleanerBasic:

    def test_instantiation_default(self):
        cleaner = FrenchCleaner()
        assert cleaner is not None

    def test_instantiation_with_kwargs(self):
        cleaner = FrenchCleaner(remove_urls=True, remove_emails=True)
        assert cleaner.config.remove_urls is True
        assert cleaner.config.remove_emails is True

    def test_instantiation_with_config(self):
        cfg = CleanerConfig(remove_urls=True)
        cleaner = FrenchCleaner(config=cfg)
        assert cleaner.config.remove_urls is True

    def test_unknown_kwarg_raises(self):
        with pytest.raises(ValueError):
            FrenchCleaner(parametre_inconnu=True)

    def test_non_string_raises(self):
        cleaner = FrenchCleaner()
        with pytest.raises(TypeError):
            cleaner.clean(42)

    def test_empty_string(self, cleaner):
        assert cleaner.clean("") == ""

    def test_clean_batch(self, cleaner):
        texts = ["Bonjour ,monde", "Comment  vas-tu ?"]
        results = cleaner.clean_batch(texts)
        assert len(results) == 2
        assert all(isinstance(r, str) for r in results)


# =========================================================================== #
# Cas réels de scraping web
# =========================================================================== #

class TestScrapingCases:

    def test_html_entities_decoded(self, cleaner):
        result = cleaner.clean("Prix&nbsp;: 10 &amp; 20 €")
        assert "&nbsp;" not in result
        assert "&amp;" not in result
        assert "10" in result
        assert "20 €" in result

    def test_crlf_normalized(self, cleaner):
        result = cleaner.clean("ligne1\r\nligne2")
        assert "\r" not in result
        # les deux lignes sont présentes dans le résultat (séparées par \n ou espace)
        assert "ligne1" in result
        assert "ligne2" in result

    def test_url_in_text(self, cleaner_full):
        result = cleaner_full.clean("Voir https://example.com pour plus d'infos.")
        assert "https://example.com" not in result
        assert "<URL>" in result

    def test_email_in_text(self, cleaner_full):
        result = cleaner_full.clean("Contacter jean@example.fr pour info.")
        assert "jean@example.fr" not in result
        assert "<EMAIL>" in result


# =========================================================================== #
# Cas réels d'OCR / PDF
# =========================================================================== #

class TestOcrCases:

    def test_soft_hyphen_fusion(self, cleaner):
        result = cleaner.clean("Le traite-\nment du texte est impor-\ntant.")
        assert "traitement" in result
        assert "important" in result

    def test_accidental_newlines_fused(self, cleaner):
        result = cleaner.clean(
            "Le chien\nmangea sa\ncroquette avec\nappétit."
        )
        assert "\n" not in result
        assert "croquette avec" in result

    def test_fi_ligature_from_pdf(self, cleaner):
        result = cleaner.clean("\ufb01chier")  # ﬁchier
        assert result == "\ufb01chier".replace("\ufb01", "fi")

    def test_zero_width_chars_removed(self, cleaner):
        result = cleaner.clean("Bonjour\u200b monde\u200c.")
        assert "\u200b" not in result
        assert "\u200c" not in result


# =========================================================================== #
# Ponctuation française
# =========================================================================== #

class TestFrenchPunctuation:

    def test_space_before_exclamation(self, cleaner):
        result = cleaner.clean("Bonjour !")
        assert result == "Bonjour" + NNBSP + "!"

    def test_space_before_question(self, cleaner):
        result = cleaner.clean("Comment vas-tu ?")
        assert result == "Comment vas-tu" + NNBSP + "?"

    def test_space_before_colon(self, cleaner):
        result = cleaner.clean("Résultat :")
        assert NNBSP + ":" in result

    def test_space_before_semicolon(self, cleaner):
        result = cleaner.clean("Premier point ; deuxième point")
        assert NNBSP + ";" in result

    def test_no_space_before_comma(self, cleaner):
        result = cleaner.clean("Bonjour ,monde")
        assert " ," not in result

    def test_space_after_comma(self, cleaner):
        result = cleaner.clean("un,deux,trois")
        assert "un, deux, trois" == result

    def test_guillemets_spaces(self, cleaner):
        result = cleaner.clean("Il dit «bonjour»")
        assert "«" + NNBSP in result
        assert NNBSP + "»" in result

    def test_ellipsis_normalized(self, cleaner):
        result = cleaner.clean("Je ne sais pas...")
        assert "…" in result

    def test_em_dash_spaces(self, cleaner):
        result = cleaner.clean("mot—autre")
        assert " — " in result


# =========================================================================== #
# Apostrophes
# =========================================================================== #

class TestFrenchApostrophes:

    def test_apostrophe_typographic(self, cleaner):
        result = cleaner.clean("l'homme")
        assert "\u2019" in result

    def test_space_after_apostrophe_removed(self, cleaner):
        result = cleaner.clean("c' est")
        assert "c\u2019est" in result

    def test_elision_corrected(self, cleaner):
        result = cleaner.clean("le arbre")
        assert "l\u2019arbre" in result or "l'arbre" in result

    def test_elision_je_arrive(self, cleaner):
        result = cleaner.clean("je arrive")
        assert "j\u2019arrive" in result or "j'arrive" in result


# =========================================================================== #
# Cas réels de copier-coller
# =========================================================================== #

class TestCopyPasteCases:

    def test_multiple_spaces(self, cleaner):
        result = cleaner.clean("Bonjour     monde")
        assert "  " not in result

    def test_trailing_spaces(self, cleaner):
        result = cleaner.clean("Bonjour   \nMonde")
        assert "   \n" not in result

    def test_multiple_blank_lines(self, cleaner):
        result = cleaner.clean("A\n\n\n\n\nB")
        assert "\n\n\n" not in result

    def test_mixed_apostrophes(self, cleaner):
        result = cleaner.clean("c`est l'homme j\u00b4arrive")
        assert "`" not in result
        assert "\u00b4" not in result

    def test_complex_real_world(self, cleaner_full):
        """Texte copié d'un site web avec de nombreuses imperfections."""
        raw = (
            "Bonjour ,   comment  vas - tu ?\r\n"
            "Je vais bien ,merci!!\r\n"
            "Visitez https://example.com ou ecrivez a test@example.fr\r\n"
            "l'homme de le epoque est arrivé ..."
        )
        result = cleaner_full.clean(raw)
        assert "\r" not in result
        assert "  " not in result
        assert "https://example.com" not in result
        assert "test@example.fr" not in result
        assert "…" in result


# =========================================================================== #
# Configuration
# =========================================================================== #

class TestCleanerConfiguration:

    def test_minimal_cleaner_passthrough(self, cleaner_minimal):
        text = "Bonjour ,monde"
        result = cleaner_minimal.clean(text)
        # Avec fix_spaces=False, l'espace avant la virgule est conservée
        assert " ," in result

    def test_no_elision_correction(self):
        cleaner = FrenchCleaner(fix_elisions=False)
        result = cleaner.clean("le arbre")
        assert "le arbre" in result

    def test_straight_apostrophe_mode(self):
        cleaner = FrenchCleaner(use_typographic_apostrophe=False)
        result = cleaner.clean("l\u2019homme")
        assert "'" in result
        assert "\u2019" not in result

    def test_max_newlines_custom(self):
        cleaner = FrenchCleaner(max_newlines=1)
        result = cleaner.clean("a\n\n\nb")
        assert "\n\n" not in result
        assert "\n" in result

    def test_ascii_quotes_conversion(self):
        cleaner = FrenchCleaner(convert_ascii_quotes=True)
        result = cleaner.clean('"Bonjour monde"')
        assert "«" in result
        assert "»" in result

    def test_repr(self, cleaner):
        assert "FrenchCleaner" in repr(cleaner)
