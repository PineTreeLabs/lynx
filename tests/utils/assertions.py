# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Custom assertions for Lynx tests."""

from lynx.diagram import ValidationResult


def assert_validation_valid(result: ValidationResult) -> None:
    """Assert that validation result is valid.

    Args:
        result: ValidationResult to check

    Raises:
        AssertionError: If validation failed
    """
    assert result.is_valid, f"Validation failed: {result.errors}"


def assert_validation_has_error(result: ValidationResult, error_substring: str) -> None:
    """Assert that validation result has specific error.

    Args:
        result: ValidationResult to check
        error_substring: Substring to search for in errors

    Raises:
        AssertionError: If validation passed or error not found
    """
    assert not result.is_valid, "Expected validation to fail"
    assert any(error_substring in err for err in result.errors), (
        f"Expected error containing '{error_substring}', got {result.errors}"
    )
