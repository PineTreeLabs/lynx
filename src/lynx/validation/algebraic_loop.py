# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Algebraic loop detection for control systems.

An algebraic loop occurs when there is a feedback path where every block
has direct feedthrough (algebraic path from input to output).

A block has direct feedthrough if:
- Gain/Sum: Always has direct feedthrough
- Transfer Function: numerator order = denominator order
- State Space: D matrix has nonzero elements
"""

from typing import List

import numpy as np

from lynx.blocks.base import Block
from lynx.diagram import Diagram
from lynx.validation.graph_validator import find_cycles


def check_algebraic_loops(diagram: Diagram) -> List[str]:
    """Check for algebraic loops in the diagram.

    An algebraic loop is a cycle where every block has direct feedthrough
    (algebraic path from input to output). Such loops cannot be simulated
    because outputs depend instantaneously on themselves.

    Args:
        diagram: Diagram to analyze

    Returns:
        List of error messages about algebraic loops
    """
    errors: List[str] = []

    # Find all cycles
    cycles = find_cycles(diagram)

    # Check each cycle for direct feedthrough
    for cycle in cycles:
        if is_algebraic_loop(diagram, cycle):
            cycle_str = " -> ".join(cycle + [cycle[0]])  # Show full cycle
            msg = (
                f"Algebraic loop detected: {cycle_str}. "
                "Add dynamics (TF with num order < den order, or SS with D=0) "
                "to break the loop."
            )
            errors.append(msg)

    return errors


def is_algebraic_loop(diagram: Diagram, cycle: List[str]) -> bool:
    """Check if a cycle is an algebraic loop.

    A cycle is algebraic if ALL blocks in the cycle have direct feedthrough.
    If at least one block has NO direct feedthrough, the cycle is valid.

    Direct feedthrough means:
    - Gain/Sum/IO blocks: Always have direct feedthrough
    - Transfer Function: Has feedthrough if num order = den order
    - State Space: Has feedthrough if D has any nonzero elements

    Args:
        diagram: Diagram containing the blocks
        cycle: List of block IDs forming a cycle

    Returns:
        True if the cycle is algebraic (all blocks have feedthrough), False otherwise
    """
    # Check if ALL blocks in cycle have direct feedthrough
    for block_id in cycle:
        block = diagram.get_block(block_id)
        if not block:
            continue

        # If this block has NO direct feedthrough, cycle is valid
        if not has_direct_feedthrough(block):
            return False

    # All blocks have direct feedthrough - this is an algebraic loop
    return True


def has_direct_feedthrough(block: Block) -> bool:
    """Check if a block has direct feedthrough (algebraic path from input to output).

    Args:
        block: Block to check

    Returns:
        True if block has direct feedthrough, False otherwise
    """
    # Gain, Sum, IO markers always have direct feedthrough
    if block.type in {"gain", "sum", "io_marker"}:
        return True

    # Transfer function: Has feedthrough if numerator order = denominator order
    if block.type == "transfer_function":
        # Get numerator and denominator parameters
        num = None
        den = None
        for param in block._parameters:
            if param.name == "numerator":
                num = np.asarray(param.value)
            elif param.name == "denominator":
                den = np.asarray(param.value)

        if num is not None and den is not None:
            # Direct feedthrough if same length (same order)
            # Also check that leading coefficients are nonzero
            if len(num) == len(den) and len(num) > 0:
                if num[0] != 0 and den[0] != 0:
                    return True
        return False

    # State space: Has feedthrough if D matrix has any nonzero elements
    if block.type == "state_space":
        # Get D matrix
        for param in block._parameters:
            if param.name == "D":
                D = np.asarray(param.value)
                # Check if any element is nonzero
                return bool(np.any(D != 0))
        return False

    # Unknown block type - assume no feedthrough (safe default)
    return False
