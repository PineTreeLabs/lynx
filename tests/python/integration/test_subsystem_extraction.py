# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for get_ss() and get_tf() subsystem extraction.

Tests the break-and-inject approach for extracting arbitrary signal paths.
Includes mathematical validation against Astrom & Murray control theory results.
"""

import control as ct
import numpy as np

from lynx.diagram import Diagram


class TestClosedLoopExtraction:
    """Test extraction of closed-loop transfer functions."""

    def test_closed_loop_reference_to_output(self):
        """Extract r→y for unity feedback system.

        Mathematical Validation (Astrom & Murray, Chapter 11):
        System: r → error_sum → controller(K=5) → plant(2/(s+3)) → y
                          ↖ negative feedback ←─────┘

        Open-loop: L(s) = P(s)·C(s) = (2/(s+3))·5 = 10/(s+3)
        Closed-loop: T(s) = L/(1+L) = 10/(s+13)
        DC gain: 10/13 ≈ 0.769
        Pole: s = -13
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

        # Connect blocks
        diagram.add_connection(
            "c1", "ref_input", "out", "error_sum", "in1"
        )  # Reference
        diagram.add_connection("c2", "error_sum", "out", "controller", "in")  # Error
        diagram.add_connection("c3", "controller", "out", "plant", "in")  # Control
        diagram.add_connection("c4", "plant", "out", "output", "in")  # Output
        diagram.add_connection("c5", "plant", "out", "error_sum", "in2")  # Feedback

        # Extract r→y transfer function
        sys_ry = diagram.get_ss("r", "y")

        # Verify system properties
        assert sys_ry.ninputs == 1, "Should have 1 input (r)"
        assert sys_ry.noutputs == 1, "Should have 1 output (y)"
        assert sys_ry.nstates == 1, "Should have 1 state (from plant)"

        # Verify DC gain: 10/13 ≈ 0.769
        dc_gain = ct.dcgain(sys_ry)
        expected_dc_gain = 10.0 / 13.0
        assert np.isclose(dc_gain, expected_dc_gain, atol=1e-6), (
            f"DC gain should be {expected_dc_gain}, got {dc_gain}"
        )

        # Verify pole at s = -13
        poles = ct.poles(sys_ry)
        assert np.isclose(poles[0].real, -13.0, atol=1e-6), (
            f"Pole should be at -13, got {poles[0].real}"
        )

    def test_sensitivity_function(self):
        """Extract r→e for sensitivity analysis.

        Mathematical Validation (Astrom & Murray, Chapter 12):
        Sensitivity: S(s) = 1/(1+L(s)) = (s+3)/(s+13)
        DC gain: 3/13 ≈ 0.231
        High-frequency gain: 1.0 (error tracks reference at high frequencies)
        Pole: s = -13
        """
        # Build same feedback system as above
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
