"""Tests pour french_cleaner.rules.misc"""

import pytest
from french_cleaner.rules.misc import (
    normalize_unicode,
    remove_control_chars,
    remove_zero_width,
    decode_html_entities,
    remove_html_tags,
    remove_urls,
    remove_emails,
    normalize_decimal_separator,
    normalize_number_separator,
    fix_ligatures,
    remove_repeated_punctuation,
)


class TestNormalizeUnicode:

    def test_nfc_normalization(self):
        # "é" en NFD (e + combining accent) → NFC (é seul)
        nfd_e = "e\u0301"  # e + COMBINING ACUTE ACCENT
        result = normalize_unicode(nfd_e)
        assert result == "\u00e9"

    def test_already_nfc_unchanged(self):
        assert normalize_unicode("éàü") == "éàü"


class TestRemoveControlChars:

    def test_null_byte_removed(self):
        assert remove_control_chars("abc\x00def") == "abcdef"

    def test_bell_removed(self):
        assert remove_control_chars("abc\x07def") == "abcdef"

    def test_newline_preserved(self):
        assert remove_control_chars("abc\ndef") == "abc\ndef"

    def test_tab_preserved(self):
        assert remove_control_chars("abc\tdef") == "abc\tdef"

    def test_zero_width_space_removed(self):
        assert remove_control_chars("abc\u200bdef") == "abcdef"

    def test_bom_removed(self):
        assert remove_control_chars("\ufeffBonjour") == "Bonjour"


class TestRemoveZeroWidth:

    def test_zwsp_removed(self):
        assert remove_zero_width("a\u200bb") == "ab"

    def test_zwnj_removed(self):
        assert remove_zero_width("a\u200cb") == "ab"

    def test_zwj_removed(self):
        assert remove_zero_width("a\u200db") == "ab"

    def test_bom_removed(self):
        assert remove_zero_width("\ufeffBonjour") == "Bonjour"

    def test_normal_text_unchanged(self):
        assert remove_zero_width("Bonjour monde") == "Bonjour monde"


class TestDecodeHtmlEntities:

    def test_amp(self):
        assert decode_html_entities("a &amp; b") == "a & b"

    def test_lt_gt(self):
        assert decode_html_entities("a &lt;b&gt; c") == "a <b> c"

    def test_nbsp(self):
        assert decode_html_entities("a&nbsp;b") == "a\u00a0b"

    def test_numeric_entity(self):
        assert decode_html_entities("&#233;") == "é"

    def test_no_entities_unchanged(self):
        assert decode_html_entities("Bonjour monde") == "Bonjour monde"


class TestRemoveHtmlTags:

    def test_bold_tag_removed(self):
        assert remove_html_tags("<b>Bonjour</b>") == "Bonjour"

    def test_multiple_tags_removed(self):
        result = remove_html_tags("<p>Un <em>texte</em>.</p>")
        assert result == "Un texte."

    def test_self_closing_removed(self):
        assert remove_html_tags("Ligne<br/>suite") == "Lignesuite"

    def test_no_tags_unchanged(self):
        assert remove_html_tags("Bonjour monde") == "Bonjour monde"


class TestRemoveUrls:

    def test_http_url_removed(self):
        result = remove_urls("Voir http://example.com pour plus.")
        assert "http://example.com" not in result
        assert "<URL>" in result

    def test_https_url_removed(self):
        result = remove_urls("Voir https://example.com/path?q=1")
        assert "https://" not in result

    def test_www_url_removed(self):
        result = remove_urls("Voir www.example.com")
        assert "www.example.com" not in result

    def test_custom_placeholder(self):
        result = remove_urls("Voir http://example.com", placeholder="[LIEN]")
        assert "[LIEN]" in result

    def test_no_url_unchanged(self):
        assert remove_urls("Bonjour monde") == "Bonjour monde"


class TestRemoveEmails:

    def test_email_removed(self):
        result = remove_emails("Contacter test@example.com pour info.")
        assert "test@example.com" not in result
        assert "<EMAIL>" in result

    def test_complex_email_removed(self):
        result = remove_emails("jean.dupont+tag@mail.example.fr")
        assert "@" not in result

    def test_no_email_unchanged(self):
        assert remove_emails("Bonjour monde") == "Bonjour monde"


class TestNormalizeDecimalSeparator:

    def test_point_to_comma(self):
        assert normalize_decimal_separator("3.14") == "3,14"

    def test_price_with_point(self):
        assert normalize_decimal_separator("19.99") == "19,99"

    def test_version_not_changed(self):
        """Les numéros de version (v3.14) ne doivent pas être changés."""
        result = normalize_decimal_separator("v3.14")
        assert "v3.14" in result

    def test_url_not_changed(self):
        """Les points dans les URLs ne doivent pas être changés."""
        result = normalize_decimal_separator("http://example.com")
        assert "example.com" in result

    def test_integer_unchanged(self):
        assert normalize_decimal_separator("42") == "42"


class TestNormalizeNumberSeparator:

    def test_thousands_comma_to_nnbsp(self):
        NNBSP = "\u202f"
        result = normalize_number_separator("1,000,000")
        assert NNBSP in result
        assert "," not in result

    def test_regular_text_unchanged(self):
        assert normalize_number_separator("Bonjour") == "Bonjour"


class TestFixLigatures:

    def test_fi_ligature(self):
        assert fix_ligatures("\ufb01n") == "fin"

    def test_fl_ligature(self):
        assert fix_ligatures("\ufb02eur") == "fleur"

    def test_ff_ligature(self):
        assert fix_ligatures("\ufb00et") == "ffet"

    def test_oe_ligature_preserved(self):
        """œ est une ligature française légitime → à conserver."""
        assert fix_ligatures("cœur") == "cœur"

    def test_ae_ligature_preserved(self):
        """æ est une ligature française légitime → à conserver."""
        assert fix_ligatures("æther") == "æther"


class TestRemoveRepeatedPunctuation:

    def test_multiple_exclamations(self):
        assert remove_repeated_punctuation("Super !!!") == "Super !"

    def test_multiple_questions(self):
        assert remove_repeated_punctuation("Quoi ???") == "Quoi ?"

    def test_mixed_punctuation(self):
        assert remove_repeated_punctuation("Vraiment !?") == "Vraiment ?"

    def test_single_unchanged(self):
        assert remove_repeated_punctuation("Super !") == "Super !"

    def test_ellipsis_not_affected(self):
        """Les points de suspension ne sont pas affectés."""
        assert remove_repeated_punctuation("Hmm...") == "Hmm..."
