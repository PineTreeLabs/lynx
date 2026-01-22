// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Shared constants - MUST stay in sync with src/lynx/config/constants.py
 */

export const BLOCK_TYPES = {
  GAIN: "gain",
  TRANSFER_FUNCTION: "transfer_function",
  STATE_SPACE: "state_space",
  SUM: "sum",
  IO_MARKER: "io_marker",
} as const;

export type BlockType = (typeof BLOCK_TYPES)[keyof typeof BLOCK_TYPES];

export const ACTION_TYPES = {
  ADD_BLOCK: "addBlock",
  DELETE_BLOCK: "deleteBlock",
  MOVE_BLOCK: "moveBlock",
  ADD_CONNECTION: "addConnection",
  DELETE_CONNECTION: "deleteConnection",
  UPDATE_PARAMETER: "updateParameter",
  UPDATE_BLOCK_LABEL: "updateBlockLabel",
  FLIP_BLOCK: "flipBlock",
  TOGGLE_LABEL_VISIBILITY: "toggleLabelVisibility",
  UNDO: "undo",
  REDO: "redo",
  UPDATE_CONNECTION_ROUTING: "updateConnectionRouting",
  RESET_CONNECTION_ROUTING: "resetConnectionRouting",
  TOGGLE_CONNECTION_LABEL_VISIBILITY: "toggleConnectionLabelVisibility",
  UPDATE_CONNECTION_LABEL: "updateConnectionLabel",
  RESIZE_BLOCK: "resizeBlock",
  UPDATE_THEME: "updateTheme",
} as const;

export const NUMBER_FORMAT = {
  sigFigs: 3,
  expNotationMin: 0.01,
  expNotationMax: 1000,
} as const;

export const INTERACTION = {
  dragThresholdPx: 5,
  positionChangeThresholdPx: 1.0,
} as const;

export const VALIDATION = {
  maxLabelLength: 100,
  maxLatexLength: 500,
  maxBlockCount: 1000,
  maxConnectionCount: 2000,
} as const;
