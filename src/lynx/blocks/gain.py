# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Gain block implementation.

Simple scalar gain: y(t) = K * u(t)

This is the simplest block type with a single scalar parameter K.
"""

from typing import Dict, Optional

from lynx.blocks.base import Block
from lynx.config.constants import BLOCK_TYPES


class GainBlock(Block):
    """Gain block with scalar multiplier K.

    Implements: y(t) = K * u(t)

    Attributes:
        K: Scalar gain value
    """

    def __init__(
        self,
        id: str,
        K: float,
        position: Optional[Dict[str, float]] = None,
        label: Optional[str] = None,
        custom_latex: Optional[str] = None,
    ) -> None:
        """Initialize Gain block.

        Args:
            id: Unique block identifier
            K: Scalar gain value (required)
            position: Optional canvas position
            label: Optional user-facing label (defaults to id)
            custom_latex: Optional custom LaTeX override for block rendering
        """
        super().__init__(
            id=id,
            block_type=BLOCK_TYPES["GAIN"],
            position=position,
            label=label,
            custom_latex=custom_latex,
        )

        # Add K parameter
        self.add_parameter(name="K", value=K)

        # Gain block has 1 input and 1 output port
        self.add_port(port_id="in", port_type="input")
        self.add_port(port_id="out", port_type="output")
