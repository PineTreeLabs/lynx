# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for python-control export functionality.

These tests verify end-to-end workflows from diagram creation to export,
checking transfer function coefficients for correctness.
"""

import control as ct
import numpy as np
import pytest

from lynx import Diagram
from lynx.conversion.interconnect import to_interconnect


def assert_tf_equals(actual_sys, expected_num, expected_den, rtol=1e-5):
    """Assert that a system's transfer function matches expected coefficients.

    Args:
        actual_sys: python-control system
        expected_num: Expected numerator coefficients (highest order first)
        expected_den: Expected denominator coefficients (highest order first)
        rtol: Relative tolerance for coefficient comparison
    """
    # Convert to transfer function if needed
    if not isinstance(actual_sys, ct.TransferFunction):
        actual_sys = ct.tf(actual_sys)

    # Get numerator and denominator
    actual_num = actual_sys.num[0][0]
    actual_den = actual_sys.den[0][0]

    # Normalize to make leading coefficient 1
    actual_num = actual_num / actual_den[0]
    actual_den = actual_den / actual_den[0]

    expected_num = np.array(expected_num, dtype=float)
    expected_den = np.array(expected_den, dtype=float)
    expected_num = expected_num / expected_den[0]
    expected_den = expected_den / expected_den[0]

    # Check coefficients match
    assert np.allclose(actual_num, expected_num, rtol=rtol), (
        f"Numerator mismatch: expected {expected_num}, got {actual_num}"
    )
    assert np.allclose(actual_den, expected_den, rtol=rtol), (
        f"Denominator mismatch: expected {expected_den}, got {actual_den}"
    )


class TestSeriesConnection:
    """Test series connection of blocks."""

    def test_series_cascade_gain_and_transfer_function(self):
        """Test series connection: input → gain(K=5) → plant(2/(s+3)) → output.

        Expected: TF = 5 * 2/(s+3) = 10/(s+3)
        """
        diagram = Diagram()

        diagram.add_block(
            "io_marker",
            "input",
            marker_type="input",
            label="u",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "controller", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "transfer_function",
            "plant",
            numerator=[2.0],
            denominator=[1.0, 3.0],
            position={"x": 200, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        diagram.add_connection("c1", "input", "out", "controller", "in")
        diagram.add_connection("c2", "controller", "out", "plant", "in")
        diagram.add_connection("c3", "plant", "out", "output", "in")

        sys = to_interconnect(diagram)

        # Expected: 10/(s+3)
        assert_tf_equals(sys, [10.0], [1.0, 3.0])

    def test_state_space_integrator(self):
        """Test state-space integrator: input → integrator(1/s) → output.

        Expected: TF = 1/s
        """
        diagram = Diagram()

        diagram.add_block(
            "io_marker",
            "input",
            marker_type="input",
            label="u",
            position={"x": 0, "y": 0},
        )

        # State-space block: simple integrator (dx/dt = u, y = x)
        diagram.add_block(
            "state_space",
            "integrator",
            A=[[0.0]],
            B=[[1.0]],
            C=[[1.0]],
            D=[[0.0]],
            position={"x": 100, "y": 0},
        )

        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        diagram.add_connection("c1", "input", "out", "integrator", "in")
        diagram.add_connection("c2", "integrator", "out", "output", "in")

        sys = to_interconnect(diagram)

        # Expected: 1/s
        assert_tf_equals(sys, [1.0], [1.0, 0.0])


class TestSumBlockSignHandling:
    """Test sum block with different sign configurations."""

    def test_sum_all_positive(self):
        """Test sum block with all positive signs: a + b + a.

        Expected: Static MIMO system with output = 2*a + 1*b
        """
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
        diagram.add_block(
            "sum", "sum1", signs=["+", "+", "+"], position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "io_marker",
            "out1",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        diagram.add_connection("c1", "input_a", "out", "sum1", "in1")
        diagram.add_connection("c2", "input_b", "out", "sum1", "in2")
        diagram.add_connection("c3", "input_a", "out", "sum1", "in3")
        diagram.add_connection("c4", "sum1", "out", "out1", "in")

        sys = to_interconnect(diagram)

        # Expected: D matrix = [[2.0, 1.0]] (static MIMO system)
        assert sys.ninputs == 2
        assert sys.noutputs == 1
        assert np.allclose(sys.D, [[2.0, 1.0]], rtol=1e-5), (
            f"Expected D = [[2.0, 1.0]], got {sys.D}"
        )

    def test_sum_mixed_signs(self):
        """Test sum block with mixed signs: a - b + a.

        Expected: Static MIMO system with output = 2*a - 1*b
        """
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
        diagram.add_block(
            "sum", "sum2", signs=["+", "-", "+"], position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "io_marker",
            "out2",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        diagram.add_connection("c1", "input_a", "out", "sum2", "in1")
        diagram.add_connection("c2", "input_b", "out", "sum2", "in2")
        diagram.add_connection("c3", "input_a", "out", "sum2", "in3")
        diagram.add_connection("c4", "sum2", "out", "out2", "in")

        sys = to_interconnect(diagram)

        # Expected: D matrix = [[2.0, -1.0]]
        assert sys.ninputs == 2
        assert sys.noutputs == 1
        assert np.allclose(sys.D, [[2.0, -1.0]], rtol=1e-5), (
            f"Expected D = [[2.0, -1.0]], got {sys.D}"
        )

    def test_sum_with_skipped_port(self):
        """Test sum block with skipped port: a + | - b = a - b.

        Expected: Static MIMO system with output = 1*a - 1*b
        """
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
        diagram.add_block(
            "sum", "sum3", signs=["+", "|", "-"], position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "io_marker",
            "out3",
            marker_type="output",
            label="y",
            position={"x": 200, "y": 0},
        )

        diagram.add_connection("c1", "input_a", "out", "sum3", "in1")
        diagram.add_connection("c2", "input_b", "out", "sum3", "in2")
        diagram.add_connection("c3", "sum3", "out", "out3", "in")

        sys = to_interconnect(diagram)

        # Expected: D matrix = [[1.0, -1.0]]
        assert sys.ninputs == 2
        assert sys.noutputs == 1
        assert np.allclose(sys.D, [[1.0, -1.0]], rtol=1e-5), (
            f"Expected D = [[1.0, -1.0]], got {sys.D}"
        )


class TestNegativeFeedback:
    """Test negative feedback control systems."""

    def test_unity_feedback_first_order_plant(self):
        """Test unity feedback with K=5, plant=2/(s+3).

        System: r → error_sum → gain(5) → plant(2/(s+3)) → y
                     ↖────────← negative feedback ←─────┘

        Expected closed-loop: T(s) = 10/(s+13)
        """
        diagram = Diagram()

        diagram.add_block(
            "io_marker",
            "ref_input",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 100},
        )
        diagram.add_block(
            "sum", "error_sum", signs=["+", "-", "|"], position={"x": 100, "y": 100}
        )
        diagram.add_block("gain", "controller", K=5.0, position={"x": 200, "y": 100})
        diagram.add_block(
            "transfer_function",
            "plant",
            numerator=[2.0],
            denominator=[1.0, 3.0],
            position={"x": 300, "y": 100},
        )
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 400, "y": 100},
        )

        diagram.add_connection("c1", "ref_input", "out", "error_sum", "in1")
        diagram.add_connection("c2", "error_sum", "out", "controller", "in")
        diagram.add_connection("c3", "controller", "out", "plant", "in")
        diagram.add_connection("c4", "plant", "out", "output", "in")
        diagram.add_connection("c5", "plant", "out", "error_sum", "in2")

        sys = to_interconnect(diagram)

        # Expected closed-loop: 10/(s+13)
        assert_tf_equals(sys, [10.0], [1.0, 13.0])

    def test_unity_feedback_simple_plant(self):
        """Test unity feedback with K=5, plant=1/(s+1).

        System: r → error_sum → gain(5) → plant(1/(s+1)) → y
                     ↖────────← negative feedback ←──────┘

        Expected closed-loop: T(s) = 5/(s+6)
        """
        diagram = Diagram()

        diagram.add_block(
            "io_marker",
            "ref_input",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 100},
        )
        diagram.add_block(
            "sum", "error_sum", signs=["+", "-", "|"], position={"x": 100, "y": 100}
        )
        diagram.add_block("gain", "controller", K=5.0, position={"x": 200, "y": 100})
        diagram.add_block(
            "transfer_function",
            "plant",
            numerator=[1.0],
            denominator=[1.0, 1.0],
            position={"x": 300, "y": 100},
        )
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 400, "y": 100},
        )

        diagram.add_connection("c1", "ref_input", "out", "error_sum", "in1")
        diagram.add_connection("c2", "error_sum", "out", "controller", "in")
        diagram.add_connection("c3", "controller", "out", "plant", "in")
        diagram.add_connection("c4", "plant", "out", "output", "in")
        diagram.add_connection("c5", "plant", "out", "error_sum", "in2")

        sys = to_interconnect(diagram)

        # Expected closed-loop: 5/(s+6)
        assert_tf_equals(sys, [5.0], [1.0, 6.0])


class TestSubsystemExtraction:
    """Test subsystem extraction with get_tf() and connection labels."""

    def test_connection_label_extraction(self):
        """Test extracting transfer functions using connection labels.

        System: r → error_sum → controller(5) → plant(1/(s+1)) → y
                     ↖─── feedback ───────────────┘
                          (labeled 'e')   (labeled 'u')

        Tests various subsystem extractions:
        - u → y: Should be just plant = 1/(s+1)
        - e → u: Should be just controller = 5
        - r → y: Should be closed-loop = 5/(s+6)
        - r → u: Should be control signal = 5(s+1)/(s+6)
        - r → e: Should be sensitivity = (s+1)/(s+6)
        """
        diagram = Diagram()

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
        diagram.add_block(
            "gain", "controller", K=5.0, label="controller", position={"x": 200, "y": 0}
        )
        diagram.add_block(
            "transfer_function",
            "plant",
            numerator=[1.0],
            denominator=[1.0, 1.0],
            label="plant",
            position={"x": 300, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 400, "y": 0},
        )

        diagram.add_connection("c1", "ref", "out", "error", "in1")
        diagram.add_connection("c2", "error", "out", "controller", "in", label="e")
        diagram.add_connection("c3", "controller", "out", "plant", "in", label="u")
        diagram.add_connection("c4", "plant", "out", "output", "in")
        diagram.add_connection("c5", "plant", "out", "error", "in2")

        # Test u → y (plant only)
        sys_uy = diagram.get_tf("u", "y")
        assert_tf_equals(sys_uy, [1.0], [1.0, 1.0])  # 1/(s+1)

        # Test e → u (controller only)
        sys_eu = diagram.get_tf("e", "u")
        # Note: This may have pole-zero cancellation, so check DC gain
        dc_gain = ct.dcgain(sys_eu)
        assert np.isclose(dc_gain, 5.0, rtol=0.01), (
            f"Expected DC gain 5.0, got {dc_gain}"
        )

        # Test r → y (closed-loop)
        sys_ry = diagram.get_tf("r", "y")
        assert_tf_equals(sys_ry, [5.0], [1.0, 6.0])  # 5/(s+6)

        # Test r → u (control signal)
        sys_ru = diagram.get_tf("r", "u")
        assert_tf_equals(sys_ru, [5.0, 5.0], [1.0, 6.0])  # (5s+5)/(s+6)

        # Test r → e (sensitivity)
        sys_re = diagram.get_tf("r", "e")
        assert_tf_equals(sys_re, [1.0, 1.0], [1.0, 6.0])  # (s+1)/(s+6)


class TestDiagramValidation:
    """Test diagram validation errors."""

    def test_unconnected_port_error(self):
        """Test that unconnected port raises ValidationError."""
        from lynx.diagram import ValidationError

        diagram = Diagram()
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        diagram.add_block("gain", "gain1", K=2.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 200, "y": 0}
        )

        # Only connect input → gain, forget gain → output
        diagram.add_connection("c1", "input", "out", "gain1", "in")

        with pytest.raises(ValidationError) as exc_info:
            to_interconnect(diagram)

        error = exc_info.value
        assert error.block_id == "output"
        assert error.port_id == "in"
        assert "not connected" in str(error).lower()

    def test_missing_input_marker_error(self):
        """Test that missing InputMarker raises ValidationError."""
        from lynx.diagram import ValidationError

        diagram = Diagram()
        diagram.add_block("gain", "gain1", K=2.0, position={"x": 100, "y": 0})
        diagram.add_block(
            "io_marker", "output", marker_type="output", position={"x": 200, "y": 0}
        )
        diagram.add_connection("c1", "gain1", "out", "output", "in")

        with pytest.raises(ValidationError) as exc_info:
            to_interconnect(diagram)

        assert "InputMarker" in str(exc_info.value)
        assert "at least one" in str(exc_info.value).lower()

    def test_missing_output_marker_error(self):
        """Test that missing OutputMarker raises ValidationError."""
        from lynx.diagram import ValidationError

        diagram = Diagram()
        diagram.add_block(
            "io_marker", "input", marker_type="input", position={"x": 0, "y": 0}
        )
        diagram.add_block("gain", "gain1", K=2.0, position={"x": 100, "y": 0})
        diagram.add_connection("c1", "input", "out", "gain1", "in")

        with pytest.raises(ValidationError) as exc_info:
            to_interconnect(diagram)

        assert "OutputMarker" in str(exc_info.value)
        assert "at least one" in str(exc_info.value).lower()
