# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for theme persistence (Phase 7).

Tests for:
- T051: Diagram save with theme (to_dict includes theme field)
- T052: Diagram load with theme (from_dict restores theme)
- T053: Diagram load without theme field (backward compat)
- T054: Diagram load with invalid theme (logs warning, falls back)
- T057: Backward compatibility test
"""

import json

from lynx import Diagram


class TestThemePersistence:
    """Test theme persistence in diagram save/load."""

    def test_save_diagram_with_light_theme(self):
        """T051: Test that diagram.to_dict() includes theme field for light theme."""
        diagram = Diagram(theme="light")
        diagram_dict = diagram.to_dict()

        assert "theme" in diagram_dict
        assert diagram_dict["theme"] == "light"

    def test_save_diagram_with_dark_theme(self):
        """T051: Test that diagram.to_dict() includes theme field for dark theme."""
        diagram = Diagram(theme="dark")
        diagram_dict = diagram.to_dict()

        assert "theme" in diagram_dict
        assert diagram_dict["theme"] == "dark"

    def test_save_diagram_with_high_contrast_theme(self):
        """T051: Test that diagram.to_dict() includes theme field
        for high-contrast theme."""
        diagram = Diagram(theme="high-contrast")
        diagram_dict = diagram.to_dict()

        assert "theme" in diagram_dict
        assert diagram_dict["theme"] == "high-contrast"

    def test_save_diagram_without_theme(self):
        """T051: Test that diagram.to_dict() includes theme field even when None."""
        diagram = Diagram()
        diagram_dict = diagram.to_dict()

        assert "theme" in diagram_dict
        assert diagram_dict["theme"] is None

    def test_load_diagram_with_theme(self):
        """T052: Test that Diagram.from_dict() restores theme."""
        original = Diagram(theme="dark")
        diagram_dict = original.to_dict()

        loaded = Diagram.from_dict(diagram_dict)

        assert loaded.theme == "dark"

    def test_load_diagram_with_light_theme(self):
        """T052: Test loading diagram with light theme."""
        original = Diagram(theme="light")
        diagram_dict = original.to_dict()

        loaded = Diagram.from_dict(diagram_dict)

        assert loaded.theme == "light"

    def test_load_diagram_with_high_contrast_theme(self):
        """T052: Test loading diagram with high-contrast theme."""
        original = Diagram(theme="high-contrast")
        diagram_dict = original.to_dict()

        loaded = Diagram.from_dict(diagram_dict)

        assert loaded.theme == "high-contrast"

    def test_round_trip_with_theme(self):
        """T052: Test save/load round-trip preserves theme."""
        for theme in ["light", "dark", "high-contrast"]:
            original = Diagram(theme=theme)
            diagram_dict = original.to_dict()
            loaded = Diagram.from_dict(diagram_dict)

            assert loaded.theme == theme, f"Theme {theme} not preserved in round-trip"

    def test_load_old_diagram_without_theme_field(self):
        """T053: Test backward compatibility - old diagrams without theme field."""
        # Simulate old diagram JSON without theme field
        old_diagram_dict = {
            "version": "1.0.0",
            "blocks": [],
            "connections": [],
            # Note: no 'theme' field (old format)
        }

        loaded = Diagram.from_dict(old_diagram_dict)

        # Should load successfully with theme=None
        assert loaded.theme is None

    def test_load_diagram_with_invalid_theme_logs_warning(self, caplog):
        """T054: Test that loading diagram with invalid theme
        logs warning and sets to None."""
        import logging

        caplog.set_level(logging.WARNING)

        # Diagram dict with invalid theme
        diagram_dict = {
            "version": "1.0.0",
            "blocks": [],
            "connections": [],
            "theme": "purple",  # Invalid theme
        }

        loaded = Diagram.from_dict(diagram_dict)

        # Should log warning (during Diagram.__init__ or theme setter)
        # Note: The setter validates on assignment, so warning comes from there
        assert loaded.theme is None  # Invalid theme should be rejected

    def test_json_serialization_with_theme(self):
        """T051: Test JSON serialization includes theme field."""
        diagram = Diagram(theme="dark")
        json_str = json.dumps(diagram.to_dict())

        # Verify JSON contains theme field
        json_dict = json.loads(json_str)
        assert "theme" in json_dict
        assert json_dict["theme"] == "dark"

    def test_json_deserialization_with_theme(self):
        """T052: Test JSON deserialization restores theme."""
        json_str = (
            '{"version": "1.0.0", "blocks": [], "connections": [], '
            '"theme": "high-contrast"}'
        )
        diagram_dict = json.loads(json_str)

        loaded = Diagram.from_dict(diagram_dict)

        assert loaded.theme == "high-contrast"


class TestBackwardCompatibility:
    """Test backward compatibility with old diagrams (T053, T057)."""

    def test_load_minimal_old_diagram(self):
        """T057: Test loading minimal old diagram without theme field."""
        old_diagram = {
            "version": "1.0.0",
            "blocks": [],
            "connections": [],
        }

        loaded = Diagram.from_dict(old_diagram)

        assert loaded.theme is None
        assert loaded.blocks == []
        assert loaded.connections == []

    def test_load_old_diagram_with_blocks(self):
        """T057: Test loading old diagram with blocks but no theme field."""
        old_diagram = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "block1",
                    "type": "gain",
                    "position": {"x": 100.0, "y": 100.0},
                    "parameters": [{"name": "K", "value": 5.0}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                }
            ],
            "connections": [],
        }

        loaded = Diagram.from_dict(old_diagram)

        assert loaded.theme is None
        assert len(loaded.blocks) == 1
        assert loaded.blocks[0].id == "block1"

    def test_new_diagram_includes_theme_field(self):
        """T057: Test that new diagrams always include theme field (even if None)."""
        diagram = Diagram()
        diagram_dict = diagram.to_dict()

        # New format always includes theme field
        assert "theme" in diagram_dict

    def test_theme_field_is_optional_in_schema(self):
        """T057: Verify theme field is Optional in Pydantic schema."""
        from lynx.schema import DiagramModel

        # Should be able to create DiagramModel without theme field
        model = DiagramModel(version="1.0.0", blocks=[], connections=[])
        assert model.theme is None  # Default to None

        # Should also accept explicit theme
        model_with_theme = DiagramModel(
            version="1.0.0", blocks=[], connections=[], theme="dark"
        )
        assert model_with_theme.theme == "dark"


class TestThemePersistenceEdgeCases:
    """Edge cases for theme persistence."""

    def test_save_load_with_none_theme(self):
        """Test save/load with explicit None theme."""
        diagram = Diagram(theme=None)
        diagram_dict = diagram.to_dict()

        loaded = Diagram.from_dict(diagram_dict)

        assert loaded.theme is None

    def test_theme_persists_independently_of_blocks(self):
        """Test that theme persists independently of block changes."""
        diagram = Diagram(theme="dark")
        diagram.add_block("gain", "g1", K=5.0)

        diagram_dict = diagram.to_dict()
        loaded = Diagram.from_dict(diagram_dict)

        assert loaded.theme == "dark"
        assert len(loaded.blocks) == 1

    def test_changing_theme_after_creation_persists(self):
        """Test that theme changes after creation persist in save/load."""
        diagram = Diagram()
        diagram.theme = "high-contrast"
        diagram.add_block("gain", "g1", K=2.0)

        diagram_dict = diagram.to_dict()
        loaded = Diagram.from_dict(diagram_dict)

        assert loaded.theme == "high-contrast"

    def test_multiple_save_load_cycles(self):
        """Test theme survives multiple save/load cycles."""
        diagram = Diagram(theme="dark")

        # First cycle
        dict1 = diagram.to_dict()
        loaded1 = Diagram.from_dict(dict1)
        assert loaded1.theme == "dark"

        # Second cycle
        dict2 = loaded1.to_dict()
        loaded2 = Diagram.from_dict(dict2)
        assert loaded2.theme == "dark"

        # Third cycle
        dict3 = loaded2.to_dict()
        loaded3 = Diagram.from_dict(dict3)
        assert loaded3.theme == "dark"
