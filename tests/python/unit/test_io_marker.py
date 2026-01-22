# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for IOMarker LaTeX Rendering - Automatic Index Display

Testing automatic index assignment for InputMarkers and OutputMarkers,
independent index sequences, legacy diagram compatibility, and JSON persistence.
"""

from lynx.diagram import Diagram


class TestAutoIndexAssignment:
    """Test automatic index assignment for new IOMarker blocks (User Story 1)"""

    def test_auto_index_assignment_inputs(self) -> None:
        """T008: InputMarkers get sequential indices 0, 1, 2... (TS-001.1)"""
        diagram = Diagram()
        diagram.add_block("io_marker", "in0", marker_type="input")
        diagram.add_block("io_marker", "in1", marker_type="input")
        diagram.add_block("io_marker", "in2", marker_type="input")

        # Assert indices are auto-assigned sequentially
        assert diagram.get_block("in0").get_parameter("index") == 0
        assert diagram.get_block("in1").get_parameter("index") == 1
        assert diagram.get_block("in2").get_parameter("index") == 2

    def test_auto_index_assignment_outputs(self) -> None:
        """T009: OutputMarkers get sequential indices 0, 1, 2..."""
        diagram = Diagram()
        diagram.add_block("io_marker", "out0", marker_type="output")
        diagram.add_block("io_marker", "out1", marker_type="output")
        diagram.add_block("io_marker", "out2", marker_type="output")

        # Assert indices are auto-assigned sequentially
        assert diagram.get_block("out0").get_parameter("index") == 0
        assert diagram.get_block("out1").get_parameter("index") == 1
        assert diagram.get_block("out2").get_parameter("index") == 2

    def test_independent_index_sequences(self) -> None:
        """T010: Input and Output markers have independent index sequences (TS-001.2)"""
        diagram = Diagram()
        diagram.add_block("io_marker", "in0", marker_type="input")
        diagram.add_block("io_marker", "in1", marker_type="input")
        diagram.add_block("io_marker", "out0", marker_type="output")
        diagram.add_block("io_marker", "out1", marker_type="output")

        # Assert inputs: 0, 1
        assert diagram.get_block("in0").get_parameter("index") == 0
        assert diagram.get_block("in1").get_parameter("index") == 1

        # Assert outputs: 0, 1 (independent from inputs)
        assert diagram.get_block("out0").get_parameter("index") == 0
        assert diagram.get_block("out1").get_parameter("index") == 1


class TestLegacyDiagramCompatibility:
    """Test backward compatibility with legacy diagrams (no index parameter)"""

    def test_legacy_diagram_auto_index_assignment(self) -> None:
        """T011: Legacy diagrams without index parameter
        get indices auto-assigned (TS-004.1)"""
        # Create legacy diagram JSON (no index parameter)
        legacy_json = {
            "blocks": [
                {
                    "id": "ref",
                    "type": "io_marker",
                    "parameters": [
                        {"name": "marker_type", "value": "input"},
                        {"name": "label", "value": "r"},
                    ],
                    "ports": [{"id": "out", "type": "output"}],
                    "position": {"x": 100, "y": 100},
                },
                {
                    "id": "dist",
                    "type": "io_marker",
                    "parameters": [
                        {"name": "marker_type", "value": "input"},
                        {"name": "label", "value": "d"},
                    ],
                    "ports": [{"id": "out", "type": "output"}],
                    "position": {"x": 100, "y": 200},
                },
                {
                    "id": "actuator",
                    "type": "io_marker",
                    "parameters": [
                        {"name": "marker_type", "value": "input"},
                        {"name": "label", "value": "u"},
                    ],
                    "ports": [{"id": "out", "type": "output"}],
                    "position": {"x": 100, "y": 300},
                },
            ],
            "connections": [],
        }

        # Load diagram
        diagram = Diagram.from_dict(legacy_json)

        # Indices should be assigned alphabetically by block ID
        # Order: actuator, dist, ref
        assert diagram.get_block("actuator").get_parameter("index") == 0
        assert diagram.get_block("dist").get_parameter("index") == 1
        assert diagram.get_block("ref").get_parameter("index") == 2

    def test_save_persists_indices(self) -> None:
        """T012: Saving diagram persists auto-assigned indices to JSON (TS-004.2)"""
        # Create legacy diagram (no indices)
        legacy_json = {
            "blocks": [
                {
                    "id": "in0",
                    "type": "io_marker",
                    "parameters": [{"name": "marker_type", "value": "input"}],
                    "ports": [{"id": "out", "type": "output"}],
                    "position": {"x": 100, "y": 100},
                }
            ],
            "connections": [],
        }

        # Load and access (triggers auto-assignment)
        diagram = Diagram.from_dict(legacy_json)
        _ = diagram.get_block("in0")  # Access triggers ensure_index

        # Save to JSON
        saved_dict = diagram.to_dict()

        # Assert index parameter is now present in saved JSON
        block_params = saved_dict["blocks"][0]["parameters"]
        index_param = next((p for p in block_params if p["name"] == "index"), None)

        assert index_param is not None
        assert isinstance(index_param["value"], int)
        assert index_param["value"] == 0


class TestIndexClamping:
    """Test index clamping behavior for out-of-range values"""

    def test_single_marker_index_1_clamps_to_0(self) -> None:
        """T013: Setting index to 1 when only 1 marker exists
        should clamp to 0 (Bug Fix)

        BUG: Currently fails - index=1 is accepted when it should be clamped to 0
        Valid range for 1 marker: [0, 0] (only index 0 is valid)
        """
        diagram = Diagram()
        diagram.add_block("io_marker", "input1", marker_type="input")

        # Verify initial state: only 1 marker with index 0
        assert diagram.get_block("input1").get_parameter("index") == 0

        # User sets index to 1 (out of range - should be clamped to 0)
        diagram.update_block_parameter("input1", "index", 1)

        # Assert index was clamped to 0 (max valid index for 1 marker is 0)
        assert diagram.get_block("input1").get_parameter("index") == 0
