// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Ellipse Quadrant SVG Path Generation
 *
 * Generates SVG path strings for quadrant overlay regions on ellipses.
 * Used for hover detection and highlighting in Sum block quadrant configuration.
 *
 * Algorithm from research.md:359-395
 */

/**
 * Generate SVG path for a quadrant overlay on an ellipse
 *
 * Creates a wedge-shaped path from the ellipse center to an arc segment.
 * Each quadrant is defined by start/end angles matching the detection logic.
 *
 * @param quadrant - Quadrant index (0=top, 1=left, 2=bottom)
 * @param cx - Ellipse center X coordinate
 * @param cy - Ellipse center Y coordinate
 * @param rx - Ellipse horizontal radius
 * @param ry - Ellipse vertical radius
 * @returns SVG path string (e.g., "M cx,cy L ... A ... Z")
 *
 * Quadrant angle ranges (matches detectEllipseQuadrant):
 * - 0: Top (-90° to -30°, 60° arc)
 * - 1: Left (150° to -150° via 180°, 60° arc wrapping around)
 * - 2: Bottom (30° to 150°, 120° arc)
 * - 3: Right (not used - output port not configurable)
 */
export function getQuadrantPath(
  quadrant: 0 | 1 | 2,
  cx: number,
  cy: number,
  rx: number,
  ry: number
): string {
  // Invalid quadrant - return empty path
  if (![0, 1, 2].includes(quadrant)) {
    return "";
  }

  // All paths start at center
  const start = `M ${cx},${cy}`;

  // Helper to convert angle (degrees) to point on ellipse
  const angleToPoint = (angleDeg: number) => {
    const angleRad = (angleDeg * Math.PI) / 180;
    const x = cx + rx * Math.cos(angleRad);
    const y = cy + ry * Math.sin(angleRad);
    return { x, y };
  };

  // Generate path based on quadrant
  // Using large-arc-flag=0 for arcs < 180°, large-arc-flag=1 for arcs >= 180°
  // Using sweep-flag=1 for clockwise arcs

  switch (quadrant) {
    case 0: {
      // Top quadrant: -135° to -45° (90° arc, centered at top)
      const startPoint = angleToPoint(-135);
      const endPoint = angleToPoint(-45);
      return `${start} L ${startPoint.x},${startPoint.y} A ${rx},${ry} 0 0 1 ${endPoint.x},${endPoint.y} Z`;
    }

    case 1: {
      // Left quadrant: 120° to -120° (90° arc on left side, via 180°)
      const startPoint = angleToPoint(135);
      const endPoint = angleToPoint(-135);
      return `${start} L ${startPoint.x},${startPoint.y} A ${rx},${ry} 0 0 1 ${endPoint.x},${endPoint.y} Z`;
    }

    case 2: {
      // Bottom quadrant: 45° to 135° (90° arc, centered at bottom)
      const startPoint = angleToPoint(45);
      const endPoint = angleToPoint(135);
      return `${start} L ${startPoint.x},${startPoint.y} A ${rx},${ry} 0 0 1 ${endPoint.x},${endPoint.y} Z`;
    }

    default:
      return "";
  }
}
