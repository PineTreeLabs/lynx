# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Subsystem extraction via break-and-inject approach.

Provides get_ss() and get_tf() methods for extracting arbitrary
signal-to-signal transfer functions from diagrams.
"""

from typing import TYPE_CHECKING, List, Tuple, cast

import control as ct

from .block_converters import convert_block

if TYPE_CHECKING:
    from lynx.blocks.base import Block
    from lynx.blocks.sum import SumBlock
    from lynx.diagram import Connection, Diagram

# Import exceptions from diagram module
from lynx.diagram import DiagramExportError, SignalNotFoundError, ValidationError


def _find_signal_source(diagram: "Diagram", signal_name: str) -> Tuple["Block", str]:
    """Find the block and port that outputs a given signal.

    Signal name resolution follows this priority order:
    1. IOMarker labels (highest priority)
    2. Connection labels
    3. Block_label.output_port_id format (e.g., "controller.out")
       - Must use block label (not ID)
       - Must use output port (not input)

    Args:
        diagram: Diagram to search
        signal_name: Signal name to find

    Returns:
        Tuple of (block, port_id) that outputs this signal

    Raises:
        SignalNotFoundError: If signal cannot be resolved
    """
    searched_locations = []

    # Priority 1: IOMarker labels
    searched_locations.append("IOMarkers")
    for block in diagram.blocks:
        if block.type == "io_marker":
            try:
                marker_label = block.get_parameter("label")
                if marker_label == signal_name:
                    # Check marker type
                    marker_type = block.get_parameter("marker_type")
                    if marker_type == "input":
                        # InputMarkers output from 'out' port
                        return (block, "out")
                    elif marker_type == "output":
                        # OutputMarkers consume signals via 'in' port
                        # Find the connection that feeds this marker
                        incoming = _find_incoming_connections(diagram, block.id, "in")
                        if incoming:
                            # Return the source of the first incoming connection
                            conn = incoming[0]
                            source_block = diagram.get_block(conn.source_block_id)
                            if source_block:
                                return (source_block, conn.source_port_id)
            except KeyError:
                # No label parameter, skip this marker
                pass

    # Priority 2: Connection labels
    searched_locations.append("connection labels")
    for conn in diagram.connections:
        if conn.label == signal_name:
            source_block = diagram.get_block(conn.source_block_id)
            if source_block:
                return (source_block, conn.source_port_id)

    # Priority 3: Block_label.port format (output ports only)
    searched_locations.append("block_label.port format")
    if "." in signal_name:
        parts = signal_name.split(".")
        if len(parts) == 2:
            block_label, port_id = parts
            # Find block by LABEL (not ID)
            for block in diagram.blocks:
                if block.label == block_label:
                    # Verify port exists and is OUTPUT
                    for port in block._ports:
                        if port.id == port_id:
                            if port.type != "output":
                                msg = (
                                    f"Port '{port_id}' on block '{block_label}' "
                                    "is not an output port"
                                )
                                raise SignalNotFoundError(
                                    signal_name, searched_locations, msg
                                )
                            return (block, port_id)

    # Signal not found
    raise SignalNotFoundError(signal_name, searched_locations)


def _find_incoming_connections(
    diagram: "Diagram", block_id: str, port_id: str
) -> List["Connection"]:
    """Find all connections feeding into a specific block port.

    Args:
        diagram: Diagram to search
        block_id: Block identifier
        port_id: Input port identifier

    Returns:
        List of connections targeting this block/port (may be empty)
    """
    return [
        conn
        for conn in diagram.connections
        if conn.target_block_id == block_id and conn.target_port_id == port_id
    ]


def _get_block_output_name(block: "Block") -> str:
    """Get the output name that will be used for a block in interconnect system.

    Args:
        block: Block to get output name for

    Returns:
        Output name (IOMarker label, block label, or block ID)
    """
    if block.type == "io_marker":
        try:
            signal_label = block.get_parameter("label")
            return signal_label if signal_label else block.id
        except KeyError:
            # No label parameter, use block ID
            return block.id
    else:
        return block.label if block.label else block.id


def _prepare_for_extraction(
    diagram: "Diagram", from_signal: str, to_signal: str
) -> Tuple[ct.LinearICSystem, str, str]:
    """Prepare diagram for subsystem extraction via break-and-inject.

    Steps:
    1. Clone the diagram for safe modification
    2. Find the blocks that output from_signal and to_signal
    3. If from_signal is not already an InputMarker:
       a. Remove incoming connections to that signal's source
       b. Inject a new InputMarker at that point
       c. Connect the injected marker to the signal source
    4. Build interconnect with ALL signals exported as outputs
    5. Return system and output names for indexing

    Args:
        diagram: Original diagram (not modified)
        from_signal: Source signal name
        to_signal: Destination signal name

    Returns:
        Tuple of (system, from_output_name, to_output_name)

    Raises:
        SignalNotFoundError: If either signal doesn't exist
        DiagramExportError: If conversion fails
    """
    try:
        import control as ct
    except ImportError as e:
        raise DiagramExportError(
            "python-control library not found. Install with: pip install control"
        ) from e

    # Step 1: Clone diagram
    modified = diagram._clone()

    # Step 1.5: Validate cloned diagram before extraction
    # This ensures we catch issues early with clear error messages
    from .interconnect import validate_for_export

    result = validate_for_export(modified)
    if not result.is_valid:
        # Raise ValidationError with all errors
        error_msg = (
            "Cannot extract subsystem - diagram validation failed:\n"
            + "\n".join(f"  - {err}" for err in result.errors)
        )
        raise ValidationError(error_msg)

    # Step 2: Find signal sources and determine output names
    from_block, from_port = _find_signal_source(modified, from_signal)
    to_block, to_port = _find_signal_source(modified, to_signal)

    # Get the output names that will be used in the interconnect system
    from_output_name = _get_block_output_name(from_block)
    to_output_name = _get_block_output_name(to_block)

    # Step 3: Break and inject if needed
    # Check if from_signal is already an external input (InputMarker)
    is_already_input = from_block.is_input_marker()

    if not is_already_input:
        # Check if from_signal is a connection label
        # If so, we inject at the connection target, not the source block input
        connection_to_break = None
        for conn in modified.connections:
            if conn.label == from_signal:
                connection_to_break = conn
                break

        if connection_to_break:
            # Case A: from_signal is a connection label
            # The signal exists ON the connection, so inject at the connection's target
            target_block_id = connection_to_break.target_block_id
            target_port_id = connection_to_break.target_port_id

            # Remove the labeled connection
            modified.remove_connection(connection_to_break.id)

            # Inject InputMarker with the signal label
            # Sanitize signal name (python-control doesn't allow dots)
            safe_signal_name = from_signal.replace(".", "_")
            injected_id = f"_injected_{safe_signal_name}"
            modified.add_block(
                "io_marker",
                injected_id,
                marker_type="input",
                label=from_signal,
                position={"x": -100, "y": 0},
            )

            # Connect injected marker to original connection target
            conn_id = f"_conn_{injected_id}"
            modified.add_connection(
                conn_id, injected_id, "out", target_block_id, target_port_id
            )
        else:
            # Case B: from_signal is block output (block.port format or block label)
            # Inject at the source block's input to make its output an external input
            input_port_id = None
            for port in from_block._ports:
                if port.type == "input":
                    input_port_id = port.id
                    break

            if input_port_id:
                # Find connections feeding this input port
                incoming = _find_incoming_connections(
                    modified, from_block.id, input_port_id
                )

                # Remove these connections
                for conn in incoming:
                    modified.remove_connection(conn.id)

            # Inject new InputMarker
            # Sanitize signal name (python-control doesn't allow dots)
            safe_signal_name = from_signal.replace(".", "_")
            injected_id = f"_injected_{safe_signal_name}"
            modified.add_block(
                "io_marker",
                injected_id,
                marker_type="input",
                label=from_signal,
                position={"x": -100, "y": 0},
            )

            # Connect injected marker to from_block's input
            if input_port_id:
                conn_id = f"_conn_{injected_id}"
                modified.add_connection(
                    conn_id, injected_id, "out", from_block.id, input_port_id
                )

        # Update from_output_name to use the injected marker's output
        # After injection, from_signal becomes an external input, not the original block
        # Sanitize the signal name (python-control doesn't allow dots in signal names)
        from_output_name = from_signal.replace(".", "_")

    # Step 4: Build interconnect with ALL signals exported
    systems = []
    connections = []
    inplist = []
    outlist = []
    input_names = []
    output_names = []

    # Convert blocks to subsystems using converter registry
    for block in modified.blocks:
        sys = convert_block(block)
        systems.append(sys)

        # Track external inputs
        if block.is_input_marker():
            inplist.append(f"{block.id}.in")
            # Use signal label as input name (sanitize dots)
            try:
                signal_label = block.get_parameter("label")
                # Sanitize label (replace dots with underscores)
                safe_label = (
                    signal_label.replace(".", "_") if signal_label else block.id
                )
                input_names.append(safe_label)
            except KeyError:
                # No label parameter, use block ID
                input_names.append(block.id)

        # Export ALL output ports for each block (supports multi-output blocks)
        output_port_ids = [p.id for p in block._ports if p.type == "output"]
        for port in block._ports:
            if port.type == "output":
                outlist.append(f"{block.id}.{port.id}")
                output_name = _get_block_output_name(block)
                # Sanitize output name (python-control disallows dots)
                safe_output_name = output_name.replace(".", "_")
                # For multi-output blocks, append port suffix
                if len(output_port_ids) > 1:
                    # Use underscore instead of dot
                    output_names.append(f"{safe_output_name}_{port.id}")
                else:
                    output_names.append(safe_output_name)

    # Convert connections to signal pairs with sign negation
    for conn in modified.connections:
        source_signal = f"{conn.source_block_id}.{conn.source_port_id}"
        target_signal = f"{conn.target_block_id}.{conn.target_port_id}"

        # Handle sum block sign negation
        target_block = modified.get_block(conn.target_block_id)
        if target_block and target_block.type == "sum":
            sum_block = cast("SumBlock", target_block)
            sign = sum_block.get_port_sign(conn.target_port_id)
            if sign == "-":
                source_signal = f"-{source_signal}"

        connections.append([target_signal, source_signal])

    # Step 5: Build and return system
    try:
        sys = ct.interconnect(
            systems,
            connections=connections if connections else None,
            inplist=inplist,
            inputs=input_names if input_names else None,
            outlist=outlist,
            outputs=output_names if output_names else None,
        )
    except Exception as e:
        raise DiagramExportError(
            f"Failed to create interconnected system for extraction: {e}"
        ) from e

    return sys, from_output_name, to_output_name


def get_ss(diagram: "Diagram", from_signal: str, to_signal: str) -> ct.StateSpace:
    """Extract state-space model from one signal to another.

    Uses the "break-and-inject" approach to extract arbitrary subsystem
    transfer functions. Works for any signal pair: external→external,
    external→internal, internal→internal, etc.

    Args:
        diagram: Diagram to extract subsystem from
        from_signal: Source signal name using one of:
                    - IOMarker label (e.g., 'r', 'u')
                    - Connection label (e.g., 'error', 'control')
                    - block_label.output_port_id format (e.g., 'controller.out')
        to_signal: Destination signal name (same naming conventions as from_signal)

    Returns:
        State-space system representing from_signal → to_signal

    Raises:
        SignalNotFoundError: If either signal doesn't exist
        DiagramExportError: If conversion fails
        ValidationError: If diagram is invalid (missing I/O markers, unconnected ports)

    Examples:
        >>> # Closed-loop transfer function (IOMarker labels)
        >>> sys_ry = diagram.get_ss('r', 'y')
        >>>
        >>> # Sensitivity function (IOMarker + connection label)
        >>> sys_re = diagram.get_ss('r', 'error')
        >>>
        >>> # Controller TF (connection labels)
        >>> sys_eu = diagram.get_ss('error', 'control')
        >>>
        >>> # Internal signal using block_label.port format (not block ID)
        >>> # Note: 'controller' and 'plant' are block labels, not IDs
        >>> sys_uy = diagram.get_ss('controller.out', 'plant.out')
    """
    sys, from_name, to_name = _prepare_for_extraction(diagram, from_signal, to_signal)
    return sys[to_name, from_name]


def get_tf(diagram: "Diagram", from_signal: str, to_signal: str) -> ct.TransferFunction:
    """Extract transfer function from one signal to another.

    Convenience wrapper around get_ss() that converts result to transfer
    function form using control.ss2tf().

    Args:
        diagram: Diagram to extract subsystem from
        from_signal: Source signal name using one of:
                    - IOMarker label (e.g., 'r', 'u')
                    - Connection label (e.g., 'error', 'control')
                    - block_label.output_port_id format (e.g., 'controller.out')
        to_signal: Destination signal name (same naming conventions as from_signal)

    Returns:
        Transfer function from from_signal → to_signal

    Raises:
        SignalNotFoundError: If either signal doesn't exist
        DiagramExportError: If conversion fails
        ValidationError: If diagram is invalid (missing I/O markers, unconnected ports)

    Note:
        For MIMO systems, use get_ss() instead as transfer functions
        are only well-defined for SISO systems.

    Examples:
        >>> # Get closed-loop transfer function as TF object (IOMarker labels)
        >>> tf_ry = diagram.get_tf('r', 'y')
        >>> print(tf_ry)
        >>>
        >>> # Extract controller transfer function using block labels
        >>> tf_controller = diagram.get_tf('error', 'controller.out')
    """
    ss = get_ss(diagram, from_signal, to_signal)
    return ct.ss2tf(ss)
