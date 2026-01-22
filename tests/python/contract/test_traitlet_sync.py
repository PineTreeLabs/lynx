# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Contract tests for traitlet synchronization

Testing the contract between Python backend and JavaScript frontend:
- diagram_state traitlet sync
- Python → JavaScript state flow
"""

from lynx.widget import LynxWidget


class TestDiagramStateSync:
    """Test diagram_state traitlet synchronization"""

    def test_widget_has_diagram_state_traitlet(self) -> None:
        """Widget exposes diagram_state traitlet for sync"""
        widget = LynxWidget()

        assert hasattr(widget, "diagram_state")
        assert isinstance(widget.diagram_state, dict)

    def test_diagram_state_includes_blocks(self) -> None:
        """diagram_state contains blocks array"""
        widget = LynxWidget()

        state = widget.diagram_state

        assert "blocks" in state
        assert isinstance(state["blocks"], list)

    def test_diagram_state_includes_connections(self) -> None:
        """diagram_state contains connections array"""
        widget = LynxWidget()

        state = widget.diagram_state

        assert "connections" in state
        assert isinstance(state["connections"], list)

    def test_diagram_state_includes_version(self) -> None:
        """diagram_state includes schema version"""
        widget = LynxWidget()

        state = widget.diagram_state

        assert "version" in state
        assert isinstance(state["version"], str)

    def test_adding_block_updates_diagram_state(self) -> None:
        """When block is added to diagram, diagram_state updates"""
        widget = LynxWidget()

        # Initially empty
        assert len(widget.diagram_state["blocks"]) == 0

        # Add a gain block via internal API
        widget.diagram.add_block(
            "gain", id="gain1", K=5.0, position={"x": 100, "y": 200}
        )
        widget.update()  # Sync state to traitlet

        # diagram_state should reflect the change
        state = widget.diagram_state
        assert len(state["blocks"]) == 1
        assert state["blocks"][0]["id"] == "gain1"
        assert state["blocks"][0]["type"] == "gain"

    def test_diagram_state_serializes_block_parameters(self) -> None:
        """diagram_state includes block parameters"""
        widget = LynxWidget()

        widget.diagram.add_block("gain", id="gain1", K=2.5, position={"x": 0, "y": 0})
        widget.update()  # Sync state to traitlet

        state = widget.diagram_state
        block_data = state["blocks"][0]

        assert "parameters" in block_data
        assert len(block_data["parameters"]) == 1
        assert block_data["parameters"][0]["name"] == "K"
        assert block_data["parameters"][0]["value"] == 2.5

    def test_diagram_state_serializes_block_ports(self) -> None:
        """diagram_state includes block ports"""
        widget = LynxWidget()

        widget.diagram.add_block("gain", id="gain1", K=1.0, position={"x": 0, "y": 0})
        widget.update()  # Sync state to traitlet

        state = widget.diagram_state
        block_data = state["blocks"][0]

        assert "ports" in block_data
        assert len(block_data["ports"]) == 2  # Gain has 1 input + 1 output


class TestActionTraitlet:
    """Test _action traitlet for JavaScript → Python commands"""

    def test_widget_has_action_traitlet(self) -> None:
        """Widget exposes _action traitlet for commands"""
        widget = LynxWidget()

        assert hasattr(widget, "_action")

    def test_add_block_action_creates_block(self) -> None:
        """addBlock action via _action traitlet creates block in diagram"""
        widget = LynxWidget()

        # Simulate JavaScript sending addBlock action
        widget._action = {
            "type": "addBlock",
            "payload": {
                "blockType": "gain",
                "id": "gain1",
                "K": 3.0,
                "position": {"x": 150, "y": 250},
            },
            "timestamp": 1234567890,
        }

        # Block should be added to diagram
        assert len(widget.diagram.blocks) == 1
        assert widget.diagram.blocks[0].id == "gain1"

    def test_action_updates_diagram_state(self) -> None:
        """Actions automatically update diagram_state traitlet"""
        widget = LynxWidget()

        widget._action = {
            "type": "addBlock",
            "payload": {
                "blockType": "gain",
                "id": "gain2",
                "K": 1.5,
                "position": {"x": 50, "y": 100},
            },
            "timestamp": 1234567891,
        }

        # diagram_state should automatically update
        state = widget.diagram_state
        assert len(state["blocks"]) == 1
        assert state["blocks"][0]["id"] == "gain2"
