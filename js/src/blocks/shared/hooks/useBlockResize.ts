// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Custom hook for managing block resize operations
 *
 * Handles:
 * - Resize callbacks to sync dimensions to Python
 * - Anchor corner calculations
 */

import { useCallback, useContext } from "react";
import { useReactFlow, useUpdateNodeInternals } from "reactflow";
import { AnyWidgetModelContext } from "../../../index";
import { sendAction } from "../../../utils/traitletSync";

/**
 * Corner identifiers for resize handles
 */
export type Corner = "top-left" | "top-right" | "bottom-left" | "bottom-right";

/**
 * Bounds representing block position and dimensions
 */
export interface Bounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Calculate new bounds after resize, keeping the anchor corner fixed.
 *
 * @param initialBounds - Starting position and dimensions
 * @param draggedCorner - Which corner is being dragged
 * @param newWidth - New width after resize
 * @param newHeight - New height after resize
 * @returns New bounds with position adjusted to keep anchor fixed
 */
export function calculateResizedBounds(
  initialBounds: Bounds,
  draggedCorner: Corner,
  newWidth: number,
  newHeight: number
): Bounds {
  const { x, y, width, height } = initialBounds;

  // Calculate corner positions
  const right = x + width;
  const bottom = y + height;

  switch (draggedCorner) {
    case "bottom-right":
      // Anchor: top-left (x, y stays fixed)
      return { x, y, width: newWidth, height: newHeight };

    case "top-left":
      // Anchor: bottom-right (right, bottom stays fixed)
      return {
        x: right - newWidth,
        y: bottom - newHeight,
        width: newWidth,
        height: newHeight,
      };

    case "top-right":
      // Anchor: bottom-left (x, bottom stays fixed)
      return {
        x,
        y: bottom - newHeight,
        width: newWidth,
        height: newHeight,
      };

    case "bottom-left":
      // Anchor: top-right (right, y stays fixed)
      return {
        x: right - newWidth,
        y,
        width: newWidth,
        height: newHeight,
      };

    default:
      return { x, y, width: newWidth, height: newHeight };
  }
}

/**
 * Constrain dimensions to maintain aspect ratio.
 * Uses the larger dimension change as the reference.
 *
 * @param width - Proposed new width
 * @param height - Proposed new height
 * @param aspectRatio - Original width/height ratio to maintain
 * @returns Constrained width and height
 */
export function constrainAspectRatio(
  width: number,
  height: number,
  aspectRatio: number
): { width: number; height: number } {
  // Calculate what height would be for given width
  const heightFromWidth = width / aspectRatio;
  // Calculate what width would be for given height
  const widthFromHeight = height * aspectRatio;

  // Use whichever results in larger dimensions (prevents shrinking to 0)
  if (widthFromHeight > width) {
    return { width: widthFromHeight, height };
  } else {
    return { width, height: heightFromWidth };
  }
}

/**
 * Hook for block resize management
 *
 * @param id - Block ID
 * @returns Object with resize handlers
 */
export function useBlockResize(id: string) {
  const model = useContext(AnyWidgetModelContext);
  const { setNodes } = useReactFlow();
  const updateNodeInternals = useUpdateNodeInternals();

  /**
   * Handle resize start (no-op, but required by NodeResizer)
   */
  const handleResizeStart = useCallback(() => {
    // No-op - NodeResizer handles the resize start
  }, []);

  /**
   * Handle resize during drag - optimistic update in React state
   */
  const handleResize = useCallback(
    (
      _event: MouseEvent | TouchEvent,
      params: { width: number; height: number; x: number; y: number }
    ) => {
      const { width, height, x, y } = params;

      // Optimistic update in React state
      setNodes((nodes) =>
        nodes.map((node) =>
          node.id === id
            ? {
                ...node,
                position: { x, y },
                data: { ...node.data, width, height },
              }
            : node
        )
      );
    },
    [id, setNodes]
  );

  /**
   * Handle resize end - sync final dimensions to Python
   */
  const handleResizeEnd = useCallback(
    (
      _event: MouseEvent | TouchEvent,
      params: { width: number; height: number; x: number; y: number }
    ) => {
      const { width, height, x, y } = params;

      // Sync to Python
      if (model) {
        sendAction(model, "resizeBlock", {
          blockId: id,
          width,
          height,
        });

        // Also update position if it changed (due to anchor corner adjustment)
        sendAction(model, "moveBlock", {
          blockId: id,
          position: { x, y },
        });
      }

      // Update node internals to recalculate handle positions
      updateNodeInternals(id);
    },
    [model, id, updateNodeInternals]
  );

  return {
    handleResizeStart,
    handleResize,
    handleResizeEnd,
  };
}
