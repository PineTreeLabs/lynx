# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for python-control export functionality.

These tests verify end-to-end workflows from diagram creation to export,
checking transfer function coefficients for correctness. Includes mathematical
validation against Astrom & Murray control theory results.
"""

import control as ct
import numpy as np

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
            num=[2.0],
            den=[1.0, 3.0],
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
            num=[2.0],
            den=[1.0, 3.0],
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
            num=[1.0],
            den=[1.0, 1.0],
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
    """Test subsystem extraction with get_tf() and connection labels.

    Includes mathematical validation against control theory textbooks.
    """

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
            num=[1.0],
            den=[1.0, 1.0],
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

    def test_sensitivity_function_mathematical_validation(self):
        """Extract r→e for sensitivity analysis with mathematical validation.

        Mathematical Validation (Astrom & Murray, Chapter 12):
        System: r → error_sum → controller(K=5) → plant(2/(s+3)) → y
                     ↖────────← negative feedback ←─────┘

        Open-loop: L(s) = P(s)·C(s) = (2/(s+3))·5 = 10/(s+3)
        Sensitivity: S(s) = 1/(1+L(s)) = (s+3)/(s+13)

        Properties:
        - DC gain: 3/13 ≈ 0.231
        - High-frequency gain: 1.0 (error tracks reference at high frequencies)
        - Pole: s = -13
        """
        # Build feedback control system
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "ref_input",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 100},
        )
        diagram.add_block(
            "sum",
            "error_sum",
            signs=["+", "-", "|"],
            position={"x": 100, "y": 100},
            label="e",
        )
        diagram.add_block("gain", "controller", K=5.0, position={"x": 200, "y": 100})
        diagram.add_block(
            "transfer_function",
            "plant",
            num=[2.0],
            den=[1.0, 3.0],
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

        # Extract r→e (sensitivity function)
        # Note: 'e' is block label, must use explicit .out format
        sys_re = diagram.get_ss("r", "e.out")

        # Verify DC gain: 3/13 ≈ 0.231
        dc_gain = ct.dcgain(sys_re)
        expected_dc_gain = 3.0 / 13.0
        assert np.isclose(dc_gain, expected_dc_gain, atol=1e-6), (
            f"DC gain should be {expected_dc_gain}, got {dc_gain}"
        )

        # Verify high-frequency gain approaches 1.0
        high_freq_gain = np.abs(ct.evalfr(sys_re, 1e6j))
        assert np.isclose(high_freq_gain, 1.0, atol=1e-2), (
            f"High-frequency gain should be 1.0, got {high_freq_gain}"
        )

        # Verify pole at s = -13
        poles = ct.poles(sys_re)
        assert np.isclose(poles[0].real, -13.0, atol=1e-6), (
            f"Pole should be at -13, got {poles[0].real}"
        )


class TestOutputMarkerExtraction:
    """Test subsystem extraction using OutputMarker labels."""

    def test_output_marker_to_output_marker(self):
        """Test extraction between two OutputMarker labels.

        This is a regression test for the bug where OutputMarker labels
        were incorrectly injecting at the upstream block's input instead
        of at the block's output, resulting in incorrect transfer functions.
        """
        diagram = Diagram()

        # Create a cascaded system with multiple outputs
        diagram.add_block(
            "io_marker",
            "input",
            marker_type="input",
            label="u",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "controller", K=2.0, position={"x": 100, "y": 0})

        # OutputMarker at controller output
        diagram.add_block(
            "io_marker",
            "tau_marker",
            marker_type="output",
            label="tau",
            position={"x": 150, "y": -50},
        )

        # Integrator plant: 1/s
        diagram.add_block(
            "transfer_function",
            "plant",
            num=[1.0],
            den=[1.0, 0.0],
            position={"x": 200, "y": 0},
        )

        # OutputMarker at plant output
        diagram.add_block(
            "io_marker",
            "rate_marker",
            marker_type="output",
            label="rate",
            position={"x": 250, "y": -50},
        )

        # Connections
        diagram.add_connection("c1", "input", "out", "controller", "in")
        diagram.add_connection("c2", "controller", "out", "tau_marker", "in")
        diagram.add_connection("c3", "controller", "out", "plant", "in")
        diagram.add_connection("c4", "plant", "out", "rate_marker", "in")

        # Extract from tau to rate
        # Expected: TF from controller output to plant output = 1/s
        sys_tau_rate = diagram.get_tf("tau", "rate")

        # Simplify to remove numerical artifacts
        sys_simplified = ct.minreal(sys_tau_rate, tol=1e-6)

        # Verify it's an integrator: 1/s
        assert_tf_equals(sys_simplified, [1.0], [1.0, 0.0])

    def test_output_marker_to_connection_label(self):
        """Test extraction from OutputMarker label to connection label downstream."""
        diagram = Diagram()

        diagram.add_block(
            "io_marker",
            "input",
            marker_type="input",
            label="u",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "gain1", K=3.0, position={"x": 100, "y": 0})

        # OutputMarker at gain1 output
        diagram.add_block(
            "io_marker",
            "mid_marker",
            marker_type="output",
            label="tau",
            position={"x": 150, "y": -50},
        )

        diagram.add_block("gain", "gain2", K=2.0, position={"x": 200, "y": 0})
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        diagram.add_connection("c1", "input", "out", "gain1", "in")
        diagram.add_connection("c2", "gain1", "out", "mid_marker", "in")
        diagram.add_connection("c3", "gain1", "out", "gain2", "in", label="v")
        diagram.add_connection("c4", "gain2", "out", "output", "in", label="z")

        # Extract from OutputMarker 'tau' to connection label 'z' (downstream)
        # Expected: gain = 2.0 (just gain2)
        sys = diagram.get_ss("tau", "z")

        # Should be static gain of 2.0
        dc_gain = ct.dcgain(sys)
        assert np.isclose(dc_gain, 2.0, atol=1e-6), (
            f"DC gain should be 2.0 (gain2), got {dc_gain}"
        )
