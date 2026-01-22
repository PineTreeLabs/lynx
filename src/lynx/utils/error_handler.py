# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Centralized error handling for Lynx operations."""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass
class OperationResult:
    """Result of an operation with error context."""

    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


class ErrorHandler:
    """Centralized error handling with logging."""

    def __init__(self, logger: logging.Logger):
        """Initialize error handler.

        Args:
            logger: Logger instance for error reporting
        """
        self.logger = logger

    def handle_operation(
        self,
        operation: Callable[[], T],
        operation_name: str,
        context: Optional[dict] = None,
        fallback: Optional[T] = None,
    ) -> OperationResult:
        """Execute operation with error handling.

        Args:
            operation: Callable to execute
            operation_name: Human-readable operation name
            context: Optional context dict for logging
            fallback: Optional fallback value if operation fails

        Returns:
            OperationResult with success status and value/error
        """
        try:
            result = operation()
            return OperationResult(success=True, value=result)
        except ValueError as e:
            self.logger.error(
                f"{operation_name} failed: {e}", extra={"context": context}
            )
            return OperationResult(False, fallback, str(e), "INVALID_VALUE")
        except KeyError as e:
            self.logger.error(
                f"{operation_name} failed: {e}", extra={"context": context}
            )
            return OperationResult(
                False, fallback, f"Key not found: {e}", "KEY_NOT_FOUND"
            )
        except Exception as e:
            self.logger.exception(
                f"{operation_name} unexpected error", extra={"context": context}
            )
            return OperationResult(
                False, fallback, f"Unexpected error: {e}", "UNKNOWN_ERROR"
            )
