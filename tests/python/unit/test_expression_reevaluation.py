# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for expression re-evaluation on diagram load."""

import numpy as np

from lynx.diagram import Diagram


class TestExpressionReEvaluation:
    """Test re-evaluation of expressions after diagram load."""

    def test_re_evaluate_with_updated_variable(self):
        """Test that expressions re-evaluate when variables change."""
        # Create diagram with expression
        diagram = Diagram()
        block = diagram.add_block("gain", "g1", K=2.5)

        # Simulate expression being stored (would normally happen in widget)
        for param in block._parameters:
            if param.name == "K":
                param.value = 2.5
                param.expression = "kp"

        # Now kp changes in notebook
        updated_namespace = {"kp": 5.0}

        # Re-evaluate
        warnings = diagram.re_evaluate_expressions(updated_namespace)

        # Value should update
        assert block.get_parameter("K") == 5.0
        assert len(warnings) == 0

    def test_re_evaluate_with_missing_variable(self):
        """Test fallback when variable is missing."""
        diagram = Diagram()
        block = diagram.add_block("gain", "g1", K=2.5)

        # Set expression and value
        for param in block._parameters:
            if param.name == "K":
                param.value = 2.5
                param.expression = "kp"

        # Variable missing in namespace
        namespace = {}

        # Re-evaluate
        warnings = diagram.re_evaluate_expressions(namespace)

        # Value should remain unchanged (fallback)
        assert block.get_parameter("K") == 2.5
        assert len(warnings) == 1
        assert "kp" in warnings[0]
        assert (
            "not found" in warnings[0].lower() or "not defined" in warnings[0].lower()
        )

    def test_re_evaluate_skips_parameters_without_expressions(self):
        """Test that parameters without expressions are unchanged."""
        diagram = Diagram()
        block = diagram.add_block("gain", "g1", K=3.5)

        # Parameter has value but no expression
        for param in block._parameters:
            if param.name == "K":
                param.expression = None  # No expression

        namespace = {"kp": 10.0}

        # Re-evaluate
        warnings = diagram.re_evaluate_expressions(namespace)

        # Value should remain unchanged
        assert block.get_parameter("K") == 3.5
        assert len(warnings) == 0

    def test_re_evaluate_with_array_expression(self):
        """Test re-evaluation with array expressions."""
        diagram = Diagram()
        block = diagram.add_block(
            "transfer_function", "tf1", numerator=[1, 2], denominator=[1, 3, 2]
        )

        # Set expression for numerator
        for param in block._parameters:
            if param.name == "numerator":
                param.value = np.array([1.0, 2.0])
                param.expression = "num_coeffs"

        # Variable available in namespace
        namespace = {"num_coeffs": [2.0, 4.0]}

        # Re-evaluate
        warnings = diagram.re_evaluate_expressions(namespace)

        # Value should update
        result = block.get_parameter("numerator")
        assert np.allclose(result, [2.0, 4.0])
        assert len(warnings) == 0

    def test_re_evaluate_with_matrix_expression(self):
        """Test re-evaluation with matrix expressions."""
        diagram = Diagram()
        block = diagram.add_block(
            "state_space", "ss1", A=[[1, 0], [0, 1]], B=[[1], [0]], C=[[1, 0]], D=[[0]]
        )

        # Set expression for A matrix
        for param in block._parameters:
            if param.name == "A":
                param.value = np.array([[1.0, 0.0], [0.0, 1.0]])
                param.expression = "A_matrix"

        # Variable available in namespace
        namespace = {"A_matrix": [[2.0, 1.0], [1.0, 2.0]]}

        # Re-evaluate
        warnings = diagram.re_evaluate_expressions(namespace)

        # Value should update
        result = block.get_parameter("A")
        assert np.allclose(result, [[2.0, 1.0], [1.0, 2.0]])
        assert len(warnings) == 0

    def test_re_evaluate_with_invalid_expression(self):
        """Test handling of invalid expressions."""
        diagram = Diagram()
        block = diagram.add_block("gain", "g1", K=2.5)

        # Set invalid expression
        for param in block._parameters:
            if param.name == "K":
                param.value = 2.5
                param.expression = "1 + "  # Syntax error

        namespace = {}

        # Re-evaluate
        warnings = diagram.re_evaluate_expressions(namespace)

        # Value should remain unchanged (fallback), warning generated
        assert block.get_parameter("K") == 2.5
        assert len(warnings) == 1
        assert "K" in warnings[0]

    def test_re_evaluate_multiple_blocks(self):
        """Test re-evaluation across multiple blocks."""
        diagram = Diagram()

        # Create multiple blocks with expressions
        g1 = diagram.add_block("gain", "g1", K=2.0)
        g2 = diagram.add_block("gain", "g2", K=3.0)

        # Set expressions
        for param in g1._parameters:
            if param.name == "K":
                param.value = 2.0
                param.expression = "kp"

        for param in g2._parameters:
            if param.name == "K":
                param.value = 3.0
                param.expression = "kp * 1.5"

        # Variables available in namespace
        namespace = {"kp": 4.0}

        # Re-evaluate
        warnings = diagram.re_evaluate_expressions(namespace)

        # Both values should update
        assert g1.get_parameter("K") == 4.0
        assert g2.get_parameter("K") == 6.0
        assert len(warnings) == 0
