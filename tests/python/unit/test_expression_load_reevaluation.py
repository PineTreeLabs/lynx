# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for automatic expression re-evaluation during diagram load.

This test file demonstrates the bug: expressions should be automatically
re-evaluated during Diagram.load() and Diagram.from_dict() when variables
are available in the Python environment, but currently they are not.
"""

import numpy as np

from lynx.diagram import Diagram


class TestExpressionLoadReEvaluation:
    """Test automatic re-evaluation of expressions during diagram load."""

    def test_load_reevaluates_expressions_with_current_namespace(self, tmp_path):
        """Test that loading a diagram re-evaluates expressions with namespace."""
        # Step 1: Create diagram with original variable values
        kp_original = 2.5

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

        # Step 3: Load diagram with namespace - expressions re-evaluate with NEW values
        diagram2 = Diagram.load(filepath, namespace={"kp": kp_current})

        # K should be re-evaluated to kp_current (5.0)
        block2 = diagram2.get_block("g1")
        assert block2.get_parameter("K") == kp_current

    def test_from_dict_with_namespace_reevaluates_expressions(self):
        """Test that from_dict() with namespace re-evaluates expressions."""
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

        # Load with namespace - should auto re-evaluate
        diagram = Diagram.from_dict(data, namespace=namespace)

        # After re-evaluation, value should match namespace
        block = diagram.get_block("g1")
        assert block.get_parameter("K") == 5.0

    def test_load_with_comma_separated_expression(self, tmp_path):
        """Test that comma-separated expressions evaluate to arrays, not tuples."""
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

        # Load with namespace - should auto re-evaluate
        kp = 500.0
        ki = 50.0
        diagram2 = Diagram.load(filepath, namespace={"kp": kp, "ki": ki})

        # Check result - should be array, not tuple
        block2 = diagram2.get_block("tf1")
        result = block2.get_parameter("num")

        # Should be array (comma-separated expressions convert to arrays)
        assert isinstance(result, np.ndarray), (
            f"Expected ndarray, got {type(result).__name__}: {result}"
        )

        # Values should match
        assert np.allclose(result, [kp, ki])
