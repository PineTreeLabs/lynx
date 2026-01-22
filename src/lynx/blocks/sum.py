# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Sum block implementation.

Sum junction block that adds/subtracts multiple inputs based on signs.
Output = sign[0]*input[0] + sign[1]*input[1] + ... + sign[n-1]*input[n-1]
"""

from typing import Dict, List, Optional

from lynx.blocks.base import Block
from lynx.config.constants import BLOCK_TYPES


class SumBlock(Block):
    """Sum block with configurable signs for each input.

    Parameters:
        signs: List of "+" or "-" strings, one per input port (minimum 2)

    Ports:
        Inputs: in1, in2, ..., inN (one per sign)
        Output: out (single output)
    """

    def __init__(
        self,
        id: str,
        signs: List[str],
        position: Optional[Dict[str, float]] = None,
        label: Optional[str] = None,
    ) -> None:
        """Initialize sum block.

        Args:
            id: Unique block identifier
            signs: List of exactly 3 signs ("+", "-", or "|") for
                  [top, left, bottom] quadrants. "|" means no connection
                  in that quadrant (Simulink convention)
            position: Optional {x, y} position on canvas
            label: Optional user-facing label (defaults to id)

        Raises:
            ValueError: If signs array doesn't have exactly 3 elements
            ValueError: If fewer than 2 active inputs (non-"|" signs)
            ValueError: If signs array contains invalid characters
        """
        # Validate signs array length (must be exactly 3: top, left, bottom)
        if len(signs) != 3:
            msg = "Sum block requires exactly 3 signs (top, left, bottom)"
            raise ValueError(f"{msg}, got {len(signs)}")

        # Validate signs characters
        valid_signs = {"+", "-", "|"}
        if not all(s in valid_signs for s in signs):
            invalid = [s for s in signs if s not in valid_signs]
            msg = f"Invalid sign(s): {invalid}. Must be '+', '-', or '|'"
            raise ValueError(msg)

        # Filter out "|" (no connection) signs to get active inputs
        active_signs = [s for s in signs if s != "|"]

        if len(active_signs) < 2:
            msg = "Sum block requires at least 2 active inputs (non-'|' signs)"
            raise ValueError(msg)

        super().__init__(
            id=id, block_type=BLOCK_TYPES["SUM"], position=position, label=label
        )

        # Store signs parameter (including "|" for position information)
        self.add_parameter(name="signs", value=signs)

        # Create input ports only for active signs (skip "|")
        # Port IDs are sequential: in1, in2, in3, etc.
        port_num = 1
        for sign in signs:
            if sign != "|":
                self.add_port(port_id=f"in{port_num}", port_type="input")
                port_num += 1

        # Create single output port
        self.add_port(port_id="out", port_type="output")

    def get_port_sign(self, port_id: str) -> str:
        """Get the sign ('+', '-', or '|') for a given port.

        Args:
            port_id: Port identifier (e.g., 'in1', 'in2', 'in3')

        Returns:
            Sign character ('+', '-', or '|')

        Raises:
            ValueError: If port_id is invalid
        """
        signs: list[str] = self.get_parameter("signs")

        # Extract port number from port_id (e.g., 'in1' → 1, 'in2' → 2)
        if not port_id.startswith("in") or port_id == "in":
            raise ValueError(f"Invalid Sum block port: {port_id}")

        try:
            port_num = int(port_id[2:])  # Extract number after 'in'
        except ValueError:
            raise ValueError(f"Invalid Sum block port: {port_id}") from None

        # Map port number to the Nth non-'|' sign in the signs array
        # For example, with signs=['+', '|', '-']:
        #   in1 → first non-'|' → signs[0] = '+'
        #   in2 → second non-'|' → signs[2] = '-'
        non_pipe_count = 0
        for sign in signs:
            if sign != "|":
                non_pipe_count += 1
                if non_pipe_count == port_num:
                    return sign

        # Port number exceeds number of non-'|' signs
        raise ValueError(f"Port {port_id} does not exist on this Sum block")
