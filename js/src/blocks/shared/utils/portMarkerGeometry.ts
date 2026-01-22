// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Port marker geometry utilities.
 *
 * Calculates SVG triangle points for Simulink-style port direction markers.
 */

import { Position } from "reactflow";

export interface TriangleGeometryOptions {
  /** Triangle size in pixels */
  size: number;
  /** Handle position - determines triangle orientation */
  position: Position;
  /** Port type - input (tip at border) or output (base at border) */
  portType: "input" | "output";
  /** Block flip state - reverses horizontal arrow direction */
  isFlipped: boolean;
  /** Use equilateral triangle (default: true) */
  isEquilateral?: boolean;
}

export interface LineCoordinates {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface ArrowheadLines {
  /** First angled line of arrowhead */
  line1: LineCoordinates;
  /** Second angled line of arrowhead */
  line2: LineCoordinates;
  /** SVG viewBox attribute */
  viewBox: string;
}

/**
 * Calculate arrowhead line coordinates for port marker based on handle position.
 *
 * Arrowheads are isosceles triangles (height = 60% of width) with two angled lines (no base):
 * - Input ports: Tip at center (handle position), base extends outward
 * - Output ports: Base at center (handle position), tip extends outward
 * - Flipped blocks: Horizontal arrows reverse direction (→ becomes ←)
 *
 * @param options - Arrowhead geometry options
 * @returns Two SVG line coordinates and viewBox
 */
export function calculateArrowheadLines(options: TriangleGeometryOptions): ArrowheadLines {
  const { size, position, portType, isFlipped } = options;

  if (size <= 0) {
    throw new Error("Size must be positive");
  }

  const halfSize = size / 2;
  // Isosceles triangle: height (perpendicular to base) = 60% of width
  const heightHalf = (size * 0.6) / 2; // Half the height for ±offset

  const isInput = portType === "input";
  let line1: LineCoordinates;
  let line2: LineCoordinates;

  switch (position) {
    case Position.Left:
    case Position.Right:
      // Horizontal arrows: direction depends on flip state
      if (!isFlipped) {
        // Not flipped: arrows point right (→)
        if (isInput) {
          // Input: tip at center, base at left
          line1 = { x1: 0, y1: halfSize - heightHalf, x2: halfSize, y2: halfSize };
          line2 = { x1: 0, y1: halfSize + heightHalf, x2: halfSize, y2: halfSize };
        } else {
          // Output: base at center, tip at right
          line1 = { x1: halfSize, y1: halfSize - heightHalf, x2: size, y2: halfSize };
          line2 = { x1: halfSize, y1: halfSize + heightHalf, x2: size, y2: halfSize };
        }
      } else {
        // Flipped: arrows point left (←)
        if (isInput) {
          // Input: tip at center, base at right
          line1 = { x1: size, y1: halfSize - heightHalf, x2: halfSize, y2: halfSize };
          line2 = { x1: size, y1: halfSize + heightHalf, x2: halfSize, y2: halfSize };
        } else {
          // Output: base at center, tip at left
          line1 = { x1: halfSize, y1: halfSize - heightHalf, x2: 0, y2: halfSize };
          line2 = { x1: halfSize, y1: halfSize + heightHalf, x2: 0, y2: halfSize };
        }
      }
      break;

    case Position.Top:
      // Top always points down (↓)
      if (isInput) {
        // Input: tip at center, base at top
        line1 = { x1: halfSize - heightHalf, y1: 0, x2: halfSize, y2: halfSize };
        line2 = { x1: halfSize + heightHalf, y1: 0, x2: halfSize, y2: halfSize };
      } else {
        // Output: base at center, tip at bottom
        line1 = { x1: halfSize - heightHalf, y1: halfSize, x2: halfSize, y2: size };
        line2 = { x1: halfSize + heightHalf, y1: halfSize, x2: halfSize, y2: size };
      }
      break;

    case Position.Bottom:
      // Bottom: input points up (↑), output points down (↓)
      if (isInput) {
        // Input: points up, tip at center, base at bottom
        line1 = { x1: halfSize - heightHalf, y1: size, x2: halfSize, y2: halfSize };
        line2 = { x1: halfSize + heightHalf, y1: size, x2: halfSize, y2: halfSize };
      } else {
        // Output: points down, base at center, tip at bottom
        line1 = { x1: halfSize - heightHalf, y1: halfSize, x2: halfSize, y2: size };
        line2 = { x1: halfSize + heightHalf, y1: halfSize, x2: halfSize, y2: size };
      }
      break;

    default:
      // Default to right-pointing input
      line1 = { x1: 0, y1: halfSize - heightHalf, x2: halfSize, y2: halfSize };
      line2 = { x1: 0, y1: halfSize + heightHalf, x2: halfSize, y2: halfSize };
  }

  return {
    line1,
    line2,
    viewBox: `0 0 ${size} ${size}`,
  };
}

/**
 * @deprecated Use calculateArrowheadLines instead
 */
export function calculateTrianglePoints(options: TriangleGeometryOptions): ArrowheadLines {
  return calculateArrowheadLines(options);
}
