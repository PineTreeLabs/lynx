// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Edge-aware fitView utility
 *
 * React Flow's built-in fitView() only considers nodes, which can cause edges
 * with waypoints (like feedback loops) to be clipped at viewport boundaries.
 * This utility calculates bounds including edge waypoints.
 */

import type { Node, Edge, Viewport } from "reactflow";

export interface FitViewOptions {
  padding?: number;
  minZoom?: number;
  maxZoom?: number;
}

export interface ContentBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Default dimensions for each block type
 * Must match BLOCK_DEFAULTS in blockDefaults.ts
 */
const BLOCK_DEFAULTS: Record<string, { width: number; height: number }> = {
  gain: { width: 120, height: 80 },
  sum: { width: 56, height: 56 },
  transfer_function: { width: 100, height: 50 },
  state_space: { width: 100, height: 60 },
  io_marker: { width: 60, height: 48 },
};

/**
 * Calculate bounds that include both nodes and edge waypoints
 *
 * Note: We can't use React Flow's getNodesBounds() because it requires
 * width/height on the node itself, but we store them in node.data.
 * So we calculate bounds manually.
 *
 * @param nodes - React Flow nodes
 * @param edges - React Flow edges
 * @returns Combined bounds
 */
export function getContentBounds(nodes: Node[], edges: Edge[]): ContentBounds {
  if (nodes.length === 0) {
    return { x: 0, y: 0, width: 800, height: 600 };
  }

  // Calculate node bounds manually (can't use getNodesBounds without width/height on node)
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  nodes.forEach((node) => {
    const defaults = BLOCK_DEFAULTS[node.type || "gain"] || { width: 100, height: 60 };
    const width = node.data?.width ?? defaults.width;
    const height = node.data?.height ?? defaults.height;

    minX = Math.min(minX, node.position.x);
    minY = Math.min(minY, node.position.y);
    maxX = Math.max(maxX, node.position.x + width);
    maxY = Math.max(maxY, node.position.y + height);
  });

  // Expand to include edge waypoints
  edges.forEach((edge) => {
    const waypoints = edge.data?.waypoints;
    if (waypoints && Array.isArray(waypoints)) {
      waypoints.forEach((waypoint: { x: number; y: number }) => {
        minX = Math.min(minX, waypoint.x);
        minY = Math.min(minY, waypoint.y);
        maxX = Math.max(maxX, waypoint.x);
        maxY = Math.max(maxY, waypoint.y);
      });
    }
  });

  return {
    x: minX,
    y: minY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

/**
 * Calculate viewport transform to fit content bounds within container
 *
 * @param contentBounds - Bounds to fit
 * @param containerWidth - Container width in pixels
 * @param containerHeight - Container height in pixels
 * @param options - Fit options (padding, zoom limits)
 * @returns Viewport transform
 */
export function calculateFitViewport(
  contentBounds: ContentBounds,
  containerWidth: number,
  containerHeight: number,
  options: FitViewOptions = {}
): Viewport {
  const { padding = 0.1, minZoom = 0.3, maxZoom = 2 } = options;

  // Calculate available space after padding
  const availableWidth = containerWidth * (1 - padding * 2);
  const availableHeight = containerHeight * (1 - padding * 2);

  // Calculate zoom to fit content
  const scaleX = availableWidth / contentBounds.width;
  const scaleY = availableHeight / contentBounds.height;
  let zoom = Math.min(scaleX, scaleY);

  // Apply zoom limits
  zoom = Math.max(minZoom, Math.min(maxZoom, zoom));

  // Calculate center position
  const contentCenterX = contentBounds.x + contentBounds.width / 2;
  const contentCenterY = contentBounds.y + contentBounds.height / 2;

  // Calculate viewport position to center content
  const x = containerWidth / 2 - contentCenterX * zoom;
  const y = containerHeight / 2 - contentCenterY * zoom;

  return { x, y, zoom };
}
