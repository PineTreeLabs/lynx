// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Capture utilities for static diagram export
 *
 * Provides functions for calculating content bounds and capturing DOM to PNG/SVG
 */

import { toPng, toSvg } from "html-to-image";
import { Node, Edge, getNodesBounds } from "reactflow";
import type { ContentBounds } from "./types";

/** Default padding around content (pixels) */
export const DEFAULT_PADDING = 40;

/**
 * Calculate content bounds from nodes and edges
 *
 * Uses React Flow's getNodesBounds and edge waypoints to calculate total content bounds.
 * Adds padding to account for labels, port markers, and ensure nothing is clipped.
 *
 * @param nodes - React Flow nodes
 * @param edges - React Flow edges (for waypoint bounds)
 * @param targetWidth - Optional target width (for fixed dimensions)
 * @param targetHeight - Optional target height (for fixed dimensions)
 * @returns Calculated content bounds
 */
export function calculateContentBounds(
  nodes: Node[],
  edges: Edge[],
  targetWidth: number | null,
  targetHeight: number | null
): ContentBounds {
  if (nodes.length === 0) {
    // Empty diagram - return default bounds
    return {
      x: 0,
      y: 0,
      width: targetWidth ?? 400,
      height: targetHeight ?? 300,
    };
  }

  // Get bounds from React Flow nodes
  const nodeBounds = getNodesBounds(nodes);

  // Calculate edge bounds from waypoints
  let minX = nodeBounds.x;
  let minY = nodeBounds.y;
  let maxX = nodeBounds.x + nodeBounds.width;
  let maxY = nodeBounds.y + nodeBounds.height;

  // Expand bounds to include edge waypoints
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

  // Recalculate bounds including edges
  const combinedBounds = {
    x: minX,
    y: minY,
    width: maxX - minX,
    height: maxY - minY,
  };

  // Add padding
  const paddedBounds: ContentBounds = {
    x: combinedBounds.x - DEFAULT_PADDING,
    y: combinedBounds.y - DEFAULT_PADDING,
    width: combinedBounds.width + DEFAULT_PADDING * 2,
    height: combinedBounds.height + DEFAULT_PADDING * 2,
  };

  // If both dimensions specified, use them directly
  if (targetWidth !== null && targetHeight !== null) {
    return {
      x: paddedBounds.x,
      y: paddedBounds.y,
      width: targetWidth,
      height: targetHeight,
    };
  }

  // If only width specified, calculate height from aspect ratio
  if (targetWidth !== null) {
    const aspectRatio = paddedBounds.height / paddedBounds.width;
    return {
      x: paddedBounds.x,
      y: paddedBounds.y,
      width: targetWidth,
      height: Math.round(targetWidth * aspectRatio),
    };
  }

  // If only height specified, calculate width from aspect ratio
  if (targetHeight !== null) {
    const aspectRatio = paddedBounds.width / paddedBounds.height;
    return {
      x: paddedBounds.x,
      y: paddedBounds.y,
      width: Math.round(targetHeight * aspectRatio),
      height: targetHeight,
    };
  }

  // No dimensions specified - use content bounds
  return paddedBounds;
}

/**
 * Filter function to exclude unnecessary elements and remove backgrounds
 * html-to-image clones elements, so we need to modify inline styles
 */
function createCaptureFilter() {
  return (node: HTMLElement): boolean => {
    // Skip elements that shouldn't be captured
    if (node.classList?.contains("react-flow__panel")) return false;
    if (node.classList?.contains("react-flow__controls")) return false;
    if (node.classList?.contains("react-flow__minimap")) return false;
    if (node.classList?.contains("react-flow__background")) return false;
    return true;
  };
}

/**
 * Capture DOM element as PNG
 *
 * Uses html-to-image library to rasterize the element.
 *
 * @param element - DOM element to capture
 * @param width - Output width in pixels
 * @param height - Output height in pixels
 * @param transparent - If true, background is transparent
 * @param backgroundColor - Background color (actual hex/rgb value, not CSS variable)
 * @returns Base64-encoded PNG data (without data URL prefix)
 */
export async function captureToPng(
  element: HTMLElement,
  width: number,
  height: number,
  transparent: boolean,
  backgroundColor: string
): Promise<string> {
  const dataUrl = await toPng(element, {
    width,
    height,
    backgroundColor: transparent ? undefined : backgroundColor,
    pixelRatio: 2, // 2x resolution for crisp output
    filter: createCaptureFilter(),
    // Force the captured element itself to have the background
    style: {
      background: transparent ? "transparent" : backgroundColor,
    },
  });

  // Remove data URL prefix to get raw base64
  const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
  return base64Data;
}

/**
 * Capture DOM element as SVG
 *
 * Uses html-to-image library to serialize the element as SVG.
 *
 * @param element - DOM element to capture
 * @param width - Output width in pixels
 * @param height - Output height in pixels
 * @param transparent - If true, background is transparent
 * @returns Base64-encoded SVG string
 */
export async function captureToSvg(
  element: HTMLElement,
  width: number,
  height: number
): Promise<string> {
  // For SVG, use minimal options - let the viewport element render as-is
  // Don't add backgroundColor since it creates an extra layer
  const dataUrl = await toSvg(element, {
    width,
    height,
    filter: createCaptureFilter(),
    skipFonts: false,
  });

  // Remove data URL prefix to get raw base64
  const base64Data = dataUrl.replace(/^data:image\/svg\+xml;charset=utf-8,/, "");

  // The SVG is URL-encoded, decode it then base64-encode
  // Use encodeURIComponent + unescape to handle Unicode characters (e.g., from KaTeX)
  const svgString = decodeURIComponent(base64Data);
  const base64Svg = btoa(unescape(encodeURIComponent(svgString)));

  return base64Svg;
}
