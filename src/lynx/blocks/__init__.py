# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Block type definitions for Lynx control system diagrams.

This package contains all block type implementations:
- base: Base Block class with common functionality
- gain: Simple scalar gain block
- io_marker: Input/Output boundary markers
- sum: Sum junction blocks (P1)
- transfer_function: Transfer function blocks (P1)
- state_space: State-space blocks (P1)
"""

from typing import Any, cast

from lynx.blocks.base import Block, Parameter, Port
from lynx.blocks.gain import GainBlock
from lynx.blocks.io_marker import InputMarker, OutputMarker
from lynx.blocks.state_space import StateSpaceBlock
from lynx.blocks.sum import SumBlock
from lynx.blocks.transfer_function import TransferFunctionBlock
from lynx.config.constants import BLOCK_TYPES

# Block factory registry
BLOCK_REGISTRY = {
    BLOCK_TYPES["GAIN"]: GainBlock,
    BLOCK_TYPES["TRANSFER_FUNCTION"]: TransferFunctionBlock,
    BLOCK_TYPES["STATE_SPACE"]: StateSpaceBlock,
    BLOCK_TYPES["SUM"]: SumBlock,
}


def create_block(block_type: str, block_id: str, **kwargs: Any) -> Block:
    """Factory function to create blocks by type.

    Args:
        block_type: Type identifier (e.g., 'gain', 'sum', 'io_marker')
        block_id: Unique block identifier
        **kwargs: Block-specific parameters

    Returns:
        Block instance

    Raises:
        ValueError: If block_type is unknown
    """
    # Special case: io_marker has two subtypes
    if block_type == BLOCK_TYPES["IO_MARKER"]:
        marker_type = kwargs.pop("marker_type", "input")
        if marker_type == "input":
            return InputMarker(block_id, **kwargs)
        elif marker_type == "output":
            return OutputMarker(block_id, **kwargs)
        else:
            raise ValueError(f"Unknown IOMarker type: {marker_type}")

    # Standard blocks
    block_class = BLOCK_REGISTRY.get(block_type)
    if block_class is None:
        raise ValueError(f"Unknown block type: {block_type}")

    try:
        return cast(Block, block_class(block_id, **kwargs))
    except TypeError as e:
        # Convert TypeError (missing required parameter) to ValueError
        error_msg = str(e)
        if "missing" in error_msg and "required" in error_msg:
            # Extract parameter name(s) from error message
            # Single: "SumBlock.__init__() missing 1 required ... 'signs'"
            # Multiple: "StateSpaceBlock.__init__() missing 2 required
            # ... 'C' and 'D'"
            if "arguments: '" in error_msg:
                # Multiple parameters case - just use generic message
                if block_type == BLOCK_TYPES["SUM"]:
                    raise ValueError("Sum block requires 'signs'") from e
                elif block_type == BLOCK_TYPES["TRANSFER_FUNCTION"]:
                    raise ValueError(
                        "Transfer function requires numerator and denominator"
                    ) from e
                elif block_type == BLOCK_TYPES["STATE_SPACE"]:
                    raise ValueError(
                        "State space block requires A, B, C, D matrices"
                    ) from e
                else:
                    msg = f"{block_type} block requires missing parameters"
                    raise ValueError(msg) from e
            elif (
                "argument: '" in error_msg and "'" in error_msg.split("argument: '")[1]
            ):
                # Single parameter case
                param_name = error_msg.split("argument: '")[1].split("'")[0]
                if block_type == BLOCK_TYPES["SUM"]:
                    raise ValueError("Sum block requires 'signs'") from e
                elif block_type == BLOCK_TYPES["TRANSFER_FUNCTION"]:
                    msg = f"Transfer function requires '{param_name}'"
                    raise ValueError(msg) from e
                elif block_type == BLOCK_TYPES["STATE_SPACE"]:
                    msg = f"State space block requires '{param_name}'"
                    raise ValueError(msg) from e
                else:
                    msg = f"{block_type} block requires '{param_name}'"
                    raise ValueError(msg) from e
            msg = f"{block_type} block requires missing parameter: {error_msg}"
            raise ValueError(msg) from e
        raise


__all__ = [
    "Block",
    "Port",
    "Parameter",
    "GainBlock",
    "InputMarker",
    "OutputMarker",
    "SumBlock",
    "TransferFunctionBlock",
    "StateSpaceBlock",
    "BLOCK_REGISTRY",
    "create_block",
]
