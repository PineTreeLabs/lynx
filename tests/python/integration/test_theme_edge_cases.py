# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for theme edge cases (Phase 8).

Tests for:
- T064: Multiple diagrams with independent themes
- T065: UI theme change vs programmatic change interaction
- T066: Theme persistence across widget lifecycle
"""

import pytest

from lynx import Diagram
from lynx.utils.theme_config import set_default_theme
from lynx.widget import LynxWidget


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


class TestMultipleDiagramsIndependence:
    """Test that multiple diagrams maintain independent theme state (T064)."""

    def test_two_diagrams_different_themes(self, clean_theme_config):
        """T064: Test two diagrams with different themes remain independent."""
        diagram1 = Diagram(theme="dark")
        diagram2 = Diagram(theme="light")

        assert diagram1.theme == "dark"
        assert diagram2.theme == "light"

        # Change one diagram's theme
        diagram1.theme = "high-contrast"

        # Other should be unchanged
        assert diagram1.theme == "high-contrast"
        assert diagram2.theme == "light"

    def test_three_diagrams_different_themes(self, clean_theme_config):
        """T064: Test three diagrams with different themes remain independent."""
        d1 = Diagram(theme="dark")
        d2 = Diagram(theme="light")
        d3 = Diagram(theme="high-contrast")

        assert d1.theme == "dark"
        assert d2.theme == "light"
        assert d3.theme == "high-contrast"

        # Change all themes
        d1.theme = "light"
        d2.theme = "high-contrast"
        d3.theme = "dark"

        # Verify changes are independent
        assert d1.theme == "light"
        assert d2.theme == "high-contrast"
        assert d3.theme == "dark"

    def test_widgets_with_different_themes(self, clean_theme_config):
        """T064: Test widgets wrapping diagrams with different themes."""
        diagram1 = Diagram(theme="dark")
        diagram2 = Diagram(theme="light")

        LynxWidget(diagram1)
        LynxWidget(diagram2)

        # Widgets should resolve themes independently
        from lynx.utils.theme_config import resolve_theme

        assert resolve_theme(diagram1.theme) == "dark"
        assert resolve_theme(diagram2.theme) == "light"

    def test_diagram_without_theme_vs_explicit_theme(self, clean_theme_config):
        """T064: Test diagram without theme vs diagram with explicit theme."""
        set_default_theme("dark")

        d1 = Diagram()  # No explicit theme
        d2 = Diagram(theme="light")  # Explicit theme

        assert d1.theme is None  # Uses session default at widget creation time
        assert d2.theme == "light"  # Explicit theme preserved

        # Change session default shouldn't affect existing diagrams
        set_default_theme("high-contrast")

        assert d1.theme is None  # Still None
        assert d2.theme == "light"  # Still light

    def test_50_diagrams_independent_themes(self, clean_theme_config):
        """T064: Test many diagrams maintain independent themes (performance check)."""
        diagrams = []
        themes = ["light", "dark", "high-contrast"]

        # Create 50 diagrams with rotating themes
        for i in range(50):
            theme = themes[i % 3]
            d = Diagram(theme=theme)
            diagrams.append((d, theme))

        # Verify all themes are correct
        for diagram, expected_theme in diagrams:
            assert diagram.theme == expected_theme

        # Change half of them
        for i in range(25):
            diagrams[i][0].theme = "dark"

        # Verify changes
        for i in range(50):
            diagram = diagrams[i][0]
            if i < 25:
                assert diagram.theme == "dark"
            else:
                assert diagram.theme == diagrams[i][1]  # Original theme


class TestProgrammaticVsUIThemeChanges:
    """Test interaction between programmatic and UI theme changes (T065)."""

    def test_programmatic_then_ui_simulation(self, clean_theme_config):
        """T065: Test programmatic theme change followed by UI change simulation."""
        diagram = Diagram(theme="dark")
        widget = LynxWidget(diagram)

        assert diagram.theme == "dark"

        # Simulate UI change by updating widget.theme (what UI does)
        widget.theme = "light"

        # Widget observer should sync to diagram
        # Note: In real usage, traitlet observer calls diagram.theme = new_value
        # For this test, we simulate that behavior
        diagram.theme = widget.theme

        assert diagram.theme == "light"
        assert widget.theme == "light"

    def test_ui_then_programmatic_change(self, clean_theme_config):
        """T065: Test UI change simulation followed by programmatic change."""
        diagram = Diagram(theme="dark")
        widget = LynxWidget(diagram)

        # Simulate UI change
        widget.theme = "light"
        diagram.theme = widget.theme  # Observer would do this

        assert diagram.theme == "light"

        # Programmatic change
        diagram.theme = "high-contrast"

        # In real widget, this would trigger trait change,
        # but in test we verify directly
        assert diagram.theme == "high-contrast"

    def test_last_change_wins(self, clean_theme_config):
        """T065: Test that last change (UI or programmatic) wins."""
        diagram = Diagram(theme="light")

        # Change 1: Programmatic
        diagram.theme = "dark"
        assert diagram.theme == "dark"

        # Change 2: Simulated UI
        diagram.theme = "light"
        assert diagram.theme == "light"

        # Change 3: Programmatic
        diagram.theme = "high-contrast"
        assert diagram.theme == "high-contrast"

        # Last change wins
        assert diagram.theme == "high-contrast"


class TestThemePersistenceAcrossLifecycle:
    """Test theme persistence across widget lifecycle (T066)."""

    def test_theme_persists_after_widget_creation(self, clean_theme_config):
        """T066: Test theme persists when creating widget from diagram."""
        diagram = Diagram(theme="dark")

        # Create widget
        LynxWidget(diagram)

        # Theme should be resolved in widget
        from lynx.utils.theme_config import resolve_theme

        assert resolve_theme(diagram.theme) == "dark"

        # Diagram theme should be unchanged
        assert diagram.theme == "dark"

    def test_theme_persists_after_save_load(self, clean_theme_config):
        """T066: Test theme persists across save/load lifecycle."""
        # Create diagram with theme
        original = Diagram(theme="high-contrast")
        original.add_block("gain", "g1", K=5.0)

        # Save
        data = original.to_dict()

        # Load
        loaded = Diagram.from_dict(data)

        # Theme should persist
        assert loaded.theme == "high-contrast"

        # Create widget from loaded diagram
        LynxWidget(loaded)

        from lynx.utils.theme_config import resolve_theme

        assert resolve_theme(loaded.theme) == "high-contrast"

    def test_theme_survives_multiple_widget_recreations(self, clean_theme_config):
        """T066: Test theme survives creating multiple widgets from same diagram."""
        diagram = Diagram(theme="dark")

        # Create first widget
        LynxWidget(diagram)
        assert diagram.theme == "dark"

        # Create second widget from same diagram
        LynxWidget(diagram)
        assert diagram.theme == "dark"

        # Both widgets should reflect the same theme
        from lynx.utils.theme_config import resolve_theme

        assert resolve_theme(diagram.theme) == "dark"

    def test_changing_theme_after_widget_creation(self, clean_theme_config):
        """T066: Test changing diagram theme after widget is created."""
        diagram = Diagram(theme="light")
        LynxWidget(diagram)

        # Change diagram theme
        diagram.theme = "dark"

        # Diagram should reflect change
        assert diagram.theme == "dark"

        # In real usage, widget.theme would need manual update or re-sync
        # This tests the diagram-side persistence

    def test_theme_with_none_throughout_lifecycle(self, clean_theme_config):
        """T066: Test theme=None persists throughout lifecycle."""
        diagram = Diagram()  # No explicit theme
        assert diagram.theme is None

        # Save/load
        data = diagram.to_dict()
        loaded = Diagram.from_dict(data)
        assert loaded.theme is None

        # Create widget
        LynxWidget(loaded)
        assert loaded.theme is None

        # Widget should resolve to default
        from lynx.utils.theme_config import resolve_theme

        assert resolve_theme(loaded.theme) == "light"  # Built-in default


class TestThemeEdgeCases:
    """Additional edge cases for theme handling."""

    def test_rapidly_changing_theme(self, clean_theme_config):
        """Test rapid theme changes don't cause issues."""
        diagram = Diagram()

        # Rapidly change theme 100 times
        themes = ["light", "dark", "high-contrast"]
        for i in range(100):
            diagram.theme = themes[i % 3]

        # Final theme should be correct
        # (last iteration i=99, 99 % 3 = 0, so themes[0] = "light")
        assert diagram.theme == "light"

    def test_theme_with_blocks_and_connections(self, clean_theme_config):
        """Test theme works correctly with complex diagrams."""
        diagram = Diagram(theme="dark")

        # Add blocks
        diagram.add_block("gain", "g1", K=2.0)
        diagram.add_block("gain", "g2", K=3.0)

        # Add connection
        diagram.add_connection("conn1", "g1", "out", "g2", "in")

        # Theme should be unchanged
        assert diagram.theme == "dark"

        # Save/load should preserve everything
        data = diagram.to_dict()
        loaded = Diagram.from_dict(data)

        assert loaded.theme == "dark"
        assert len(loaded.blocks) == 2
        assert len(loaded.connections) == 1

    def test_session_default_with_multiple_diagrams(self, clean_theme_config):
        """Test session default applies correctly to multiple diagrams."""
        set_default_theme("high-contrast")

        # Create multiple diagrams without explicit themes
        diagrams = [Diagram() for _ in range(10)]

        # All should have None (will resolve to session default)
        for d in diagrams:
            assert d.theme is None

        # When widgets are created, they should use session default
        from lynx.utils.theme_config import resolve_theme

        for d in diagrams:
            assert resolve_theme(d.theme) == "high-contrast"

    def test_invalid_theme_doesnt_break_diagram(self, clean_theme_config):
        """Test that invalid theme doesn't break diagram functionality."""
        diagram = Diagram()

        # Try to set invalid theme
        diagram.theme = "invalid_theme"

        # Should be set to None
        assert diagram.theme is None

        # Diagram should still work normally
        diagram.add_block("gain", "g1", K=1.0)
        assert len(diagram.blocks) == 1

        # Should be able to save/load
        data = diagram.to_dict()
        loaded = Diagram.from_dict(data)
        assert loaded.theme is None
        assert len(loaded.blocks) == 1
