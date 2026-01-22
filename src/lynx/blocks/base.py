# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Base Block class for all control system blocks.

All block types inherit from this base class which provides:
- Common attributes (id, type, position)
- Parameter management
- Port management
- Serialization to dictionary
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Port:
    """Connection point on a block."""

    id: str
    type: str  # "input" or "output"
    label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize port to dictionary."""
        result: Dict[str, Any] = {
            "id": self.id,
            "type": self.type,
        }
        if self.label is not None:
            result["label"] = self.label
        return result


@dataclass
class Parameter:
    """Block parameter with name and value."""

    name: str
    value: Any
    expression: Optional[str] = None  # For P2: hybrid storage

    def to_dict(self) -> Dict[str, Any]:
        """Serialize parameter to dictionary.

        Converts NumPy arrays to lists for JSON compatibility.
        """
        # Convert NumPy arrays to lists for JSON serialization
        value = self.value
        if hasattr(value, "tolist"):  # NumPy arrays, scalars have .tolist()
            value = value.tolist()

        result: Dict[str, Any] = {
            "name": self.name,
            "value": value,
        }
        if self.expression is not None:
            result["expression"] = self.expression
        return result


class Block:
    """Base class for all control system blocks.

    Attributes:
        id: Unique identifier for the block
        type: Block type identifier (gain, transfer_function, etc.)
        position: Canvas position {"x": number, "y": number}
        parameters: List of block parameters
        ports: List of input/output ports
    """

    def __init__(
        self,
        id: str,
        block_type: str,
        position: Optional[Dict[str, float]] = None,
        label: Optional[str] = None,
        flipped: bool = False,
        custom_latex: Optional[str] = None,
        label_visible: bool = False,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> None:
        """Initialize block with id and type.

        Args:
            id: Unique block identifier
            block_type: Type of block (gain, transfer_function, etc.)
            position: Optional canvas position, defaults to {x: 0, y: 0}
            label: Optional user-facing label (defaults to id if not set)
            flipped: Horizontal flip for visual layout (Gain/TF blocks)
            custom_latex: Optional custom LaTeX override for block rendering
            label_visible: Whether the block label is displayed (default: hidden)
            width: Optional block width in pixels (uses block-type default if None)
            height: Optional block height in pixels (uses block-type default if None)
        """
        self.id = id
        self.type = block_type
        self.position = position if position is not None else {"x": 0.0, "y": 0.0}
        self.label = label if label is not None else id
        self.flipped = flipped
        self.custom_latex = custom_latex
        self.label_visible = label_visible
        self.width = width
        self.height = height
        self._parameters: List[Parameter] = []
        self._ports: List[Port] = []

    def add_parameter(
        self, name: str, value: Any, expression: Optional[str] = None
    ) -> None:
        """Add a parameter to the block.

        Args:
            name: Parameter name
            value: Parameter value
            expression: Optional Python expression (for P2)
        """
        self._parameters.append(
            Parameter(name=name, value=value, expression=expression)
        )

    def get_parameter(self, name: str) -> Any:
        """Get parameter value by name.

        Args:
            name: Parameter name

        Returns:
            Parameter value

        Raises:
            KeyError: If parameter not found
        """
        for param in self._parameters:
            if param.name == name:
                return param.value
        raise KeyError(f"Parameter '{name}' not found")

    def add_port(
        self, port_id: str, port_type: str, label: Optional[str] = None
    ) -> None:
        """Add a port to the block.

        Args:
            port_id: Port identifier
            port_type: "input" or "output"
            label: Optional port label
        """
        self._ports.append(Port(id=port_id, type=port_type, label=label))

    def get_ports(self) -> List[Dict[str, Any]]:
        """Get all ports as dictionaries.

        Returns:
            List of port dictionaries
        """
        return [port.to_dict() for port in self._ports]

    def is_input_marker(self) -> bool:
        """Check if this is an input marker block.

        Returns:
            True if this is an IOMarker with marker_type='input'
        """
        try:
            return (
                self.type == "io_marker"
                and self.get_parameter("marker_type") == "input"
            )
        except KeyError:
            return False

    def is_output_marker(self) -> bool:
        """Check if this is an output marker block.

        Returns:
            True if this is an IOMarker with marker_type='output'
        """
        try:
            return (
                self.type == "io_marker"
                and self.get_parameter("marker_type") == "output"
            )
        except KeyError:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize block to dictionary for JSON export.

        Returns:
            Dictionary representation of block
        """
        result: Dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            # Deep copy for undo/redo
            "position": dict(self.position) if self.position else None,
            "label": self.label,
            "flipped": self.flipped,
            "label_visible": self.label_visible,
            "parameters": [p.to_dict() for p in self._parameters],
            "ports": self.get_ports(),
        }
        # Include custom_latex only if set (backward compatibility)
        if self.custom_latex is not None:
            result["custom_latex"] = self.custom_latex
        # Include width/height only if set (backward compatibility)
        if self.width is not None:
            result["width"] = self.width
        if self.height is not None:
            result["height"] = self.height
        return result
