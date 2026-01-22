// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Block dimension defaults and constraints.
 *
 * Defines default sizes and minimum constraints for each block type.
 * Used by block components for rendering and by NodeResizer for constraints.
 */

export interface BlockDimensions {
  width: number;
  height: number;
  minWidth: number;
  minHeight: number;
}

/**
 * Default dimensions per block type.
 *
 * - width/height: Default size when no custom dimensions specified
 * - minWidth/minHeight: Minimum allowed size for resize constraints
 */
export const BLOCK_DEFAULTS: Record<string, BlockDimensions> = {
  gain: { width: 120, height: 80, minWidth: 60, minHeight: 40 },
  sum: { width: 56, height: 56, minWidth: 40, minHeight: 40 },
  transfer_function: { width: 100, height: 50, minWidth: 80, minHeight: 40 },
  state_space: { width: 120, height: 60, minWidth: 80, minHeight: 40 },
  io_marker: { width: 60, height: 32, minWidth: 60, minHeight: 32 },
} as const;

/**
 * Get dimensions for a block, using defaults if custom dimensions not specified.
 *
 * @param blockType - The type of block (gain, sum, etc.)
 * @param customWidth - Optional custom width from block data
 * @param customHeight - Optional custom height from block data
 * @returns The effective width and height to use for rendering
 */
export function getBlockDimensions(
  blockType: string,
  customWidth?: number,
  customHeight?: number
): { width: number; height: number } {
  const defaults = BLOCK_DEFAULTS[blockType] || BLOCK_DEFAULTS.gain;
  return {
    width: customWidth ?? defaults.width,
    height: customHeight ?? defaults.height,
  };
}

/**
 * Get minimum dimensions for a block type.
 *
 * @param blockType - The type of block (gain, sum, etc.)
 * @returns The minimum width and height for resize constraints
 */
export function getBlockMinDimensions(blockType: string): { minWidth: number; minHeight: number } {
  const defaults = BLOCK_DEFAULTS[blockType] || BLOCK_DEFAULTS.gain;
  return {
    minWidth: defaults.minWidth,
    minHeight: defaults.minHeight,
  };
}
