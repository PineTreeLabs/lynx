# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Full system interconnect conversion.

Converts Lynx Diagram to python-control LinearICSystem for simulation and analysis.
"""

from typing import TYPE_CHECKING, List, cast

import control as ct

from .block_converters import convert_block

if TYPE_CHECKING:
    from lynx.blocks.sum import SumBlock
    from lynx.diagram import Diagram, ValidationResult

# Import exceptions from diagram module
from lynx.diagram import DiagramExportError, ValidationError


def validate_for_export(diagram: "Diagram") -> "ValidationResult":
    """Validate diagram completeness before export to python-control.

    Performs layered validation and returns result:
    1. System boundary validation (I/O markers)
    2. Label uniqueness check (errors for duplicates)
    3. Port connection validation (unconnected inputs)

    Args:
        diagram: Diagram to validate

    Returns:
        ValidationResult with is_valid, errors, and warnings
    """
    from lynx.diagram import ValidationResult
    from lynx.validation import check_label_uniqueness

    errors: List[str] = []
    warnings: List[str] = []

    # Layer 1 - Validate at least one InputMarker exists
    has_input_marker = any(block.is_input_marker() for block in diagram.blocks)
    if not has_input_marker:
        errors.append(
            "Diagram has no InputMarker blocks. Add at least one system input."
        )

    # Layer 1 - Validate at least one OutputMarker exists
    has_output_marker = any(block.is_output_marker() for block in diagram.blocks)
    if not has_output_marker:
        errors.append(
            "Diagram has no OutputMarker blocks. Add at least one system output."
        )

    # Layer 1.5 - Check for duplicate labels (ERRORS, blocking)
    label_errors = check_label_uniqueness(diagram)
    errors.extend(label_errors)

    # Layer 2 - Validate all non-InputMarker input ports are connected
    # Build set of connected target ports for fast lookup
    connected_ports = set()
    for conn in diagram.connections:
        connected_ports.add((conn.target_block_id, conn.target_port_id))

    # Check each block's input ports (except InputMarkers which have no inputs)
    for block in diagram.blocks:
        # Skip InputMarkers - they don't need connected inputs
        if block.is_input_marker():
            continue

        # Check all input ports are connected
        for port in block._ports:
            if port.type == "input":
                if (block.id, port.id) not in connected_ports:
                    errors.append(
                        f"Block '{block.id}' input port '{port.id}' is not connected"
                    )

    # Return validation result
    return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)


def to_interconnect(diagram: "Diagram", validate: bool = True) -> ct.LinearICSystem:
    """Convert diagram to python-control LinearICSystem.

    Converts all blocks and connections in the Lynx diagram to a python-control
    InterconnectedSystem object that can be used for simulation and analysis.

    Args:
        diagram: Diagram to convert
        validate: If True, validate diagram before conversion (default: True)

    Returns:
        Python-control LinearICSystem representing the full diagram

    Raises:
        ValidationError: If diagram is incomplete (validate=True only)
        DiagramExportError: If python-control conversion fails

    Example:
        >>> diagram = Diagram()
        >>> diagram.add_block('io_marker', 'input', marker_type='input')
        >>> diagram.add_block('gain', 'g1', K=5.0)
        >>> diagram.add_block('io_marker', 'output', marker_type='output')
        >>> diagram.add_connection('c1', 'input', 'out', 'g1', 'in')
        >>> diagram.add_connection('c2', 'g1', 'out', 'output', 'in')
        >>> from lynx.conversion import to_interconnect
        >>> sys = to_interconnect(diagram)
        >>> import control as ct
        >>> t, y = ct.step_response(sys)
    """
    # Validate python-control is available
    try:
        import control as ct
    except ImportError as e:
        raise DiagramExportError(
            "python-control library not found. Install with: pip install control"
        ) from e

    # Validate diagram before attempting export
    if validate:
        result = validate_for_export(diagram)
        if not result.is_valid:
            # Raise ValidationError with all errors
            errors_fmt = "\n".join(f"  - {err}" for err in result.errors)
            error_msg = f"Diagram validation failed:\n{errors_fmt}"

            # Try to extract block_id and port_id from first error
            # Error format: "Block 'id' input port 'port' is not connected"
            block_id = None
            port_id = None
            if result.errors:
                import re

                first_error = result.errors[0]
                pattern = r"Block '([^']+)' input port '([^']+)' is not connected"
                match = re.match(pattern, first_error)
                if match:
                    block_id = match.group(1)
                    port_id = match.group(2)

            raise ValidationError(error_msg, block_id=block_id, port_id=port_id)

    # Build lists for python-control interconnect()
    systems = []  # Subsystem objects
    connections = []  # Signal routing pairs
    inplist = []  # System input signals
    outlist = []  # System output signals

    # Convert blocks to subsystems using converter registry
    for block in diagram.blocks:
        sys = convert_block(block)
        systems.append(sys)

        # Track I/O markers for inplist/outlist
        if block.is_input_marker():
            inplist.append(f"{block.id}.in")
        elif block.is_output_marker():
            outlist.append(f"{block.id}.out")

    # Convert connections to signal pairs with sign negation
    # Note: python-control connection format is [target, source] not [source, target]
    for conn in diagram.connections:
        source_signal = f"{conn.source_block_id}.{conn.source_port_id}"
        target_signal = f"{conn.target_block_id}.{conn.target_port_id}"

        # Check if target is a sum block and apply sign negation if needed
        target_block = diagram.get_block(conn.target_block_id)
        if target_block and target_block.type == "sum":
            # Get the sign for this specific port using SumBlock method
            sum_block = cast("SumBlock", target_block)
            sign = sum_block.get_port_sign(conn.target_port_id)
            if sign == "-":
                # Prepend '-' for signal negation in python-control
                source_signal = f"-{source_signal}"

        connections.append([target_signal, source_signal])

    # Build interconnected system
    try:
        # Use None for connections if empty (python-control convention)
        return ct.interconnect(
            systems,
            connections=connections if connections else None,
            inplist=inplist,
            outlist=outlist,
        )
    except Exception as e:
        # Wrap python-control exceptions with context
        raise DiagramExportError(f"Failed to create interconnected system: {e}") from e
