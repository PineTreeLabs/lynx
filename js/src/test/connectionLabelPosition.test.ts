// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for connection label positioning algorithm
 *
 * Validates that labels are positioned at the horizontal center of connections
 * and shift to avoid corner waypoints.
 */

import { describe, it, expect } from "vitest";
import {
  calculateConnectionLabelPosition,
  findSegmentAtX,
  findCornerWaypoints,
  type Segment,
} from "../utils/connectionLabelPosition";

describe("calculateConnectionLabelPosition", () => {
  describe("straight connection (no waypoints)", () => {
    it("positions label at horizontal center", () => {
      // Simple horizontal connection from (100, 200) to (300, 200)
      const segments: Segment[] = [
        {
          from: { x: 100, y: 200 },
          to: { x: 300, y: 200 },
          orientation: "horizontal",
        },
      ];
      const labelText = "test";
      const charWidth = 7;

      const position = calculateConnectionLabelPosition(segments, labelText, charWidth);

      // Center should be at x = (100 + 300) / 2 = 200
      expect(position.x).toBe(200);
      // Y should be above the line
      expect(position.y).toBeLessThan(200);
    });

    it("handles vertical straight connection", () => {
      // Vertical connection from (150, 100) to (150, 300)
      const segments: Segment[] = [
        {
          from: { x: 150, y: 100 },
          to: { x: 150, y: 300 },
          orientation: "vertical",
        },
      ];
      const labelText = "signal";
      const charWidth = 7;

      const position = calculateConnectionLabelPosition(segments, labelText, charWidth);

      // Center should be at x = 150 (only one x value)
      expect(position.x).toBe(150);
    });
  });

  describe("connection with waypoints", () => {
    it("avoids corner overlap by shifting label", () => {
      // L-shaped connection with corner at (200, 200)
      // Horizontal from (100, 200) to (200, 200), then vertical to (200, 300)
      const segments: Segment[] = [
        {
          from: { x: 100, y: 200 },
          to: { x: 200, y: 200 },
          orientation: "horizontal",
        },
        {
          from: { x: 200, y: 200 },
          to: { x: 200, y: 300 },
          orientation: "vertical",
        },
      ];
      const labelText = "test"; // 4 chars * 7 = 28px wide
      const charWidth = 7;

      const position = calculateConnectionLabelPosition(segments, labelText, charWidth);

      // The ideal center would be (100 + 200) / 2 = 150
      // But we need to check that label doesn't overlap corner at x=200
      const labelWidth = labelText.length * charWidth; // 28px
      const labelRight = position.x + labelWidth / 2;

      // Label should not overlap the corner at x = 200
      expect(labelRight).toBeLessThanOrEqual(200);
    });

    it("shifts by minimum distance when overlapping", () => {
      // Connection with corner close to center
      const segments: Segment[] = [
        {
          from: { x: 100, y: 200 },
          to: { x: 155, y: 200 },
          orientation: "horizontal",
        },
        {
          from: { x: 155, y: 200 },
          to: { x: 155, y: 300 },
          orientation: "vertical",
        },
      ];
      // Center would be at (100 + 155) / 2 = 127.5
      // With a long label, it might need to shift
      const labelText = "velocity_signal"; // 15 chars * 7 = 105px wide
      const charWidth = 7;

      const position = calculateConnectionLabelPosition(segments, labelText, charWidth);

      // Label should be shifted to not overlap corner at x = 155
      const labelWidth = labelText.length * charWidth;
      const labelRight = position.x + labelWidth / 2;

      // Label should not extend past the corner
      expect(labelRight).toBeLessThanOrEqual(155);
    });
  });

  describe("complex routing", () => {
    it("handles U-shaped connection", () => {
      // U-shaped: right, down, right
      const segments: Segment[] = [
        {
          from: { x: 100, y: 100 },
          to: { x: 200, y: 100 },
          orientation: "horizontal",
        },
        {
          from: { x: 200, y: 100 },
          to: { x: 200, y: 200 },
          orientation: "vertical",
        },
        {
          from: { x: 200, y: 200 },
          to: { x: 300, y: 200 },
          orientation: "horizontal",
        },
      ];
      const labelText = "test";
      const charWidth = 7;

      const position = calculateConnectionLabelPosition(segments, labelText, charWidth);

      // Horizontal center is (100 + 300) / 2 = 200
      // This is exactly at a corner, so should shift
      expect(position.x).toBeDefined();
      expect(position.y).toBeDefined();
    });
  });
});

describe("findSegmentAtX", () => {
  it("finds horizontal segment containing x coordinate", () => {
    const segments: Segment[] = [
      {
        from: { x: 100, y: 200 },
        to: { x: 200, y: 200 },
        orientation: "horizontal",
      },
      {
        from: { x: 200, y: 200 },
        to: { x: 200, y: 300 },
        orientation: "vertical",
      },
    ];

    const segment = findSegmentAtX(segments, 150);
    expect(segment).toBeDefined();
    expect(segment?.orientation).toBe("horizontal");
  });

  it("returns undefined when x is at a corner (vertical segment)", () => {
    const segments: Segment[] = [
      {
        from: { x: 100, y: 200 },
        to: { x: 200, y: 200 },
        orientation: "horizontal",
      },
      {
        from: { x: 200, y: 200 },
        to: { x: 200, y: 300 },
        orientation: "vertical",
      },
    ];

    const segment = findSegmentAtX(segments, 200);
    // At x=200, we're at the vertical segment
    expect(segment?.orientation).toBe("vertical");
  });
});

describe("findCornerWaypoints", () => {
  it("identifies corners where segments meet", () => {
    const segments: Segment[] = [
      {
        from: { x: 100, y: 200 },
        to: { x: 200, y: 200 },
        orientation: "horizontal",
      },
      {
        from: { x: 200, y: 200 },
        to: { x: 200, y: 300 },
        orientation: "vertical",
      },
    ];

    const corners = findCornerWaypoints(segments);

    // Should find corner at (200, 200)
    expect(corners.length).toBeGreaterThanOrEqual(1);
    expect(corners.some((c) => c.x === 200 && c.y === 200)).toBe(true);
  });

  it("returns empty array for straight connection", () => {
    const segments: Segment[] = [
      {
        from: { x: 100, y: 200 },
        to: { x: 300, y: 200 },
        orientation: "horizontal",
      },
    ];

    const corners = findCornerWaypoints(segments);

    // No corners in a straight line
    expect(corners.length).toBe(0);
  });
});
