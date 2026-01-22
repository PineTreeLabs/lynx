# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test data factories for Lynx tests."""

from lynx.diagram import Diagram


class DiagramFactory:
    """Factory for creating test diagrams."""

    @staticmethod
    def simple_feedback_loop() -> Diagram:
        """Standard feedback loop.

        ref → error → controller → plant → output (with feedback).

        Returns:
            Diagram with a complete feedback control loop
        """
        diagram = Diagram()

        diagram.add_block(
            "io_marker",
            "ref",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 100},
        )
        diagram.add_block(
            "sum",
            "error",
            signs=["+", "-", "|"],
            position={"x": 100, "y": 100},
        )
        diagram.add_block(
            "gain",
            "controller",
            K=5.0,
            label="C",
            position={"x": 200, "y": 100},
        )
        diagram.add_block(
            "transfer_function",
            "plant",
            numerator=[2.0],
            denominator=[1.0, 3.0],
            label="P",
            position={"x": 300, "y": 100},
        )
        diagram.add_block(
            "io_marker",
            "output",
            marker_type="output",
            label="y",
            position={"x": 400, "y": 100},
        )

        diagram.add_connection("c1", "ref", "out", "error", "in1")
        diagram.add_connection("c2", "error", "out", "controller", "in")
        diagram.add_connection("c3", "controller", "out", "plant", "in")
        diagram.add_connection("c4", "plant", "out", "output", "in")
        diagram.add_connection("c5", "plant", "out", "error", "in2")

        return diagram

    @staticmethod
    def empty() -> Diagram:
        """Empty diagram with no blocks or connections.

        Returns:
            Empty Diagram instance
        """
        return Diagram()
