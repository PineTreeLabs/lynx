# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared fixtures for widget integration tests."""

from unittest.mock import MagicMock, patch

import pytest

from lynx.diagram import Diagram
from lynx.widget import LynxWidget


@pytest.fixture
def widget():
    """Create fresh widget with empty diagram.

    Returns
    -------
    LynxWidget
        Widget with empty diagram for testing.
    """
    return LynxWidget()


@pytest.fixture
def widget_with_blocks():
    """Pre-populated widget with 2 gain blocks and 1 connection.

    Creates:
        - g1: Gain block (K=2.0) at (100, 100)
        - g2: Gain block (K=3.0) at (300, 100)
        - c1: Connection from g1.out → g2.in

    Returns
    -------
    LynxWidget
        Widget with pre-populated diagram for testing.
    """
    widget = LynxWidget()
    widget.diagram.add_block("gain", "g1", K=2.0, position={"x": 100, "y": 100})
    widget.diagram.add_block("gain", "g2", K=3.0, position={"x": 300, "y": 100})
    widget.diagram.add_connection("c1", "g1", "out", "g2", "in")
    widget.update()
    return widget


@pytest.fixture
def action_factory():
    """Factory for creating action payloads with auto-incrementing timestamps.

    Returns
    -------
    callable
        Function(action_type: str, payload: dict, increment: bool = True) -> dict
        Creates action dict with unique timestamp.
    """
    timestamp = 1000.0

    def create_action(action_type: str, payload: dict, increment: bool = True) -> dict:
        nonlocal timestamp
        if increment:
            timestamp += 1.0
        return {
            "type": action_type,
            "timestamp": timestamp,
            "payload": payload,
        }

    return create_action


@pytest.fixture
def mock_ipython_namespace():
    """Mock IPython.get_ipython() for expression evaluation tests.

    Provides mock namespace with:
        - K_value: 5.5 (scalar)
        - A_matrix: [[1, 0], [0, 1]] (2x2 identity)
        - B_matrix: [[0], [1]] (2x1 vector)

    Yields
    ------
    MagicMock
        Mock IPython instance with user_ns dict.
    """
    with patch("IPython.get_ipython") as mock:
        mock_instance = MagicMock()
        mock_instance.user_ns = {
            "K_value": 5.5,
            "A_matrix": [[1, 0], [0, 1]],
            "B_matrix": [[0], [1]],
        }
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def feedback_control_loop():
    """Complete feedback control loop for workflow tests.

    Creates control loop:
        ref (input) → sum → controller (K=5) → plant (TF) → output
                      ↑_________________________________|
                      (negative feedback)

    Returns
    -------
    LynxWidget
        Widget with complete feedback control loop.
    """
    diagram = Diagram()
    diagram.add_block("io_marker", "ref", marker_type="input", label="r")
    diagram.add_block("sum", "error_sum", signs=["+", "-", "|"])
    diagram.add_block("gain", "controller", K=5.0)
    diagram.add_block(
        "transfer_function",
        "plant",
        numerator=[2.0],
        denominator=[1.0, 3.0],
    )
    diagram.add_block("io_marker", "output", marker_type="output", label="y")

    diagram.add_connection("c1", "ref", "out", "error_sum", "in1")
    diagram.add_connection("c2", "error_sum", "out", "controller", "in")
    diagram.add_connection("c3", "controller", "out", "plant", "in")
    diagram.add_connection("c4", "plant", "out", "output", "in")
    diagram.add_connection("c5", "plant", "out", "error_sum", "in2")

    widget = LynxWidget(diagram=diagram)
    return widget
