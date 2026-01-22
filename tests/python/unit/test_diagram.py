# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for Diagram class.

Tests serialization, deserialization, connections, and validation.
"""

import pytest

from lynx.diagram import Connection, Diagram, ValidationResult


class TestConnection:
    """Test Connection dataclass."""

    def test_connection_creation(self):
        """Test creating a connection."""
        conn = Connection(
            id="c1",
            source_block_id="b1",
            source_port_id="out",
            target_block_id="b2",
            target_port_id="in",
        )
        assert conn.id == "c1"
        assert conn.source_block_id == "b1"
        assert conn.target_block_id == "b2"

    def test_connection_to_dict(self):
        """Test connection serialization."""
        conn = Connection(
            id="c1",
            source_block_id="b1",
            source_port_id="out",
            target_block_id="b2",
            target_port_id="in",
        )
        data = conn.to_dict()
        assert data["id"] == "c1"
        assert data["source_block_id"] == "b1"
        assert data["source_port_id"] == "out"
        assert data["target_block_id"] == "b2"
        assert data["target_port_id"] == "in"


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_success(self):
        """Test validation result for successful validation."""
        result = ValidationResult(is_valid=True, errors=[])
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_validation_result_with_errors(self):
        """Test validation result with errors."""
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.errors[0] == "Error 1"

    def test_validation_result_with_warnings(self):
        """Test validation result with warnings."""
        result = ValidationResult(is_valid=True, errors=[], warnings=["Warning 1"])
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Warning 1"

    def test_validation_result_to_dict(self):
        """Test validation result serialization."""
        result = ValidationResult(is_valid=False, errors=["Error 1"])
        data = result.to_dict()
        assert data["is_valid"] is False
        assert data["errors"] == ["Error 1"]
        assert "timestamp" in data


class TestDiagram:
    """Test Diagram class."""

    def test_diagram_initialization(self):
        """Test creating empty diagram."""
        diagram = Diagram()
        assert len(diagram.blocks) == 0
        assert len(diagram.connections) == 0
        assert diagram._version == "1.0.0"

    def test_add_block_gain(self):
        """Test adding a gain block."""
        diagram = Diagram()
        block = diagram.add_block("gain", "g1", K=2.5)
        assert block.id == "g1"
        assert block.type == "gain"
        assert len(diagram.blocks) == 1

    def test_add_block_input_marker(self):
        """Test adding an input marker."""
        diagram = Diagram()
        block = diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        assert block.id == "in1"
        assert block.type == "io_marker"

    def test_add_block_output_marker(self):
        """Test adding an output marker."""
        diagram = Diagram()
        block = diagram.add_block("io_marker", "out1", marker_type="output", label="y")
        assert block.id == "out1"
        assert block.type == "io_marker"

    def test_add_block_sum(self):
        """Test adding a sum block."""
        diagram = Diagram()
        block = diagram.add_block("sum", "s1", signs=["+", "+", "-"])
        assert block.id == "s1"
        assert block.type == "sum"

    def test_add_block_transfer_function(self):
        """Test adding a transfer function block."""
        diagram = Diagram()
        block = diagram.add_block(
            "transfer_function", "tf1", numerator=[1], denominator=[1, 1]
        )
        assert block.id == "tf1"
        assert block.type == "transfer_function"

    def test_add_block_state_space(self):
        """Test adding a state space block."""
        diagram = Diagram()
        block = diagram.add_block(
            "state_space",
            "ss1",
            A=[[1, 0], [0, 1]],
            B=[[1], [0]],
            C=[[1, 0]],
            D=[[0]],
        )
        assert block.id == "ss1"
        assert block.type == "state_space"

    def test_add_block_duplicate_id(self):
        """Test that duplicate block IDs are rejected."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0)
        with pytest.raises(ValueError, match="already exists"):
            diagram.add_block("gain", "g1", K=2.0)

    def test_add_block_unknown_type(self):
        """Test that unknown block types are rejected."""
        diagram = Diagram()
        with pytest.raises(ValueError, match="Unknown block type"):
            diagram.add_block("unknown_type", "b1")

    def test_add_block_missing_parameter(self):
        """Test that missing required parameters are caught."""
        diagram = Diagram()
        with pytest.raises(ValueError, match="requires"):
            diagram.add_block("gain", "g1")  # Missing K

    def test_add_block_sum_missing_signs(self):
        """Test that sum block requires signs parameter."""
        diagram = Diagram()
        with pytest.raises(ValueError, match="Sum block requires 'signs'"):
            diagram.add_block("sum", "s1")  # Missing signs

    def test_add_block_sum_with_pipe(self):
        """Test sum block with pipe (no connection) signs."""
        diagram = Diagram()
        # ["|", "+", "+"] means no top input, left and bottom inputs
        block = diagram.add_block("sum", "s1", signs=["|", "+", "+"])
        assert block.id == "s1"
        # Should create 2 input ports (in1, in2) for the two "+" signs
        input_ports = [p for p in block.get_ports() if p["type"] == "input"]
        assert len(input_ports) == 2
        assert input_ports[0]["id"] == "in1"
        assert input_ports[1]["id"] == "in2"

    def test_add_block_sum_too_few_active_inputs(self):
        """Test sum block with fewer than 2 active (non-pipe) inputs."""
        diagram = Diagram()
        with pytest.raises(ValueError, match="at least 2 active inputs"):
            diagram.add_block("sum", "s1", signs=["|", "+", "|"])  # Only 1 active input

    def test_add_block_sum_invalid_signs(self):
        """Test sum block with invalid sign characters."""
        diagram = Diagram()
        with pytest.raises(ValueError, match="Invalid sign"):
            diagram.add_block("sum", "s1", signs=["+", "x", "-"])  # "x" is invalid

    def test_add_block_transfer_function_missing_numerator(self):
        """Test that transfer function requires numerator."""
        diagram = Diagram()
        with pytest.raises(ValueError, match="Transfer function requires"):
            diagram.add_block("transfer_function", "tf1", denominator=[1, 1])

    def test_add_block_state_space_missing_matrices(self):
        """Test that state space requires all matrices."""
        diagram = Diagram()
        with pytest.raises(ValueError, match="State space block requires"):
            diagram.add_block("state_space", "ss1", A=[[1]], B=[[1]])  # Missing C, D

    def test_get_block(self):
        """Test getting a block by ID."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        block = diagram.get_block("g1")
        assert block is not None
        assert block.id == "g1"

    def test_get_block_not_found(self):
        """Test getting non-existent block returns None."""
        diagram = Diagram()
        block = diagram.get_block("nonexistent")
        assert block is None

    def test_remove_block(self):
        """Test removing a block."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        assert len(diagram.blocks) == 1

        result = diagram.remove_block("g1")
        assert result is True
        assert len(diagram.blocks) == 0

    def test_remove_block_not_found(self):
        """Test removing non-existent block returns False."""
        diagram = Diagram()
        result = diagram.remove_block("nonexistent")
        assert result is False

    def test_remove_block_cascades_connections(self):
        """Test that removing a block also removes connected edges."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        diagram.add_connection("c1", "in1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "out1", "in")

        assert len(diagram.connections) == 2

        # Remove middle block
        diagram.remove_block("g1")

        # Both connections should be removed
        assert len(diagram.connections) == 0

    def test_add_connection_success(self):
        """Test adding a valid connection."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)

        result = diagram.add_connection("c1", "in1", "out", "g1", "in")
        assert result.is_valid is True
        assert len(diagram.connections) == 1

    def test_add_connection_duplicate_id(self):
        """Test that duplicate connection IDs are rejected."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_block("gain", "g2", K=1.0)

        diagram.add_connection("c1", "in1", "out", "g1", "in")

        result = diagram.add_connection("c1", "in1", "out", "g2", "in")
        assert result.is_valid is False
        assert "already exists" in result.errors[0]

    def test_add_connection_source_block_not_found(self):
        """Test connection with non-existent source block."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)

        result = diagram.add_connection("c1", "nonexistent", "out", "g1", "in")
        assert result.is_valid is False
        assert "not found" in result.errors[0]

    def test_add_connection_target_block_not_found(self):
        """Test connection with non-existent target block."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")

        result = diagram.add_connection("c1", "in1", "out", "nonexistent", "in")
        assert result.is_valid is False
        assert "not found" in result.errors[0]

    def test_add_connection_source_port_not_found(self):
        """Test connection with non-existent source port."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)

        result = diagram.add_connection("c1", "in1", "invalid", "g1", "in")
        assert result.is_valid is False
        assert "not found" in result.errors[0]

    def test_add_connection_target_port_not_found(self):
        """Test connection with non-existent target port."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)

        result = diagram.add_connection("c1", "in1", "out", "g1", "invalid")
        assert result.is_valid is False
        assert "not found" in result.errors[0]

    def test_add_connection_source_not_output(self):
        """Test connection where source port is not an output."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_block("gain", "g2", K=1.0)

        result = diagram.add_connection("c1", "g1", "in", "g2", "in")
        assert result.is_valid is False
        assert "must be an output port" in result.errors[0]

    def test_add_connection_target_not_input(self):
        """Test connection where target port is not an input."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_block("gain", "g2", K=1.0)

        result = diagram.add_connection("c1", "g1", "out", "g2", "out")
        assert result.is_valid is False
        assert "must be an input port" in result.errors[0]

    def test_add_connection_target_already_connected(self):
        """Test that input ports can only have one connection."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("io_marker", "in2", marker_type="input", label="v")
        diagram.add_block("gain", "g1", K=2.5)

        diagram.add_connection("c1", "in1", "out", "g1", "in")

        result = diagram.add_connection("c2", "in2", "out", "g1", "in")
        assert result.is_valid is False
        assert "already has a connection" in result.errors[0]

    def test_remove_connection(self):
        """Test removing a connection."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)

        diagram.add_connection("c1", "in1", "out", "g1", "in")
        assert len(diagram.connections) == 1

        result = diagram.remove_connection("c1")
        assert result is True
        assert len(diagram.connections) == 0

    def test_remove_connection_not_found(self):
        """Test removing non-existent connection returns False."""
        diagram = Diagram()
        result = diagram.remove_connection("nonexistent")
        assert result is False

    def test_to_dict(self):
        """Test diagram serialization."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5, position={"x": 100, "y": 200})

        data = diagram.to_dict()
        assert data["version"] == "1.0.0"
        assert len(data["blocks"]) == 1
        assert data["blocks"][0]["id"] == "g1"
        assert data["blocks"][0]["type"] == "gain"
        assert data["blocks"][0]["position"] == {"x": 100, "y": 200}

    def test_from_dict(self):
        """Test diagram deserialization."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 200},
                    "parameters": [{"name": "K", "value": 2.5}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                }
            ],
            "connections": [],
        }

        diagram = Diagram.from_dict(data)
        assert len(diagram.blocks) == 1
        block = diagram.get_block("g1")
        assert block is not None
        assert block.position == {"x": 100, "y": 200}

    def test_from_dict_with_connections(self):
        """Test deserialization with connections."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "in1",
                    "type": "io_marker",
                    "position": {"x": 0, "y": 0},
                    "parameters": [
                        {"name": "marker_type", "value": "input"},
                        {"name": "label", "value": "u"},
                    ],
                    "ports": [{"id": "out", "type": "output", "label": "u"}],
                },
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 0},
                    "parameters": [{"name": "K", "value": 2.5}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                },
            ],
            "connections": [
                {
                    "id": "c1",
                    "source_block_id": "in1",
                    "source_port_id": "out",
                    "target_block_id": "g1",
                    "target_port_id": "in",
                }
            ],
        }

        diagram = Diagram.from_dict(data)
        assert len(diagram.blocks) == 2
        assert len(diagram.connections) == 1
        assert diagram.connections[0].id == "c1"

    def test_from_dict_invalid_schema(self):
        """Test that invalid data raises ValidationError."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "invalid_type",  # Invalid block type
                    "position": {"x": 100, "y": 200},
                    "parameters": [],
                    "ports": [],
                }
            ],
            "connections": [],
        }

        with pytest.raises(ValueError, match="Invalid diagram data"):
            Diagram.from_dict(data)

    def test_from_dict_with_invalid_connection(self):
        """Test that invalid connections during load are silently skipped."""
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 0},
                    "parameters": [{"name": "K", "value": 2.5}],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                },
            ],
            "connections": [
                {
                    "id": "c1",
                    "source_block_id": "nonexistent",  # Invalid source
                    "source_port_id": "out",
                    "target_block_id": "g1",
                    "target_port_id": "in",
                }
            ],
        }

        # Should load successfully but skip invalid connection
        diagram = Diagram.from_dict(data)
        assert len(diagram.blocks) == 1
        assert len(diagram.connections) == 0  # Invalid connection was skipped

    def test_save_and_load(self, tmp_path):
        """Test saving and loading diagram to/from file."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5, position={"x": 100, "y": 200})
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_connection("c1", "in1", "out", "g1", "in")

        # Save
        filepath = tmp_path / "test_diagram.json"
        diagram.save(filepath)
        assert filepath.exists()

        # Load
        loaded = Diagram.load(filepath)
        assert len(loaded.blocks) == 2
        assert len(loaded.connections) == 1

        # Verify block
        g1 = loaded.get_block("g1")
        assert g1 is not None
        assert g1.position == {"x": 100, "y": 200}

    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            Diagram.load("/nonexistent/path/diagram.json")

    def test_save_creates_parent_directory(self, tmp_path):
        """Test that save creates parent directories."""
        filepath = tmp_path / "subdir" / "diagram.json"
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0)

        diagram.save(filepath)
        assert filepath.exists()

    def test_round_trip_all_block_types(self, tmp_path):
        """Test save/load with all block types."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")
        diagram.add_block("sum", "s1", signs=["+", "+", "-"])
        diagram.add_block(
            "transfer_function", "tf1", numerator=[1, 2], denominator=[1, 3, 2]
        )
        diagram.add_block(
            "state_space",
            "ss1",
            A=[[1, 0], [0, 1]],
            B=[[1], [0]],
            C=[[1, 0]],
            D=[[0]],
        )

        filepath = tmp_path / "full_diagram.json"
        diagram.save(filepath)

        loaded = Diagram.load(filepath)
        assert len(loaded.blocks) == 6

        # Verify each block type
        assert loaded.get_block("g1").type == "gain"
        assert loaded.get_block("in1").type == "io_marker"
        assert loaded.get_block("s1").type == "sum"
        assert loaded.get_block("tf1").type == "transfer_function"
        assert loaded.get_block("ss1").type == "state_space"

    def test_flipped_state_serialization(self):
        """Test that flipped state persists through to_dict/from_dict."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_block(
            "transfer_function", "tf1", numerator=[1, 2], denominator=[1, 3, 2]
        )

        # Flip one block
        diagram.flip_block("g1")

        # Serialize
        data = diagram.to_dict()

        # Verify flipped state in serialized data
        g1_data = next(b for b in data["blocks"] if b["id"] == "g1")
        tf1_data = next(b for b in data["blocks"] if b["id"] == "tf1")
        assert g1_data["flipped"] is True
        assert tf1_data.get("flipped", False) is False

        # Deserialize
        loaded = Diagram.from_dict(data)

        # Verify flipped state is restored
        assert loaded.get_block("g1").flipped is True
        assert loaded.get_block("tf1").flipped is False

    def test_flipped_state_file_round_trip(self, tmp_path):
        """Test that flipped state persists through save/load."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_block("sum", "s1", signs=["+", "-", "|"])
        diagram.add_block("state_space", "ss1", A=[[1]], B=[[1]], C=[[1]], D=[[0]])

        # Flip multiple blocks
        diagram.flip_block("g1")
        diagram.flip_block("ss1")

        # Save to file
        filepath = tmp_path / "flipped_diagram.json"
        diagram.save(filepath)

        # Load from file
        loaded = Diagram.load(filepath)

        # Verify flipped state is preserved
        assert loaded.get_block("g1").flipped is True
        assert loaded.get_block("s1").flipped is False
        assert loaded.get_block("ss1").flipped is True


class TestUndoRedo:
    """Test undo/redo functionality"""

    def test_undo_add_block(self):
        """Test undoing block addition."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        assert len(diagram.blocks) == 1

        # Undo
        result = diagram.undo()
        assert result is True
        assert len(diagram.blocks) == 0

    def test_undo_on_empty_history(self):
        """Test that undo on empty history returns False."""
        diagram = Diagram()
        result = diagram.undo()
        assert result is False

    def test_redo_add_block(self):
        """Test redoing block addition."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        diagram.undo()
        assert len(diagram.blocks) == 0

        # Redo
        result = diagram.redo()
        assert result is True
        assert len(diagram.blocks) == 1
        assert diagram.get_block("g1") is not None

    def test_redo_on_empty_future(self):
        """Test that redo on empty future returns False."""
        diagram = Diagram()
        result = diagram.redo()
        assert result is False

    def test_undo_redo_multiple_actions(self):
        """Test undo/redo with multiple actions."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_block("gain", "g3", K=3.0)
        assert len(diagram.blocks) == 3

        # Undo twice
        diagram.undo()
        assert len(diagram.blocks) == 2
        diagram.undo()
        assert len(diagram.blocks) == 1

        # Redo once
        diagram.redo()
        assert len(diagram.blocks) == 2

        # Add new action (should clear redo history)
        diagram.add_block("gain", "g4", K=4.0)
        assert len(diagram.blocks) == 3

        # Redo should fail now
        result = diagram.redo()
        assert result is False

    def test_undo_remove_block(self):
        """Test undoing block removal."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        diagram.remove_block("g1")
        assert len(diagram.blocks) == 0

        # Undo removal
        diagram.undo()
        assert len(diagram.blocks) == 1
        assert diagram.get_block("g1") is not None

    def test_undo_add_connection(self):
        """Test undoing connection addition."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_connection("c1", "in1", "out", "g1", "in")
        assert len(diagram.connections) == 1

        # Undo connection
        diagram.undo()
        assert len(diagram.connections) == 0

    def test_undo_remove_connection(self):
        """Test undoing connection removal."""
        diagram = Diagram()
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=2.5)
        diagram.add_connection("c1", "in1", "out", "g1", "in")
        diagram.remove_connection("c1")
        assert len(diagram.connections) == 0

        # Undo removal
        diagram.undo()
        assert len(diagram.connections) == 1

    def test_undo_redo_preserves_block_state(self):
        """Test that undo/redo preserves complete block state."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5, position={"x": 100, "y": 200})

        block = diagram.get_block("g1")
        assert block.position == {"x": 100, "y": 200}

        # Undo then redo
        diagram.undo()
        diagram.redo()

        # Verify state is preserved
        block = diagram.get_block("g1")
        assert block is not None
        assert block.position == {"x": 100, "y": 200}
        assert block.get_parameter("K") == 2.5

    def test_undo_move_block(self):
        """Test undoing block position update."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0, position={"x": 100, "y": 100})

        # Move block
        diagram.update_block_position("g1", {"x": 200, "y": 300})
        block = diagram.get_block("g1")
        assert block.position == {"x": 200, "y": 300}

        # Undo move
        diagram.undo()
        block = diagram.get_block("g1")
        assert block.position == {"x": 100, "y": 100}

    def test_undo_update_parameter(self):
        """Test undoing parameter update."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)

        # Update parameter
        diagram.update_block_parameter("g1", "K", 5.0)
        assert diagram.get_block("g1").get_parameter("K") == 5.0

        # Undo parameter change
        diagram.undo()
        assert diagram.get_block("g1").get_parameter("K") == 2.5

    def test_undo_update_label(self):
        """Test undoing label update."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0, label="Original")

        # Update label
        diagram.update_block_label("g1", "Modified")
        assert diagram.get_block("g1").label == "Modified"

        # Undo label change
        diagram.undo()
        assert diagram.get_block("g1").label == "Original"

    def test_undo_redo_mixed_operations(self):
        """Test undo/redo with mixed operation types."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0, position={"x": 0, "y": 0}, label="G1")
        diagram.add_block("gain", "g2", K=2.0, position={"x": 100, "y": 0})

        # Series of mixed operations
        diagram.update_block_position("g1", {"x": 50, "y": 50})
        diagram.update_block_parameter("g1", "K", 1.5)
        diagram.update_block_label("g1", "Gain Block")
        diagram.add_connection("c1", "g1", "out", "g2", "in")

        # Undo all operations
        diagram.undo()  # Undo add_connection
        assert len(diagram.connections) == 0

        diagram.undo()  # Undo update_label
        assert diagram.get_block("g1").label == "G1"

        diagram.undo()  # Undo update_parameter
        assert diagram.get_block("g1").get_parameter("K") == 1.0

        diagram.undo()  # Undo update_position
        assert diagram.get_block("g1").position == {"x": 0, "y": 0}

        # Redo all
        diagram.redo()  # Redo position
        assert diagram.get_block("g1").position == {"x": 50, "y": 50}

        diagram.redo()  # Redo parameter
        assert diagram.get_block("g1").get_parameter("K") == 1.5

        diagram.redo()  # Redo label
        assert diagram.get_block("g1").label == "Gain Block"

        diagram.redo()  # Redo connection
        assert len(diagram.connections) == 1

    def test_undo_flip_block(self):
        """Test undoing block flip."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)
        block = diagram.get_block("g1")
        assert block.flipped is False

        # Flip the block
        diagram.flip_block("g1")
        assert block.flipped is True

        # Undo flip
        diagram.undo()
        block = diagram.get_block("g1")
        assert block.flipped is False

    def test_redo_flip_block(self):
        """Test redoing block flip."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.5)

        # Flip, then undo
        diagram.flip_block("g1")
        diagram.undo()
        block = diagram.get_block("g1")
        assert block.flipped is False

        # Redo flip
        diagram.redo()
        block = diagram.get_block("g1")
        assert block.flipped is True

    def test_flip_block_toggle(self):
        """Test that flip_block toggles state."""
        diagram = Diagram()
        diagram.add_block("transfer_function", "tf1", numerator=[1], denominator=[1, 1])
        block = diagram.get_block("tf1")

        # Initial state
        assert block.flipped is False

        # First flip
        diagram.flip_block("tf1")
        assert block.flipped is True

        # Second flip (toggle back)
        diagram.flip_block("tf1")
        assert block.flipped is False

        # Third flip
        diagram.flip_block("tf1")
        assert block.flipped is True

    def test_flip_block_nonexistent(self):
        """Test flipping non-existent block returns False."""
        diagram = Diagram()
        result = diagram.flip_block("nonexistent")
        assert result is False


class TestWaypointClearing:
    """Test that waypoints are cleared when blocks move (Simulink-style UX)."""

    def test_moving_source_block_clears_waypoints(self):
        """Moving the source block of a connection should clear its waypoints."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.0, position={"x": 100, "y": 200})
        diagram.add_block("gain", "g2", K=3.0, position={"x": 400, "y": 200})
        diagram.add_connection("c1", "g1", "out", "g2", "in")

        # Set some waypoints
        conn = diagram.connections[0]
        conn.waypoints = [
            {"x": 200, "y": 200},
            {"x": 200, "y": 150},
            {"x": 300, "y": 150},
        ]
        assert len(conn.waypoints) == 3

        # Move source block
        diagram.update_block_position("g1", {"x": 120, "y": 220})

        # Waypoints should be cleared
        assert len(conn.waypoints) == 0

    def test_moving_target_block_clears_waypoints(self):
        """Moving the target block of a connection should clear its waypoints."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.0, position={"x": 100, "y": 200})
        diagram.add_block("gain", "g2", K=3.0, position={"x": 400, "y": 200})
        diagram.add_connection("c1", "g1", "out", "g2", "in")

        # Set some waypoints
        conn = diagram.connections[0]
        conn.waypoints = [
            {"x": 200, "y": 200},
            {"x": 200, "y": 150},
            {"x": 300, "y": 150},
        ]
        assert len(conn.waypoints) == 3

        # Move target block
        diagram.update_block_position("g2", {"x": 420, "y": 180})

        # Waypoints should be cleared
        assert len(conn.waypoints) == 0

    def test_moving_unrelated_block_preserves_waypoints(self):
        """Moving a block not connected to an edge should preserve its waypoints."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=2.0, position={"x": 100, "y": 200})
        diagram.add_block("gain", "g2", K=3.0, position={"x": 400, "y": 200})
        diagram.add_block(
            "gain", "g3", K=4.0, position={"x": 250, "y": 400}
        )  # Unconnected
        diagram.add_connection("c1", "g1", "out", "g2", "in")

        # Set waypoints on connection between g1 and g2
        conn = diagram.connections[0]
        conn.waypoints = [{"x": 200, "y": 200}, {"x": 200, "y": 150}]
        assert len(conn.waypoints) == 2

        # Move g3 (unrelated to connection)
        diagram.update_block_position("g3", {"x": 260, "y": 420})

        # Waypoints should be preserved
        assert len(conn.waypoints) == 2
        assert conn.waypoints[0] == {"x": 200, "y": 200}

    def test_moving_block_clears_multiple_connections(self):
        """Moving a block should clear waypoints on all its connections."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=1.0, position={"x": 200, "y": 200})
        diagram.add_block("gain", "g2", K=2.0, position={"x": 100, "y": 100})
        diagram.add_block("gain", "g3", K=3.0, position={"x": 400, "y": 200})

        # g2 -> g1 -> g3 (g1 is both target and source)
        diagram.add_connection("c1", "g2", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "g3", "in")

        # Set waypoints on both connections
        diagram.connections[0].waypoints = [{"x": 150, "y": 150}]
        diagram.connections[1].waypoints = [{"x": 300, "y": 200}]

        # Move g1 (in the middle)
        diagram.update_block_position("g1", {"x": 220, "y": 220})

        # Both connections' waypoints should be cleared
        assert len(diagram.connections[0].waypoints) == 0
        assert len(diagram.connections[1].waypoints) == 0


class TestBlockLabelEdgeCases:
    """Test edge cases for block label editing (Feature 013)."""

    def test_empty_label_reverts_to_id(self):
        """T004: Empty label should revert to block ID (FR-006)."""
        diagram = Diagram()
        block = diagram.add_block("gain", "controller", K=5.0)

        # Set a custom label first
        diagram.update_block_label("controller", "PID Controller")
        assert block.label == "PID Controller"

        # Set empty label - should revert to block ID
        diagram.update_block_label("controller", "")
        assert block.label == "controller", "Empty label should revert to block ID"

    def test_whitespace_only_label_reverts_to_id(self):
        """T005: Whitespace-only label should revert to block ID (FR-006)."""
        diagram = Diagram()
        block = diagram.add_block("gain", "plant", K=2.0)

        # Set whitespace-only labels - should all revert to ID
        test_cases = ["   ", "\t", "\n", "  \t\n  ", "\r\n"]
        for whitespace_label in test_cases:
            diagram.update_block_label("plant", whitespace_label)
            assert block.label == "plant", (
                f"Whitespace-only label '{repr(whitespace_label)}' should revert to ID"
            )

    def test_unicode_label_acceptance(self):
        """T006: Unicode characters should be accepted in labels (FR-011)."""
        diagram = Diagram()
        block = diagram.add_block("gain", "g1", K=1.0)

        # Test various Unicode labels
        unicode_labels = [
            "α Controller",
            "Contrôleur",
            "控制器",
            "Контроллер",
            "🚀 Rocket",
            "θ_ref",
        ]

        for label in unicode_labels:
            diagram.update_block_label("g1", label)
            assert block.label == label, f"Unicode label '{label}' should be accepted"

    def test_duplicate_labels_allowed(self):
        """T007: Multiple blocks can have the same label (Edge Case 1)."""
        diagram = Diagram()
        block1 = diagram.add_block("gain", "g1", K=1.0)
        block2 = diagram.add_block("gain", "g2", K=2.0)
        block3 = diagram.add_block("gain", "g3", K=3.0)

        # Set all blocks to same label
        duplicate_label = "Controller"
        diagram.update_block_label("g1", duplicate_label)
        diagram.update_block_label("g2", duplicate_label)
        diagram.update_block_label("g3", duplicate_label)

        # All should have same label (blocks identified by ID, not label)
        assert block1.label == duplicate_label
        assert block2.label == duplicate_label
        assert block3.label == duplicate_label

        # Verify blocks remain uniquely identified by ID
        assert diagram.get_block("g1").id == "g1"
        assert diagram.get_block("g2").id == "g2"
        assert diagram.get_block("g3").id == "g3"


class TestIOMarkerIndexRenumbering:
    """Test automatic index renumbering for IOMarker blocks (User Story 3).

    Tests verify Simulink-style automatic renumbering behavior when:
    - Manually changing marker indices
    - Deleting markers
    - Handling out-of-range/negative values
    """

    def test_downward_shift_renumbering(self):
        """T043: Verify automatic renumbering when index changed
        to lower value (TS-003.1).

        Scenario: Change index from high to low value
        Given: InputMarkers in0(0), in1(1), in2(2)
        When: Change in2's index from 2 → 0
        Then: in2=0, in0=1, in1=2 (downward shift)
        """
        diagram = Diagram()
        diagram.add_block("io_marker", "in0", marker_type="input")
        diagram.add_block("io_marker", "in1", marker_type="input")
        diagram.add_block("io_marker", "in2", marker_type="input")

        # Initial: in0=0, in1=1, in2=2
        # Change in2: 2 → 0
        diagram.update_block_parameter("in2", "index", 0)

        # Assert renumbering
        assert diagram.get_block("in2").get_parameter("index") == 0
        assert diagram.get_block("in0").get_parameter("index") == 1
        assert diagram.get_block("in1").get_parameter("index") == 2

    def test_upward_shift_renumbering(self):
        """T044: Verify automatic renumbering when index changed
        to higher value (TS-003.2).

        Scenario: Change index from low to high value
        Given: InputMarkers in0(0), in1(1), in2(2)
        When: Change in0's index from 0 → 2
        Then: in1=0, in2=1, in0=2 (upward shift)
        """
        diagram = Diagram()
        diagram.add_block("io_marker", "in0", marker_type="input")
        diagram.add_block("io_marker", "in1", marker_type="input")
        diagram.add_block("io_marker", "in2", marker_type="input")

        # Initial: in0=0, in1=1, in2=2
        # Change in0: 0 → 2
        diagram.update_block_parameter("in0", "index", 2)

        # Assert renumbering
        assert diagram.get_block("in1").get_parameter("index") == 0
        assert diagram.get_block("in2").get_parameter("index") == 1
        assert diagram.get_block("in0").get_parameter("index") == 2

    def test_delete_cascade_renumbering(self):
        """T045: Verify automatic renumbering when marker deleted (TS-003.3).

        Scenario: Delete marker in middle of sequence
        Given: InputMarkers in0(0), in1(1), in2(2), in3(3)
        When: Delete in1 (index 1)
        Then: in0=0, in2=1, in3=2 (cascade down)
        """
        diagram = Diagram()
        diagram.add_block("io_marker", "in0", marker_type="input")
        diagram.add_block("io_marker", "in1", marker_type="input")
        diagram.add_block("io_marker", "in2", marker_type="input")
        diagram.add_block("io_marker", "in3", marker_type="input")

        # Delete in1 (index 1)
        diagram.remove_block("in1")

        # Assert cascade
        assert diagram.get_block("in0").get_parameter("index") == 0
        assert diagram.get_block("in2").get_parameter("index") == 1
        assert diagram.get_block("in3").get_parameter("index") == 2
        assert diagram.get_block("in1") is None

    def test_out_of_range_index_clamping(self):
        """T046: Verify out-of-range manual index is clamped to valid range (TS-003.4).

        Scenario: Set index beyond valid range
        Given: InputMarkers in0(0), in1(1)
        When: Set in0's index to 10 (max valid is 1)
        Then: in0 clamped to 1, in1 shifted to 0
        """
        diagram = Diagram()
        diagram.add_block("io_marker", "in0", marker_type="input")
        diagram.add_block("io_marker", "in1", marker_type="input")

        # Try to set in0 to index 10 (out of range, max valid is 1)
        diagram.update_block_parameter("in0", "index", 10)

        # Assert clamped and renumbered
        assert diagram.get_block("in0").get_parameter("index") == 1
        assert diagram.get_block("in1").get_parameter("index") == 0

    def test_negative_index_handling(self):
        """T047: Verify negative index treated as 0 and triggers renumbering (TS-003.5).

        Scenario: Set negative index value
        Given: InputMarkers in0(0), in1(1)
        When: Set in1's index to -5
        Then: in1 clamped to 0, in0 shifted to 1
        """
        diagram = Diagram()
        diagram.add_block("io_marker", "in0", marker_type="input")
        diagram.add_block("io_marker", "in1", marker_type="input")

        # Set in1 to -5 (invalid, should become 0)
        diagram.update_block_parameter("in1", "index", -5)

        # Assert clamped to 0 and renumbered
        assert diagram.get_block("in1").get_parameter("index") == 0
        assert diagram.get_block("in0").get_parameter("index") == 1

    def test_renumbering_performance_large_diagram(self):
        """T048: Verify renumbering meets <20ms target for large diagrams (TS-005.2).

        Scenario: Performance with 100 markers
        Given: 100 InputMarkers (0-99)
        When: Change marker at index 50 to index 0
        Then: Renumbering completes in <20ms
        """
        import time

        diagram = Diagram()

        # Create 100 InputMarkers
        for i in range(100):
            diagram.add_block("io_marker", f"in{i}", marker_type="input")

        # Measure downward shift renumbering
        start = time.perf_counter()
        diagram.update_block_parameter("in50", "index", 0)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        assert elapsed < 20, f"Renumbering took {elapsed:.2f}ms (target: <20ms)"
        assert diagram.get_block("in50").get_parameter("index") == 0
