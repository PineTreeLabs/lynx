# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for python-control export functionality.

Tests the conversion of Lynx diagrams to python-control InterconnectedSystem objects.
Follows TDD approach: RED-GREEN-REFACTOR cycle.
"""

import numpy as np
import numpy.testing as npt
import pytest

from lynx import Diagram
from lynx.conversion.interconnect import to_interconnect
from lynx.diagram import DiagramExportError, ValidationError


class TestExceptions:
    """Tests for foundational exception types (Phase 2)."""

    def test_validation_error_structure(self):
        """T001: Test ValidationError exception structure."""
        # ValidationError should accept message, optional block_id, optional port_id
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
        assert not hasattr(error, "block_id") or error.block_id is None
        assert not hasattr(error, "port_id") or error.port_id is None

        # With block_id
        error_with_block = ValidationError("Block error", block_id="block_1")
        assert error_with_block.block_id == "block_1"

        # With block_id and port_id
        error_with_port = ValidationError(
            "Port error", block_id="block_1", port_id="in1"
        )
        assert error_with_port.block_id == "block_1"
        assert error_with_port.port_id == "in1"

    def test_diagram_export_error_base_exception(self):
        """T002: Test DiagramExportError base exception."""
        # DiagramExportError should be a base exception for export failures
        error = DiagramExportError("Export failed")
        assert str(error) == "Export failed"
        assert isinstance(error, Exception)

        # ValidationError should inherit from DiagramExportError
        validation_error = ValidationError("Validation failed")
        assert isinstance(validation_error, DiagramExportError)
        assert isinstance(validation_error, Exception)


class TestBasicExport:
    """Tests for export Basic Linear Diagram."""

    def test_gain_block_conversion(self):
        """T005: Test Gain block conversion (K=5.0 → ct.tf(5.0, 1))."""

        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input",
            marker_type="input",
            label="u",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "gain1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        diagram.add_connection("c1", "input", "out", "gain1", "in")
        diagram.add_connection("c2", "gain1", "out", "output", "in")

        sys = to_interconnect(diagram)

        # Verify system properties
        assert sys.ninputs == 1
        assert sys.noutputs == 1

        assert sys.A.shape == (0, 0)  # No states
        assert sys.B.shape == (0, 1)
        assert sys.C.shape == (1, 0)
        assert sys.D.shape == (1, 1)
        assert np.isclose(sys.D[0, 0], 5.0)

    def test_transfer_function_block_conversion(self):
        """T006: Test TransferFunction block conversion (num/den → ct.tf())."""
        import control as ct

        diagram = Diagram()
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        # First-order system: 2/(s+3)
        diagram.add_block(
            "transfer_function",
            "tf1",
            numerator=[2.0],
            denominator=[1.0, 3.0],
            position={"x": 100, "y": 0},
        )
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 200, "y": 0}
        )

        diagram.add_connection("c1", "input", "out", "tf1", "in")
        diagram.add_connection("c2", "tf1", "out", "output", "in")

        sys = to_interconnect(diagram)

        # Check transfer function conversion
        sys_tf = ct.tf(sys)
        npt.assert_allclose(sys_tf.num[0][0], [2.0])
        npt.assert_allclose(sys_tf.den[0][0], [1.0, 3.0])

    def test_state_space_block_conversion(self):
        """T007: Test StateSpace block conversion (A/B/C/D → ct.ss())."""
        import control as ct

        diagram = Diagram()
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        # Integrator: dx/dt = u, y = x
        diagram.add_block(
            "state_space",
            "ss1",
            A=[[0.0]],
            B=[[1.0]],
            C=[[1.0]],
            D=[[0.0]],
            position={"x": 100, "y": 0},
        )
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 200, "y": 0}
        )

        diagram.add_connection("c1", "input", "out", "ss1", "in")
        diagram.add_connection("c2", "ss1", "out", "output", "in")

        sys = to_interconnect(diagram)

        # Verify integrator: step response should be ramp
        t = np.linspace(0, 5, 500)
        t_out, y_out = ct.step_response(sys, t)
        # Slope should be approximately 1.0 for integrator
        slope = (y_out[-1] - y_out[0]) / (t_out[-1] - t_out[0])
        assert np.isclose(slope, 1.0, rtol=0.1)

    def test_sum_block_conversion(self):
        """T008: Test Sum block conversion (signs → ct.summing_junction())."""
        import control as ct

        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input_a",
            marker_type="input",
            label="a",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "input_b",
            marker_type="input",
            label="b",
            position={"x": 0, "y": 100},
        )

        # Sum block: a + b + a (three inputs, all positive)
        diagram.add_block(
            "sum", "sum1", signs=["+", "+", "+"], position={"x": 100, "y": 50}
        )

        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 200, "y": 50}
        )

        diagram.add_connection("c1", "input_a", "out", "sum1", "in1")
        diagram.add_connection("c2", "input_b", "out", "sum1", "in2")
        diagram.add_connection("c3", "input_a", "out", "sum1", "in3")
        diagram.add_connection("c4", "sum1", "out", "output", "in")

        sys = to_interconnect(diagram)

        # With inputs a=1, b=2: output should be 1+2+1=4
        t = np.linspace(0, 1, 100)
        # Two inputs, constant over time: shape (2, 100)
        u = np.array([[1.0] * len(t), [2.0] * len(t)])
        t_out, y_out = ct.input_output_response(sys, t, u)
        assert np.isclose(y_out[0, -1], 4.0, rtol=0.01)

    def test_input_marker_extraction(self):
        """T009: Test InputMarker extraction to inplist."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="u",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "gain1", K=2.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker", "output1", marker_type="output", position={"x": 200, "y": 0}
        )

        diagram.add_connection("c1", "input1", "out", "gain1", "in")
        diagram.add_connection("c2", "gain1", "out", "output1", "in")

        sys = to_interconnect(diagram)

        # System should have 1 input from InputMarker
        assert sys.ninputs == 1
        # Input name should be 'input1.out' (inplist entry)
        # Note: python-control doesn't expose inplist directly,
        # but we verify via ninputs

    def test_output_marker_extraction(self):
        """T010: Test OutputMarker extraction to outlist."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker", "input1", marker_type="input", position={"x": 0, "y": 0}
        )
        diagram.add_block("gain", "gain1", K=3.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        diagram.add_connection("c1", "input1", "out", "gain1", "in")
        diagram.add_connection("c2", "gain1", "out", "output1", "in")

        sys = to_interconnect(diagram)

        # System should have 1 output to OutputMarker
        assert sys.noutputs == 1
        # Output name should be 'output1.in' (outlist entry)

    def test_connection_mapping(self):
        """T011: Connection mapping (Lynx Connection → ['source.port',
        'target.port'])."""

        diagram = Diagram()
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        diagram.add_block("gain", "g1", K=2.0, position={"x": 100, "y": 0})
        diagram.add_block("gain", "g2", K=3.0, position={"x": 200, "y": 0})
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 300, "y": 0}
        )

        diagram.add_connection("c1", "input", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "g2", "in")
        diagram.add_connection("c3", "g2", "out", "output", "in")

        sys = to_interconnect(diagram)

        # Cascade of gains: 2 * 3 = 6 (pure feedthrough)
        assert sys.ninputs == 1
        assert sys.noutputs == 1

        assert sys.A.shape == (0, 0)  # No states
        assert sys.B.shape == (0, 1)
        assert sys.C.shape == (1, 0)
        assert sys.D.shape == (1, 1)
        assert np.isclose(sys.D[0, 0], 6.0)


class TestSumBlockSignHandling:
    """Tests for sum block sign configuration handling."""

    def test_get_sign_for_port_basic(self):
        """T026: Test get_sign_for_port() with signs=["+", "-", "|"]
        → port in1="+", in2="-"."""
        from lynx.blocks.sum import SumBlock

        # Create sum block with mixed signs: top (+), left (-), bottom unused (|)
        sum_block = SumBlock(
            id="sum1", signs=["+", "-", "|"], position={"x": 0, "y": 0}
        )

        # Port in1 should map to signs[0] = "+"
        sign1 = sum_block.get_port_sign("in1")
        assert sign1 == "+"

        # Port in2 should map to signs[1] = "-"
        sign2 = sum_block.get_port_sign("in2")
        assert sign2 == "-"

    def test_get_sign_for_port_all_positive(self):
        """T027: Test get_sign_for_port() with signs=["+", "+", "+"]
        → all ports positive."""
        from lynx.blocks.sum import SumBlock

        sum_block = SumBlock(
            id="sum2", signs=["+", "+", "+"], position={"x": 0, "y": 0}
        )

        # All ports should be positive
        assert sum_block.get_port_sign("in1") == "+"
        assert sum_block.get_port_sign("in2") == "+"
        assert sum_block.get_port_sign("in3") == "+"

    def test_get_sign_for_port_skipped_middle(self):
        """T028: Test get_sign_for_port() with signs=["+", "|", "-"]
        → in1="+", in2="-" (skipped middle)."""
        from lynx.blocks.sum import SumBlock

        # Top (+), left skipped (|), bottom (-)
        sum_block = SumBlock(
            id="sum3", signs=["+", "|", "-"], position={"x": 0, "y": 0}
        )

        # Port in1 → signs[0] = "+"
        sign1 = sum_block.get_port_sign("in1")
        assert sign1 == "+"

        # Port in2 → signs[2] = "-" (skipped signs[1])
        sign2 = sum_block.get_port_sign("in2")
        assert sign2 == "-"

    def test_connection_negation_for_negative_sign(self):
        """T029: Test connection negation applied when target port has "-" sign."""
        import control as ct

        diagram = Diagram()

        # Create system with negative feedback and dynamics (to avoid algebraic loop)
        diagram.add_block(
            "io_marker",
            "ref",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "sum", "error", signs=["+", "-", "|"], position={"x": 100, "y": 0}
        )
        diagram.add_block("gain", "controller", K=5.0, position={"x": 200, "y": 0})
        # Add plant with dynamics: 1/(s+1) to avoid algebraic loop
        diagram.add_block(
            "transfer_function",
            "plant",
            numerator=[1.0],
            denominator=[1.0, 1.0],  # 1/(s+1)
            position={"x": 300, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 400, "y": 0},
        )

        # Connections: ref → sum.in1 (+), plant.out → sum.in2 (-),
        # sum → controller → plant → output
        diagram.add_connection("c1", "ref", "out", "error", "in1")
        diagram.add_connection("c2", "error", "out", "controller", "in")
        diagram.add_connection("c3", "controller", "out", "plant", "in")
        diagram.add_connection("c4", "plant", "out", "output", "in")
        diagram.add_connection(
            "c5", "plant", "out", "error", "in2"
        )  # Negative feedback

        sys = to_interconnect(diagram)

        # System should have 1 input, 1 output
        assert sys.ninputs == 1
        assert sys.noutputs == 1

        # Transfer function: G(s) = 5/(s+1), Closed-loop: G/(1+G) = 5/(s+6)
        sys_tf = ct.tf(sys)
        npt.assert_allclose(sys_tf.num[0][0], [5.0])
        npt.assert_allclose(sys_tf.den[0][0], [1.0, 6.0])

        # With unit step input, closed-loop should stabilize
        # DC gain should be 5/6 ≈ 0.833
        t = np.linspace(0, 10, 1000)
        t_out, y_out = ct.step_response(sys, t)

        # Final value should approach 5/(1+5) = 5/6 ≈ 0.833
        expected_final = 5.0 / (1.0 + 5.0)
        assert np.isclose(y_out[-1], expected_final, rtol=0.05)


class TestDiagramValidation:
    """Tests for diagram validation before export."""

    def test_missing_input_marker_error(self):
        """Test validation error for missing InputMarker."""
        from lynx.diagram import ValidationError

        diagram = Diagram()

        # Create diagram with no InputMarker (only output)
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 200, "y": 0}
        )
        diagram.add_connection("c1", "g1", "out", "output", "in")

        # Should raise ValidationError for missing InputMarker
        with pytest.raises(ValidationError) as exc_info:
            to_interconnect(diagram)

        assert "InputMarker" in str(exc_info.value)
        assert "at least one" in str(exc_info.value).lower()

    def test_missing_output_marker_error(self):
        """T040: Test validation error for missing OutputMarker."""
        from lynx.diagram import ValidationError

        diagram = Diagram()

        # Create diagram with no OutputMarker (only input)
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_connection("c1", "input", "out", "g1", "in")

        # Should raise ValidationError for missing OutputMarker
        with pytest.raises(ValidationError) as exc_info:
            to_interconnect(diagram)

        assert "OutputMarker" in str(exc_info.value)
        assert "at least one" in str(exc_info.value).lower()

    def test_unconnected_input_port_error(self):
        """T041: Test validation error for unconnected input port
        (identifies block + port)."""
        from lynx.diagram import ValidationError

        diagram = Diagram()

        # Create diagram with unconnected gain input
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "gain", "g2", K=3.0, position={"x": 200, "y": 0}
        )  # g2.in is not connected
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 300, "y": 0}
        )

        diagram.add_connection("c1", "input", "out", "g1", "in")
        # Missing: connection to g2.in
        diagram.add_connection("c2", "g2", "out", "output", "in")

        # Should raise ValidationError mentioning the unconnected port
        with pytest.raises(ValidationError) as exc_info:
            to_interconnect(diagram)

        error_msg = str(exc_info.value).lower()
        assert "g2" in error_msg, "Error should mention block 'g2'"
        assert "in" in error_msg or "input" in error_msg, (
            "Error should mention input port"
        )
        assert "not connected" in error_msg, (
            "Error should mention port is not connected"
        )

    def test_validation_passes_for_complete_diagram(self):
        """T042: Test validation passes when diagram is complete."""

        diagram = Diagram()

        # Create complete, valid diagram
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 200, "y": 0}
        )

        diagram.add_connection("c1", "input", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "output", "in")

        # Should NOT raise any validation error
        sys = to_interconnect(diagram)

        # Verify it actually works
        assert sys.ninputs == 1
        assert sys.noutputs == 1

    def test_duplicate_block_labels_error(self):
        """Duplicate block labels should result in validation error."""
        from lynx.conversion.interconnect import validate_for_export

        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "gain", "g2", K=3.0, label="controller", position={"x": 150, "y": 0}
        )  # Duplicate!
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        # Connect ALL blocks properly (validation requires all input ports connected)
        diagram.add_connection("c1", "input1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "g2", "in")
        diagram.add_connection("c3", "g2", "out", "output1", "in")

        # validate_for_export now returns ValidationResult
        result = validate_for_export(diagram)

        assert not result.is_valid, "Diagram with duplicate labels should be invalid"
        assert len(result.errors) > 0, "Should have errors for duplicate labels"
        assert any(
            "duplicate" in err.lower() and "controller" in err.lower()
            for err in result.errors
        )

    def test_duplicate_connection_labels_error(self):
        """Duplicate connection labels should result in validation error."""
        from lynx.conversion.interconnect import validate_for_export

        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block("gain", "g2", K=3.0, position={"x": 150, "y": 0})
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        # Create duplicate connection labels
        diagram.add_connection("c1", "input1", "out", "g1", "in", label="signal")
        diagram.add_connection(
            "c2", "g1", "out", "g2", "in", label="signal"
        )  # Duplicate!
        diagram.add_connection("c3", "g2", "out", "output1", "in")

        # validate_for_export now returns ValidationResult
        result = validate_for_export(diagram)

        assert not result.is_valid, "Diagram with duplicate labels should be invalid"
        assert len(result.errors) > 0, "Should have errors for duplicate labels"
        assert any(
            "duplicate" in err.lower() and "signal" in err.lower()
            for err in result.errors
        )

    def test_get_ss_validates_diagram(self):
        """get_ss() should validate diagram before extraction
        and raise ValidationError on failure."""
        from lynx.diagram import ValidationError

        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 100, "y": 0}
        )
        # Missing output marker and g1 input not connected

        with pytest.raises(ValidationError) as exc_info:
            diagram.get_ss("r", "controller.out")

        # Should mention validation failure
        assert "validation failed" in str(exc_info.value).lower()
