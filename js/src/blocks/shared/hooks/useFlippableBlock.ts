// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * useFlippableBlock - Shared hook for block flipping logic
 *
 * Handles port position swapping when block is flipped horizontally.
 * Used by all block components to support flip functionality.
 */

import { Position } from "reactflow";

interface FlippableBlockHook {
  /** Get the correct handle position based on flip state */
  getHandlePosition: (defaultPosition: Position) => Position;
  /** Get transform style for visual elements that should flip */
  getFlipTransform: () => string;
}

/**
 * Hook for making blocks flippable
 *
 * @param isFlipped - Whether the block is currently flipped
 * @returns Helper functions for rendering flipped blocks
 */
export function useFlippableBlock(isFlipped: boolean): FlippableBlockHook {
  /**
   * Get the correct handle position based on flip state.
   * Swaps left/right positions when flipped.
   *
   * @param defaultPosition - The normal (unflipped) position
   * @returns The actual position to use
   */
  const getHandlePosition = (defaultPosition: Position): Position => {
    if (!isFlipped) return defaultPosition;

    // Swap left <-> right when flipped
    switch (defaultPosition) {
      case Position.Left:
        return Position.Right;
      case Position.Right:
        return Position.Left;
      default:
        // Top/Bottom don't change
        return defaultPosition;
    }
  };

  /**
   * Get CSS transform for visual elements that should flip.
   * Use this for SVG graphics or other visual elements that should mirror.
   *
   * @returns CSS transform string
   */
  const getFlipTransform = (): string => {
    return isFlipped ? "scaleX(-1)" : "none";
  };

  return {
    getHandlePosition,
    getFlipTransform,
  };
}
