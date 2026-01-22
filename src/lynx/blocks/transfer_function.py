# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Transfer Function block implementation.

Transfer function block representing H(s) = N(s) / D(s) in Laplace domain.
"""

from typing import Dict, List, Optional

from lynx.blocks.base import Block
from lynx.config.constants import BLOCK_TYPES


class TransferFunctionBlock(Block):
    """Transfer function block with numerator and denominator polynomials.

    Parameters:
        numerator: Coefficients of numerator polynomial (highest degree first)
        denominator: Coefficients of denominator polynomial (highest degree first)

    Example:
        H(s) = (s + 2) / (s^2 + 3s + 2)
        numerator = [1, 2]
        denominator = [1, 3, 2]

    Ports:
        Input: in (single input)
        Output: out (single output)
    """

    def __init__(
        self,
        id: str,
        numerator: List[float],
        denominator: List[float],
        position: Optional[Dict[str, float]] = None,
        label: Optional[str] = None,
    ) -> None:
        """Initialize transfer function block.

        Args:
            id: Unique block identifier
            numerator: Numerator polynomial coefficients
            denominator: Denominator polynomial coefficients
            position: Optional {x, y} position on canvas
            label: Optional user-facing label (defaults to id)
        """
        super().__init__(
            id=id,
            block_type=BLOCK_TYPES["TRANSFER_FUNCTION"],
            position=position,
            label=label,
        )

        # Store parameters
        self.add_parameter(name="numerator", value=numerator)
        self.add_parameter(name="denominator", value=denominator)

        # Create ports (SISO - Single Input Single Output)
        self.add_port(port_id="in", port_type="input")
        self.add_port(port_id="out", port_type="output")
