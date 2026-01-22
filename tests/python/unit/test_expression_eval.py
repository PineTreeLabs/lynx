# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for expression evaluation module.

Tests cover:
- T076: Safe evaluation of numpy expressions
- T078: Missing variable fallback to stored value
"""

import numpy as np

from lynx.expression_eval import evaluate_expression


class TestExpressionEvaluation:
    """Test expression evaluation functionality."""

    def test_evaluate_simple_matrix(self):
        """Test evaluating a simple numpy matrix expression."""
        # User namespace with a variable
        namespace = {"A": np.array([[1, 0], [0, 1]])}

        result = evaluate_expression("A", namespace)

        assert result.success is True
        assert result.value is not None
        np.testing.assert_array_equal(result.value, np.array([[1, 0], [0, 1]]))
        assert result.error is None

    def test_evaluate_matrix_expression(self):
        """Test evaluating numpy matrix operations."""
        namespace = {
            "A": np.array([[1, 2], [3, 4]]),
            "B": np.array([[0, 1], [1, 0]]),
        }

        result = evaluate_expression("A + B", namespace)

        assert result.success is True
        np.testing.assert_array_equal(result.value, np.array([[1, 3], [4, 4]]))

    def test_evaluate_numpy_function(self):
        """Test evaluating numpy function calls."""
        namespace = {"np": np}

        result = evaluate_expression("np.eye(2)", namespace)

        assert result.success is True
        np.testing.assert_array_equal(result.value, np.array([[1, 0], [0, 1]]))

    def test_evaluate_missing_variable(self):
        """Test that missing variable returns error."""
        namespace = {}  # Empty namespace

        result = evaluate_expression("A", namespace)

        assert result.success is False
        assert result.value is None
        assert "A" in result.error  # Error message should mention variable name

    def test_evaluate_invalid_syntax(self):
        """Test that invalid syntax returns error."""
        namespace = {}

        result = evaluate_expression("[[1, 2", namespace)  # Missing closing bracket

        assert result.success is False
        assert result.value is None
        assert result.error is not None

    def test_evaluate_unsafe_expression(self):
        """Test that unsafe operations are blocked."""
        namespace = {}

        # Try to execute system command (should fail)
        result = evaluate_expression("__import__('os').system('ls')", namespace)

        assert result.success is False
        assert result.value is None
        assert result.error is not None

    def test_evaluate_literal_array(self):
        """Test evaluating literal array syntax."""
        namespace = {}

        result = evaluate_expression("[[1, 0], [0, 1]]", namespace)

        assert result.success is True
        np.testing.assert_array_equal(result.value, np.array([[1, 0], [0, 1]]))


class TestMissingVariableFallback:
    """Test fallback to stored value when variable is missing (T078)."""

    def test_fallback_to_stored_value(self):
        """Test that evaluator can use fallback value when variable missing."""
        namespace = {}  # Variable 'A' not in namespace
        fallback_value = np.array([[1, 0], [0, 1]])

        result = evaluate_expression("A", namespace, fallback=fallback_value)

        # Should succeed with fallback value
        assert result.success is True
        np.testing.assert_array_equal(result.value, fallback_value)
        assert result.used_fallback is True
        assert "A" in result.warning  # Should warn about missing variable

    def test_no_fallback_needed_when_variable_exists(self):
        """Test that fallback is not used when variable exists."""
        namespace = {"A": np.array([[2, 1], [1, 2]])}
        fallback_value = np.array([[1, 0], [0, 1]])

        result = evaluate_expression("A", namespace, fallback=fallback_value)

        assert result.success is True
        np.testing.assert_array_equal(result.value, namespace["A"])
        assert result.used_fallback is False
        assert result.warning is None

    def test_fallback_without_stored_value(self):
        """Test that missing variable without fallback returns error."""
        namespace = {}

        result = evaluate_expression("A", namespace, fallback=None)

        assert result.success is False
        assert result.value is None
        assert result.used_fallback is False
