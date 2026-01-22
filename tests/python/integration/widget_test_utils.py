# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test utilities for widget integration tests."""

from typing import Any, Dict, Optional

from lynx.widget import LynxWidget


def assert_block_in_state(
    widget: LynxWidget,
    block_id: str,
    expected_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Assert block exists in widget diagram_state.

    Parameters
    ----------
    widget : LynxWidget
        Widget instance to check.
    block_id : str
        Block ID to find.
    expected_type : str, optional
        Expected block type (gain, sum, etc.). If provided, asserts match.

    Returns
    -------
    dict
        Block data from diagram_state.

    Raises
    ------
    AssertionError
        If block not found or type mismatch.
    """
    blocks = widget.diagram_state["blocks"]
    block = next((b for b in blocks if b["id"] == block_id), None)
    assert block is not None, f"Block {block_id} not found in diagram_state"
    if expected_type:
        assert block["type"] == expected_type, (
            f"Expected block type {expected_type}, got {block['type']}"
        )
    return block


def assert_connection_in_state(
    widget: LynxWidget,
    connection_id: str,
) -> Dict[str, Any]:
    """Assert connection exists in widget diagram_state.

    Parameters
    ----------
    widget : LynxWidget
        Widget instance to check.
    connection_id : str
        Connection ID to find.

    Returns
    -------
    dict
        Connection data from diagram_state.

    Raises
    ------
    AssertionError
        If connection not found.
    """
    connections = widget.diagram_state["connections"]
    conn = next((c for c in connections if c["id"] == connection_id), None)
    assert conn is not None, f"Connection {connection_id} not found in diagram_state"
    return conn


def assert_validation_has_error(
    widget: LynxWidget,
    error_substring: str,
) -> None:
    """Assert validation_result contains error with substring.

    Parameters
    ----------
    widget : LynxWidget
        Widget instance to check.
    error_substring : str
        Substring to search for in error messages (case-insensitive).

    Raises
    ------
    AssertionError
        If error substring not found in any validation error.
    """
    errors = widget.validation_result.get("errors", [])
    found = any(error_substring.lower() in e.lower() for e in errors)
    assert found, f"Expected error containing '{error_substring}', got errors: {errors}"


def simulate_ui_action(
    widget: LynxWidget,
    action_type: str,
    payload: Dict[str, Any],
    timestamp: Optional[float] = None,
) -> None:
    """Simulate UI action by setting widget._action traitlet.

    Parameters
    ----------
    widget : LynxWidget
        Widget instance.
    action_type : str
        Action type (addBlock, deleteBlock, etc.).
    payload : dict
        Action payload with type-specific fields.
    timestamp : float, optional
        Action timestamp. If None, auto-increments from last action.
    """
    if timestamp is None:
        timestamp = widget._last_action_timestamp + 1.0

    widget._action = {
        "type": action_type,
        "timestamp": timestamp,
        "payload": payload,
    }


def get_block_from_state(
    widget: LynxWidget,
    block_id: str,
) -> Optional[Dict[str, Any]]:
    """Get block from diagram_state by ID.

    Parameters
    ----------
    widget : LynxWidget
        Widget instance.
    block_id : str
        Block ID to find.

    Returns
    -------
    dict or None
        Block data if found, None otherwise.
    """
    blocks = widget.diagram_state["blocks"]
    return next((b for b in blocks if b["id"] == block_id), None)


def get_connection_from_state(
    widget: LynxWidget,
    connection_id: str,
) -> Optional[Dict[str, Any]]:
    """Get connection from diagram_state by ID.

    Parameters
    ----------
    widget : LynxWidget
        Widget instance.
    connection_id : str
        Connection ID to find.

    Returns
    -------
    dict or None
        Connection data if found, None otherwise.
    """
    connections = widget.diagram_state["connections"]
    return next((c for c in connections if c["id"] == connection_id), None)
