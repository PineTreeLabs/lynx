# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for persistence with hybrid parameter storage.

Tests cover:
- T077: Hybrid parameter storage (expression + value)
- Round-trip serialization with expressions
"""

import json

import numpy as np
import pytest

from lynx.diagram import Diagram


class TestHybridParameterStorage:
    """Test hybrid parameter storage (expression + value) - T077."""

    def test_serialize_parameter_with_expression(self):
        """Test that parameters with expressions are serialized with both fields."""
        diagram = Diagram()

        # Create State Space block with expression stored
        block = diagram.add_block(
            "state_space",
            "ss1",
            A="A_matrix",  # Expression
            B="B_matrix",
            C="C_matrix",
            D="D_matrix",
        )

        # Manually set the evaluated values
        # (would normally be done by expression evaluator)
        for param in block._parameters:
            if param.name == "A":
                param.value = [[1, 0], [0, 1]]
                param.expression = "A_matrix"

        # Serialize to dict
        data = diagram.to_dict()

        # Find the state space block in serialized data
        ss_block = next(b for b in data["blocks"] if b["id"] == "ss1")

        # Find the A parameter
        a_param = next(p for p in ss_block["parameters"] if p["name"] == "A")

        # Should have both expression and value
        assert "expression" in a_param
        assert a_param["expression"] == "A_matrix"
        assert "value" in a_param
        assert a_param["value"] == [[1, 0], [0, 1]]

    def test_deserialize_parameter_with_expression(self):
        """Test that parameters with expressions are deserialized correctly."""
        # Create diagram data with hybrid storage
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "ss1",
                    "type": "state_space",
                    "position": {"x": 100, "y": 100},
                    "parameters": [
                        {
                            "name": "A",
                            "expression": "A_matrix",
                            "value": [[1, 0], [0, 1]],
                        },
                        {
                            "name": "B",
                            "expression": "B_matrix",
                            "value": [[1], [0]],
                        },
                        {
                            "name": "C",
                            "expression": "C_matrix",
                            "value": [[1, 0]],
                        },
                        {
                            "name": "D",
                            "expression": "D_matrix",
                            "value": [[0]],
                        },
                    ],
                    "ports": [],
                }
            ],
            "connections": [],
        }

        # Deserialize
        diagram = Diagram.from_dict(data)

        # Get block and check parameters
        block = diagram.get_block("ss1")
        assert block is not None

        # Find A parameter
        a_param = next(p for p in block._parameters if p.name == "A")

        # Should have both expression and value preserved
        assert hasattr(a_param, "expression")
        assert a_param.expression == "A_matrix"
        assert a_param.value == [[1, 0], [0, 1]]

    def test_round_trip_with_expressions(self, tmp_path):
        """Test save/load with hybrid parameter storage."""
        # Create diagram with State Space block
        diagram1 = Diagram()
        block = diagram1.add_block(
            "state_space",
            "ss1",
            A="A_matrix",
            B="B_matrix",
            C="C_matrix",
            D="D_matrix",
        )

        # Set hybrid storage (expression + value)
        for param in block._parameters:
            if param.name == "A":
                param.expression = "A_matrix"
                param.value = [[1, 0], [0, 1]]
            elif param.name == "B":
                param.expression = "B_matrix"
                param.value = [[1], [0]]
            elif param.name == "C":
                param.expression = "C_matrix"
                param.value = [[1, 0]]
            elif param.name == "D":
                param.expression = "D_matrix"
                param.value = [[0]]

        # Save to file
        filepath = tmp_path / "test_hybrid.json"
        diagram1.save(filepath)

        # Load from file
        diagram2 = Diagram.load(filepath)

        # Verify block loaded
        block2 = diagram2.get_block("ss1")
        assert block2 is not None

        # Verify all parameters have hybrid storage
        for param_name in ["A", "B", "C", "D"]:
            param = next(p for p in block2._parameters if p.name == param_name)
            assert hasattr(param, "expression")
            assert param.expression == f"{param_name}_matrix"
            assert param.value is not None

    def test_backward_compatibility_without_expressions(self):
        """Test that old diagrams without expression field still load."""
        # Old format (value only, no expression)
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "ss1",
                    "type": "state_space",
                    "position": {"x": 100, "y": 100},
                    "parameters": [
                        {"name": "A", "value": [[1, 0], [0, 1]]},
                        {"name": "B", "value": [[1], [0]]},
                        {"name": "C", "value": [[1, 0]]},
                        {"name": "D", "value": [[0]]},
                    ],
                    "ports": [],
                }
            ],
            "connections": [],
        }

        # Should load successfully (expression field optional)
        diagram = Diagram.from_dict(data)
        block = diagram.get_block("ss1")
        assert block is not None

        # Parameters should have values
        a_param = next(p for p in block._parameters if p.name == "A")
        assert a_param.value == [[1, 0], [0, 1]]


class TestNumPyArraySerialization:
    """Test NumPy array serialization in persistence (T101 partial)."""

    def test_state_space_with_numpy_arrays_serializes(self):
        """Test that state space blocks with NumPy arrays can be saved to JSON."""
        diagram = Diagram()

        # Create state space block with NumPy arrays (common use case)
        A = np.array([[0, 1], [-1, -2]])
        B = np.array([[0], [1]])
        C = np.array([[1, 0]])
        D = np.array([[0]])

        diagram.add_block("state_space", "ss1", A=A, B=B, C=C, D=D)

        # Try to serialize to dict (should work)
        diagram_dict = diagram.to_dict()

        # Try to serialize to JSON (should work, not raise TypeError)
        json_str = json.dumps(diagram_dict)
        assert isinstance(json_str, str)

        # Verify we can deserialize back
        loaded_dict = json.loads(json_str)
        loaded_diagram = Diagram.from_dict(loaded_dict)

        # Check that matrices are preserved
        ss1 = loaded_diagram.get_block("ss1")
        assert ss1 is not None

        # Get parameters
        params = {p.name: p.value for p in ss1._parameters}

        # Verify matrices match
        # (compare as lists since they may be deserialized as lists)
        assert np.array_equal(params["A"], A)
        assert np.array_equal(params["B"], B)
        assert np.array_equal(params["C"], C)
        assert np.array_equal(params["D"], D)

    def test_transfer_function_with_numpy_arrays_serializes(self):
        """Test that transfer function blocks with NumPy arrays can be saved."""
        diagram = Diagram()

        # Create TF with NumPy arrays
        num = np.array([1, 2, 3])
        den = np.array([1, 4, 5, 6])

        diagram.add_block("transfer_function", "tf1", numerator=num, denominator=den)

        # Serialize to JSON
        json_str = json.dumps(diagram.to_dict())

        # Deserialize and verify
        loaded_diagram = Diagram.from_dict(json.loads(json_str))
        tf1 = loaded_diagram.get_block("tf1")

        params = {p.name: p.value for p in tf1._parameters}
        assert np.array_equal(params["numerator"], num)
        assert np.array_equal(params["denominator"], den)


class TestErrorHandling:
    """Test error handling for file operations and malformed data (T102, T103)."""

    def test_file_not_found_error(self, tmp_path):
        """Test that loading nonexistent file raises FileNotFoundError."""
        nonexistent_file = tmp_path / "does_not_exist.json"

        with pytest.raises(FileNotFoundError):
            Diagram.load(nonexistent_file)

    def test_malformed_json_error(self, tmp_path):
        """Test that malformed JSON raises appropriate error."""
        # Create file with invalid JSON
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{this is not valid JSON}")

        with pytest.raises(json.JSONDecodeError):
            Diagram.load(malformed_file)

    def test_missing_fields_have_defaults(self):
        """Test that missing optional fields use defaults (Pydantic feature)."""
        # Missing blocks and connections - should use defaults (empty lists)
        data = {
            "version": "1.0.0",
        }

        diagram = Diagram.from_dict(data)
        assert diagram is not None
        assert len(diagram.blocks) == 0
        assert len(diagram.connections) == 0

    def test_invalid_block_type(self):
        """Test that unknown block type raises ValueError."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "block1",
                    "type": "unknown_type",  # Invalid type
                    "position": {"x": 0, "y": 0},
                    "parameters": [],
                    "ports": [],
                }
            ],
            "connections": [],
        }

        # Pydantic ValidationError is caught and re-raised as ValueError
        with pytest.raises(ValueError, match="Invalid diagram data"):
            Diagram.from_dict(data)


class TestConnectionWaypointPersistence:
    """Test connection waypoint serialization/deserialization (T030-T035)."""

    def test_serialize_connection_with_waypoints(self):
        """Test that connections with waypoints are serialized correctly."""
        diagram = Diagram()

        # Create two blocks
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)

        # Add connection
        diagram.add_connection(
            connection_id="conn1",
            source_block_id="g1",
            source_port_id="out",
            target_block_id="g2",
            target_port_id="in",
        )

        # Add waypoints
        conn = diagram.connections[0]
        conn.waypoints = [{"x": 200.0, "y": 100.0}, {"x": 200.0, "y": 150.0}]

        # Serialize
        data = diagram.to_dict()

        # Verify waypoints are included
        conn_data = data["connections"][0]
        assert "waypoints" in conn_data
        assert len(conn_data["waypoints"]) == 2
        assert conn_data["waypoints"][0] == {"x": 200.0, "y": 100.0}
        assert conn_data["waypoints"][1] == {"x": 200.0, "y": 150.0}

    def test_deserialize_connection_with_waypoints(self):
        """Test that connections with waypoints are deserialized correctly."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 100},
                    "parameters": [{"name": "K", "value": 1.0}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                },
                {
                    "id": "g2",
                    "type": "gain",
                    "position": {"x": 300, "y": 100},
                    "parameters": [{"name": "K", "value": 2.0}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                },
            ],
            "connections": [
                {
                    "id": "conn1",
                    "source_block_id": "g1",
                    "source_port_id": "out",
                    "target_block_id": "g2",
                    "target_port_id": "in",
                    "waypoints": [{"x": 200.0, "y": 100.0}, {"x": 200.0, "y": 150.0}],
                }
            ],
        }

        diagram = Diagram.from_dict(data)

        # Verify waypoints are loaded
        assert len(diagram.connections) == 1
        conn = diagram.connections[0]
        assert len(conn.waypoints) == 2
        assert conn.waypoints[0] == {"x": 200.0, "y": 100.0}
        assert conn.waypoints[1] == {"x": 200.0, "y": 150.0}

    def test_backward_compatibility_without_waypoints(self):
        """Test that old diagrams without waypoints still load."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 100},
                    "parameters": [{"name": "K", "value": 1.0}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                },
                {
                    "id": "g2",
                    "type": "gain",
                    "position": {"x": 300, "y": 100},
                    "parameters": [{"name": "K", "value": 2.0}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                },
            ],
            "connections": [
                {
                    "id": "conn1",
                    "source_block_id": "g1",
                    "source_port_id": "out",
                    "target_block_id": "g2",
                    "target_port_id": "in",
                    # No waypoints field - old format
                }
            ],
        }

        diagram = Diagram.from_dict(data)

        # Should load successfully with empty waypoints
        assert len(diagram.connections) == 1
        conn = diagram.connections[0]
        assert conn.waypoints == []

    def test_round_trip_with_waypoints(self, tmp_path):
        """Test save/load with connection waypoints."""
        diagram1 = Diagram()
        diagram1.add_block("gain", "g1", K=1.0)
        diagram1.add_block("gain", "g2", K=2.0)
        diagram1.add_connection(
            connection_id="conn1",
            source_block_id="g1",
            source_port_id="out",
            target_block_id="g2",
            target_port_id="in",
        )

        # Add waypoints
        diagram1.connections[0].waypoints = [
            {"x": 200.0, "y": 100.0},
            {"x": 200.0, "y": 150.0},
        ]

        # Save
        filepath = tmp_path / "test_waypoints.json"
        diagram1.save(filepath)

        # Load
        diagram2 = Diagram.load(filepath)

        # Verify
        assert len(diagram2.connections) == 1
        conn = diagram2.connections[0]
        assert len(conn.waypoints) == 2
        assert conn.waypoints[0] == {"x": 200.0, "y": 100.0}
        assert conn.waypoints[1] == {"x": 200.0, "y": 150.0}

    def test_update_connection_waypoints(self):
        """Test updating waypoints via diagram method."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_connection(
            connection_id="conn1",
            source_block_id="g1",
            source_port_id="out",
            target_block_id="g2",
            target_port_id="in",
        )

        # Update waypoints
        new_waypoints = [{"x": 150.0, "y": 120.0}]
        result = diagram.update_connection_waypoints("conn1", new_waypoints)

        assert result is True
        assert diagram.connections[0].waypoints == new_waypoints

    def test_update_connection_waypoints_nonexistent(self):
        """Test updating waypoints for nonexistent connection returns False."""
        diagram = Diagram()

        result = diagram.update_connection_waypoints("nonexistent", [{"x": 0, "y": 0}])

        assert result is False

    def test_undo_restores_previous_waypoints(self):
        """Test that undo restores previous waypoints (T049)."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_connection(
            connection_id="conn1",
            source_block_id="g1",
            source_port_id="out",
            target_block_id="g2",
            target_port_id="in",
        )

        # Initial state - no waypoints
        assert diagram.connections[0].waypoints == []

        # Add waypoints
        diagram.update_connection_waypoints("conn1", [{"x": 200.0, "y": 150.0}])
        assert diagram.connections[0].waypoints == [{"x": 200.0, "y": 150.0}]

        # Undo
        result = diagram.undo()
        assert result is True
        assert diagram.connections[0].waypoints == []

    def test_redo_restores_changed_waypoints(self):
        """Test that redo restores changed waypoints (T050)."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_connection(
            connection_id="conn1",
            source_block_id="g1",
            source_port_id="out",
            target_block_id="g2",
            target_port_id="in",
        )

        # Add waypoints and undo
        waypoints = [{"x": 200.0, "y": 150.0}]
        diagram.update_connection_waypoints("conn1", waypoints)
        diagram.undo()
        assert diagram.connections[0].waypoints == []

        # Redo
        result = diagram.redo()
        assert result is True
        assert diagram.connections[0].waypoints == waypoints


class TestSchemaVersioning:
    """Test schema version compatibility (T104)."""

    def test_current_version_loads(self):
        """Test that current version diagrams load successfully."""
        data = {
            "version": "1.0.0",
            "blocks": [],
            "connections": [],
        }

        diagram = Diagram.from_dict(data)
        assert diagram is not None

    def test_unknown_fields_rejected(self):
        """Test that unknown fields are rejected (fail-fast on schema mismatch)."""
        data = {
            "version": "1.0.0",
            "blocks": [],
            "connections": [],
            "future_field": "this should be rejected",  # Unknown field
        }

        # Should raise ValueError due to extra field
        with pytest.raises(ValueError, match="Invalid diagram data"):
            Diagram.from_dict(data)

    def test_block_with_unknown_fields_rejected(self):
        """Test that blocks with unknown fields are rejected
        (fail-fast on schema mismatch)."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 0, "y": 0},
                    "parameters": [{"name": "K", "value": 1.0}],
                    "ports": [],
                    "future_field": "rejected",  # Unknown field
                }
            ],
            "connections": [],
        }

        # Should raise ValueError due to extra field in block
        with pytest.raises(ValueError, match="Invalid diagram data"):
            Diagram.from_dict(data)
