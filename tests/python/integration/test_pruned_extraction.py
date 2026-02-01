# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for pruned subsystem extraction."""

import pytest
import numpy as np
import control as ct
from lynx import Diagram


class TestUS1SingleBlockExtraction:
    """User Story 1: Extract single block without downstream coupling."""

    def test_scenario_1_single_block_with_downstream_feedback(self):
        """Test Scenario 1 from quickstart.md: extract plant without downstream feedback coupling."""
        diagram = Diagram()

        # Create diagram with DYNAMIC downstream feedback to show the bug
        # u → controller → [signal_x] → plant(1/(s+2)) → y
        #                                      ↓
        #                               feedback_filter(1/(s+1)) → back to plant
        diagram.add_block("io_marker", "input", marker_type="input", label="u")
        diagram.add_block("gain", "controller", K=2.0)
        diagram.add_block("transfer_function", "plant", num=[1.0], den=[1.0, 2.0])  # 1st order
        diagram.add_block("io_marker", "output", marker_type="output", label="y")
        diagram.add_block("transfer_function", "feedback_filter", num=[1.0], den=[1.0, 1.0])  # Adds state

        diagram.add_connection("c1", "input", "out", "controller", "in")
        diagram.add_connection("c2", "controller", "out", "plant", "in", label="signal_x")
        diagram.add_connection("c3", "plant", "out", "output", "in")
        diagram.add_connection("c4", "plant", "out", "feedback_filter", "in")  # Downstream
        diagram.add_connection("c5", "feedback_filter", "out", "plant", "in")  # Creates 2nd-order loop

        # Extract just signal_x → y
        # WITHOUT pruning: would include feedback_filter → 2 states
        # WITH pruning: should be just plant → 1 state
        sys = diagram.get_ss("signal_x", "y")

        # ACCEPTANCE: Should be 1st-order (just plant), not 2nd-order
        assert sys.nstates == 1, f"Expected 1 state (plant only), got {sys.nstates} (includes feedback)"

    def test_acceptance_1a_simple_chain_with_middle_block(self):
        """Test acceptance scenario 1a: A→B→C, extract just B."""
        diagram = Diagram()
        diagram.add_block("io_marker", "input", marker_type="input", label="u")
        diagram.add_block("gain", "A", K=2.0, label="A")
        diagram.add_block("gain", "B", K=3.0, label="B")
        diagram.add_block("gain", "C", K=5.0, label="C")
        diagram.add_block("io_marker", "output", marker_type="output", label="y")

        diagram.add_connection("c1", "input", "out", "A", "in", label="u_sig")
        diagram.add_connection("c2", "A", "out", "B", "in", label="a_out")
        diagram.add_connection("c3", "B", "out", "C", "in", label="b_out")
        diagram.add_connection("c4", "C", "out", "output", "in")

        # Extract just B (from A output to B output)
        sys = diagram.get_ss("a_out", "b_out")

        # Should be just B's gain = 3.0 (pure gain, no states)
        assert sys.nstates == 0
        assert np.allclose(ct.dcgain(sys), 3.0)

    def test_acceptance_1c_feedforward_path_excludes_downstream(self):
        """Test extracting feedforward path excludes unrelated downstream blocks."""
        diagram = Diagram()
        diagram.add_block("io_marker", "input", marker_type="input", label="u")
        diagram.add_block("gain", "A", K=2.0)
        diagram.add_block("gain", "B", K=3.0)
        diagram.add_block("gain", "C_downstream", K=5.0)  # Unrelated downstream
        diagram.add_block("io_marker", "output", marker_type="output", label="y")

        diagram.add_connection("c1", "input", "out", "A", "in", label="u_sig")
        diagram.add_connection("c2", "A", "out", "B", "in", label="a_to_b")
        diagram.add_connection("c3", "B", "out", "C_downstream", "in", label="b_out")
        diagram.add_connection("c4", "C_downstream", "out", "output", "in")

        # Extract u_sig → b_out (should be A*B = 6, excluding C_downstream)
        sys = diagram.get_ss("u_sig", "b_out")

        # Should be A*B = 2*3 = 6 (no C_downstream)
        assert sys.nstates == 0, f"Expected 0 states (gains only), got {sys.nstates}"
        assert np.allclose(ct.dcgain(sys), 6.0)


class TestUS2InternalFeedback:
    """User Story 2: Preserve internal feedback loops."""

    def test_scenario_2_inner_loop_with_external_cascade(self):
        """Test Scenario 2 from quickstart.md: extract inner loop, exclude outer controller."""
        diagram = Diagram()

        # External cascade controller (upstream of extraction)
        diagram.add_block("io_marker", "ext_input", marker_type="input", label="r")
        diagram.add_block("gain", "outer_controller", K=3.0)

        # Inner loop with feedback
        diagram.add_block("sum", "inner_sum", signs=["+", "-", "|"])
        diagram.add_block("gain", "inner_controller", K=5.0)
        diagram.add_block("transfer_function", "inner_plant", num=[1.0], den=[1.0, 2.0])
        diagram.add_block("io_marker", "output", marker_type="output", label="y")

        # Connections
        diagram.add_connection("c1", "ext_input", "out", "outer_controller", "in")
        diagram.add_connection("c2", "outer_controller", "out", "inner_sum", "in1", label="inner_ref")
        diagram.add_connection("c3", "inner_sum", "out", "inner_controller", "in")
        diagram.add_connection("c4", "inner_controller", "out", "inner_plant", "in")
        diagram.add_connection("c5", "inner_plant", "out", "output", "in")
        diagram.add_connection("c6", "inner_plant", "out", "inner_sum", "in2")  # Inner feedback

        # Extract just the inner loop (inner_ref → y)
        sys = diagram.get_ss("inner_ref", "y")

        # Should include: inner_sum, inner_controller, inner_plant (with feedback)
        # Should exclude: outer_controller (upstream)
        # Closed-loop TF: 5/(s+2+5) = 5/(s+7)
        assert sys.nstates == 1, f"Expected 1 state (closed inner loop), got {sys.nstates}"
        dc_gain = ct.dcgain(sys)
        expected_dc_gain = 5.0 / 7.0  # 5/(2+5)
        assert np.allclose(dc_gain, expected_dc_gain, rtol=1e-3)

    def test_acceptance_2a_inner_outer_loop_extraction(self):
        """Test extracting inner loop from nested control structure."""
        diagram = Diagram()

        diagram.add_block("io_marker", "input", marker_type="input", label="r")
        diagram.add_block("sum", "outer_sum", signs=["+", "-", "|"])
        diagram.add_block("gain", "outer_ctrl", K=2.0)
        diagram.add_block("sum", "inner_sum", signs=["+", "-", "|"])
        diagram.add_block("gain", "inner_ctrl", K=3.0)
        diagram.add_block("transfer_function", "plant", num=[1.0], den=[1.0, 1.0])
        diagram.add_block("io_marker", "output", marker_type="output", label="y")

        # Outer loop
        diagram.add_connection("c1", "input", "out", "outer_sum", "in1")
        diagram.add_connection("c2", "outer_sum", "out", "outer_ctrl", "in")
        diagram.add_connection("c3", "outer_ctrl", "out", "inner_sum", "in1", label="inner_ref")

        # Inner loop
        diagram.add_connection("c4", "inner_sum", "out", "inner_ctrl", "in")
        diagram.add_connection("c5", "inner_ctrl", "out", "plant", "in")
        diagram.add_connection("c6", "plant", "out", "output", "in", label="y_sig")
        diagram.add_connection("c7", "plant", "out", "inner_sum", "in2")  # Inner feedback
        diagram.add_connection("c8", "plant", "out", "outer_sum", "in2")  # Outer feedback

        # Extract inner loop only
        sys = diagram.get_ss("inner_ref", "y_sig")

        # Should include inner_sum, inner_ctrl, plant with inner feedback
        # Should exclude outer_sum, outer_ctrl (upstream)
        assert sys.nstates == 1  # Plant is 1st order, inner loop preserves this

    def test_feedback_blocks_in_both_directions(self):
        """Test that blocks in feedback loop are reachable both forward and backward."""
        diagram = Diagram()
        diagram.add_block("io_marker", "input", marker_type="input", label="u")
        diagram.add_block("sum", "sum_block", signs=["+", "-", "|"])
        diagram.add_block("gain", "controller", K=2.0)
        diagram.add_block("transfer_function", "plant", num=[1.0], den=[1.0, 1.0])
        diagram.add_block("io_marker", "output", marker_type="output", label="y")

        diagram.add_connection("c1", "input", "out", "sum_block", "in1")
        diagram.add_connection("c2", "sum_block", "out", "controller", "in")
        diagram.add_connection("c3", "controller", "out", "plant", "in")
        diagram.add_connection("c4", "plant", "out", "output", "in")
        diagram.add_connection("c5", "plant", "out", "sum_block", "in2")  # Feedback

        # Extract full closed loop
        sys = diagram.get_ss("u", "y")

        # All blocks should be included
        assert sys.nstates == 1  # Plant order preserved
        # Verify closed-loop DC gain
        cl_gain = ct.dcgain(sys)
        expected = (2.0 * 1.0) / (1 + 2.0 * 1.0)  # 2/3
        assert np.allclose(cl_gain, expected, rtol=1e-3)


class TestUS3ParallelPaths:
    """User Story 3: Handle complex path topologies."""

    def test_scenario_3_parallel_paths_with_side_branch(self):
        """Test Scenario 3 from quickstart.md: feedforward + feedback paths, exclude side branch."""
        diagram = Diagram()

        diagram.add_block("io_marker", "input", marker_type="input", label="u")
        diagram.add_block("sum", "sum1", signs=["+", "+", "|"])

        # Feedforward path
        diagram.add_block("gain", "ff_gain", K=1.0)

        # Feedback path
        diagram.add_block("gain", "fb_gain", K=0.5)

        diagram.add_block("io_marker", "output", marker_type="output", label="y")

        # Unrelated side branch
        diagram.add_block("gain", "side_branch", K=0.1)

        # Connections
        diagram.add_connection("c1", "input", "out", "ff_gain", "in")
        diagram.add_connection("c2", "input", "out", "fb_gain", "in")
        diagram.add_connection("c3", "ff_gain", "out", "sum1", "in1")
        diagram.add_connection("c4", "fb_gain", "out", "sum1", "in2")
        diagram.add_connection("c5", "sum1", "out", "output", "in")
        diagram.add_connection("c6", "sum1", "out", "side_branch", "in")  # Not on path

        # Extract u → y
        sys = diagram.get_ss("u", "y")

        # Should include: ff_gain, fb_gain, sum1 (all on parallel paths)
        # Should exclude: side_branch (downstream, not on path)
        dc_gain = ct.dcgain(sys)
        expected = 1.0 + 0.5  # 1.5
        assert np.allclose(dc_gain, expected, rtol=1e-3)

    def test_acceptance_3a_feedforward_plus_feedback_exclude_branch(self):
        """Test parallel feedforward and feedback paths with unrelated branch D."""
        diagram = Diagram()

        diagram.add_block("io_marker", "input", marker_type="input", label="u")
        diagram.add_block("gain", "A", K=2.0)  # Feedforward
        diagram.add_block("gain", "B", K=3.0)  # Feedback
        diagram.add_block("gain", "C", K=4.0)  # Feedforward continues
        diagram.add_block("sum", "combiner", signs=["+", "+", "|"])
        diagram.add_block("gain", "D", K=5.0)  # Unrelated branch
        diagram.add_block("io_marker", "output", marker_type="output", label="y")

        # Feedforward: u → A → C → combiner
        diagram.add_connection("c1", "input", "out", "A", "in")
        diagram.add_connection("c2", "A", "out", "C", "in")
        diagram.add_connection("c3", "C", "out", "combiner", "in1")

        # Feedback: u → B → combiner
        diagram.add_connection("c4", "input", "out", "B", "in")
        diagram.add_connection("c5", "B", "out", "combiner", "in2")

        # Output
        diagram.add_connection("c6", "combiner", "out", "output", "in")

        # Unrelated: u → D (not connected to output)
        diagram.add_connection("c7", "input", "out", "D", "in")

        # Extract u → y
        sys = diagram.get_ss("u", "y")

        # Should include A, B, C, combiner (both paths)
        # Should exclude D (not on path to y)
        dc_gain = ct.dcgain(sys)
        expected = (2.0 * 4.0) + 3.0  # A*C + B = 8 + 3 = 11
        assert np.allclose(dc_gain, expected, rtol=1e-3)

    def test_parallel_paths_unit_verification(self):
        """Verify parallel path blocks appear in intersection."""
        from lynx.conversion.graph_pruning import _find_reachable_blocks

        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        diagram.add_block("sum", "D", signs=["+", "+", "|"])  # Sum to accept multiple inputs

        # A → B → D (path 1)
        # A → C → D (path 2)
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "D", "in1")
        diagram.add_connection("c3", "A", "out", "C", "in")
        diagram.add_connection("c4", "C", "out", "D", "in2")

        block_a = diagram.get_block("A")
        block_d = diagram.get_block("D")

        path_blocks = _find_reachable_blocks(diagram, block_a, block_d)

        # Should include all blocks (both paths)
        assert path_blocks == {"A", "B", "C", "D"}


class TestEdgeCases:
    """Edge cases and error handling."""
    pass


class TestPerformance:
    """Performance benchmarks."""
    pass
