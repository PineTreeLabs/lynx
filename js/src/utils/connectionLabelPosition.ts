// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Connection Label Positioning Utilities
 *
 * Calculates optimal label position at horizontal center of connections,
 * shifting to avoid overlap with corner waypoints.
 */

export interface Point {
  x: number;
  y: number;
}

export interface Segment {
  from: Point;
  to: Point;
  orientation: "horizontal" | "vertical";
}

/**
 * Finds corner waypoints where segments meet at right angles
 */
export function findCornerWaypoints(segments: Segment[]): Point[] {
  const corners: Point[] = [];

  for (let i = 0; i < segments.length - 1; i++) {
    const current = segments[i];
    const next = segments[i + 1];

    // A corner exists where two segments of different orientation meet
    if (current.orientation !== next.orientation) {
      // The corner is at the end of the current segment (which is the start of the next)
      corners.push({ x: current.to.x, y: current.to.y });
    }
  }

  return corners;
}

/**
 * Finds the segment that contains a given x coordinate
 * Returns the segment whose x-range includes the target x
 *
 * Priority: vertical segments at exact x match first, then horizontal segments
 */
export function findSegmentAtX(segments: Segment[], x: number): Segment | undefined {
  // First, check horizontal segments that span this x (exclusive endpoints)
  // This is the most common case and ensures labels stay on horizontal segments
  for (const segment of segments) {
    if (segment.orientation === "horizontal") {
      const minX = Math.min(segment.from.x, segment.to.x);
      const maxX = Math.max(segment.from.x, segment.to.x);
      // Use exclusive check for endpoints to avoid returning horizontal segment at corners
      if (x > minX && x < maxX) {
        return segment;
      }
    }
  }

  // Then check horizontal segments with inclusive bounds (for straight lines)
  for (const segment of segments) {
    if (segment.orientation === "horizontal") {
      const minX = Math.min(segment.from.x, segment.to.x);
      const maxX = Math.max(segment.from.x, segment.to.x);
      if (x >= minX && x <= maxX) {
        return segment;
      }
    }
  }

  // Finally, fall back to vertical segments at this exact x (corners)
  // This should rarely happen as we shift labels to avoid corners
  for (const segment of segments) {
    if (segment.orientation === "vertical") {
      if (Math.abs(segment.from.x - x) < 0.5) {
        return segment;
      }
    }
  }

  return undefined;
}

/**
 * Calculates the Y coordinate for a label at a given X position
 */
function calculateYAtX(segments: Segment[], x: number, defaultY: number): number {
  const segment = findSegmentAtX(segments, x);

  if (!segment) {
    return defaultY;
  }

  if (segment.orientation === "horizontal") {
    return segment.from.y;
  } else {
    // For vertical segments, interpolate Y based on X position
    // (though vertical segments have constant X, so this handles edge cases)
    const t =
      segment.to.x !== segment.from.x
        ? (x - segment.from.x) / (segment.to.x - segment.from.x)
        : 0.5;
    return segment.from.y + t * (segment.to.y - segment.from.y);
  }
}

/**
 * Calculates optimal label position for a connection
 *
 * Strategy:
 * 1. Calculate horizontal center of the entire connection path
 * 2. Find the segment at that x position to determine y
 * 3. Check if label would overlap any corner waypoints
 * 4. If overlapping, shift label by minimum distance to avoid overlap
 *
 * @param segments - The segments that make up the connection path
 * @param labelText - The text to display in the label
 * @param charWidth - Approximate width of each character in pixels
 * @param labelPadding - Extra padding around the label (default: 4px)
 * @returns The calculated position { x, y } for the label center
 */
export function calculateConnectionLabelPosition(
  segments: Segment[],
  labelText: string,
  charWidth: number = 7,
  labelPadding: number = 4
): Point {
  if (segments.length === 0) {
    return { x: 0, y: 0 };
  }

  // Exclude PORT_OFFSET extension segments (first and last) from bounding box calculation.
  // These are the 20px perpendicular extensions from port positions.
  // We want the label centered on the visual connection path, not including port stubs.
  // Note: Sub-pixel segments are already filtered by the routing algorithm.

  const PORT_OFFSET_THRESHOLD = 25; // Slightly larger than PORT_OFFSET (20px)

  let segmentsForBounds = segments;

  // If we have multiple segments, check if first/last are short PORT_OFFSET extensions
  if (segments.length > 1) {
    const visibleSegments = [...segments];

    // Remove first segment if it's a PORT_OFFSET extension (< 25px)
    const firstLength =
      Math.abs(segments[0].to.x - segments[0].from.x) +
      Math.abs(segments[0].to.y - segments[0].from.y);
    if (firstLength < PORT_OFFSET_THRESHOLD) {
      visibleSegments.shift();
    }

    // Remove last segment if it's a PORT_OFFSET extension (< 25px)
    if (visibleSegments.length > 0) {
      const lastSeg = visibleSegments[visibleSegments.length - 1];
      const lastLength =
        Math.abs(lastSeg.to.x - lastSeg.from.x) + Math.abs(lastSeg.to.y - lastSeg.from.y);
      if (lastLength < PORT_OFFSET_THRESHOLD) {
        visibleSegments.pop();
      }
    }

    // Only use filtered segments if we still have at least one segment
    if (visibleSegments.length > 0) {
      segmentsForBounds = visibleSegments;
    }
  }

  // Collect all x coordinates from visible segment endpoints
  const allX: number[] = [];
  for (const segment of segmentsForBounds) {
    allX.push(segment.from.x, segment.to.x);
  }

  const minX = Math.min(...allX);
  const maxX = Math.max(...allX);

  // Calculate horizontal center
  let centerX = (minX + maxX) / 2;

  console.log("[calculateConnectionLabelPosition] Bounding box calculation:", {
    totalSegments: segments.length,
    segmentsUsedForBounds: segmentsForBounds.length,
    segments,
    segmentsForBounds,
    allX,
    minX,
    maxX,
    centerX,
    labelText,
  });

  // Calculate label dimensions
  const labelWidth = labelText.length * charWidth + labelPadding * 2;
  const halfLabelWidth = labelWidth / 2;

  // Find corner waypoints (use filtered segments to avoid detecting artifact corners)
  const corners = findCornerWaypoints(segmentsForBounds);

  // Check for overlap with corners and shift if needed
  if (corners.length > 0) {
    // Calculate initial label bounds
    let labelLeft = centerX - halfLabelWidth;
    let labelRight = centerX + halfLabelWidth;

    // Find the closest corner that the label would overlap
    for (const corner of corners) {
      // Check if label bounds would overlap this corner
      if (labelLeft < corner.x && labelRight > corner.x) {
        // Label overlaps this corner - need to shift

        // Calculate the ideal position to clear the corner on each side
        const idealCenterIfLeft = corner.x - halfLabelWidth; // Place right edge at corner
        const idealCenterIfRight = corner.x + halfLabelWidth; // Place left edge at corner

        // Calculate distance to shift in each direction
        const shiftLeftDistance = centerX - idealCenterIfLeft;
        const shiftRightDistance = idealCenterIfRight - centerX;

        // Check if each direction keeps the other edge within reasonable bounds
        // Allow some overflow past minX/maxX since label text is flexible
        const leftShiftKeepsCenterInRange = idealCenterIfLeft >= minX - halfLabelWidth;
        const rightShiftKeepsCenterInRange = idealCenterIfRight <= maxX + halfLabelWidth;

        // Prefer shifting by smaller distance, but always shift to avoid corner
        if (shiftLeftDistance <= shiftRightDistance && leftShiftKeepsCenterInRange) {
          // Shift left - place label right edge at corner position
          centerX = idealCenterIfLeft;
        } else if (rightShiftKeepsCenterInRange) {
          // Shift right - place label left edge at corner position
          centerX = idealCenterIfRight;
        } else if (leftShiftKeepsCenterInRange) {
          // Fallback to left shift
          centerX = idealCenterIfLeft;
        }
        // If neither direction works, keep current position (rare edge case)

        // Recalculate bounds for next corner check
        labelLeft = centerX - halfLabelWidth;
        labelRight = centerX + halfLabelWidth;
      }
    }
  }

  // Calculate Y position based on segment at centerX (use filtered segments)
  const defaultY = segmentsForBounds[0].from.y;
  let y = calculateYAtX(segmentsForBounds, centerX, defaultY);

  // Offset label above the line
  const verticalOffset = 12;
  y -= verticalOffset;

  return { x: centerX, y };
}
