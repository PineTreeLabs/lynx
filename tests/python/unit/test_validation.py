# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for control theory validation.

Tests cover:
- T089: Algebraic loop detection (pure gain feedback)
- T090: Valid feedback loop (with dynamics)
- T091: System completeness (at least one I/O block)
- T092: Disconnected block detection
"""

from lynx.diagram import Diagram
from lynx.validation import validate_diagram


class TestAlgebraicLoopDetection:
    """Test algebraic loop detection (T089, T090)."""

    def test_pure_gain_feedback_loop_detected(self):
        """Test that pure gain feedback loop (no dynamics) is detected as error."""
        diagram = Diagram()

        # Create a pure gain feedback loop (algebraic loop)
        # Input -> Sum -> Gain1 -> Gain2 -> Output
        #           ^               |
        #           |_______________|  (feedback through Gain3)
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("sum", "sum1", signs=["+", "-", "|"])
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_block("gain", "g3", K=0.5)  # Feedback gain
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        # Connect forward path: in1 -> sum1 -> g1 -> g2 -> out1
        diagram.add_connection("c1", "in1", "out", "sum1", "in1")
        diagram.add_connection("c2", "sum1", "out", "g1", "in")
        diagram.add_connection("c3", "g1", "out", "g2", "in")
        diagram.add_connection("c4", "g2", "out", "out1", "in")

        # Add feedback: g2 -> g3 -> sum1
        # (creates algebraic loop - all gains, no dynamics)
        diagram.add_connection("c5", "g2", "out", "g3", "in")
        diagram.add_connection("c6", "g3", "out", "sum1", "in2")

        # Validate
        result = validate_diagram(diagram)

        # Should detect algebraic loop
        assert result.is_valid is False
        assert any("algebraic loop" in err.lower() for err in result.errors)

    def test_transfer_function_feedback_loop_valid(self):
        """Test that feedback loop with proper TF (no direct feedthrough) is valid."""
        diagram = Diagram()

        # Create feedback loop with transfer function
        # (num order < den order, no feedthrough)
        # Input -> Sum -> TF -> Output
        #           ^     |
        #           |_____|  (feedback through Gain)
        diagram.add_block("io_marker", "in1", marker_type="input", label="r")
        diagram.add_block("sum", "sum1", signs=["+", "-", "|"])
        diagram.add_block("transfer_function", "tf1", numerator=[1], denominator=[1, 1])
        diagram.add_block("gain", "g1", K=0.5)  # Feedback gain
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        # Connect forward path: in1 -> sum1 -> tf1 -> out1
        diagram.add_connection("c1", "in1", "out", "sum1", "in1")
        diagram.add_connection("c2", "sum1", "out", "tf1", "in")
        diagram.add_connection("c3", "tf1", "out", "out1", "in")

        # Add feedback: tf1 -> g1 -> sum1 (valid - TF has no feedthrough)
        diagram.add_connection("c4", "tf1", "out", "g1", "in")
        diagram.add_connection("c5", "g1", "out", "sum1", "in2")

        # Validate
        result = validate_diagram(diagram)

        # Should be valid (TF has no feedthrough, breaks algebraic loop)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_state_space_feedback_loop_valid(self):
        """Test that feedback loop with state space (D=0, no feedthrough) is valid."""
        diagram = Diagram()

        # Create feedback loop with state space block (D=0, no direct feedthrough)
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block(
            "state_space",
            "ss1",
            A=[[0, 1], [-1, -2]],
            B=[[0], [1]],
            C=[[1, 0]],
            D=[[0]],
        )  # D=0, no feedthrough
        diagram.add_block("gain", "g1", K=0.5)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        # Connect with feedback
        diagram.add_connection("c1", "in1", "out", "ss1", "in")
        diagram.add_connection("c2", "ss1", "out", "out1", "in")
        diagram.add_connection("c3", "ss1", "out", "g1", "in")
        diagram.add_connection("c4", "g1", "out", "ss1", "in")

        # Validate
        result = validate_diagram(diagram)

        # Should be valid (state space has no feedthrough, breaks algebraic loop)
        assert result.is_valid is True

    def test_transfer_function_with_feedthrough_creates_algebraic_loop(self):
        """Test that TF with direct feedthrough (num order = den order)
        creates algebraic loop."""
        diagram = Diagram()

        # Create feedback loop with TF that has direct feedthrough
        diagram.add_block("io_marker", "in1", marker_type="input", label="r")
        diagram.add_block("sum", "sum1", signs=["+", "-", "|"])
        diagram.add_block(
            "transfer_function", "tf1", numerator=[2, 1], denominator=[1, 1]
        )  # Same order!
        diagram.add_block("gain", "g1", K=0.5)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        # Connect forward path
        diagram.add_connection("c1", "in1", "out", "sum1", "in1")
        diagram.add_connection("c2", "sum1", "out", "tf1", "in")
        diagram.add_connection("c3", "tf1", "out", "out1", "in")

        # Add feedback - creates algebraic loop since TF has feedthrough
        diagram.add_connection("c4", "tf1", "out", "g1", "in")
        diagram.add_connection("c5", "g1", "out", "sum1", "in2")

        # Validate
        result = validate_diagram(diagram)

        # Should detect algebraic loop (TF has direct feedthrough)
        assert result.is_valid is False
        assert any("algebraic loop" in err.lower() for err in result.errors)

    def test_state_space_with_feedthrough_creates_algebraic_loop(self):
        """Test that state space with D≠0 creates algebraic loop."""
        diagram = Diagram()

        # Create feedback loop with state space that has direct feedthrough
        # Input -> Sum -> SS(D≠0) -> Output
        #           ^         |
        #           |___G1____|  (feedback creates algebraic loop)
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("sum", "sum1", signs=["+", "-", "|"])
        diagram.add_block(
            "state_space",
            "ss1",
            A=[[0, 1], [-1, -2]],
            B=[[0], [1]],
            C=[[1, 0]],
            D=[[0.5]],
        )  # D≠0, has feedthrough!
        diagram.add_block("gain", "g1", K=0.5)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        # Connect forward path
        diagram.add_connection("c1", "in1", "out", "sum1", "in1")
        diagram.add_connection("c2", "sum1", "out", "ss1", "in")
        diagram.add_connection("c3", "ss1", "out", "out1", "in")

        # Add feedback - creates algebraic loop since SS has feedthrough
        diagram.add_connection("c4", "ss1", "out", "g1", "in")
        diagram.add_connection("c5", "g1", "out", "sum1", "in2")

        # Validate
        result = validate_diagram(diagram)

        # Should detect algebraic loop (SS has direct feedthrough via D)
        assert result.is_valid is False
        assert any("algebraic loop" in err.lower() for err in result.errors)


class TestSystemCompleteness:
    """Test system completeness validation (T091)."""

    def test_diagram_without_io_blocks_warning(self):
        """Test that diagram without I/O blocks generates warning."""
        diagram = Diagram()

        # Create diagram with only internal blocks (no I/O markers)
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_connection("c1", "g1", "out", "g2", "in")

        # Validate
        result = validate_diagram(diagram)

        # Should have warning about missing I/O blocks
        assert any(
            "input" in warn.lower() or "output" in warn.lower()
            for warn in result.warnings
        )

    def test_diagram_with_only_input_warning(self):
        """Test that diagram with only input (no output) generates warning."""
        diagram = Diagram()

        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_connection("c1", "in1", "out", "g1", "in")

        # Validate
        result = validate_diagram(diagram)

        # Should have warning about missing output
        assert any("output" in warn.lower() for warn in result.warnings)

    def test_diagram_with_only_output_warning(self):
        """Test that diagram with only output (no input) generates warning."""
        diagram = Diagram()

        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")
        diagram.add_connection("c1", "g1", "out", "out1", "in")

        # Validate
        result = validate_diagram(diagram)

        # Should have warning about missing input
        assert any("input" in warn.lower() for warn in result.warnings)

    def test_complete_system_no_warning(self):
        """Test that complete system (with input and output) has no warnings."""
        diagram = Diagram()

        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        diagram.add_connection("c1", "in1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "out1", "in")

        # Validate
        result = validate_diagram(diagram)

        # Should have no warnings about I/O completeness
        assert not any(
            "input" in warn.lower() or "output" in warn.lower()
            for warn in result.warnings
        )


class TestDisconnectedBlocks:
    """Test disconnected block detection (T092)."""

    def test_disconnected_block_warning(self):
        """Test that disconnected blocks generate warnings."""
        diagram = Diagram()

        # Create connected system
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")
        diagram.add_connection("c1", "in1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "out1", "in")

        # Add disconnected block
        diagram.add_block("gain", "g2", K=2.0)

        # Validate
        result = validate_diagram(diagram)

        # Should have warning about disconnected block
        assert any(
            "disconnected" in warn.lower() or "g2" in warn for warn in result.warnings
        )

    def test_multiple_disconnected_components_warning(self):
        """Test that multiple disconnected components are detected."""
        diagram = Diagram()

        # Component 1: in1 -> g1 -> out1
        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")
        diagram.add_connection("c1", "in1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "out1", "in")

        # Component 2 (disconnected): g2 -> g3
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_block("gain", "g3", K=3.0)
        diagram.add_connection("c3", "g2", "out", "g3", "in")

        # Validate
        result = validate_diagram(diagram)

        # Should warn about disconnected blocks
        assert any("disconnected" in warn.lower() for warn in result.warnings)
        # Should mention the disconnected blocks
        warnings_str = " ".join(result.warnings).lower()
        assert "g2" in warnings_str or "g3" in warnings_str

    def test_fully_connected_diagram_no_warning(self):
        """Test that fully connected diagram has no disconnected warnings."""
        diagram = Diagram()

        diagram.add_block("io_marker", "in1", marker_type="input", label="u")
        diagram.add_block("gain", "g1", K=1.0)
        diagram.add_block("gain", "g2", K=2.0)
        diagram.add_block("io_marker", "out1", marker_type="output", label="y")

        # All blocks connected
        diagram.add_connection("c1", "in1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "g2", "in")
        diagram.add_connection("c3", "g2", "out", "out1", "in")

        # Validate
        result = validate_diagram(diagram)

        # Should have no disconnected warnings
        assert not any("disconnected" in warn.lower() for warn in result.warnings)
