# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Block-to-python-control converter registry.

Each converter function extracts parameters from a block and creates
the corresponding python-control system object (StateSpace or TransferFunction).

Converters are pure functions that don't modify blocks.
"""

from typing import Callable, Dict

import control as ct

from lynx.blocks.base import Block


def convert_gain(block: Block) -> ct.StateSpace:
    """Convert Gain block to python-control static gain.

    Gain blocks are implemented as state-space systems with D matrix only
    (pure algebraic gain, no dynamics).

    Args:
        block: Gain block with parameter 'K'

    Returns:
        State-space system with D = [[K]]
    """
    K = block.get_parameter("K")
    # Query actual port IDs from block (future-proofs for custom ports)
    input_ports = [p.id for p in block._ports if p.type == "input"]
    output_ports = [p.id for p in block._ports if p.type == "output"]
    return ct.ss(
        [], [], [], [[K]], name=block.id, inputs=input_ports, outputs=output_ports
    )


def convert_transfer_function(block: Block) -> ct.TransferFunction:
    """Convert TransferFunction block to python-control transfer function.

    Args:
        block: TransferFunction block with parameters 'numerator', 'denominator'

    Returns:
        Transfer function system
    """
    numerator = block.get_parameter("numerator")
    denominator = block.get_parameter("denominator")
    # Query actual port IDs from block (future-proofs for custom ports)
    input_ports = [p.id for p in block._ports if p.type == "input"]
    output_ports = [p.id for p in block._ports if p.type == "output"]
    return ct.tf(
        numerator, denominator, name=block.id, inputs=input_ports, outputs=output_ports
    )


def convert_state_space(block: Block) -> ct.StateSpace:
    """Convert StateSpace block to python-control state-space system.

    Args:
        block: StateSpace block with parameters 'A', 'B', 'C', 'D'

    Returns:
        State-space system
    """
    A = block.get_parameter("A")
    B = block.get_parameter("B")
    C = block.get_parameter("C")
    D = block.get_parameter("D")
    # Query actual port IDs from block (future-proofs for custom ports)
    input_ports = [p.id for p in block._ports if p.type == "input"]
    output_ports = [p.id for p in block._ports if p.type == "output"]
    return ct.ss(A, B, C, D, name=block.id, inputs=input_ports, outputs=output_ports)


def convert_sum(block: Block) -> ct.StateSpace:
    """Convert Sum block to python-control summing junction.

    Uses the block's actual input ports (determined by signs parameter).
    Ports with '|' sign are omitted.

    Args:
        block: Sum block with parameter 'signs' and input ports

    Returns:
        Summing junction system
    """
    # Get actual input port IDs (only non-"|" signs create ports)
    input_ports = [p.id for p in block._ports if p.type == "input"]
    # Get output port (should be exactly one)
    output_ports = [p.id for p in block._ports if p.type == "output"]
    if len(output_ports) != 1:
        msg = f"Sum block must have exactly 1 output, has {len(output_ports)}"
        raise ValueError(msg)
    return ct.summing_junction(
        inputs=input_ports, output=output_ports[0], name=block.id
    )


def convert_io_marker(block: Block) -> ct.StateSpace:
    """Convert IOMarker to unity passthrough system.

    IOMarkers (both input and output) are implemented as pass-through
    systems with unity gain (D=1). This allows fan-out from InputMarkers
    and fan-in to OutputMarkers.

    Note: IOMarkers are special - InputMarkers only have 'out' port and
    OutputMarkers only have 'in' port, but python-control requires both.
    We hardcode both port names here since they're always the same.

    Args:
        block: IOMarker block (InputMarker or OutputMarker)

    Returns:
        State-space system with D = [[1.0]] (perfect algebraic pass-through)
    """
    # IOMarkers always use 'in'/'out' port names (not customizable)
    return ct.ss([], [], [], [[1.0]], name=block.id, inputs=["in"], outputs=["out"])


# Converter registry: maps block type string to converter function
BLOCK_CONVERTERS: Dict[str, Callable[[Block], ct.InputOutputSystem]] = {
    "gain": convert_gain,
    "transfer_function": convert_transfer_function,
    "state_space": convert_state_space,
    "sum": convert_sum,
    "io_marker": convert_io_marker,
}


def convert_block(block: Block) -> ct.InputOutputSystem:
    """Convert a block to python-control system using registered converter.

    This is the main entry point for block conversion. It dispatches to the
    appropriate converter function based on block type.

    Args:
        block: Block to convert

    Returns:
        Python-control system (StateSpace or TransferFunction)

    Raises:
        ValueError: If block type has no registered converter
    """
    converter = BLOCK_CONVERTERS.get(block.type)
    if converter is None:
        raise ValueError(f"No converter registered for block type: {block.type}")

    return converter(block)
