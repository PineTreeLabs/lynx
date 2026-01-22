# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for LynxWidget - Python ↔ JavaScript communication.

These tests verify the widget's traitlet synchronization, action handling,
and integration between the Python backend and UI layer.

Tests cover:
- Widget initialization and state sync
- Block/connection operations via Python API
- Block/connection operations via UI actions (_action traitlet)
- Expression evaluation with notebook namespace
- Validation triggering
- Save/load workflow
"""

import json
from unittest.mock import MagicMock, patch

import numpy as np

from lynx.widget import LynxWidget


class TestWidgetInitialization:
    """Test widget creation and initial state synchronization."""

    def test_widget_creates_empty_diagram(self):
        """Test that new widget initializes with empty diagram."""
        widget = LynxWidget()

        # Check diagram_state is initialized
        assert "blocks" in widget.diagram_state
        assert "connections" in widget.diagram_state
        assert len(widget.diagram_state["blocks"]) == 0
        assert len(widget.diagram_state["connections"]) == 0

    def test_widget_syncs_diagram_state_on_init(self):
        """Test that diagram_state traitlet reflects initial diagram."""
        widget = LynxWidget()

        # Internal diagram should match traitlet (excluding _version timestamp)
        state_without_version = {
            k: v for k, v in widget.diagram_state.items() if k != "_version"
        }
        diagram_dict = widget.diagram.to_dict()
        assert state_without_version == diagram_dict


class TestPythonAPIOperations:
    """Test operations via Python API (widget.diagram.* + widget.update())."""

    def test_add_block_via_python_api(self):
        """Test adding block via Python API updates diagram_state."""
        widget = LynxWidget()

        # Add block via Python API
        widget.diagram.add_block("gain", "g1", position={"x": 100, "y": 200}, K=2.5)
        widget.update()  # Sync to JavaScript

        # Check diagram_state was updated
        assert len(widget.diagram_state["blocks"]) == 1
        block = widget.diagram_state["blocks"][0]
        assert block["id"] == "g1"
        assert block["type"] == "gain"
        assert block["position"] == {"x": 100, "y": 200}

        # Check parameters
        params = {p["name"]: p["value"] for p in block["parameters"]}
        assert params["K"] == 2.5

    def test_add_connection_via_python_api(self):
        """Test adding connection via Python API updates diagram_state."""
        widget = LynxWidget()

        # Create two blocks
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.diagram.add_block("gain", "g2", K=2.0)

        # Add connection
        widget.diagram.add_connection("c1", "g1", "out", "g2", "in")
        widget.update()

        # Check diagram_state has connection
        assert len(widget.diagram_state["connections"]) == 1
        conn = widget.diagram_state["connections"][0]
        assert conn["id"] == "c1"
        assert conn["source_block_id"] == "g1"
        assert conn["target_block_id"] == "g2"

    def test_python_api_triggers_validation(self):
        """Test that widget.update() triggers validation."""
        widget = LynxWidget()

        # Add block without I/O markers
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.update()

        # Should have validation warning about missing I/O markers
        assert "warnings" in widget.validation_result
        warnings = widget.validation_result["warnings"]
        assert any("input" in w.lower() or "output" in w.lower() for w in warnings)


class TestUIActionHandling:
    """Test operations via UI actions (_action traitlet)."""

    def test_add_block_via_ui_action(self):
        """Test addBlock action from UI updates diagram."""
        widget = LynxWidget()

        # Simulate UI action
        action = {
            "type": "addBlock",
            "timestamp": 1000.0,
            "payload": {
                "blockType": "gain",
                "id": "g1",
                "position": {"x": 50, "y": 100},
                "K": 3.0,
            },
        }

        widget._action = action

        # Check block was added
        assert len(widget.diagram_state["blocks"]) == 1
        assert widget.diagram_state["blocks"][0]["id"] == "g1"

    def test_delete_block_via_ui_action(self):
        """Test deleteBlock action from UI removes block."""
        widget = LynxWidget()

        # Add block first
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.update()

        # Delete via UI action
        action = {
            "type": "deleteBlock",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1"},
        }

        widget._action = action

        # Block should be removed
        assert len(widget.diagram_state["blocks"]) == 0

    def test_delete_block_cascades_connections(self):
        """Test deleting block via UI removes connected edges."""
        widget = LynxWidget()

        # Create blocks and connection
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.diagram.add_block("gain", "g2", K=2.0)
        widget.diagram.add_connection("c1", "g1", "out", "g2", "in")
        widget.update()

        # Delete source block via UI
        action = {
            "type": "deleteBlock",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1"},
        }

        widget._action = action

        # Connection should be removed (cascading deletion)
        assert len(widget.diagram_state["connections"]) == 0

    def test_add_connection_via_ui_action(self):
        """Test addConnection action from UI creates connection."""
        widget = LynxWidget()

        # Create blocks
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.diagram.add_block("gain", "g2", K=2.0)
        widget.update()

        # Add connection via UI
        action = {
            "type": "addConnection",
            "timestamp": 1000.0,
            "payload": {
                "connectionId": "c1",
                "sourceBlockId": "g1",
                "sourcePortId": "out",
                "targetBlockId": "g2",
                "targetPortId": "in",
            },
        }

        widget._action = action

        # Connection should exist
        assert len(widget.diagram_state["connections"]) == 1

    def test_move_block_via_ui_action(self):
        """Test moveBlock action updates block position."""
        widget = LynxWidget()

        # Add block
        widget.diagram.add_block("gain", "g1", position={"x": 0, "y": 0}, K=1.0)
        widget.update()

        # Move via UI action
        action = {
            "type": "moveBlock",
            "timestamp": 1000.0,
            "payload": {
                "blockId": "g1",
                "position": {"x": 150, "y": 250},
            },
        }

        widget._action = action

        # Position should be updated
        block = widget.diagram_state["blocks"][0]
        assert block["position"] == {"x": 150, "y": 250}

    def test_duplicate_action_ignored(self):
        """Test that duplicate actions (same timestamp) are ignored."""
        widget = LynxWidget()

        # First action
        action = {
            "type": "addBlock",
            "timestamp": 1000.0,
            "payload": {
                "blockType": "gain",
                "id": "g1",
                "position": {"x": 0, "y": 0},
                "K": 1.0,
            },
        }
        widget._action = action
        assert len(widget.diagram_state["blocks"]) == 1

        # Duplicate action (same timestamp)
        action2 = {
            "type": "addBlock",
            "timestamp": 1000.0,  # Same timestamp
            "payload": {
                "blockType": "gain",
                "id": "g2",
                "position": {"x": 100, "y": 100},
                "K": 2.0,
            },
        }
        widget._action = action2

        # Second block should NOT be added (duplicate filtered)
        assert len(widget.diagram_state["blocks"]) == 1


class TestExpressionEvaluation:
    """Test parameter updates with expression evaluation."""

    @patch("IPython.get_ipython")
    def test_update_parameter_with_expression_success(self, mock_get_ipython):
        """Test parameter update with valid expression evaluates correctly."""
        # Mock notebook namespace
        mock_ipython = MagicMock()
        mock_ipython.user_ns = {"A_matrix": [[1, 0], [0, 1]]}
        mock_get_ipython.return_value = mock_ipython

        widget = LynxWidget()

        # Add state space block
        widget.diagram.add_block(
            "state_space", "ss1", A=[[0, 0], [0, 0]], B=[[0], [0]], C=[[0, 0]], D=[[0]]
        )
        widget.update()

        # Update A parameter with expression
        action = {
            "type": "updateParameter",
            "timestamp": 1000.0,
            "payload": {
                "blockId": "ss1",
                "parameterName": "A",
                "value": "A_matrix",  # Expression
            },
        }

        widget._action = action

        # Check parameter was evaluated
        block = widget.diagram.get_block("ss1")
        a_param = next(p for p in block._parameters if p.name == "A")
        assert a_param.value == [[1, 0], [0, 1]]
        assert a_param.expression == "A_matrix"

    @patch("IPython.get_ipython")
    def test_update_parameter_with_invalid_expression_shows_error(
        self, mock_get_ipython
    ):
        """Test parameter update with invalid expression shows validation error."""
        # Mock notebook namespace (no A_matrix defined)
        mock_ipython = MagicMock()
        mock_ipython.user_ns = {}
        mock_get_ipython.return_value = mock_ipython

        widget = LynxWidget()

        # Add state space block
        widget.diagram.add_block(
            "state_space", "ss1", A=[[1, 0], [0, 1]], B=[[0], [0]], C=[[0, 0]], D=[[0]]
        )
        widget.update()

        # Update A parameter with undefined expression
        action = {
            "type": "updateParameter",
            "timestamp": 1000.0,
            "payload": {
                "blockId": "ss1",
                "parameterName": "A",
                "value": "undefined_var",
            },
        }

        widget._action = action

        # Should have validation warning (fallback used)
        assert (
            not widget.validation_result["is_valid"]
            or len(widget.validation_result["warnings"]) > 0
        )

    @patch("IPython.get_ipython")
    def test_update_gain_parameter_with_scalar_expression(self, mock_get_ipython):
        """Test gain parameter update with scalar expression."""
        # Mock notebook namespace
        mock_ipython = MagicMock()
        mock_ipython.user_ns = {"gain_value": 5.5}
        mock_get_ipython.return_value = mock_ipython

        widget = LynxWidget()

        # Add gain block
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.update()

        # Update K with expression
        action = {
            "type": "updateParameter",
            "timestamp": 1000.0,
            "payload": {
                "blockId": "g1",
                "parameterName": "K",
                "value": "gain_value",
            },
        }

        widget._action = action

        # Check parameter
        block = widget.diagram.get_block("g1")
        k_param = next(p for p in block._parameters if p.name == "K")
        assert k_param.value == 5.5
        assert k_param.expression == "gain_value"


class TestValidationIntegration:
    """Test validation triggering and error reporting."""

    def test_algebraic_loop_detected(self):
        """Test that algebraic loops are detected and reported."""
        widget = LynxWidget()

        # Create algebraic loop: g1 -> g2 -> g1
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.diagram.add_block("gain", "g2", K=2.0)
        widget.diagram.add_connection("c1", "g1", "out", "g2", "in")
        widget.diagram.add_connection("c2", "g2", "out", "g1", "in")
        widget.update()

        # Should have algebraic loop error
        assert not widget.validation_result["is_valid"]
        errors = widget.validation_result["errors"]
        assert any("algebraic loop" in e.lower() for e in errors)

    def test_disconnected_block_warning(self):
        """Test that incomplete systems trigger warnings."""
        widget = LynxWidget()

        # Add block without I/O markers (incomplete system)
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.update()

        # Should have warning about missing I/O markers
        warnings = widget.validation_result["warnings"]
        assert any("input" in w.lower() or "output" in w.lower() for w in warnings)

    def test_invalid_connection_rejected(self):
        """Test that invalid connections are rejected with error."""
        widget = LynxWidget()

        # Create blocks
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.diagram.add_block("gain", "g2", K=2.0)

        # Try to create connection with duplicate target (not allowed)
        widget.diagram.add_connection("c1", "g1", "out", "g2", "in")
        widget.update()

        # Try to add second connection to same input
        action = {
            "type": "addConnection",
            "timestamp": 1000.0,
            "payload": {
                "connectionId": "c2",
                "sourceBlockId": "g1",
                "sourcePortId": "out",
                "targetBlockId": "g2",
                "targetPortId": "in",  # Already connected
            },
        }

        widget._action = action

        # Should have validation error
        assert not widget.validation_result["is_valid"]


class TestSaveLoadWorkflow:
    """Test diagram persistence via widget interface."""

    def test_save_and_load_diagram(self, tmp_path):
        """Test save/load workflow preserves diagram state."""
        # Create widget with diagram
        widget1 = LynxWidget()
        widget1.diagram.add_block("gain", "g1", position={"x": 100, "y": 200}, K=2.5)
        widget1.diagram.add_block(
            "state_space", "ss1", A=[[1, 0], [0, 1]], B=[[1], [0]], C=[[1, 0]], D=[[0]]
        )
        widget1.diagram.add_connection("c1", "g1", "out", "ss1", "in")
        widget1.update()

        # Save to file
        filepath = tmp_path / "test_widget.json"
        widget1._save_request = str(filepath)

        # Create new widget and load
        widget2 = LynxWidget()
        widget2._load_request = str(filepath)

        # Verify state matches
        assert len(widget2.diagram_state["blocks"]) == 2
        assert len(widget2.diagram_state["connections"]) == 1

        # Check block details
        g1 = next(b for b in widget2.diagram_state["blocks"] if b["id"] == "g1")
        assert g1["position"] == {"x": 100, "y": 200}

    def test_save_preserves_expressions(self, tmp_path):
        """Test that save/load preserves parameter expressions."""
        widget1 = LynxWidget()

        # Add block with expression
        block = widget1.diagram.add_block(
            "state_space", "ss1", A="A_matrix", B="B_matrix", C="C_matrix", D="D_matrix"
        )

        # Set hybrid storage (expression + value)
        for param in block._parameters:
            if param.name == "A":
                param.expression = "A_matrix"
                param.value = [[1, 0], [0, 1]]

        widget1.update()

        # Save
        filepath = tmp_path / "expr_test.json"
        widget1._save_request = str(filepath)

        # Load
        widget2 = LynxWidget()
        widget2._load_request = str(filepath)

        # Check expression preserved
        block2 = widget2.diagram.get_block("ss1")
        a_param = next(p for p in block2._parameters if p.name == "A")
        assert a_param.expression == "A_matrix"
        assert a_param.value == [[1, 0], [0, 1]]


class TestNumPyIntegration:
    """Test NumPy array handling in widget operations."""

    def test_add_block_with_numpy_arrays(self):
        """Test adding blocks with NumPy arrays works correctly."""
        widget = LynxWidget()

        # Create with NumPy arrays
        A = np.array([[0, 1], [-1, -2]])
        B = np.array([[0], [1]])
        C = np.array([[1, 0]])
        D = np.array([[0]])

        widget.diagram.add_block("state_space", "ss1", A=A, B=B, C=C, D=D)
        widget.update()

        # Should serialize to JSON successfully
        state_json = json.dumps(widget.diagram_state)
        assert isinstance(state_json, str)

        # Deserialize and verify
        loaded_state = json.loads(state_json)
        ss1 = next(b for b in loaded_state["blocks"] if b["id"] == "ss1")
        params = {p["name"]: p["value"] for p in ss1["parameters"]}

        # Should match original (as lists)
        assert np.array_equal(params["A"], A)
        assert np.array_equal(params["B"], B)


class TestConnectionOperations:
    """Test connection operations via UI actions."""

    def test_delete_connection_via_ui_action(self, widget_with_blocks):
        """Test deleteConnection action removes connection.

        Verifies:
        - deleteConnection action updates diagram_state
        - Connection removed from internal diagram
        - Validation runs after deletion
        """
        # widget_with_blocks has c1: g1.out -> g2.in
        initial_conn_count = len(widget_with_blocks.diagram_state["connections"])
        assert initial_conn_count == 1, (
            f"Expected 1 connection in fixture, got {initial_conn_count}"
        )

        # Delete connection via UI action
        action = {
            "type": "deleteConnection",
            "timestamp": 1000.0,
            "payload": {"connectionId": "c1"},
        }
        widget_with_blocks._action = action

        # Connection should be removed from diagram_state
        assert len(widget_with_blocks.diagram_state["connections"]) == 0, (
            "Expected 0 connections after deletion, "
            f"got {len(widget_with_blocks.diagram_state['connections'])}"
        )

        # Connection should be removed from internal diagram
        conn = next(
            (c for c in widget_with_blocks.diagram.connections if c.id == "c1"), None
        )
        assert conn is None, "Connection should not exist in internal diagram"


class TestBlockLabelOperations:
    """Test block label editing via UI actions."""

    def test_update_block_label_via_action(self, widget_with_blocks):
        """Test updateBlockLabel action changes block label.

        Verifies:
        - updateBlockLabel action updates diagram_state
        - Label persists in internal diagram
        """
        # Update label via UI action
        action = {
            "type": "updateBlockLabel",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1", "label": "Controller"},
        }
        widget_with_blocks._action = action

        # Check diagram_state updated
        block = next(
            b for b in widget_with_blocks.diagram_state["blocks"] if b["id"] == "g1"
        )
        assert block["label"] == "Controller", (
            f"Expected label 'Controller', got '{block['label']}'"
        )

        # Check internal diagram matches
        internal_block = widget_with_blocks.diagram.get_block("g1")
        assert internal_block.label == "Controller", (
            f"Expected internal label 'Controller', got '{internal_block.label}'"
        )

    def test_update_block_label_empty_reverts_to_id(self, widget_with_blocks):
        """Test empty label reverts to block ID.

        Verifies:
        - Setting label to empty string uses block ID as fallback
        """
        # Set label to empty string
        action = {
            "type": "updateBlockLabel",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1", "label": ""},
        }
        widget_with_blocks._action = action

        # Check label falls back to block ID
        internal_block = widget_with_blocks.diagram.get_block("g1")
        # Empty label should result in label being set to block ID
        assert internal_block.label == "g1", (
            f"Expected label to be block ID 'g1', got '{internal_block.label}'"
        )


class TestBlockTransformOperations:
    """Test block transformation operations (resize, flip, label visibility)."""

    def test_resize_block_via_action(self, widget_with_blocks):
        """Test resizeBlock action updates dimensions.

        Verifies:
        - resizeBlock action updates width/height
        - Dimensions persist in diagram_state
        """
        # Resize block via UI action
        action = {
            "type": "resizeBlock",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1", "width": 150, "height": 100},
        }
        widget_with_blocks._action = action

        # Check diagram_state updated
        block = next(
            b for b in widget_with_blocks.diagram_state["blocks"] if b["id"] == "g1"
        )
        assert block.get("width") == 150, (
            f"Expected width 150, got {block.get('width')}"
        )
        assert block.get("height") == 100, (
            f"Expected height 100, got {block.get('height')}"
        )

        # Check internal diagram matches
        internal_block = widget_with_blocks.diagram.get_block("g1")
        assert internal_block.width == 150, (
            f"Expected internal width 150, got {internal_block.width}"
        )
        assert internal_block.height == 100, (
            f"Expected internal height 100, got {internal_block.height}"
        )

    def test_resize_block_clears_waypoints(self, widget_with_blocks):
        """Test resizing clears connection waypoints.

        Verifies:
        - Resizing a block clears waypoints on connected edges
        """
        # First add waypoints to connection
        update_routing_action = {
            "type": "updateConnectionRouting",
            "timestamp": 1000.0,
            "payload": {
                "connectionId": "c1",
                "waypoints": [{"x": 150, "y": 100}, {"x": 200, "y": 150}],
            },
        }
        widget_with_blocks._action = update_routing_action

        # Verify waypoints were set
        conn = next(
            c
            for c in widget_with_blocks.diagram_state["connections"]
            if c["id"] == "c1"
        )
        assert len(conn.get("waypoints", [])) == 2, "Waypoints should be set"

        # Now resize the source block
        resize_action = {
            "type": "resizeBlock",
            "timestamp": 1001.0,
            "payload": {"blockId": "g1", "width": 180, "height": 120},
        }
        widget_with_blocks._action = resize_action

        # Waypoints should be cleared
        conn = next(
            c
            for c in widget_with_blocks.diagram_state["connections"]
            if c["id"] == "c1"
        )
        assert len(conn.get("waypoints", [])) == 0, (
            "Waypoints should be cleared after resize"
        )

    def test_flip_block_via_action(self, widget_with_blocks):
        """Test flipBlock action flips block horizontally.

        Verifies:
        - flipBlock action sets flipped attribute
        - Flipped state persists in diagram_state
        """
        # Flip block via UI action
        action = {
            "type": "flipBlock",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1"},
        }
        widget_with_blocks._action = action

        # Check diagram_state updated
        block = next(
            b for b in widget_with_blocks.diagram_state["blocks"] if b["id"] == "g1"
        )
        assert block.get("flipped") is True, (
            f"Expected flipped=True, got {block.get('flipped')}"
        )

        # Check internal diagram matches
        internal_block = widget_with_blocks.diagram.get_block("g1")
        assert internal_block.flipped is True, (
            f"Expected internal flipped=True, got {internal_block.flipped}"
        )

    def test_flip_block_preserves_connections(self, widget_with_blocks):
        """Test flipping doesn't break connections.

        Verifies:
        - Flipping a block maintains existing connections
        - Connection count unchanged after flip
        """
        # Verify initial connection exists
        initial_conn_count = len(widget_with_blocks.diagram_state["connections"])
        assert initial_conn_count == 1, "Should start with 1 connection"

        # Flip block
        action = {
            "type": "flipBlock",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1"},
        }
        widget_with_blocks._action = action

        # Connection should still exist
        assert len(widget_with_blocks.diagram_state["connections"]) == 1, (
            f"Expected 1 connection after flip, "
            f"got {len(widget_with_blocks.diagram_state['connections'])}"
        )

        # Connection should have same endpoints
        conn = widget_with_blocks.diagram_state["connections"][0]
        assert conn["source_block_id"] == "g1", (
            f"Expected source g1, got {conn['source_block_id']}"
        )
        assert conn["target_block_id"] == "g2", (
            f"Expected target g2, got {conn['target_block_id']}"
        )

    def test_toggle_label_visibility_via_action(self, widget_with_blocks):
        """Test toggleLabelVisibility action.

        Verifies:
        - toggleLabelVisibility action updates label_visible attribute
        """
        # Toggle label visibility
        action = {
            "type": "toggleLabelVisibility",
            "timestamp": 1000.0,
            "payload": {"blockId": "g1"},
        }
        widget_with_blocks._action = action

        # Check diagram_state updated
        block = next(
            b for b in widget_with_blocks.diagram_state["blocks"] if b["id"] == "g1"
        )
        # Should toggle to opposite of default (default is False)
        assert block.get("label_visible") is True, (
            f"Expected label_visible=True, got {block.get('label_visible')}"
        )

        # Check internal diagram matches
        internal_block = widget_with_blocks.diagram.get_block("g1")
        assert internal_block.label_visible is True, (
            f"Expected internal label_visible=True, got {internal_block.label_visible}"
        )


class TestConnectionRoutingOperations:
    """Test connection routing operations (waypoints)."""

    def test_update_connection_routing_via_action(self, widget_with_blocks):
        """Test updateConnectionRouting action sets waypoints.

        Verifies:
        - updateConnectionRouting action updates waypoints
        - Waypoints persist in diagram_state
        """
        # Set waypoints via UI action
        waypoints = [{"x": 150, "y": 100}, {"x": 200, "y": 150}, {"x": 250, "y": 100}]
        action = {
            "type": "updateConnectionRouting",
            "timestamp": 1000.0,
            "payload": {"connectionId": "c1", "waypoints": waypoints},
        }
        widget_with_blocks._action = action

        # Check diagram_state updated
        conn = next(
            c
            for c in widget_with_blocks.diagram_state["connections"]
            if c["id"] == "c1"
        )
        assert conn.get("waypoints") == waypoints, (
            f"Expected waypoints {waypoints}, got {conn.get('waypoints')}"
        )

        # Check internal diagram matches
        internal_conn = next(
            c for c in widget_with_blocks.diagram.connections if c.id == "c1"
        )
        assert internal_conn.waypoints == waypoints, (
            f"Expected internal waypoints {waypoints}, got {internal_conn.waypoints}"
        )

    def test_reset_connection_routing_via_action(self, widget_with_blocks):
        """Test resetConnectionRouting action clears waypoints.

        Verifies:
        - resetConnectionRouting action clears waypoints
        - Empty waypoints list in diagram_state
        """
        # First set waypoints
        set_action = {
            "type": "updateConnectionRouting",
            "timestamp": 1000.0,
            "payload": {
                "connectionId": "c1",
                "waypoints": [{"x": 150, "y": 100}],
            },
        }
        widget_with_blocks._action = set_action

        # Verify waypoints were set
        conn = next(
            c
            for c in widget_with_blocks.diagram_state["connections"]
            if c["id"] == "c1"
        )
        assert len(conn.get("waypoints", [])) > 0, "Waypoints should be set initially"

        # Reset waypoints
        reset_action = {
            "type": "resetConnectionRouting",
            "timestamp": 1001.0,
            "payload": {"connectionId": "c1"},
        }
        widget_with_blocks._action = reset_action

        # Check waypoints cleared
        conn = next(
            c
            for c in widget_with_blocks.diagram_state["connections"]
            if c["id"] == "c1"
        )
        assert len(conn.get("waypoints", [])) == 0, (
            f"Expected empty waypoints, got {conn.get('waypoints')}"
        )

        # Check internal diagram matches
        internal_conn = next(
            c for c in widget_with_blocks.diagram.connections if c.id == "c1"
        )
        assert len(internal_conn.waypoints) == 0, (
            f"Expected empty internal waypoints, got {internal_conn.waypoints}"
        )


class TestConnectionLabelOperations:
    """Test connection label operations."""

    def test_update_connection_label_via_action(self, widget_with_blocks):
        """Test updateConnectionLabel action.

        Verifies:
        - updateConnectionLabel action sets label
        - Label persists in diagram_state
        """
        # Set connection label via UI action
        action = {
            "type": "updateConnectionLabel",
            "timestamp": 1000.0,
            "payload": {"connectionId": "c1", "label": "signal_1"},
        }
        widget_with_blocks._action = action

        # Check diagram_state updated
        conn = next(
            c
            for c in widget_with_blocks.diagram_state["connections"]
            if c["id"] == "c1"
        )
        assert conn.get("label") == "signal_1", (
            f"Expected label 'signal_1', got {conn.get('label')}"
        )

        # Check internal diagram matches
        internal_conn = next(
            c for c in widget_with_blocks.diagram.connections if c.id == "c1"
        )
        assert internal_conn.label == "signal_1", (
            f"Expected internal label 'signal_1', got {internal_conn.label}"
        )

    def test_toggle_connection_label_visibility_via_action(self, widget_with_blocks):
        """Test toggleConnectionLabelVisibility action.

        Verifies:
        - toggleConnectionLabelVisibility action updates label_visible
        """
        # Toggle connection label visibility
        action = {
            "type": "toggleConnectionLabelVisibility",
            "timestamp": 1000.0,
            "payload": {"connectionId": "c1"},
        }
        widget_with_blocks._action = action

        # Check diagram_state updated
        conn = next(
            c
            for c in widget_with_blocks.diagram_state["connections"]
            if c["id"] == "c1"
        )
        # Should toggle to opposite of default (default is False)
        assert conn.get("label_visible") is True, (
            f"Expected label_visible=True, got {conn.get('label_visible')}"
        )

        # Check internal diagram matches
        internal_conn = next(
            c for c in widget_with_blocks.diagram.connections if c.id == "c1"
        )
        assert internal_conn.label_visible is True, (
            f"Expected internal label_visible=True, got {internal_conn.label_visible}"
        )


class TestUndoRedoOperations:
    """Test undo/redo operations."""

    def test_undo_via_action(self, widget):
        """Test undo action restores previous state.

        Verifies:
        - undo action reverts last operation
        - Block added then undone is removed
        """
        # Add block via action
        add_action = {
            "type": "addBlock",
            "timestamp": 1000.0,
            "payload": {
                "blockType": "gain",
                "id": "g1",
                "position": {"x": 100, "y": 100},
                "K": 2.0,
            },
        }
        widget._action = add_action

        # Verify block added
        assert len(widget.diagram_state["blocks"]) == 1, (
            "Block should be added before undo"
        )

        # Undo the addition
        undo_action = {
            "type": "undo",
            "timestamp": 1001.0,
            "payload": {},
        }
        widget._action = undo_action

        # Block should be removed
        assert len(widget.diagram_state["blocks"]) == 0, (
            f"Expected 0 blocks after undo, got {len(widget.diagram_state['blocks'])}"
        )

    def test_redo_via_action(self, widget):
        """Test redo action re-applies undone operation.

        Verifies:
        - redo action restores undone change
        - Block added, undone, then redone is present
        """
        # Add block
        add_action = {
            "type": "addBlock",
            "timestamp": 1000.0,
            "payload": {
                "blockType": "gain",
                "id": "g1",
                "position": {"x": 100, "y": 100},
                "K": 2.0,
            },
        }
        widget._action = add_action

        # Undo
        undo_action = {
            "type": "undo",
            "timestamp": 1001.0,
            "payload": {},
        }
        widget._action = undo_action

        # Verify block removed
        assert len(widget.diagram_state["blocks"]) == 0, (
            "Block should be removed by undo"
        )

        # Redo
        redo_action = {
            "type": "redo",
            "timestamp": 1002.0,
            "payload": {},
        }
        widget._action = redo_action

        # Block should be restored
        assert len(widget.diagram_state["blocks"]) == 1, (
            f"Expected 1 block after redo, got {len(widget.diagram_state['blocks'])}"
        )
        block = widget.diagram_state["blocks"][0]
        assert block["id"] == "g1", f"Expected block id 'g1', got {block['id']}"

    def test_undo_redo_sequence(self, widget):
        """Test multiple undo/redo operations.

        Verifies:
        - Multiple undos work correctly
        - Partial redo works correctly
        """
        # Add 3 blocks
        for i in range(1, 4):
            action = {
                "type": "addBlock",
                "timestamp": 1000.0 + i,
                "payload": {
                    "blockType": "gain",
                    "id": f"g{i}",
                    "position": {"x": 100 * i, "y": 100},
                    "K": float(i),
                },
            }
            widget._action = action

        # Verify all blocks added
        assert len(widget.diagram_state["blocks"]) == 3, "Should have 3 blocks"

        # Undo twice (remove g3, g2)
        for i in range(2):
            undo_action = {
                "type": "undo",
                "timestamp": 2000.0 + i,
                "payload": {},
            }
            widget._action = undo_action

        # Should have 1 block (g1)
        assert len(widget.diagram_state["blocks"]) == 1, (
            f"Expected 1 block after 2 undos, got {len(widget.diagram_state['blocks'])}"
        )
        assert widget.diagram_state["blocks"][0]["id"] == "g1", (
            "Should have g1 remaining"
        )

        # Redo once (restore g2)
        redo_action = {
            "type": "redo",
            "timestamp": 3000.0,
            "payload": {},
        }
        widget._action = redo_action

        # Should have 2 blocks (g1, g2)
        assert len(widget.diagram_state["blocks"]) == 2, (
            f"Expected 2 blocks after redo, got {len(widget.diagram_state['blocks'])}"
        )
        block_ids = {b["id"] for b in widget.diagram_state["blocks"]}
        assert block_ids == {"g1", "g2"}, f"Expected g1 and g2, got {block_ids}"


class TestThemeOperations:
    """Test theme switching operations."""

    def test_update_theme_via_action(self, widget):
        """Test updateTheme action changes widget theme.

        Verifies:
        - updateTheme action updates theme traitlet
        """
        # Change theme via UI action
        action = {
            "type": "updateTheme",
            "timestamp": 1000.0,
            "payload": {"theme": "dark"},
        }
        widget._action = action

        # Check theme traitlet updated
        assert widget.theme == "dark", f"Expected theme 'dark', got {widget.theme}"

    def test_update_theme_syncs_to_diagram(self, widget):
        """Test theme persists to diagram.theme attribute.

        Verifies:
        - Theme change updates diagram.theme
        - Theme persists across updates
        """
        # Change theme
        action = {
            "type": "updateTheme",
            "timestamp": 1000.0,
            "payload": {"theme": "light"},
        }
        widget._action = action

        # Check diagram.theme matches
        assert widget.diagram.theme == "light", (
            f"Expected diagram.theme 'light', got {widget.diagram.theme}"
        )

        # Add a block and update
        widget.diagram.add_block("gain", "g1", K=1.0)
        widget.update()

        # Theme should still be 'light'
        assert widget.diagram.theme == "light", (
            "Theme should persist after diagram update"
        )
