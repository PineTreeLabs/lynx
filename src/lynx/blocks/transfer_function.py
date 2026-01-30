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
        num: Coefficients of numerator polynomial (highest degree first)
        den: Coefficients of denominator polynomial (highest degree first)

    Example:
        H(s) = (s + 2) / (s^2 + 3s + 2)
        num = [1, 2]
        den = [1, 3, 2]

    Ports:
        Input: in (single input)
        Output: out (single output)
    """

    def __init__(
        self,
        id: str,
        num: List[float],
        den: List[float],
        position: Optional[Dict[str, float]] = None,
        label: Optional[str] = None,
    ) -> None:
        """Initialize transfer function block.

        Args:
            id: Unique block identifier
            num: Numerator polynomial coefficients
            den: Denominator polynomial coefficients
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
        self.add_parameter(name="num", value=num)
        self.add_parameter(name="den", value=den)

        # Create ports (SISO - Single Input Single Output)
        self.add_port(port_id="in", port_type="input")
        self.add_port(port_id="out", port_type="output")
