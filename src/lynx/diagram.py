# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Diagram class for managing block diagrams.

The Diagram class is the central data structure that manages:
- Collection of blocks (Gain, TransferFunction, StateSpace, Sum, IOMarker)
- Connections between blocks with optional labels
- Serialization to/from JSON using Pydantic validation
- Python-control export for analysis and simulation

Python-Control Export API:
    The Diagram class provides methods to convert diagrams to
    python-control system objects for analysis, simulation, and control
    design. Two primary methods are available:

    - get_ss(from_signal, to_signal): Extract state-space model between two signals
    - get_tf(from_signal, to_signal): Extract transfer function between two signals

    Signals can be referenced using a 4-tier priority system:
    1. IOMarker labels (e.g., 'r', 'y')
    2. Connection labels (e.g., 'error', 'control')
    3. Block.port format (e.g., 'controller.out', 'plant.in')
    4. Block labels for SISO blocks (e.g., 'controller', 'plant')

    Example:
        >>> diagram = Diagram()
        >>> diagram.add_block('io_marker', 'ref', marker_type='input', label='r')
        >>> diagram.add_block('gain', 'controller', K=5.0)
        >>> diagram.add_block('transfer_function', 'plant',
        ...                  numerator=[2.0], denominator=[1.0, 3.0])
        >>> diagram.add_block('io_marker', 'output', marker_type='output', label='y')
        >>> # ... add connections ...
        >>> sys = diagram.get_ss('r', 'y')  # Extract closed-loop system
        >>> tf = diagram.get_tf('r', 'y')   # As transfer function

    For implementation details, see the lynx.conversion module.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import ValidationError as PydanticValidationError

from lynx.blocks.base import Block
from lynx.schema import DiagramModel


# Export-related exceptions
class DiagramExportError(Exception):
    """Base exception for diagram export failures.

    Raised when exporting a Lynx diagram to external formats (e.g., python-control)
    fails due to conversion errors or incompatibilities.
    """

    pass


class ValidationError(DiagramExportError):
    """Raised when diagram validation fails before export.

    Attributes:
        message: Error message describing the validation failure
        block_id: Optional ID of the block where validation failed
        port_id: Optional ID of the port where validation failed
    """

    def __init__(
        self,
        message: str,
        block_id: Optional[str] = None,
        port_id: Optional[str] = None,
    ):
        """Initialize validation error with optional block/port context.

        Args:
            message: Error message describing what validation failed
            block_id: Block identifier where error occurred (if applicable)
            port_id: Port identifier where error occurred (if applicable)
        """
        super().__init__(message)
        self.block_id = block_id
        self.port_id = port_id


class SignalNotFoundError(DiagramExportError):
    """Raised when a signal name cannot be resolved.

    Attributes:
        signal_name: The signal that wasn't found
        searched_locations: List of places searched (IOMarkers, connections, etc.)
    """

    def __init__(
        self,
        signal_name: str,
        searched_locations: List[str],
        custom_message: Optional[str] = None,
    ):
        """Initialize signal not found error with search context.

        Args:
            signal_name: The signal name that wasn't found
            searched_locations: List of location types that were searched
            custom_message: Optional custom error message (for port validation)
        """
        if custom_message:
            msg = custom_message
        else:
            msg = (
                f"Signal '{signal_name}' not found. "
                f"Searched: {', '.join(searched_locations)}"
            )
        super().__init__(msg)
        self.signal_name = signal_name
        self.searched_locations = searched_locations


@dataclass
class Connection:
    """Connection between two block ports.

    Attributes:
        id: Unique connection identifier
        source_block_id: ID of source block
        source_port_id: ID of source port (output)
        target_block_id: ID of target block
        target_port_id: ID of target port (input)
        waypoints: Ordered list of intermediate routing points (absolute
                  canvas coordinates)
        label: User-defined label text (defaults to connection ID if None)
        label_visible: Whether the connection label is displayed (default: False)
    """

    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: List[Dict[str, float]] = field(default_factory=list)
    label: Optional[str] = None
    label_visible: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize connection to dictionary."""
        return {
            "id": self.id,
            "source_block_id": self.source_block_id,
            "source_port_id": self.source_port_id,
            "target_block_id": self.target_block_id,
            "target_port_id": self.target_port_id,
            "waypoints": self.waypoints,
            "label": self.label,
            "label_visible": self.label_visible,
        }


class ValidationResult:
    """Result of diagram validation.

    Thin wrapper around Pydantic ValidationResultModel for backward compatibility.
    """

    def __init__(
        self,
        is_valid: bool,
        errors: List[str],
        warnings: Optional[List[str]] = None,
    ):
        """Initialize validation result.

        Args:
            is_valid: True if validation passed
            errors: List of error messages
            warnings: Optional list of warning messages
        """
        from lynx.schema import ValidationResultModel

        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings or []
        self._model = ValidationResultModel(
            is_valid=is_valid,
            errors=errors,
            warnings=self.warnings,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize validation result using Pydantic."""
        return self._model.model_dump()


class Diagram:
    """Container for a complete block diagram.

    Manages blocks and their connections, provides serialization,
    and coordinates validation.

    Attributes:
        blocks: List of Block objects in the diagram
        connections: List of connections (P1 - Walking Skeleton has none yet)
    """

    def __init__(self, theme: Optional[str] = None) -> None:
        """Initialize empty diagram.

        Args:
            theme: Optional theme name ("light", "dark", "high-contrast").
                   If None, theme will be resolved via precedence chain.
        """
        from lynx.utils.theme_config import validate_theme_name

        self.blocks: List[Block] = []
        self.connections: List[Connection] = []
        self._version = "1.0.0"
        self._theme: Optional[str] = validate_theme_name(theme)  # Internal storage
        self._deserializing: bool = False  # Flag for deserialization state

        # Undo/Redo stacks
        self._history: List[Dict[str, Any]] = []  # Past states
        self._future: List[Dict[str, Any]] = []  # Future states (for redo)

    @property
    def theme(self) -> Optional[str]:
        """Get the diagram's theme name.

        Returns:
            Theme name ("light", "dark", "high-contrast") or None if not explicitly set.
        """
        return self._theme

    @theme.setter
    def theme(self, value: Optional[str]) -> None:
        """Set the diagram's theme with validation.

        Args:
            value: Theme name to set, or None to clear explicit theme.

        Notes:
            If the theme name is invalid, a warning is logged and the theme
            is set to None.
        """
        from lynx.utils.theme_config import validate_theme_name

        self._theme = validate_theme_name(value)

    def _auto_assign_index(self, marker_type: str) -> int:
        """Auto-assign next sequential index for IOMarker of given type.

        Args:
            marker_type: "input" or "output"

        Returns:
            Next available index (0 if no markers of this type exist, else max+1)
        """
        # Get all markers of the same type
        markers = [
            block
            for block in self.blocks
            if block.type == "io_marker"
            and block.get_parameter("marker_type") == marker_type
        ]

        # If no markers exist, start at 0
        if not markers:
            return 0

        # Find max index among existing markers (that have index parameter)
        max_index = -1
        for marker in markers:
            try:
                index_value = marker.get_parameter("index")
                max_index = max(max_index, index_value)
            except KeyError:
                # Marker doesn't have index parameter yet
                pass

        return max_index + 1

    def _ensure_index(self, block: Block) -> int:
        """Ensure IOMarker block has index parameter, assign if missing.

        For backward compatibility with diagrams created before index feature.

        Args:
            block: IOMarker block to ensure has an index

        Returns:
            The index value (existing or newly assigned)
        """
        # Check if block already has index parameter
        try:
            return int(block.get_parameter("index"))
        except KeyError:
            pass  # Index not present, need to assign

        # Get marker type
        marker_type = block.get_parameter("marker_type")

        # Get all markers of same type without indices
        markers_without_index = []
        for b in self.blocks:
            if b.type == "io_marker" and b.get_parameter("marker_type") == marker_type:
                try:
                    b.get_parameter("index")
                except KeyError:
                    markers_without_index.append(b)

        # Sort by block ID alphabetically (deterministic)
        markers_without_index.sort(key=lambda b: b.id)

        # Find the starting index (max of existing indices + 1, or 0)
        markers_with_index = []
        for b in self.blocks:
            if b.type == "io_marker" and b.get_parameter("marker_type") == marker_type:
                try:
                    b.get_parameter("index")
                    markers_with_index.append(b)
                except KeyError:
                    pass

        if markers_with_index:
            start_index = max(b.get_parameter("index") for b in markers_with_index) + 1
        else:
            start_index = 0

        # Assign indices to all markers without indices
        for i, marker in enumerate(markers_without_index):
            new_index = start_index + i
            marker.add_parameter("index", new_index)

        # Return this block's assigned index
        return int(block.get_parameter("index"))

    def add_block(
        self,
        block_type: str,
        id: str,
        position: Optional[Dict[str, float]] = None,
        **kwargs: Any,
    ) -> Block:
        """Add a block to the diagram.

        Args:
            block_type: Type of block ("gain", "io_marker")
            id: Unique identifier for the block
            position: Optional canvas position
            **kwargs: Block-specific parameters (including optional 'label')

        Returns:
            The created Block object

        Raises:
            ValueError: If block type is unknown or id already exists
        """
        # Check for duplicate ID
        if any(block.id == id for block in self.blocks):
            raise ValueError(f"Block with id '{id}' already exists")

        # Prepare factory kwargs
        factory_kwargs = {"position": position}

        # For IOMarker, 'label' in kwargs is the signal label (inside block)
        # For other blocks, 'label' is the block label (below block)
        if block_type == "io_marker":
            # For IOMarkers, don't pop 'label' - it's the signal label
            # block_label would be passed separately if provided
            # IOMarkers typically don't have block labels
            factory_kwargs["block_label"] = None

            # Auto-assign index if not provided (new blocks only)
            # During deserialization, _ensure_index handles missing indices
            if "index" not in kwargs and not hasattr(self, "_deserializing"):
                # Get marker_type to determine which sequence to use
                marker_type = kwargs.get("marker_type", "input")
                kwargs["index"] = self._auto_assign_index(marker_type)

            # Pass all kwargs (label for signal name + auto index)
            factory_kwargs.update(kwargs)
        else:
            # For other blocks, pop 'label' as the block label
            block_label = kwargs.pop("label", None)
            if block_label is not None:
                factory_kwargs["label"] = block_label
            # Add remaining kwargs (K, signs, numerator, etc.)
            factory_kwargs.update(kwargs)

        # Create block using factory
        from lynx.blocks import create_block

        block = create_block(block_type, id, **factory_kwargs)

        # Save state before modification (for undo)
        self._save_state()

        self.blocks.append(block)
        return block

    def get_block(self, block_id: str) -> Optional[Block]:
        """Get block by ID.

        Args:
            block_id: Block identifier

        Returns:
            Block if found, None otherwise
        """
        for block in self.blocks:
            if block.id == block_id:
                # Ensure IOMarker blocks have index (backward compatibility)
                if block.type == "io_marker":
                    self._ensure_index(block)
                return block
        return None

    def remove_block(self, block_id: str) -> bool:
        """Remove block from diagram and all connected edges.

        For IOMarker blocks, automatically renumbers remaining markers of the same
        type to maintain valid sequence (0, 1, 2, ..., N-1).

        Args:
            block_id: Block identifier

        Returns:
            True if block was removed, False if not found
        """
        for i, block in enumerate(self.blocks):
            if block.id == block_id:
                # Save state before modification (for undo)
                self._save_state()

                # Capture IOMarker info before deletion (for cascade renumbering)
                is_iomarker = block.type == "io_marker"
                if is_iomarker:
                    # Ensure block has index (backward compatibility)
                    self._ensure_index(block)
                    marker_type = block.get_parameter("marker_type")
                    deleted_index = block.get_parameter("index")

                # Remove the block
                del self.blocks[i]

                # Remove all connections to/from this block
                self.connections = [
                    conn
                    for conn in self.connections
                    if (
                        conn.source_block_id != block_id
                        and conn.target_block_id != block_id
                    )
                ]

                # Cascade renumbering for IOMarker deletion
                if is_iomarker:
                    # Decrement indices for all markers with index > deleted_index
                    markers = [
                        b
                        for b in self.blocks
                        if b.type == "io_marker"
                        and b.get_parameter("marker_type") == marker_type
                        and b.get_parameter("index") > deleted_index
                    ]
                    for marker in markers:
                        current_idx = marker.get_parameter("index")
                        marker._parameters = [
                            p for p in marker._parameters if p.name != "index"
                        ]
                        marker.add_parameter(name="index", value=current_idx - 1)

                return True
        return False

    def add_connection(
        self,
        connection_id: str,
        source_block_id: str,
        source_port_id: str,
        target_block_id: str,
        target_port_id: str,
        label: Optional[str] = None,
    ) -> ValidationResult:
        """Add a connection between two block ports with validation.

        Args:
            connection_id: Unique connection identifier
            source_block_id: ID of source block
            source_port_id: ID of source port (must be output)
            target_block_id: ID of target block
            target_port_id: ID of target port (must be input)
            label: Optional label for the connection

        Returns:
            ValidationResult indicating success or failure with error messages
        """
        errors: List[str] = []

        # Check for duplicate connection ID
        if any(conn.id == connection_id for conn in self.connections):
            errors.append(f"Connection with id '{connection_id}' already exists")
            return ValidationResult(is_valid=False, errors=errors)

        # Validate source block exists
        source_block = self.get_block(source_block_id)
        if source_block is None:
            errors.append(f"Source block '{source_block_id}' not found")
            return ValidationResult(is_valid=False, errors=errors)

        # Validate target block exists
        target_block = self.get_block(target_block_id)
        if target_block is None:
            errors.append(f"Target block '{target_block_id}' not found")
            return ValidationResult(is_valid=False, errors=errors)

        # Validate source port exists and is an output
        source_port = None
        for port in source_block._ports:
            if port.id == source_port_id:
                source_port = port
                break

        if source_port is None:
            msg = f"Source port '{source_port_id}' not found on block"
            errors.append(f"{msg} '{source_block_id}'")
            return ValidationResult(is_valid=False, errors=errors)

        if source_port.type != "output":
            msg = (
                f"Source port '{source_port_id}' must be an output port "
                f"(found '{source_port.type}')"
            )
            errors.append(msg)
            return ValidationResult(is_valid=False, errors=errors)

        # Validate target port exists and is an input
        target_port = None
        for port in target_block._ports:
            if port.id == target_port_id:
                target_port = port
                break

        if target_port is None:
            msg = f"Target port '{target_port_id}' not found on block"
            errors.append(f"{msg} '{target_block_id}'")
            return ValidationResult(is_valid=False, errors=errors)

        if target_port.type != "input":
            msg = (
                f"Target port '{target_port_id}' must be an input port "
                f"(found '{target_port.type}')"
            )
            errors.append(msg)
            return ValidationResult(is_valid=False, errors=errors)

        # Check if target input port already has a connection
        for existing_conn in self.connections:
            if (
                existing_conn.target_block_id == target_block_id
                and existing_conn.target_port_id == target_port_id
            ):
                msg = (
                    f"Target port '{target_port_id}' on block '{target_block_id}' "
                    f"already has a connection"
                )
                errors.append(msg)
                return ValidationResult(is_valid=False, errors=errors)

        # Save state before modification (for undo)
        self._save_state()

        # All validations passed - create connection
        connection = Connection(
            id=connection_id,
            source_block_id=source_block_id,
            source_port_id=source_port_id,
            target_block_id=target_block_id,
            target_port_id=target_port_id,
            label=label,
        )
        self.connections.append(connection)

        return ValidationResult(is_valid=True, errors=[])

    def remove_connection(self, connection_id: str) -> bool:
        """Remove connection from diagram.

        Args:
            connection_id: Connection identifier

        Returns:
            True if connection was removed, False if not found
        """
        for i, conn in enumerate(self.connections):
            if conn.id == connection_id:
                # Save state before modification (for undo)
                self._save_state()

                del self.connections[i]
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize diagram to dictionary using Pydantic for validation.

        Returns:
            Dictionary representation with version, blocks, connections
        """
        # Build data structure
        data = {
            "version": self._version,
            "blocks": [block.to_dict() for block in self.blocks],
            "connections": [conn.to_dict() for conn in self.connections],
            "theme": self.theme,  # Theme name (light, dark, high-contrast) or None
        }

        # Validate with Pydantic and return as dict
        model = DiagramModel(**data)  # type: ignore[arg-type]
        return model.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Diagram":
        """Deserialize diagram from dictionary with Pydantic validation.

        Args:
            data: Dictionary with version, blocks, connections

        Returns:
            Diagram object

        Raises:
            ValidationError: If data doesn't match schema
            ValueError: If block type is unknown
        """
        # Validate with Pydantic first
        try:
            model = DiagramModel(**data)
        except PydanticValidationError as e:
            raise ValueError(f"Invalid diagram data: {e}") from e

        diagram = cls()
        diagram._version = model.version
        diagram.theme = model.theme  # Restore theme (None for old diagrams)
        diagram._deserializing = True  # Flag to skip auto-index assignment

        # Deserialize blocks
        for block_data in model.blocks:
            block_dict = block_data.model_dump()
            block_type = block_dict["type"]
            block_id = block_dict["id"]
            position = block_dict["position"]
            block_label = block_dict.get("label")  # Extract block label
            block_flipped = block_dict.get("flipped", False)  # Extract flipped state

            # Extract parameters as kwargs
            params = {}
            for param in block_dict.get("parameters", []):
                params[param["name"]] = param["value"]

            # Add label to params if present (but not for IOMarkers)
            # For IOMarkers, 'label' in params is the signal label, not block label
            if block_label is not None and block_type != "io_marker":
                params["label"] = block_label

            # Create block using add_block
            block = diagram.add_block(
                block_type=block_type, id=block_id, position=position, **params
            )

            # Restore additional attributes after creation
            if block:
                block.flipped = block_flipped
                # Restore optional attributes from block_dict
                if block_dict.get("custom_latex") is not None:
                    block.custom_latex = block_dict["custom_latex"]
                if block_dict.get("label_visible") is not None:
                    block.label_visible = block_dict["label_visible"]
                if block_dict.get("width") is not None:
                    block.width = block_dict["width"]
                if block_dict.get("height") is not None:
                    block.height = block_dict["height"]

            # Restore expression fields if present
            for param_data in block_dict.get("parameters", []):
                if "expression" in param_data and param_data["expression"] is not None:
                    # Find matching parameter and set expression
                    for param in block._parameters:
                        if param.name == param_data["name"]:
                            param.expression = param_data["expression"]
                            break

        # Ensure all IOMarker blocks have indices (backward compatibility)
        for block in diagram.blocks:
            if block.type == "io_marker":
                diagram._ensure_index(block)

        # Clear deserializing flag
        del diagram._deserializing

        # Deserialize connections
        for conn_data in model.connections:
            conn_dict = conn_data.model_dump()
            result = diagram.add_connection(
                connection_id=conn_dict["id"],
                source_block_id=conn_dict["source_block_id"],
                source_port_id=conn_dict["source_port_id"],
                target_block_id=conn_dict["target_block_id"],
                target_port_id=conn_dict["target_port_id"],
            )
            # If connection was added successfully, restore waypoints and label fields
            if result.is_valid:
                # Find the connection we just added and set waypoints and label
                for conn in diagram.connections:
                    if conn.id == conn_dict["id"]:
                        # Convert WaypointModel list to dict list
                        waypoints = conn_dict.get("waypoints", [])
                        conn.waypoints = waypoints if waypoints else []
                        # Restore label fields
                        conn.label = conn_dict.get("label")
                        conn.label_visible = conn_dict.get("label_visible", False)
                        break
            # Silently skip invalid connections during deserialization
            # (could raise exception in strict mode if needed)

        return diagram

    def save(self, filename: Union[str, Path]) -> None:
        """Save diagram to JSON file.

        Args:
            filename: Path to save file

        Raises:
            IOError: If file cannot be written
        """
        filepath = Path(filename)

        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Serialize and write
        data = self.to_dict()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filename: Union[str, Path]) -> "Diagram":
        """Load diagram from JSON file.

        Args:
            filename: Path to load file

        Returns:
            Diagram object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is malformed or invalid diagram data
        """
        filepath = Path(filename)

        if not filepath.exists():
            raise FileNotFoundError(f"Diagram file not found: {filepath}")

        # Read and deserialize
        with open(filepath, "r") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def _save_state(self) -> None:
        """Save current diagram state to history for undo/redo.

        Creates a snapshot of current blocks and connections.
        Clears future stack (redo history) when new action is performed.
        """
        # Snapshot current state
        state = {
            "blocks": [block.to_dict() for block in self.blocks],
            "connections": [conn.to_dict() for conn in self.connections],
        }
        self._history.append(state)

        # Clear future stack (new action invalidates redo history)
        self._future.clear()

    def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restore diagram state from snapshot.

        Args:
            state: Dictionary containing blocks and connections snapshot
        """
        # Clear current state
        self.blocks.clear()
        self.connections.clear()

        # Restore blocks
        for block_data in state.get("blocks", []):
            params = {}

            # Extract parameters
            for param in block_data.get("parameters", []):
                params[param["name"]] = param.get("value")

            # Add block (without saving state - internal operation)
            self.blocks.append(self._create_block_from_dict(block_data))

        # Restore connections
        for conn_data in state.get("connections", []):
            conn = Connection(
                id=conn_data["id"],
                source_block_id=conn_data["source_block_id"],
                source_port_id=conn_data["source_port_id"],
                target_block_id=conn_data["target_block_id"],
                target_port_id=conn_data["target_port_id"],
                waypoints=conn_data.get("waypoints", []),
                label=conn_data.get("label"),
                label_visible=conn_data.get("label_visible", False),
            )
            self.connections.append(conn)

    def _create_block_from_dict(self, block_data: Dict[str, Any]) -> Block:
        """Create a block instance from dictionary data (helper for undo/redo).

        Args:
            block_data: Block dictionary with type, id, parameters, etc.

        Returns:
            Block instance
        """
        block_type = block_data["type"]
        block_id = block_data["id"]
        position = block_data.get("position")
        label = block_data.get("label")
        flipped = block_data.get("flipped", False)

        # Extract parameters into kwargs
        param_kwargs = {}
        for param in block_data.get("parameters", []):
            param_kwargs[param["name"]] = param.get("value")

        # Prepare factory kwargs
        factory_kwargs = {"position": position}

        # For IOMarker, handle special label semantics
        if block_type == "io_marker":
            factory_kwargs["block_label"] = label
            # Signal label comes from parameters
            if "label" in param_kwargs:
                factory_kwargs["label"] = param_kwargs["label"]
            if "marker_type" in param_kwargs:
                factory_kwargs["marker_type"] = param_kwargs["marker_type"]
        else:
            # For other blocks, block label is just 'label'
            if label is not None:
                factory_kwargs["label"] = label
            # Add all parameters
            factory_kwargs.update(param_kwargs)

        # Create block using factory
        from lynx.blocks import create_block

        block = create_block(block_type, block_id, **factory_kwargs)

        # Restore additional block attributes
        block.flipped = flipped
        # Restore optional attributes if present in data
        if "custom_latex" in block_data:
            block.custom_latex = block_data["custom_latex"]
        if "label_visible" in block_data:
            block.label_visible = block_data["label_visible"]
        if "width" in block_data:
            block.width = block_data["width"]
        if "height" in block_data:
            block.height = block_data["height"]

        return block

    def undo(self) -> bool:
        """Undo the last action.

        Returns:
            True if undo successful, False if no history
        """
        if not self._history:
            return False

        # Save current state to future stack
        current_state = {
            "blocks": [block.to_dict() for block in self.blocks],
            "connections": [conn.to_dict() for conn in self.connections],
        }
        self._future.append(current_state)

        # Restore previous state
        previous_state = self._history.pop()
        self._restore_state(previous_state)

        return True

    def redo(self) -> bool:
        """Redo the last undone action.

        Returns:
            True if redo successful, False if no future
        """
        if not self._future:
            return False

        # Save current state to history stack
        current_state = {
            "blocks": [block.to_dict() for block in self.blocks],
            "connections": [conn.to_dict() for conn in self.connections],
        }
        self._history.append(current_state)

        # Restore future state
        future_state = self._future.pop()
        self._restore_state(future_state)

        return True

    def update_block_position(self, block_id: str, position: Dict[str, float]) -> bool:
        """Update block position (with undo support).

        When a block moves, waypoints for all connections to/from that block
        are cleared, forcing the connections to auto-route. This matches
        Simulink's UX where manual routing is reset when blocks move.

        Args:
            block_id: Block identifier
            position: New position dictionary with 'x' and 'y' keys

        Returns:
            True if block was found and updated, False otherwise
        """
        block = self.get_block(block_id)
        if not block:
            return False

        # Save state before modification (for undo)
        self._save_state()

        # Update position (deep copy to avoid reference issues)
        block.position = dict(position)

        # Clear waypoints for all connections involving this block
        # This forces connections to auto-route after block move
        self._clear_waypoints_for_block(block_id)

        return True

    def _clear_waypoints_for_block(self, block_id: str) -> None:
        """Clear waypoints for all connections to/from a block.

        This is called when a block moves to reset manual routing.
        The frontend will auto-route these connections fresh.

        Args:
            block_id: Block identifier
        """
        for conn in self.connections:
            if conn.source_block_id == block_id or conn.target_block_id == block_id:
                conn.waypoints = []

    def _renumber_markers_downward_shift(
        self, marker_type: str, target_block_id: str, old_index: int, new_index: int
    ) -> None:
        """Renumber markers when index changes to a lower value.

        When a marker's index changes from high to low (e.g., 2→0), markers in
        the range [new_index, old_index-1] shift up by 1.

        Example: [0:A, 1:B, 2:C] + change C(2→0) = [0:C, 1:A, 2:B]

        Args:
            marker_type: "input" or "output"
            target_block_id: Block being renumbered
            old_index: Original index value
            new_index: New index value (< old_index)
        """
        # Get all markers of same type (excluding target block)
        markers = [
            b
            for b in self.blocks
            if b.type == "io_marker"
            and b.id != target_block_id
            and b.get_parameter("marker_type") == marker_type
        ]

        # Sort by current index (ascending) to avoid collisions during shift
        markers.sort(key=lambda b: b.get_parameter("index"))

        # Shift markers in range [new_index, old_index-1] up by 1
        for marker in markers:
            current_idx = marker.get_parameter("index")
            if new_index <= current_idx < old_index:
                # Update parameter directly (no undo, internal operation)
                marker._parameters = [
                    p for p in marker._parameters if p.name != "index"
                ]
                marker.add_parameter(name="index", value=current_idx + 1)

    def _renumber_markers_upward_shift(
        self, marker_type: str, target_block_id: str, old_index: int, new_index: int
    ) -> None:
        """Renumber markers when index changes to a higher value.

        When a marker's index changes from low to high (e.g., 0→2), markers in
        the range [old_index+1, new_index] shift down by 1.

        Example: [0:A, 1:B, 2:C] + change A(0→2) = [0:B, 1:C, 2:A]

        Args:
            marker_type: "input" or "output"
            target_block_id: Block being renumbered
            old_index: Original index value
            new_index: New index value (> old_index)
        """
        # Get all markers of same type (excluding target block)
        markers = [
            b
            for b in self.blocks
            if b.type == "io_marker"
            and b.id != target_block_id
            and b.get_parameter("marker_type") == marker_type
        ]

        # Sort by current index (descending) to avoid collisions during shift
        markers.sort(key=lambda b: b.get_parameter("index"), reverse=True)

        # Shift markers in range [old_index+1, new_index] down by 1
        for marker in markers:
            current_idx = marker.get_parameter("index")
            if old_index < current_idx <= new_index:
                # Update parameter directly (no undo, internal operation)
                marker._parameters = [
                    p for p in marker._parameters if p.name != "index"
                ]
                marker.add_parameter(name="index", value=current_idx - 1)

    def _renumber_markers(self, block_id: str, new_index: int, old_index: int) -> None:
        """Orchestrate automatic index renumbering for IOMarker blocks.

        Implements Simulink-style renumbering:
        - Clamps out-of-range/negative values to valid range [0, N-1]
        - Triggers downward or upward shift based on index change direction
        - Maintains valid sequence 0, 1, 2, ..., N-1 without gaps

        Args:
            block_id: IOMarker block being renumbered
            new_index: Desired new index (may be clamped)
            old_index: Original index value (before update)
        """
        block = self.get_block(block_id)
        if not block or block.type != "io_marker":
            return

        marker_type = block.get_parameter("marker_type")

        # Count total markers of same type
        num_markers = sum(
            1
            for b in self.blocks
            if b.type == "io_marker" and b.get_parameter("marker_type") == marker_type
        )

        # Clamp new_index to valid range [0, N-1]
        clamped_index = max(0, min(new_index, num_markers - 1))

        # Update the target block's index to the clamped value first
        # (update_block_parameter may have set it to an out-of-range value)
        block._parameters = [p for p in block._parameters if p.name != "index"]
        block.add_parameter(name="index", value=clamped_index)

        # No renumbering of other blocks needed if clamped index equals old index
        if clamped_index == old_index:
            return

        # Trigger appropriate shift direction for other blocks
        if clamped_index < old_index:
            self._renumber_markers_downward_shift(
                marker_type, block_id, old_index, clamped_index
            )
        else:  # clamped_index > old_index
            self._renumber_markers_upward_shift(
                marker_type, block_id, old_index, clamped_index
            )

    def update_block_parameter(
        self,
        block_id: str,
        param_name: str,
        value: Any,
        expression: Optional[str] = None,
    ) -> bool:
        """Update block parameter (with undo support).

        Args:
            block_id: Block identifier
            param_name: Parameter name (e.g., "K", "numerator", "A")
            value: New parameter value
            expression: Optional expression string (for hybrid storage)

        Returns:
            True if block and parameter were found and updated, False otherwise
        """
        block = self.get_block(block_id)
        if not block:
            return False

        # Check if parameter exists
        try:
            old_value = block.get_parameter(param_name)
        except KeyError:
            return False

        # Save state before modification (for undo)
        self._save_state()

        # Capture old index for IOMarker renumbering (before update)
        old_index = None
        if block.type == "io_marker" and param_name == "index":
            old_index = old_value

        # Update parameter by removing old and adding new
        block._parameters = [p for p in block._parameters if p.name != param_name]
        block.add_parameter(name=param_name, value=value, expression=expression)

        # Special handling for Sum block signs parameter - regenerate input ports
        if block.type == "sum" and param_name == "signs":
            # Collect old input port IDs before removing them
            old_input_port_ids = [p.id for p in block._ports if p.type == "input"]

            # Remove all existing input ports (keep output port)
            block._ports = [p for p in block._ports if p.type != "input"]

            # Recreate input ports based on new signs (skip "|")
            port_num = 1
            for sign in value:
                if sign != "|":
                    block.add_port(port_id=f"in{port_num}", port_type="input")
                    port_num += 1

            # Remove connections to deleted ports
            new_input_port_ids = [p.id for p in block._ports if p.type == "input"]
            deleted_port_ids = set(old_input_port_ids) - set(new_input_port_ids)

            if deleted_port_ids:
                # Remove connections where target is a deleted port on this block
                self.connections = [
                    conn
                    for conn in self.connections
                    if not (
                        conn.target_block_id == block_id
                        and conn.target_port_id in deleted_port_ids
                    )
                ]

        # Special handling for IOMarker index - trigger automatic renumbering
        if (
            block.type == "io_marker"
            and param_name == "index"
            and old_index is not None
        ):
            self._renumber_markers(block_id, value, old_index)

        return True

    def update_block_dimensions(
        self, block_id: str, width: float, height: float
    ) -> bool:
        """Update block dimensions (with undo support).

        When a block is resized, port positions change. Waypoints for all
        connections to/from that block are cleared, forcing auto-route.
        This matches the behavior when blocks move.

        Args:
            block_id: Block identifier
            width: New width in pixels
            height: New height in pixels

        Returns:
            True if block was found and updated, False otherwise
        """
        block = self.get_block(block_id)
        if not block:
            return False

        # Save state before modification (for undo)
        self._save_state()

        # Update dimensions
        block.width = width
        block.height = height

        # Clear waypoints for all connections involving this block
        # This forces connections to auto-route after resize
        self._clear_waypoints_for_block(block_id)

        return True

    def re_evaluate_expressions(self, namespace: Dict[str, Any]) -> List[str]:
        """Re-evaluate all parameter expressions against current notebook namespace.

        Called after loading a diagram to update values based on current variables.
        This allows diagrams to be parametric - when variables change in the notebook,
        the diagram values update automatically on load.

        Args:
            namespace: Dictionary of available variables (from notebook)

        Returns:
            List of warning messages for parameters that used fallback values

        Example:
            >>> diagram = Diagram.load("mydiagram.json")
            >>> namespace = get_notebook_namespace()
            >>> warnings = diagram.re_evaluate_expressions(namespace)
            >>> # warnings = ["Block 'gain1' parameter 'K': Variable 'kp'
            >>> # not found, using stored value"]
        """
        from lynx.expression_eval import evaluate_expression

        warnings: List[str] = []

        for block in self.blocks:
            for param in block._parameters:
                # Only re-evaluate if expression exists
                if param.expression is not None:
                    # Use stored value if variable missing
                    result = evaluate_expression(
                        expression=param.expression,
                        namespace=namespace,
                        fallback=param.value,
                    )

                    if result.success:
                        # Update parameter value with re-evaluated result
                        param.value = result.value

                        # Collect warning if fallback was used
                        if result.used_fallback and result.warning:
                            msg = (
                                f"Block '{block.id}' parameter "
                                f"'{param.name}': {result.warning}"
                            )
                            warnings.append(msg)
                    else:
                        # Evaluation failed - keep existing value and warn
                        msg = (
                            f"Block '{block.id}' parameter "
                            f"'{param.name}': {result.error}"
                        )
                        warnings.append(msg)

        return warnings

    def update_block_label(self, block_id: str, label: str) -> bool:
        """Update block label (with undo support).

        Args:
            block_id: Block identifier
            label: New label string (empty/whitespace-only reverts to block ID)

        Returns:
            True if block was found and updated, False otherwise
        """
        block = self.get_block(block_id)
        if not block:
            return False

        # Save state before modification (for undo)
        self._save_state()

        # Update label - empty or whitespace-only labels revert to block ID (FR-006)
        block.label = label if label.strip() else block.id
        return True

    def flip_block(self, block_id: str) -> bool:
        """Toggle block horizontal flip (with undo support).

        When a block is flipped, port positions change. Waypoints for all
        connections to/from that block are cleared, forcing auto-route.
        This matches the behavior when blocks move or resize.

        Args:
            block_id: Block identifier

        Returns:
            True if block was found and flipped, False otherwise
        """
        block = self.get_block(block_id)
        if not block:
            return False

        # Save state before modification (for undo)
        self._save_state()

        # Toggle flip state
        block.flipped = not block.flipped

        # Clear waypoints for all connections involving this block
        # This forces connections to auto-route after flip
        self._clear_waypoints_for_block(block_id)

        return True

    def toggle_label_visibility(self, block_id: str) -> bool:
        """Toggle block label visibility (with undo support).

        Args:
            block_id: Block identifier

        Returns:
            True if block was found and toggled, False otherwise
        """
        block = self.get_block(block_id)
        if not block:
            return False

        # Save state before modification (for undo)
        self._save_state()

        # Toggle label visibility
        block.label_visible = not block.label_visible
        return True

    def update_connection_waypoints(
        self, connection_id: str, waypoints: List[Dict[str, float]]
    ) -> bool:
        """Update waypoints for a connection's custom routing.

        Args:
            connection_id: Connection identifier
            waypoints: List of waypoint dictionaries with x, y coordinates

        Returns:
            True if connection was found and updated, False otherwise
        """
        for conn in self.connections:
            if conn.id == connection_id:
                # Save state before modification (for undo)
                self._save_state()

                # Update waypoints
                conn.waypoints = waypoints
                return True

        return False

    def toggle_connection_label_visibility(self, connection_id: str) -> bool:
        """Toggle connection label visibility (with undo support).

        Args:
            connection_id: Connection identifier

        Returns:
            True if connection was found and toggled, False otherwise
        """
        for conn in self.connections:
            if conn.id == connection_id:
                # Save state before modification (for undo)
                self._save_state()

                # Toggle label visibility
                conn.label_visible = not conn.label_visible
                return True

        return False

    def update_connection_label(self, connection_id: str, label: str) -> bool:
        """Update connection label text (with undo support).

        Args:
            connection_id: Connection identifier
            label: New label text

        Returns:
            True if connection was found and updated, False otherwise
        """
        for conn in self.connections:
            if conn.id == connection_id:
                # Save state before modification (for undo)
                self._save_state()

                # Update label
                conn.label = label
                return True

        return False

    def _clone(self) -> "Diagram":
        """Create a deep copy of the diagram for safe modification.

        Used internally by signal extraction in conversion module.

        Returns:
            Independent Diagram instance with same blocks and connections
        """
        return Diagram.from_dict(self.to_dict())

    def get_ss(self, from_signal: str, to_signal: str) -> Any:
        """Extract state-space model from one signal to another.

        Converts a Lynx diagram to a python-control StateSpace object representing
        the system dynamics from from_signal to to_signal. Automatically handles
        subsystem extraction, sign negation for sum blocks, and connection routing.

        Signal Reference Patterns (4-tier priority system):
            1. **IOMarker labels** (highest priority): Use the 'label' parameter from
               InputMarker or OutputMarker blocks (e.g., 'r', 'y', 'u')
            2. **Connection labels**: Reference labeled connections between blocks
               (e.g., 'error', 'control')
            3. **Block.port format**: Explicit block ID and port using dot notation
               (e.g., 'controller.out', 'plant.in')
            4. **Block labels** (lowest priority, SISO only): For
               single-input/single-output blocks, reference by block label
               (e.g., 'controller', 'plant')

        Args:
            from_signal: Source signal name using any of the 4 reference patterns
            to_signal: Destination signal name using any of the 4 reference patterns

        Returns:
            control.StateSpace: State-space system from from_signal → to_signal

        Raises:
            SignalNotFoundError: If either signal doesn't exist in the diagram
            ValidationError: If diagram has missing I/O markers or unconnected ports
            DiagramExportError: If python-control conversion fails

        Examples:
            >>> # Complete feedback loop example
            >>> diagram = Diagram()
            >>> diagram.add_block('io_marker', 'ref', marker_type='input', label='r')
            >>> diagram.add_block('sum', 'error_sum', signs=['+', '-', '|'])
            >>> diagram.add_block('gain', 'controller', K=5.0, label='C')
            >>> diagram.add_block('transfer_function', 'plant',
            ...                  numerator=[2.0], denominator=[1.0, 3.0], label='P')
            >>> diagram.add_block(
            ...     'io_marker', 'output', marker_type='output', label='y'
            ... )
            >>>
            >>> diagram.add_connection('c1', 'ref', 'out', 'error_sum', 'in1')
            >>> diagram.add_connection(
            ...     'c2', 'error_sum', 'out', 'controller', 'in', label='e'
            ... )
            >>> diagram.add_connection(
            ...     'c3', 'controller', 'out', 'plant', 'in', label='u'
            ... )
            >>> diagram.add_connection('c4', 'plant', 'out', 'output', 'in')
            >>> diagram.add_connection('c5', 'plant', 'out', 'error_sum', 'in2')
            >>>
            >>> # Extract closed-loop transfer function (IOMarker labels)
            >>> sys_ry = diagram.get_ss('r', 'y')
            >>> print(f"DC gain: {sys_ry.dcgain()}")  # Should be ~0.769
            >>>
            >>> # Extract sensitivity function (IOMarker + connection label)
            >>> sys_re = diagram.get_ss('r', 'e')
            >>>
            >>> # Extract controller transfer function (connection labels)
            >>> sys_eu = diagram.get_ss('e', 'u')
            >>>
            >>> # Extract using block.port format (explicit)
            >>> sys_cp = diagram.get_ss('controller.out', 'plant.out')
            >>>
            >>> # Extract using block labels (SISO blocks only)
            >>> sys_CP = diagram.get_ss('C', 'P')  # Same as controller → plant
        """
        from lynx.conversion import get_ss as extract_ss

        return extract_ss(self, from_signal, to_signal)

    def get_tf(self, from_signal: str, to_signal: str) -> Any:
        """Extract transfer function from one signal to another.

        Converts a Lynx diagram to a python-control TransferFunction object. This is
        the preferred method for SISO subsystem analysis where you want the classic
        numerator/denominator representation.

        Signal Reference Patterns:
            Uses the same 4-tier priority system as get_ss():
            1. IOMarker labels ('r', 'y')
            2. Connection labels ('error', 'control')
            3. Block.port format ('controller.out', 'plant.in')
            4. Block labels - SISO only ('controller', 'plant')

        Args:
            from_signal: Source signal name using any of the 4 reference patterns
            to_signal: Destination signal name using any of the 4 reference patterns

        Returns:
            control.TransferFunction: Transfer function from from_signal → to_signal

        Raises:
            SignalNotFoundError: If either signal doesn't exist in the diagram
            ValidationError: If diagram has missing I/O markers or unconnected ports
            DiagramExportError: If python-control conversion fails

        Note:
            For MIMO systems, use get_ss() instead as transfer functions
            are only well-defined for SISO systems. python-control will raise
            an error if you try to convert a MIMO state-space to transfer function.

        Examples:
            >>> # Extract closed-loop transfer function using IOMarker labels
            >>> tf_ry = diagram.get_tf('r', 'y')
            >>> print(tf_ry)
            >>> # TransferFunction:
            >>> #     10
            >>> # -------------
            >>> # s^2 + 5 s + 6
            >>>
            >>> # Analyze using python-control functions
            >>> import control as ct
            >>> import numpy as np
            >>> t = np.linspace(0, 5, 500)
            >>> t_out, y_out = ct.step_response(tf_ry, t)
            >>>
            >>> # Extract plant transfer function using block labels
            >>> tf_plant = diagram.get_tf('plant.in', 'plant.out')
            >>> print(f"Plant DC gain: {tf_plant.dcgain()}")
            >>>
            >>> # Compute loop gain for stability analysis
            >>> L = diagram.get_tf('error', 'y')  # Loop gain
            >>> gm, pm, wgm, wpm = ct.margin(L)
            >>> print(f"Phase margin: {pm:.1f} degrees")
        """
        from lynx.conversion import get_tf as extract_tf

        return extract_tf(self, from_signal, to_signal)
