# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Control theory validation for block diagrams.

Validates:
- Algebraic loops (cycles without dynamics)
- System completeness (at least one I/O block)
- Disconnected blocks
- Label uniqueness (duplicate block/connection labels)
"""

from typing import List

from lynx.diagram import Diagram, ValidationResult
from lynx.validation.algebraic_loop import check_algebraic_loops
from lynx.validation.graph_validator import (
    check_system_completeness,
    find_disconnected_blocks,
)
from lynx.validation.graph_validator import (
    find_cycles as find_cycles,
)

__all__ = [
    "validate_diagram",
    "check_label_uniqueness",
    "check_algebraic_loops",
    "check_system_completeness",
    "find_disconnected_blocks",
    "find_cycles",
]


def check_label_uniqueness(diagram: Diagram) -> List[str]:
    """Check for duplicate block and connection labels.

    Args:
        diagram: Diagram to check

    Returns:
        List of error messages for duplicate labels
    """
    errors: List[str] = []

    # Check block labels
    block_labels: dict[str, str] = {}
    for block in diagram.blocks:
        if block.label:
            if block.label in block_labels:
                errors.append(
                    f"Duplicate block label '{block.label}' found on blocks "
                    f"'{block_labels[block.label]}' and '{block.id}'. "
                    f"Block labels must be unique for signal references."
                )
            else:
                block_labels[block.label] = block.id

    # Check connection labels
    connection_labels: dict[str, str] = {}
    for conn in diagram.connections:
        if conn.label:
            if conn.label in connection_labels:
                errors.append(
                    f"Duplicate connection label '{conn.label}' found on connections "
                    f"'{connection_labels[conn.label]}' and '{conn.id}'. "
                    f"Connection labels must be unique for signal references."
                )
            else:
                connection_labels[conn.label] = conn.id

    return errors


def validate_diagram(diagram: Diagram) -> ValidationResult:
    """Validate a block diagram for control theory issues.

    Checks:
    - Algebraic loops (errors)
    - Label uniqueness (errors)
    - System completeness (warnings)
    - Disconnected blocks (warnings)

    Args:
        diagram: Diagram to validate

    Returns:
        ValidationResult with errors and warnings
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Check for algebraic loops (errors)
    algebraic_loop_errors = check_algebraic_loops(diagram)
    errors.extend(algebraic_loop_errors)

    # Check for duplicate labels (errors)
    label_errors = check_label_uniqueness(diagram)
    errors.extend(label_errors)

    # Check system completeness (warnings)
    completeness_warnings = check_system_completeness(diagram)
    warnings.extend(completeness_warnings)

    # Check for disconnected blocks (warnings)
    disconnected_warnings = find_disconnected_blocks(diagram)
    warnings.extend(disconnected_warnings)

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
