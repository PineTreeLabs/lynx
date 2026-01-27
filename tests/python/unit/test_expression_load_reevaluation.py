# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for automatic expression re-evaluation during diagram load.

This test file demonstrates the bug: expressions should be automatically
re-evaluated during Diagram.load() and Diagram.from_dict() when variables
are available in the Python environment, but currently they are not.
"""

import numpy as np
import pytest

from lynx.diagram import Diagram


class TestExpressionLoadReEvaluation:
    """Test automatic re-evaluation of expressions during diagram load."""

    def test_load_reevaluates_expressions_with_current_namespace(self, tmp_path):
        """Test that loading a diagram re-evaluates expressions from current namespace.

        EXPECTED BEHAVIOR:
        When a diagram is loaded, expressions should be re-evaluated against
        the current Python environment. If variables are available, the values
        should be recomputed. If variables are missing, stored values are used
        as fallback.

        CURRENT BUG:
        Expressions are preserved during load but NOT re-evaluated. This means
        parameter values remain at their stored values even when corresponding
        variables exist in the current environment.
        """
        # Step 1: Create diagram with original variable values
        kp_original = 2.5
        ki_original = 0.5

        diagram1 = Diagram()
        block = diagram1.add_block("gain", "g1", K=kp_original)

        # Simulate expression being stored (would normally happen in widget)
        for param in block._parameters:
            if param.name == "K":
                param.expression = "kp"
                param.value = kp_original

        # Save to file
        filepath = tmp_path / "test_diagram.json"
        diagram1.save(filepath)

        # Step 2: In a new session, variables have DIFFERENT values
        kp_current = 5.0  # CHANGED
        ki_current = 1.0  # CHANGED

        # Step 3: Load diagram - expressions should re-evaluate with NEW values
        # TODO: Need mechanism to pass namespace to load()
        diagram2 = Diagram.load(filepath)

        # THIS TEST WILL FAIL - showing the bug
        # Expected: K should be re-evaluated to kp_current (5.0)
        # Actual: K remains at stored value kp_original (2.5)
        block2 = diagram2.get_block("g1")

        # This assertion FAILS, demonstrating the bug
        # Expected: 5.0 (from kp_current)
        # Actual: 2.5 (from stored value)
        assert block2.get_parameter("K") == kp_current, (
            f"Expected K to be re-evaluated to {kp_current}, "
            f"but got stored value {block2.get_parameter('K')}"
        )

    def test_from_dict_with_namespace_reevaluates_expressions(self):
        """Test that from_dict() with namespace re-evaluates expressions.

        PROPOSED API:
        Diagram.from_dict(data, namespace=...)  # Pass namespace for re-evaluation
        """
        # Create diagram data with expression
        data = {
            "version": "1.0.0",
            "blocks": [
                {
                    "id": "g1",
                    "type": "gain",
                    "position": {"x": 100, "y": 100},
                    "parameters": [
                        {
                            "name": "K",
                            "value": 2.5,  # Old value
                            "expression": "kp",  # Expression
                        }
                    ],
                    "ports": [
                        {"id": "in", "type": "input"},
                        {"id": "out", "type": "output"},
                    ],
                }
            ],
            "connections": [],
        }

        # Current namespace has different value
        namespace = {"kp": 5.0}

        # Load with namespace (API doesn't exist yet - will fail)
        # diagram = Diagram.from_dict(data, namespace=namespace)

        # For now, test manual re-evaluation
        diagram = Diagram.from_dict(data)
        diagram.re_evaluate_expressions(namespace)

        # After re-evaluation, value should match namespace
        block = diagram.get_block("g1")
        assert block.get_parameter("K") == 5.0

    def test_load_with_comma_separated_expression(self, tmp_path):
        """Test that comma-separated expressions evaluate to arrays, not tuples.

        BUG #2: Comma-separated expressions like "kp, ki" evaluate to tuples
        instead of arrays/lists, which causes type mismatches.
        """
        # Create transfer function with comma-separated expression
        diagram1 = Diagram()
        block = diagram1.add_block(
            "transfer_function", "tf1", num=[611.0, 63.0], den=[1, 0]
        )

        # Set expression for numerator
        for param in block._parameters:
            if param.name == "num":
                param.expression = "kp, ki"
                param.value = [611.0, 63.0]

        # Save
        filepath = tmp_path / "test_tf.json"
        diagram1.save(filepath)

        # Load and manually re-evaluate
        kp = 500.0
        ki = 50.0
        namespace = {"kp": kp, "ki": ki}

        diagram2 = Diagram.load(filepath)
        diagram2.re_evaluate_expressions(namespace)

        # Check result
        block2 = diagram2.get_block("tf1")
        result = block2.get_parameter("num")

        # BUG: Result is a tuple (500.0, 50.0) instead of array [500.0, 50.0]
        # This causes type mismatches in python-control export
        assert isinstance(result, (list, np.ndarray)), (
            f"Expected list or array, got {type(result).__name__}: {result}"
        )

        # Values should match
        if isinstance(result, np.ndarray):
            assert np.allclose(result, [kp, ki])
        else:
            assert result == [kp, ki]

    def test_load_cruise_control_with_expressions(self):
        """Test loading the actual cruise control diagram with re-evaluation.

        This is the real-world test case reported by the user.
        """
        # Define current environment variables
        b = 1.32
        a = 0.0101
        kp = 611.0
        ki = 63.0

        # Load diagram
        diagram = Diagram.load("local/release/cruise-control.json")

        # Manually re-evaluate (should be automatic, but test current workaround)
        namespace = {"b": b, "a": a, "kp": kp, "ki": ki}
        warnings = diagram.re_evaluate_expressions(namespace)

        # Check that controller numerator was re-evaluated
        controller = diagram.get_block("transfer_function_1769426900123")
        result = controller.get_parameter("num")

        # Should match current namespace values
        assert np.allclose(result, [kp, ki]), (
            f"Expected controller num=[{kp}, {ki}], got {result}"
        )
