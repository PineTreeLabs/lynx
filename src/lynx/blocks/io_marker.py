# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Input/Output marker blocks.

These blocks mark system boundaries:
- InputMarker: Marks where signals enter the system
- OutputMarker: Marks where signals leave the system

No parameters except optional label.
"""

from typing import Dict, Optional

from lynx.blocks.base import Block
from lynx.config.constants import BLOCK_TYPES


class InputMarker(Block):
    """Input marker - signals flow OUT of this block into the system.

    Marks the input boundary of a control system diagram.

    Attributes:
        label: Optional signal name (e.g., "u", "r", "disturbance")
    """

    def __init__(
        self,
        id: str,
        label: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        index: Optional[int] = None,
        custom_latex: Optional[str] = None,
    ) -> None:
        """Initialize Input marker.

        Args:
            id: Unique block identifier
            label: Signal name (block label, e.g., "u", "r", "disturbance")
            position: Optional canvas position
            index: Optional visual display index (auto-assigned if None)
            custom_latex: Optional custom LaTeX override for block rendering
        """
        super().__init__(
            id=id,
            block_type=BLOCK_TYPES["IO_MARKER"],
            position=position,
            label=label if label is not None else id,
            custom_latex=custom_latex,
        )

        # Store marker type for serialization
        self.add_parameter(name="marker_type", value="input")

        # Optional index parameter (auto-assigned by Diagram if None)
        if index is not None:
            self.add_parameter(name="index", value=index)

        # Input marker has 1 OUTPUT port (signals flow out)
        # Port label is same as block label for display consistency
        self.add_port(port_id="out", port_type="output", label=self.label)


class OutputMarker(Block):
    """Output marker - signals flow IN to this block from the system.

    Marks the output boundary of a control system diagram.

    Attributes:
        label: Optional signal name (e.g., "y", "e", "tracking_error")
    """

    def __init__(
        self,
        id: str,
        label: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        index: Optional[int] = None,
        custom_latex: Optional[str] = None,
    ) -> None:
        """Initialize Output marker.

        Args:
            id: Unique block identifier
            label: Signal name (block label, e.g., "y", "e", "tracking_error")
            position: Optional canvas position
            index: Optional visual display index (auto-assigned if None)
            custom_latex: Optional custom LaTeX override for block rendering
        """
        super().__init__(
            id=id,
            block_type=BLOCK_TYPES["IO_MARKER"],
            position=position,
            label=label if label is not None else id,
            custom_latex=custom_latex,
        )

        # Store marker type for serialization
        self.add_parameter(name="marker_type", value="output")

        # Optional index parameter (auto-assigned by Diagram if None)
        if index is not None:
            self.add_parameter(name="index", value=index)

        # Output marker has 1 INPUT port (signals flow in)
        # Port label is same as block label for display consistency
        self.add_port(port_id="in", port_type="input", label=self.label)
