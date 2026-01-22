# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Pydantic schemas for Lynx diagram serialization.

Provides type-safe serialization/deserialization with automatic validation.
Supports schema versioning and forward/backward compatibility.
"""

import time
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PortModel(BaseModel):
    """Port schema - connection point on a block."""

    model_config = ConfigDict(extra="forbid")  # Fail loudly on unexpected fields

    id: str
    type: Literal["input", "output"]
    label: Optional[str] = None


class ParameterModel(BaseModel):
    """Parameter schema - block configuration value."""

    model_config = ConfigDict(extra="forbid")  # Fail loudly on unexpected fields

    name: str
    value: Any
    expression: Optional[str] = None  # Future: support for expression-based parameters


class BaseBlockModel(BaseModel):
    """Base block schema - common fields for all block types."""

    model_config = ConfigDict(extra="forbid")  # Fail loudly on unexpected fields

    id: str
    type: str
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    label: Optional[str] = None  # User-facing block label (defaults to id if not set)
    flipped: bool = False  # Horizontal flip for visual layout (Gain/TF blocks)
    custom_latex: Optional[str] = None  # Custom LaTeX override for block rendering
    label_visible: bool = (
        False  # Whether the block label is displayed (default: hidden)
    )
    width: Optional[float] = (
        None  # Block width in pixels (uses block-type default if None)
    )
    height: Optional[float] = (
        None  # Block height in pixels (uses block-type default if None)
    )
    parameters: list[ParameterModel] = Field(default_factory=list)
    ports: list[PortModel] = Field(default_factory=list)


class GainBlockModel(BaseBlockModel):
    """Gain block schema."""

    type: Literal["gain"] = "gain"


class IOMarkerBlockModel(BaseBlockModel):
    """I/O Marker block schema (InputMarker or OutputMarker)."""

    type: Literal["io_marker"] = "io_marker"


class SumBlockModel(BaseBlockModel):
    """Sum block schema."""

    type: Literal["sum"] = "sum"


class TransferFunctionBlockModel(BaseBlockModel):
    """Transfer function block schema."""

    type: Literal["transfer_function"] = "transfer_function"


class StateSpaceBlockModel(BaseBlockModel):
    """State space block schema."""

    type: Literal["state_space"] = "state_space"


# Discriminated union for all block types
BlockModel = Union[
    GainBlockModel,
    IOMarkerBlockModel,
    SumBlockModel,
    TransferFunctionBlockModel,
    StateSpaceBlockModel,
]


class WaypointModel(BaseModel):
    """Waypoint schema - intermediate routing point for connection paths."""

    model_config = ConfigDict(extra="forbid")  # Fail loudly on unexpected fields

    x: float
    y: float


class ConnectionModel(BaseModel):
    """Connection schema - edge between two block ports."""

    model_config = ConfigDict(extra="forbid")  # Fail loudly on unexpected fields

    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: list[WaypointModel] = Field(default_factory=list)
    label: Optional[str] = (
        None  # User-defined label text (defaults to connection ID if not set)
    )
    label_visible: bool = (
        False  # Whether the connection label is displayed (default: hidden)
    )


class ValidationResultModel(BaseModel):
    """Validation result schema - errors and warnings."""

    model_config = ConfigDict(extra="forbid")  # Fail loudly on unexpected fields

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class DiagramModel(BaseModel):
    """Diagram schema - complete block diagram with version."""

    model_config = ConfigDict(extra="forbid")  # Fail loudly on unexpected fields

    version: str = "1.0.0"
    blocks: list[BlockModel] = Field(default_factory=list)
    connections: list[ConnectionModel] = Field(default_factory=list)
    # Theme name (light, dark, high-contrast) - Optional for back compat
    theme: Optional[str] = None
    _version: Optional[float] = (
        None  # Internal timestamp for traitlet sync (not persisted to file)
    )

    @field_validator("blocks", mode="before")
    @classmethod
    def parse_blocks(cls, v: Any) -> Any:
        """Parse blocks with discriminator support."""
        # Pydantic handles discriminated unions automatically via 'type' field
        return v
