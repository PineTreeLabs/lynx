// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Shared React Flow configuration
 *
 * Ensures consistent rendering between DiagramCanvas (widget) and CaptureCanvas (static export)
 */

import type { FitViewOptions, DefaultEdgeOptions, Viewport } from "reactflow";

/** Shared viewport configuration */
export const DEFAULT_VIEWPORT: Viewport = {
  x: 0,
  y: 0,
  zoom: 0.5,
};

/** Shared zoom limits */
export const MIN_ZOOM = 0.3;
export const MAX_ZOOM = 2;

/** Shared fitView options - padding ensures content isn't cut off */
export const FIT_VIEW_OPTIONS: FitViewOptions = {
  padding: 0.4,
  minZoom: MIN_ZOOM,
  maxZoom: MAX_ZOOM,
};

/** Shared edge marker dimensions */
export const MARKER_END_SIZE = {
  width: 14,
  height: 14,
};

/** Shared edge stroke width */
export const EDGE_STROKE_WIDTH = 2.5;

/**
 * Get default edge options with consistent styling
 * @param markerColor - Color for edges and markers
 */
export function getDefaultEdgeOptions(markerColor: string): DefaultEdgeOptions {
  return {
    style: { stroke: markerColor, strokeWidth: EDGE_STROKE_WIDTH },
    type: "orthogonal",
    markerEnd: {
      type: "arrowclosed",
      width: MARKER_END_SIZE.width,
      height: MARKER_END_SIZE.height,
      color: markerColor,
    },
  };
}
