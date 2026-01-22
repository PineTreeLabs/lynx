# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for signal extraction helper methods.

Tests the helper methods used by get_ss() and get_tf() for arbitrary
subsystem extraction via the break-and-inject approach.
"""

import pytest

from lynx.conversion.signal_extraction import (
    _find_incoming_connections,
    _find_signal_source,
)
from lynx.diagram import Diagram, SignalNotFoundError


class TestSignalResolution:
    """Test __find_signal_source() with priority:
    IOMarker > Connection > Block > Block.port."""

    def test_find_signal_by_iomarker_label(self):
        """Priority 1: IOMarker labels take precedence."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})

        block, port_id = _find_signal_source(diagram, "r")

        assert block.id == "input1"
        assert port_id == "out"

    def test_find_signal_by_connection_label(self):
        """Priority 2: Connection labels used when no IOMarker match."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block("gain", "g2", K=2.0, position={"x": 200, "y": 0})
        diagram.add_connection("c1", "input1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "g2", "in")

        # Set connection label
        diagram.update_connection_label("c2", "control_signal")

        block, port_id = _find_signal_source(diagram, "control_signal")

        assert block.id == "g1"
        assert port_id == "out"

    def test_find_signal_by_block_label_port_format(self):
        """Priority 3: Block_label.port format (labels only, not IDs)."""
        diagram = Diagram()
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 0, "y": 0}
        )

        # Block label.port format should work
        block, port_id = _find_signal_source(diagram, "controller.out")
        assert block.id == "g1"
        assert port_id == "out"

    def test_block_label_port_format_required(self):
        """Block labels must use explicit .port format (no bare labels)."""
        diagram = Diagram()
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 0, "y": 0}
        )

        # Bare label should fail (Priority 4 removed)
        with pytest.raises(SignalNotFoundError):
            _find_signal_source(diagram, "controller")

    def test_block_id_not_supported_in_port_format(self):
        """Block IDs not allowed in block.port format (labels only)."""
        diagram = Diagram()
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 0, "y": 0}
        )

        # Block ID should fail
        with pytest.raises(SignalNotFoundError):
            _find_signal_source(diagram, "g1.out")

    def test_input_ports_rejected(self):
        """Input ports cannot be referenced (output ports only)."""
        diagram = Diagram()
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 0, "y": 0}
        )

        # Input port should fail
        with pytest.raises(SignalNotFoundError) as exc_info:
            _find_signal_source(diagram, "controller.in")

        assert "not an output port" in str(exc_info.value)

    def test_signal_not_found_error(self):
        """Raises SignalNotFoundError with search context."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=5.0, position={"x": 0, "y": 0})

        with pytest.raises(SignalNotFoundError) as exc_info:
            _find_signal_source(diagram, "nonexistent")

        assert "nonexistent" in str(exc_info.value)
        assert "IOMarkers" in str(exc_info.value)  # Shows where it searched

    def test_ambiguous_signal_uses_priority(self):
        """When multiple matches exist, priority order is respected."""
        diagram = Diagram()
        # Create IOMarker with label 'signal'
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="signal",
            position={"x": 0, "y": 0},
        )
        # Create gain
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        # Create connection with label 'signal'
        diagram.add_connection("c1", "input1", "out", "g1", "in")
        diagram.update_connection_label("c1", "signal")

        block, port_id = _find_signal_source(diagram, "signal")

        # IOMarker should win (Priority 1 > Priority 2)
        assert block.id == "input1"
        assert block.type == "io_marker"


class TestConnectionFinding:
    """Test __find_incoming_connections() for identifying connections to break."""

    def test__find_incoming_connections_single(self):
        """Single connection feeding a port."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_connection("c1", "input1", "out", "g1", "in")

        connections = _find_incoming_connections(diagram, "g1", "in")

        assert len(connections) == 1
        assert connections[0].id == "c1"
        assert connections[0].source_block_id == "input1"

    def test__find_incoming_connections_multiple(self):
        """Multiple connections feeding same port (fan-in via sum block)."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r1",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "input2",
            marker_type="input",
            label="r2",
            position={"x": 0, "y": 50},
        )
        diagram.add_block(
            "sum", "sum1", signs=["+", "+", "|"], position={"x": 100, "y": 25}
        )
        diagram.add_connection("c1", "input1", "out", "sum1", "in1")
        diagram.add_connection("c2", "input2", "out", "sum1", "in2")

        # Find connections to first input
        connections_in1 = _find_incoming_connections(diagram, "sum1", "in1")
        # Find connections to second input
        connections_in2 = _find_incoming_connections(diagram, "sum1", "in2")

        assert len(connections_in1) == 1
        assert connections_in1[0].id == "c1"
        assert len(connections_in2) == 1
        assert connections_in2[0].id == "c2"

    def test__find_incoming_connections_none(self):
        """No connections feeding port (e.g., InputMarker or broken connection)."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )

        # InputMarker output port has no incoming connections
        connections = _find_incoming_connections(diagram, "input1", "out")

        assert len(connections) == 0


class TestDiagramCloning:
    """Test _clone() for safe diagram duplication."""

    def test_clone_preserves_blocks(self):
        """All blocks present in cloned diagram."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        cloned = diagram._clone()

        assert len(cloned.blocks) == 3
        assert cloned.get_block("input1") is not None
        assert cloned.get_block("g1") is not None
        assert cloned.get_block("output1") is not None

    def test_clone_preserves_connections(self):
        """All connections present in cloned diagram."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )
        diagram.add_connection("c1", "input1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "output1", "in")

        cloned = diagram._clone()

        assert len(cloned.connections) == 2
        conn_ids = [c.id for c in cloned.connections]
        assert "c1" in conn_ids
        assert "c2" in conn_ids

    def test_clone_is_independent(self):
        """Modifying clone doesn't affect original."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=5.0, position={"x": 0, "y": 0})

        cloned = diagram._clone()

        # Modify clone
        cloned.add_block("gain", "g2", K=10.0, position={"x": 100, "y": 0})

        # Original unchanged
        assert len(diagram.blocks) == 1
        assert len(cloned.blocks) == 2

    def test_clone_preserves_parameters(self):
        """Block parameters are preserved in clone."""
        diagram = Diagram()
        diagram.add_block("gain", "g1", K=7.5, position={"x": 0, "y": 0})
        diagram.add_block(
            "transfer_function",
            "tf1",
            numerator=[1.0, 2.0],
            denominator=[1.0, 3.0, 4.0],
            position={"x": 100, "y": 0},
        )

        cloned = diagram._clone()

        g1_clone = cloned.get_block("g1")
        tf1_clone = cloned.get_block("tf1")

        assert g1_clone.get_parameter("K") == 7.5
        assert tf1_clone.get_parameter("numerator") == [1.0, 2.0]
        assert tf1_clone.get_parameter("denominator") == [1.0, 3.0, 4.0]
