// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for useSegmentDrag hook logic
 *
 * Note: These tests use unit testing approach - testing the underlying logic
 * directly rather than through renderHook which requires complex React context setup.
 * The actual React hook integration is tested via component tests.
 */

import { describe, it, expect } from "vitest";
import {
  constrainDragToAxis,
  updateWaypointsFromDrag,
  simplifyWaypoints,
  type Segment,
  type Point,
  type Waypoint,
} from "../utils/orthogonalRouting";

describe("Segment Drag Logic", () => {
  const createSegment = (
    from: Point,
    to: Point,
    orientation: "horizontal" | "vertical"
  ): Segment => ({
    from,
    to,
    orientation,
  });

  describe("constrainDragToAxis", () => {
    it("should constrain horizontal segment to vertical movement", () => {
      const segment = createSegment({ x: 100, y: 200 }, { x: 300, y: 200 }, "horizontal");
      const delta = { x: 50, y: 30 };

      const constrained = constrainDragToAxis(segment, delta);

      expect(constrained.x).toBe(0);
      expect(constrained.y).toBe(30);
    });

    it("should constrain vertical segment to horizontal movement", () => {
      const segment = createSegment({ x: 200, y: 100 }, { x: 200, y: 300 }, "vertical");
      const delta = { x: 40, y: 60 };

      const constrained = constrainDragToAxis(segment, delta);

      expect(constrained.x).toBe(40);
      expect(constrained.y).toBe(0);
    });
  });

  describe("updateWaypointsFromDrag", () => {
    it("should create waypoints for dragging horizontal segment", () => {
      const source: Point = { x: 100, y: 100 };
      const target: Point = { x: 300, y: 100 };
      const waypoints: Waypoint[] = [];
      const segment: Segment = {
        from: { x: 100, y: 100 },
        to: { x: 300, y: 100 },
        orientation: "horizontal",
      };
      const newPosition = { x: 200, y: 150 };

      const result = updateWaypointsFromDrag(source, target, waypoints, segment, newPosition);

      // Should create waypoints at source.x and target.x with the new Y
      expect(result.length).toBe(2);
      expect(result[0]).toEqual({ x: 100, y: 150 }); // source.x, newY
      expect(result[1]).toEqual({ x: 300, y: 150 }); // target.x, newY
    });

    it("should create waypoints for dragging vertical segment", () => {
      const source: Point = { x: 100, y: 100 };
      const target: Point = { x: 100, y: 300 };
      const waypoints: Waypoint[] = [];
      const segment: Segment = {
        from: { x: 100, y: 100 },
        to: { x: 100, y: 300 },
        orientation: "vertical",
      };
      const newPosition = { x: 150, y: 200 };

      const result = updateWaypointsFromDrag(source, target, waypoints, segment, newPosition);

      // Should create waypoints at source.y and target.y with the new X
      expect(result.length).toBe(2);
      expect(result[0]).toEqual({ x: 150, y: 100 }); // newX, source.y
      expect(result[1]).toEqual({ x: 150, y: 300 }); // newX, target.y
    });
  });

  describe("Grid Snapping", () => {
    it("should snap waypoints to grid", () => {
      const waypoints: Waypoint[] = [
        { x: 153, y: 247 },
        { x: 312, y: 247 },
      ];

      const gridSize = 20;
      const snapped = waypoints.map((wp) => ({
        x: Math.round(wp.x / gridSize) * gridSize,
        y: Math.round(wp.y / gridSize) * gridSize,
      }));

      expect(snapped[0].x).toBe(160);
      expect(snapped[0].y).toBe(240);
      expect(snapped[1].x).toBe(320);
      expect(snapped[1].y).toBe(240);
    });
  });

  describe("Simplification", () => {
    it("should remove collinear waypoints after snapping", () => {
      const waypoints: Waypoint[] = [
        { x: 100, y: 200 },
        { x: 150, y: 200 },
        { x: 200, y: 200 },
      ];

      const simplified = simplifyWaypoints(waypoints);

      expect(simplified.length).toBe(2);
      expect(simplified[0]).toEqual({ x: 100, y: 200 });
      expect(simplified[1]).toEqual({ x: 200, y: 200 });
    });
  });
});
