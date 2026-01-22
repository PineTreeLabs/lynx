# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Safe expression evaluation for numpy matrix parameters.

Provides secure evaluation of user expressions with fallback support.
"""

import ast
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class EvaluationResult:
    """Result of expression evaluation.

    Attributes:
        success: True if evaluation succeeded
        value: Evaluated value (numpy array or other)
        error: Error message if evaluation failed
        warning: Warning message (e.g., used fallback)
        used_fallback: True if fallback value was used
    """

    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    warning: Optional[str] = None
    used_fallback: bool = False


def evaluate_expression(
    expression: str,
    namespace: Dict[str, Any],
    fallback: Optional[Any] = None,
) -> EvaluationResult:
    """Safely evaluate a Python expression in the given namespace.

    Args:
        expression: Python expression to evaluate (e.g., "A_matrix" or "np.eye(2)")
        namespace: Dictionary of available variables (typically notebook globals)
        fallback: Optional value to use if expression evaluation fails

    Returns:
        EvaluationResult with success status, value, and any errors/warnings

    Security:
        - Uses ast.literal_eval for simple literals (safest)
        - For complex expressions, validates AST before evaluation
        - Blocks unsafe operations (imports, attribute access to private members, etc.)
    """
    if not expression or not isinstance(expression, str):
        return EvaluationResult(
            success=False,
            error="Expression must be a non-empty string",
        )

    expression = expression.strip()

    # Try literal evaluation first (safest - only allows literals)
    try:
        value = ast.literal_eval(expression)
        # Convert lists to numpy arrays
        if isinstance(value, list):
            value = np.array(value)
        return EvaluationResult(success=True, value=value)
    except (ValueError, SyntaxError):
        # Not a literal, need to do full evaluation
        pass

    # Validate expression AST for safety
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        return EvaluationResult(
            success=False,
            error=f"Syntax error: {e}",
        )

    # Check for unsafe operations
    if not _is_safe_ast(tree):
        return EvaluationResult(
            success=False,
            error="Expression contains unsafe operations (imports, etc.)",
        )

    # Create safe namespace with numpy available
    safe_namespace = {"np": np, "numpy": np}
    safe_namespace.update(namespace)

    # Try to evaluate
    try:
        value = eval(
            compile(tree, "<string>", "eval"), {"__builtins__": {}}, safe_namespace
        )
        return EvaluationResult(success=True, value=value)
    except NameError as e:
        # Variable not found - try fallback
        if fallback is not None:
            variable_name = str(e).split("'")[1] if "'" in str(e) else "variable"
            return EvaluationResult(
                success=True,
                value=fallback,
                warning=f"Variable '{variable_name}' not found, using stored value",
                used_fallback=True,
            )
        else:
            return EvaluationResult(
                success=False,
                error=str(e),
            )
    except Exception as e:
        return EvaluationResult(
            success=False,
            error=f"Evaluation error: {e}",
        )


def _is_safe_ast(tree: ast.AST) -> bool:
    """Check if AST contains only safe operations.

    Blocks:
    - Import statements
    - Attribute access to private members (__xxx__)
    - Calls to dangerous builtins (eval, exec, compile, __import__)
    - Delete, global, nonlocal statements

    Allows:
    - Basic arithmetic, comparisons, boolean operations
    - Function calls (to safe functions like np.eye, np.array)
    - Attribute access to public members
    - List/dict comprehensions
    - Indexing, slicing
    """
    for node in ast.walk(tree):
        # Block import statements
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return False

        # Block dangerous statements
        if isinstance(node, (ast.Delete, ast.Global, ast.Nonlocal)):
            return False

        # Block attribute access to private members
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("_"):
                return False

        # Block calls to dangerous builtins
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "compile", "__import__", "open"):
                    return False

    return True
