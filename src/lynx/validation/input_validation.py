# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Input validation for user-provided data."""

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from lynx.config.constants import VALIDATION


@dataclass
class ValidationResult:
    """Result of input validation."""

    is_valid: bool
    value: Any
    error: Optional[str] = None
    warning: Optional[str] = None


class InputValidator:
    """Validator for user input with configurable limits."""

    def validate_label(self, label: str, field_name: str = "Label") -> ValidationResult:
        """Validate label text with length and character checks.

        Args:
            label: Label text to validate
            field_name: Name of the field for error messages

        Returns:
            ValidationResult with sanitized value and any errors
        """
        sanitized = label.strip()

        if len(sanitized) > VALIDATION.max_label_length:
            return ValidationResult(
                is_valid=False,
                value=sanitized[: VALIDATION.max_label_length],
                error=f"{field_name} exceeds {VALIDATION.max_label_length} characters",
            )

        if "\n" in sanitized or "\r" in sanitized or "\0" in sanitized:
            return ValidationResult(
                is_valid=False,
                value=sanitized.replace("\n", " ").replace("\r", " ").replace("\0", ""),
                error=f"{field_name} contains invalid characters",
            )

        return ValidationResult(is_valid=True, value=sanitized)

    def validate_gain(self, K: Any) -> ValidationResult:
        """Validate gain parameter (no NaN/Inf, bounds checking).

        Args:
            K: Gain value to validate

        Returns:
            ValidationResult with validated value and any errors
        """
        try:
            k_float = float(K)
        except (TypeError, ValueError):
            return ValidationResult(
                False, 1.0, f"Gain must be numeric, got {type(K).__name__}"
            )

        if np.isnan(k_float):
            return ValidationResult(False, 1.0, "Gain cannot be NaN")

        if np.isinf(k_float):
            return ValidationResult(False, 1.0, "Gain cannot be infinite")

        if not (VALIDATION.min_gain_value <= k_float <= VALIDATION.max_gain_value):
            return ValidationResult(
                False,
                np.clip(k_float, VALIDATION.min_gain_value, VALIDATION.max_gain_value),
                f"Gain must be between {VALIDATION.min_gain_value} and "
                f"{VALIDATION.max_gain_value}",
            )

        return ValidationResult(True, k_float)

    def validate_custom_latex(self, latex: str) -> ValidationResult:
        """Validate custom LaTeX (length, brace balance, nesting depth).

        Args:
            latex: LaTeX string to validate

        Returns:
            ValidationResult with sanitized value and any errors/warnings
        """
        sanitized = latex.strip()

        if len(sanitized) > VALIDATION.max_latex_length:
            return ValidationResult(
                False,
                sanitized[: VALIDATION.max_latex_length],
                f"LaTeX exceeds {VALIDATION.max_latex_length} characters",
            )

        # Brace balance
        if sanitized.count("{") != sanitized.count("}"):
            return ValidationResult(False, sanitized, "LaTeX has unbalanced braces")

        # Warn on deep nesting (>10 levels)
        max_depth = 0
        current_depth = 0
        for char in sanitized:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth -= 1

        warning = (
            "LaTeX has deeply nested braces (may render slowly)"
            if max_depth > 10
            else None
        )
        return ValidationResult(True, sanitized, warning=warning)
