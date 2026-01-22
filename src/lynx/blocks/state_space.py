# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""State Space block implementation.

State space representation of a linear time-invariant system:
    dx/dt = Ax + Bu
    y = Cx + Du

where x is the state vector, u is the input, and y is the output.
"""

from typing import Dict, List, Optional

from lynx.blocks.base import Block
from lynx.config.constants import BLOCK_TYPES


class StateSpaceBlock(Block):
    """State space block with A, B, C, D matrices.

    Parameters:
        A: State matrix (n x n)
        B: Input matrix (n x m)
        C: Output matrix (p x n)
        D: Feedthrough matrix (p x m)

    For MVP (SISO systems): m=1 (single input), p=1 (single output)

    Example:
        Second-order system:
        A = [[0, 1], [-2, -3]]
        B = [[0], [1]]
        C = [[1, 0]]
        D = [[0]]

    Ports:
        Input: in (single input for SISO)
        Output: out (single output for SISO)
    """

    def __init__(
        self,
        id: str,
        A: List[List[float]],
        B: List[List[float]],
        C: List[List[float]],
        D: List[List[float]],
        position: Optional[Dict[str, float]] = None,
        label: Optional[str] = None,
    ) -> None:
        """Initialize state space block.

        Args:
            id: Unique block identifier
            A: State matrix
            B: Input matrix
            C: Output matrix
            D: Feedthrough matrix
            position: Optional {x, y} position on canvas
            label: Optional user-facing label (defaults to id)
        """
        super().__init__(
            id=id, block_type=BLOCK_TYPES["STATE_SPACE"], position=position, label=label
        )

        # Store matrix parameters
        # Note: Currently uses simple arrays, expressions may be added later
        self.add_parameter(name="A", value=A)
        self.add_parameter(name="B", value=B)
        self.add_parameter(name="C", value=C)
        self.add_parameter(name="D", value=D)

        # Create ports (SISO for MVP)
        self.add_port(port_id="in", port_type="input")
        self.add_port(port_id="out", port_type="output")
