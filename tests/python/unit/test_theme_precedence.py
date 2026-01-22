# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for theme precedence resolution.

Tests for resolve_theme() function in src/lynx/utils/theme_config.py

Precedence order (highest to lowest):
1. diagram_theme (instance attribute)
2. session_default (set via set_default_theme())
3. environment_default (LYNX_DEFAULT_THEME env var)
4. BUILT_IN_DEFAULT_THEME ("light")
"""

import pytest

from lynx.utils.theme_config import (
    BUILT_IN_DEFAULT_THEME,
    resolve_theme,
    set_default_theme,
)


@pytest.fixture
def clean_theme_config():
    """Reset global theme config before each test."""
    # Import the module to access internal state
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


@pytest.fixture
def mock_env_theme(monkeypatch):
    """Fixture to mock environment variable."""

    def _set_env(theme_value):
        if theme_value is None:
            monkeypatch.delenv("LYNX_DEFAULT_THEME", raising=False)
        else:
            monkeypatch.setenv("LYNX_DEFAULT_THEME", theme_value)
        # Reload the module to pick up env var changes
        import importlib

        import lynx.utils.theme_config as config

        importlib.reload(config)

    return _set_env


class TestResolvePrecedence:
    """Test suite for resolve_theme() precedence logic.

    Tests all 16 combinations of precedence levels (2^4):
    - Diagram: None | Valid
    - Session: None | Valid
    - Environment: None | Valid
    - Built-in: Always "light"
    """

    def test_all_none_uses_builtin(self, clean_theme_config):
        """Test 0000: No config set → built-in default."""
        import lynx.utils.theme_config as config

        config._session_default = None
        config._environment_default = None

        result = resolve_theme(diagram_theme=None)
        assert result == BUILT_IN_DEFAULT_THEME

    def test_only_env_set(self, clean_theme_config):
        """Test 0010: Environment only → environment default."""
        import lynx.utils.theme_config as config

        config._session_default = None
        config._environment_default = "dark"

        result = resolve_theme(diagram_theme=None)
        assert result == "dark"

    def test_only_session_set(self, clean_theme_config):
        """Test 0100: Session only → session default."""
        import lynx.utils.theme_config as config

        config._session_default = "dark"
        config._environment_default = None

        result = resolve_theme(diagram_theme=None)
        assert result == "dark"

    def test_only_diagram_set(self, clean_theme_config):
        """Test 1000: Diagram only → diagram theme."""
        import lynx.utils.theme_config as config

        config._session_default = None
        config._environment_default = None

        result = resolve_theme(diagram_theme="dark")
        assert result == "dark"

    def test_session_overrides_env(self, clean_theme_config):
        """Test 0110: Session + Environment → session wins."""
        import lynx.utils.theme_config as config

        config._session_default = "light"
        config._environment_default = "dark"

        result = resolve_theme(diagram_theme=None)
        assert result == "light"

    def test_diagram_overrides_session(self, clean_theme_config):
        """Test 1100: Diagram + Session → diagram wins."""
        import lynx.utils.theme_config as config

        config._session_default = "dark"
        config._environment_default = None

        result = resolve_theme(diagram_theme="light")
        assert result == "light"

    def test_diagram_overrides_env(self, clean_theme_config):
        """Test 1010: Diagram + Environment → diagram wins."""
        import lynx.utils.theme_config as config

        config._session_default = None
        config._environment_default = "dark"

        result = resolve_theme(diagram_theme="light")
        assert result == "light"

    def test_diagram_overrides_all(self, clean_theme_config):
        """Test 1110: Diagram + Session + Environment → diagram wins."""
        import lynx.utils.theme_config as config

        config._session_default = "dark"
        config._environment_default = "high-contrast"

        result = resolve_theme(diagram_theme="light")
        assert result == "light"

    def test_invalid_diagram_falls_back_to_session(self, clean_theme_config):
        """Test: Invalid diagram theme falls back to session."""
        import lynx.utils.theme_config as config

        config._session_default = "dark"
        config._environment_default = None

        result = resolve_theme(diagram_theme="invalid")
        assert result == "dark"

    def test_invalid_diagram_falls_back_to_env(self, clean_theme_config):
        """Test: Invalid diagram theme falls back to environment."""
        import lynx.utils.theme_config as config

        config._session_default = None
        config._environment_default = "high-contrast"

        result = resolve_theme(diagram_theme="invalid")
        assert result == "high-contrast"

    def test_invalid_diagram_falls_back_to_builtin(self, clean_theme_config):
        """Test: Invalid diagram theme with no other config → built-in."""
        import lynx.utils.theme_config as config

        config._session_default = None
        config._environment_default = None

        result = resolve_theme(diagram_theme="purple")
        assert result == BUILT_IN_DEFAULT_THEME

    def test_all_valid_themes_resolved_correctly(self, clean_theme_config):
        """Test: All valid themes can be resolved at each level."""
        import lynx.utils.theme_config as config

        for theme in ["light", "dark", "high-contrast"]:
            # Diagram level
            result = resolve_theme(diagram_theme=theme)
            assert result == theme

            # Session level
            config._session_default = theme
            config._environment_default = None
            result = resolve_theme(diagram_theme=None)
            assert result == theme

            # Environment level
            config._session_default = None
            config._environment_default = theme
            result = resolve_theme(diagram_theme=None)
            assert result == theme


class TestSetDefaultTheme:
    """Test suite for set_default_theme() function."""

    def test_set_valid_theme(self, clean_theme_config):
        """Test setting a valid session default theme."""
        set_default_theme("dark")

        import lynx.utils.theme_config as config

        assert config._session_default == "dark"

    def test_set_invalid_theme_logs_warning(self, clean_theme_config, caplog):
        """Test that invalid theme logs warning and doesn't change session default."""
        import logging

        caplog.set_level(logging.WARNING)

        set_default_theme("invalid")

        import lynx.utils.theme_config as config

        assert config._session_default is None
        assert any("invalid" in record.message.lower() for record in caplog.records)

    def test_set_theme_affects_future_diagrams(self, clean_theme_config):
        """Test that session default affects new diagrams."""
        set_default_theme("dark")

        result = resolve_theme(diagram_theme=None)
        assert result == "dark"

    def test_session_default_overrides_env(self, clean_theme_config):
        """Test that session default overrides environment variable."""
        import lynx.utils.theme_config as config

        config._environment_default = "high-contrast"
        set_default_theme("light")

        result = resolve_theme(diagram_theme=None)
        assert result == "light"

    def test_changing_session_default_affects_only_future_diagrams(
        self, clean_theme_config
    ):
        """T040: Test that changing session default doesn't affect
        existing diagram themes."""
        from lynx import Diagram

        # Set initial session default
        set_default_theme("dark")

        # Create diagrams without explicit themes
        diagram1 = Diagram()
        diagram2 = Diagram()

        # Diagrams should have None (will resolve to "dark" when widget is created)
        assert diagram1.theme is None
        assert diagram2.theme is None

        # Change session default
        set_default_theme("light")

        # Create new diagram
        diagram3 = Diagram()

        # Existing diagrams should still have None (unchanged)
        assert diagram1.theme is None
        assert diagram2.theme is None

        # New diagram should also have None (resolved at widget creation time)
        assert diagram3.theme is None

        # Verify resolve_theme() uses the new session default
        assert resolve_theme(diagram1.theme) == "light"
        assert resolve_theme(diagram2.theme) == "light"
        assert resolve_theme(diagram3.theme) == "light"


class TestPrecedenceCombinations:
    """Exhaustive test of all 16 precedence combinations."""

    @pytest.mark.parametrize(
        "diagram,session,env,expected",
        [
            # All None → built-in
            (None, None, None, "light"),
            # Only one set
            (None, None, "dark", "dark"),  # Env only
            (None, "dark", None, "dark"),  # Session only
            ("dark", None, None, "dark"),  # Diagram only
            # Two set
            (None, "light", "dark", "light"),  # Session > Env
            ("light", "dark", None, "light"),  # Diagram > Session
            ("light", None, "dark", "light"),  # Diagram > Env
            # Three set
            ("light", "dark", "high-contrast", "light"),  # Diagram > Session > Env
            # Invalid diagram theme
            ("invalid", None, None, "light"),  # Falls back to built-in
            ("invalid", "dark", None, "dark"),  # Falls back to session
            ("invalid", None, "dark", "dark"),  # Falls back to env
            ("invalid", "light", "dark", "light"),  # Falls back to session (not env)
            # All valid themes at each level
            ("high-contrast", "dark", "light", "high-contrast"),
            (None, "high-contrast", "light", "high-contrast"),
            (None, None, "high-contrast", "high-contrast"),
        ],
    )
    def test_precedence_matrix(
        self, diagram, session, env, expected, clean_theme_config
    ):
        """Test all precedence combinations systematically."""
        import lynx.utils.theme_config as config

        config._session_default = session
        config._environment_default = env

        result = resolve_theme(diagram_theme=diagram)
        assert result == expected, (
            f"Failed for diagram={diagram}, session={session}, env={env}"
        )
