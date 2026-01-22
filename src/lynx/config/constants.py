# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared constants and configuration for Lynx."""

from dataclasses import dataclass
from typing import Literal

# Block Types (must match TypeScript exactly)
BlockType = Literal["gain", "transfer_function", "state_space", "sum", "io_marker"]

BLOCK_TYPES = {
    "GAIN": "gain",
    "TRANSFER_FUNCTION": "transfer_function",
    "STATE_SPACE": "state_space",
    "SUM": "sum",
    "IO_MARKER": "io_marker",
}


# Action Types (synced with TypeScript)
class ActionTypes:
    """Action type constants for widget communication."""

    ADD_BLOCK = "addBlock"
    DELETE_BLOCK = "deleteBlock"
    MOVE_BLOCK = "moveBlock"
    ADD_CONNECTION = "addConnection"
    DELETE_CONNECTION = "deleteConnection"
    UPDATE_PARAMETER = "updateParameter"
    UPDATE_BLOCK_LABEL = "updateBlockLabel"
    FLIP_BLOCK = "flipBlock"
    TOGGLE_LABEL_VISIBILITY = "toggleLabelVisibility"
    UNDO = "undo"
    REDO = "redo"
    UPDATE_CONNECTION_ROUTING = "updateConnectionRouting"
    RESET_CONNECTION_ROUTING = "resetConnectionRouting"
    TOGGLE_CONNECTION_LABEL_VISIBILITY = "toggleConnectionLabelVisibility"
    UPDATE_CONNECTION_LABEL = "updateConnectionLabel"
    RESIZE_BLOCK = "resizeBlock"
    UPDATE_THEME = "updateTheme"


# Number Formatting (must match TypeScript)
@dataclass
class NumberFormatConfig:
    """Configuration for number formatting."""

    sig_figs: int = 3
    exp_notation_min: float = 0.01
    exp_notation_max: float = 1000


NUMBER_FORMAT = NumberFormatConfig()


# Interaction Thresholds
@dataclass
class InteractionConfig:
    """Configuration for user interaction thresholds."""

    drag_threshold_px: int = 5  # DiagramCanvas.tsx:491
    position_change_threshold_px: float = 1.0  # DiagramCanvas.tsx:266


INTERACTION = InteractionConfig()


# Validation Limits
@dataclass
class ValidationLimits:
    """Validation limits for user inputs."""

    max_label_length: int = 100
    max_latex_length: int = 500
    max_block_count: int = 1000
    max_connection_count: int = 2000
    min_gain_value: float = -1e6
    max_gain_value: float = 1e6


VALIDATION = ValidationLimits()
