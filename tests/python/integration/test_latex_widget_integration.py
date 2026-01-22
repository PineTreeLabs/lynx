# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for custom LaTeX rendering feature.

These tests verify the custom_latex parameter integration between Python API
and the widget UI, including persistence across save/load cycles.

Tests cover:
- Setting custom_latex via Python API
- Custom LaTeX persistence in diagram save/load
- UI reflection of Python API changes
"""

import json

from lynx.widget import LynxWidget


class TestCustomLatexPythonAPI:
    """Test custom LaTeX via Python API - T047."""

    def test_set_custom_latex_via_python_api_gain(self):
        """Test setting custom LaTeX on Gain block via Python API."""
        widget = LynxWidget()

        # Add gain block
        widget.diagram.add_block("gain", "g1", position={"x": 100, "y": 100}, K=2.5)
        widget.update()

        # Set custom LaTeX via Python API
        block = widget.diagram.blocks[0]
        block.custom_latex = r"K = 2.5"
        widget.update()

        # Verify custom_latex appears in diagram_state
        block_state = next(
            (b for b in widget.diagram_state["blocks"] if b["id"] == block.id), None
        )
        assert block_state is not None, "Block not found in diagram_state"

        # Verify custom_latex at block level (not in parameters)
        assert block_state["custom_latex"] == r"K = 2.5"

    def test_set_custom_latex_via_python_api_transfer_function(self):
        """Test setting custom LaTeX on TransferFunction block via Python API."""
        widget = LynxWidget()

        # Add transfer function block
        widget.diagram.add_block(
            "transfer_function",
            "tf1",
            position={"x": 100, "y": 100},
            numerator=[1],
            denominator=[1, 1],
        )
        widget.update()

        # Set custom LaTeX via Python API
        block = widget.diagram.blocks[0]
        block.custom_latex = r"G(s) = \frac{1}{s+1}"
        widget.update()

        # Verify custom_latex appears in diagram_state
        block_state = next(
            (b for b in widget.diagram_state["blocks"] if b["id"] == block.id), None
        )
        assert block_state is not None

        # Verify custom_latex at block level (not in parameters)
        assert block_state["custom_latex"] == r"G(s) = \frac{1}{s+1}"

    def test_set_custom_latex_via_python_api_state_space(self):
        """Test setting custom LaTeX on StateSpace block via Python API."""
        widget = LynxWidget()

        # Add state space block
        widget.diagram.add_block(
            "state_space",
            "ss1",
            position={"x": 100, "y": 100},
            A=[[1]],
            B=[[1]],
            C=[[1]],
            D=[[0]],
        )
        widget.update()

        # Set custom LaTeX via Python API
        block = widget.diagram.blocks[0]
        block.custom_latex = r"\dot{x} = x + u"
        widget.update()

        # Verify custom_latex appears in diagram_state
        block_state = next(
            (b for b in widget.diagram_state["blocks"] if b["id"] == block.id), None
        )
        assert block_state is not None

        # Verify custom_latex at block level (not in parameters)
        assert block_state["custom_latex"] == r"\dot{x} = x + u"

    def test_clear_custom_latex_via_python_api(self):
        """Test clearing custom LaTeX by setting to None."""
        widget = LynxWidget()

        # Add block with custom LaTeX
        widget.diagram.add_block("gain", "g1", position={"x": 100, "y": 100}, K=2.5)
        widget.update()

        block = widget.diagram.blocks[0]
        block.custom_latex = r"K = 2.5"
        widget.update()

        # Clear custom LaTeX
        block.custom_latex = None
        widget.update()

        # Verify custom_latex is None or not present
        block_state = next(
            (b for b in widget.diagram_state["blocks"] if b["id"] == block.id), None
        )
        assert block_state is not None

        custom_latex_param = next(
            (p for p in block_state["parameters"] if p["name"] == "custom_latex"),
            None,
        )

        # Either parameter doesn't exist or value is None
        if custom_latex_param:
            assert custom_latex_param["value"] is None


class TestCustomLatexPersistence:
    """Test custom LaTeX persistence in save/load - T048."""

    def test_custom_latex_persists_in_diagram_json(self):
        """Test that custom LaTeX is included in diagram JSON."""
        widget = LynxWidget()

        # Add block with custom LaTeX
        widget.diagram.add_block("gain", "g1", position={"x": 100, "y": 100}, K=2.5)
        widget.update()

        block = widget.diagram.blocks[0]
        block.custom_latex = r"K = 2.5"
        widget.update()

        # Get diagram state (which is serialized to JSON)
        diagram_dict = widget.diagram_state

        # Verify custom_latex in state
        block_data = diagram_dict["blocks"][0]
        assert block_data["custom_latex"] == r"K = 2.5"

    def test_custom_latex_restores_from_json(self):
        """Test that custom LaTeX is restored when loading from JSON."""
        # Create diagram with custom LaTeX
        widget1 = LynxWidget()
        widget1.diagram.add_block("gain", "g1", position={"x": 100, "y": 100}, K=2.5)
        widget1.update()

        block = widget1.diagram.blocks[0]
        block.custom_latex = r"K = 2.5"
        widget1.update()

        # Get diagram state
        diagram_dict = widget1.diagram_state
        state_json = json.dumps(diagram_dict)

        # Load into new widget by setting diagram_state
        widget2 = LynxWidget()
        widget2.diagram_state = json.loads(state_json)

        # Verify custom LaTeX restored in diagram_state
        block_state = widget2.diagram_state["blocks"][0]
        assert block_state["custom_latex"] == r"K = 2.5"

    def test_diagram_without_custom_latex_loads_correctly(self):
        """Test backward compatibility - diagrams without custom_latex load fine."""
        # Create diagram without custom LaTeX (using default rendering)
        widget1 = LynxWidget()
        widget1.diagram.add_block("gain", "g1", position={"x": 100, "y": 100}, K=2.5)
        widget1.update()

        # Get diagram state
        diagram_dict = widget1.diagram_state
        state_json = json.dumps(diagram_dict)

        # Load into new widget
        widget2 = LynxWidget()
        widget2.diagram_state = json.loads(state_json)

        # Should work fine - custom_latex will be None
        assert len(widget2.diagram_state["blocks"]) == 1
        block_state = widget2.diagram_state["blocks"][0]
        assert block_state.get("custom_latex") is None
