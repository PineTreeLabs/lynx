// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Central block registry
 *
 * Consolidates all block-related registries:
 * - nodeTypes: Maps block types to React components (for React Flow)
 * - PARAMETER_EDITORS: Maps block types to parameter editor components (for ParameterPanel)
 *
 * This is the single source of truth for block registration.
 * Adding a new block type requires updating only this file.
 */

import type { NodeTypes } from "reactflow";
import type React from "react";
import type { Block } from "../utils/traitletSync";
import { BLOCK_TYPES } from "../config/constants";

// Import all block components
import { GainBlock } from "./gain";
import { SumBlock } from "./sum";
import { TransferFunctionBlock } from "./transfer_function";
import { StateSpaceBlock } from "./state_space";
import { IOMarkerBlock } from "./io_marker";

// Import all parameter editors
import { GainParameterEditor } from "./gain";
import { TransferFunctionParameterEditor } from "./transfer_function";
import { StateSpaceParameterEditor } from "./state_space";
import { IOMarkerParameterEditor } from "./io_marker";

// Re-export shared utilities for convenience
export * from "./shared";
export { BLOCK_DEFAULTS } from "./shared/utils";

// Re-export individual blocks and editors for direct import if needed
export { GainBlock, SumBlock, TransferFunctionBlock, StateSpaceBlock, IOMarkerBlock };
export {
  GainParameterEditor,
  TransferFunctionParameterEditor,
  StateSpaceParameterEditor,
  IOMarkerParameterEditor,
};

/**
 * Registry: Block type -> React component
 * Used by DiagramCanvas and CaptureCanvas
 */
export const nodeTypes: NodeTypes = {
  [BLOCK_TYPES.GAIN]: GainBlock,
  [BLOCK_TYPES.IO_MARKER]: IOMarkerBlock,
  [BLOCK_TYPES.SUM]: SumBlock,
  [BLOCK_TYPES.TRANSFER_FUNCTION]: TransferFunctionBlock,
  [BLOCK_TYPES.STATE_SPACE]: StateSpaceBlock,
};

/**
 * Shared interface for all parameter editors
 */
export interface ParameterEditorProps {
  block: Block;
  onUpdate: (blockId: string, parameterName: string, value: unknown) => void;
}

/**
 * Registry: Block type -> Parameter editor component
 * Used by ParameterPanel
 */
export const PARAMETER_EDITORS: Record<string, React.ComponentType<ParameterEditorProps>> = {
  [BLOCK_TYPES.GAIN]: GainParameterEditor,
  [BLOCK_TYPES.IO_MARKER]: IOMarkerParameterEditor,
  [BLOCK_TYPES.TRANSFER_FUNCTION]: TransferFunctionParameterEditor,
  [BLOCK_TYPES.STATE_SPACE]: StateSpaceParameterEditor,
};
