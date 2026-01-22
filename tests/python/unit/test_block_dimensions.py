# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for block dimension functionality.

Tests dimension storage, serialization, and diagram update methods.
"""

from lynx.blocks.gain import GainBlock
from lynx.diagram import Diagram


class TestBlockDimensions:
    """Test block dimension attributes."""

    def test_block_has_dimension_attributes(self):
        """Test that blocks have width and height attributes."""
        block = GainBlock(id="g1", K=2.0)
        assert hasattr(block, "width")
        assert hasattr(block, "height")

    def test_block_dimensions_default_to_none(self):
        """Test that dimension attributes default to None."""
        block = GainBlock(id="g1", K=2.0)
        assert block.width is None
        assert block.height is None

    def test_block_dimensions_can_be_set(self):
        """Test that dimension attributes can be set."""
        block = GainBlock(id="g1", K=2.0)
        block.width = 150.0
        block.height = 100.0
        assert block.width == 150.0
        assert block.height == 100.0

    def test_block_to_dict_excludes_none_dimensions(self):
        """Test that None dimensions are not included in serialization."""
        block = GainBlock(id="g1", K=2.0)
        data = block.to_dict()
        assert "width" not in data
        assert "height" not in data

    def test_block_to_dict_includes_set_dimensions(self):
        """Test that set dimensions are included in serialization."""
        block = GainBlock(id="g1", K=2.0)
        block.width = 150.0
        block.height = 100.0
        data = block.to_dict()
        assert data["width"] == 150.0
        assert data["height"] == 100.0


class TestDiagramUpdateDimensions:
    """Test Diagram.update_block_dimensions() method."""

    def test_update_dimensions_success(self):
        """Test updating block dimensions."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.0)

        result = diagram.update_block_dimensions("g1", 150.0, 100.0)

        assert result is True
        block = diagram.get_block("g1")
        assert block.width == 150.0
        assert block.height == 100.0

    def test_update_dimensions_nonexistent_block(self):
        """Test updating dimensions of nonexistent block returns False."""
        diagram = Diagram()

        result = diagram.update_block_dimensions("nonexistent", 100.0, 50.0)

        assert result is False

    def test_update_dimensions_clears_waypoints(self):
        """Test that updating dimensions clears connection waypoints."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.0)
        diagram.add_block("gain", "g2", K=3.0)
        diagram.add_connection("c1", "g1", "out", "g2", "in")

        # Manually add waypoints to the connection
        conn = diagram.connections[0]
        conn.waypoints = [{"x": 100, "y": 50}, {"x": 150, "y": 50}]
        assert len(conn.waypoints) == 2

        # Update dimensions should clear waypoints
        diagram.update_block_dimensions("g1", 150.0, 100.0)

        assert len(conn.waypoints) == 0

    def test_update_dimensions_supports_undo(self):
        """Test that update_dimensions supports undo."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.0)

        # Set initial dimensions
        diagram.update_block_dimensions("g1", 150.0, 100.0)

        # Update to new dimensions
        diagram.update_block_dimensions("g1", 200.0, 120.0)
        assert diagram.get_block("g1").width == 200.0

        # Undo should restore previous dimensions
        diagram.undo()
        assert diagram.get_block("g1").width == 150.0


class TestDimensionSerialization:
    """Test dimension serialization and deserialization."""

    def test_diagram_to_dict_includes_dimensions(self):
        """Test that diagram serialization includes block dimensions."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.0)
        diagram.get_block("g1").width = 150.0
        diagram.get_block("g1").height = 100.0

        data = diagram.to_dict()

        block_data = data["blocks"][0]
        assert block_data["width"] == 150.0
        assert block_data["height"] == 100.0

    def test_diagram_from_dict_loads_dimensions(self):
        """Test that diagram deserialization loads block dimensions."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 100},
                    "label": "g1",
                    "flipped": False,
                    "label_visible": False,
                    "width": 150.0,
                    "height": 100.0,
                    "parameters": [{"name": "K", "value": 2.0}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                }
            ],
            "connections": [],
        }

        diagram = Diagram.from_dict(data)

        block = diagram.get_block("g1")
        assert block.width == 150.0
        assert block.height == 100.0

    def test_backward_compatibility_no_dimensions(self):
        """Test loading diagrams without dimension fields."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 100},
                    "label": "g1",
                    "flipped": False,
                    "label_visible": False,
                    "parameters": [{"name": "K", "value": 2.0}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                }
            ],
            "connections": [],
        }

        diagram = Diagram.from_dict(data)

        block = diagram.get_block("g1")
        # Dimensions should be None (not set) for backward compatibility
        assert block.width is None
        assert block.height is None
