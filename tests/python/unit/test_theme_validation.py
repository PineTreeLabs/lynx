# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for theme name validation.

Tests for validate_theme_name() function in src/lynx/utils/theme_config.py
"""

from lynx.utils.theme_config import VALID_THEMES, validate_theme_name


class TestValidateThemeName:
    """Test suite for validate_theme_name() function."""

    def test_valid_theme_names(self):
        """Test that all valid theme names are accepted."""
        for theme in VALID_THEMES:
            result = validate_theme_name(theme)
            assert result == theme, f"Valid theme '{theme}' should be accepted"

    def test_none_input(self):
        """Test that None input is considered valid (no explicit theme set)."""
        result = validate_theme_name(None)
        assert result is None, "None should be accepted as valid (no explicit theme)"

    def test_invalid_theme_names(self):
        """Test that invalid theme names return None and log warnings."""
        invalid_themes = [
            "purple",
            "neon",
            "rainbow",
            "custom",
            "Light",  # Wrong case
            "DARK",  # Wrong case
            "high contrast",  # Space instead of hyphen
            "high_contrast",  # Underscore instead of hyphen
            "",  # Empty string
        ]

        for invalid_theme in invalid_themes:
            result = validate_theme_name(invalid_theme)
            assert result is None, f"Invalid theme '{invalid_theme}' should return None"

    def test_case_sensitivity(self):
        """Test that theme names are case-sensitive."""
        # Only lowercase should be valid
        assert validate_theme_name("light") == "light"
        assert validate_theme_name("Light") is None
        assert validate_theme_name("LIGHT") is None

        assert validate_theme_name("dark") == "dark"
        assert validate_theme_name("Dark") is None
        assert validate_theme_name("DARK") is None

        assert validate_theme_name("high-contrast") == "high-contrast"
        assert validate_theme_name("High-Contrast") is None
        assert validate_theme_name("HIGH-CONTRAST") is None

    def test_whitespace_handling(self):
        """Test that themes with whitespace are invalid."""
        assert validate_theme_name(" light") is None
        assert validate_theme_name("light ") is None
        assert validate_theme_name(" light ") is None
        assert validate_theme_name("high contrast") is None  # Space instead of hyphen

    def test_special_characters(self):
        """Test that themes with special characters
        (except hyphen in 'high-contrast') are invalid."""
        assert validate_theme_name("light!") is None
        assert validate_theme_name("dark#") is None
        assert (
            validate_theme_name("high_contrast") is None
        )  # Underscore instead of hyphen

    def test_warning_logged_for_invalid(self, caplog):
        """Test that warnings are logged for invalid theme names."""
        import logging

        caplog.set_level(logging.WARNING)

        validate_theme_name("invalid_theme")

        # Check that a warning was logged
        assert len(caplog.records) > 0
        assert any("invalid" in record.message.lower() for record in caplog.records)
