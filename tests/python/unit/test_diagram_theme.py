# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for Diagram-level theme control

Tests for:
- T027: Diagram constructor with theme parameter
- T028: Diagram.theme attribute assignment
- T029: Diagram constructor without theme (uses resolve_theme())
- T030: Invalid theme in constructor
- T031: Invalid theme in attribute assignment
"""

import pytest

from lynx import Diagram
from lynx.utils.theme_config import set_default_theme


@pytest.fixture
def clean_theme_config():
    """Reset global theme config before each test."""
    import lynx.utils.theme_config as config

    # Save original values
    original_session = config._session_default
    original_env = config._environment_default

    # Reset session default
    config._session_default = None

    yield

    # Restore original values
    config._session_default = original_session
    config._environment_default = original_env


class TestDiagramConstructorTheme:
    """Test Diagram constructor with theme parameter (T027, T029, T030)."""

    def test_constructor_with_dark_theme(self, clean_theme_config):
        """T027: Test Diagram constructor with theme='dark' sets diagram.theme."""
        diagram = Diagram(theme="dark")
        assert diagram.theme == "dark", "Constructor should set theme attribute"

    def test_constructor_with_light_theme(self, clean_theme_config):
        """T027: Test Diagram constructor with theme='light' sets diagram.theme."""
        diagram = Diagram(theme="light")
        assert diagram.theme == "light"

    def test_constructor_with_high_contrast_theme(self, clean_theme_config):
        """T027: Test Diagram constructor with theme='high-contrast'
        sets diagram.theme."""
        diagram = Diagram(theme="high-contrast")
        assert diagram.theme == "high-contrast"

    def test_constructor_without_theme_uses_default(self, clean_theme_config):
        """T029: Test Diagram constructor without theme
        uses resolve_theme() for default."""
        diagram = Diagram()
        # Should use built-in default when no other config exists
        assert diagram.theme is None, (
            "Constructor without theme should set theme to None (resolved later)"
        )

    def test_constructor_without_theme_respects_session_default(
        self, clean_theme_config
    ):
        """T029: Test Diagram constructor without theme respects session default."""
        set_default_theme("dark")
        diagram = Diagram()
        # Theme should remain None until widget initialization
        # Widget will call resolve_theme() to get effective theme
        assert diagram.theme is None

    def test_constructor_with_invalid_theme_logs_warning(
        self, clean_theme_config, caplog
    ):
        """T030: Test invalid theme in constructor logs warning
        and falls back to None."""
        import logging

        caplog.set_level(logging.WARNING)

        diagram = Diagram(theme="purple")

        # Should log warning
        assert len(caplog.records) > 0
        assert any("invalid" in record.message.lower() for record in caplog.records)

        # Should set theme to None (invalid theme rejected)
        assert diagram.theme is None

    def test_constructor_with_none_theme_explicit(self, clean_theme_config):
        """T029: Test Diagram constructor with explicit theme=None."""
        diagram = Diagram(theme=None)
        assert diagram.theme is None


class TestDiagramThemeAttributeAssignment:
    """Test Diagram.theme attribute assignment (T028, T031)."""

    def test_assign_light_theme(self, clean_theme_config):
        """T028: Test diagram.theme = 'light' updates attribute."""
        diagram = Diagram()
        diagram.theme = "light"
        assert diagram.theme == "light"

    def test_assign_dark_theme(self, clean_theme_config):
        """T028: Test diagram.theme = 'dark' updates attribute."""
        diagram = Diagram()
        diagram.theme = "dark"
        assert diagram.theme == "dark"

    def test_assign_high_contrast_theme(self, clean_theme_config):
        """T028: Test diagram.theme = 'high-contrast' updates attribute."""
        diagram = Diagram()
        diagram.theme = "high-contrast"
        assert diagram.theme == "high-contrast"

    def test_assign_none_theme(self, clean_theme_config):
        """T028: Test diagram.theme = None clears explicit theme."""
        diagram = Diagram(theme="dark")
        diagram.theme = None
        assert diagram.theme is None

    def test_assign_invalid_theme_logs_warning(self, clean_theme_config, caplog):
        """T031: Test invalid theme in attribute assignment
        logs warning and sets to None."""
        import logging

        caplog.set_level(logging.WARNING)

        diagram = Diagram()
        diagram.theme = "invalid_theme"

        # Should log warning
        assert len(caplog.records) > 0
        assert any("invalid" in record.message.lower() for record in caplog.records)

        # Should set theme to None
        assert diagram.theme is None

    def test_assign_invalid_theme_preserves_none_not_previous(self, clean_theme_config):
        """T031: Test invalid theme assignment sets to None, not previous value."""
        diagram = Diagram(theme="dark")
        assert diagram.theme == "dark"

        diagram.theme = "purple"
        # Should be None, not "dark"
        assert diagram.theme is None

    def test_change_theme_multiple_times(self, clean_theme_config):
        """T028: Test theme can be changed multiple times."""
        diagram = Diagram()

        diagram.theme = "light"
        assert diagram.theme == "light"

        diagram.theme = "dark"
        assert diagram.theme == "dark"

        diagram.theme = "high-contrast"
        assert diagram.theme == "high-contrast"

        diagram.theme = None
        assert diagram.theme is None


class TestDiagramThemeEdgeCases:
    """Edge cases for diagram-level theme control."""

    def test_theme_attribute_is_optional(self, clean_theme_config):
        """Test that theme attribute is Optional (can be None)."""
        diagram = Diagram()
        # Theme is None by default
        assert diagram.theme is None
        assert hasattr(diagram, "theme")

    def test_case_sensitivity(self, clean_theme_config):
        """Test that theme names are case-sensitive."""
        diagram = Diagram()

        # Uppercase should be invalid
        diagram.theme = "DARK"
        assert diagram.theme is None

        # Mixed case should be invalid
        diagram.theme = "Dark"
        assert diagram.theme is None

        # Lowercase should be valid
        diagram.theme = "dark"
        assert diagram.theme == "dark"

    def test_whitespace_handling(self, clean_theme_config):
        """Test that themes with whitespace are invalid."""
        diagram = Diagram()

        diagram.theme = " light"
        assert diagram.theme is None

        diagram.theme = "light "
        assert diagram.theme is None

        diagram.theme = " light "
        assert diagram.theme is None

    def test_hyphen_vs_underscore(self, clean_theme_config):
        """Test that only hyphen is valid for 'high-contrast'."""
        diagram = Diagram()

        # Underscore should be invalid
        diagram.theme = "high_contrast"
        assert diagram.theme is None

        # Hyphen should be valid
        diagram.theme = "high-contrast"
        assert diagram.theme == "high-contrast"

    def test_constructor_theme_survives_attribute_access(self, clean_theme_config):
        """Test that theme set in constructor persists after attribute access."""
        diagram = Diagram(theme="dark")
        _ = diagram.theme  # Access attribute
        assert diagram.theme == "dark"  # Should still be "dark"

    def test_multiple_diagrams_independent_themes(self, clean_theme_config):
        """Test that multiple diagrams have independent theme state."""
        diagram1 = Diagram(theme="dark")
        diagram2 = Diagram(theme="light")
        diagram3 = Diagram(theme="high-contrast")

        assert diagram1.theme == "dark"
        assert diagram2.theme == "light"
        assert diagram3.theme == "high-contrast"

        # Change one diagram's theme
        diagram1.theme = "light"

        # Others should be unchanged
        assert diagram1.theme == "light"
        assert diagram2.theme == "light"
        assert diagram3.theme == "high-contrast"
