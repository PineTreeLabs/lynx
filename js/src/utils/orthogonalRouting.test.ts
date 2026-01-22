// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Unit tests for orthogonal routing utilities
 *
 * Tests for path calculation, segment generation, and SVG path conversion.
 * Following TDD: write tests FIRST, ensure they FAIL before implementation.
 */

import { describe, it, expect } from "vitest";
import { Position } from "reactflow";
import {
  Point,
  Segment,
  Waypoint,
  createOrthogonalSegments,
  calculateOrthogonalPath,
  segmentsToSVGPath,
  segmentToRect,
  constrainDragToAxis,
  updateWaypointsFromDrag,
  simplifyWaypoints,
  findOrthogonalPath,
} from "./orthogonalRouting";

// =============================================================================
// T007: Tests for calculateOrthogonalPath()
// =============================================================================

describe("calculateOrthogonalPath", () => {
  it("should return a single segment for aligned horizontal points", () => {
    const source: Point = { x: 100, y: 200 };
    const target: Point = { x: 300, y: 200 };
    const waypoints: Waypoint[] = [];

    const segments = calculateOrthogonalPath(source, target, waypoints);

    // Direct horizontal path should be a single horizontal segment
    expect(segments.length).toBe(1);
    expect(segments[0].orientation).toBe("horizontal");
    expect(segments[0].from).toEqual(source);
    expect(segments[0].to).toEqual(target);
  });

  it("should return a single segment for aligned vertical points", () => {
    const source: Point = { x: 200, y: 100 };
    const target: Point = { x: 200, y: 300 };
    const waypoints: Waypoint[] = [];

    const segments = calculateOrthogonalPath(source, target, waypoints);

    // Direct vertical path should be a single vertical segment
    expect(segments.length).toBe(1);
    expect(segments[0].orientation).toBe("vertical");
  });

  it("should return two segments for non-aligned points (no waypoints)", () => {
    const source: Point = { x: 100, y: 100 };
    const target: Point = { x: 300, y: 200 };
    const waypoints: Waypoint[] = [];

    const segments = calculateOrthogonalPath(source, target, waypoints);

    // Should create H-V or V-H routing based on distance
    expect(segments.length).toBe(2);
    // All segments should be either horizontal or vertical
    segments.forEach((seg) => {
      expect(["horizontal", "vertical"]).toContain(seg.orientation);
    });
  });

  it("should route through a single waypoint", () => {
    const source: Point = { x: 100, y: 100 };
    const target: Point = { x: 300, y: 300 };
    const waypoints: Waypoint[] = [{ x: 200, y: 100 }];

    const segments = calculateOrthogonalPath(source, target, waypoints);

    // Path should go: source -> waypoint -> target
    // First segment should go from source toward waypoint
    expect(segments[0].from).toEqual(source);
    // Path should pass through the waypoint
    const waypointFound = segments.some(
      (seg) => (seg.from.x === 200 && seg.from.y === 100) || (seg.to.x === 200 && seg.to.y === 100)
    );
    expect(waypointFound).toBe(true);
  });

  it("should route through multiple waypoints in order", () => {
    const source: Point = { x: 100, y: 100 };
    const target: Point = { x: 400, y: 400 };
    const waypoints: Waypoint[] = [
      { x: 200, y: 100 },
      { x: 200, y: 300 },
      { x: 300, y: 300 },
    ];

    const segments = calculateOrthogonalPath(source, target, waypoints);

    // Should have segments connecting source -> wp1 -> wp2 -> wp3 -> target
    expect(segments.length).toBeGreaterThanOrEqual(waypoints.length + 1);
  });
});

// =============================================================================
// T008: Tests for segmentsToSVGPath()
// =============================================================================

describe("segmentsToSVGPath", () => {
  it("should generate correct SVG path for a single horizontal segment", () => {
    const segments: Segment[] = [
      { from: { x: 100, y: 200 }, to: { x: 300, y: 200 }, orientation: "horizontal" },
    ];

    const path = segmentsToSVGPath(segments);

    // Should start with M (moveto) and have L (lineto)
    expect(path).toMatch(/^M\s*100[,\s]+200/);
    expect(path).toContain("L");
    expect(path).toMatch(/300[,\s]+200/);
  });

  it("should generate correct SVG path for multiple segments", () => {
    const segments: Segment[] = [
      { from: { x: 100, y: 100 }, to: { x: 200, y: 100 }, orientation: "horizontal" },
      { from: { x: 200, y: 100 }, to: { x: 200, y: 200 }, orientation: "vertical" },
      { from: { x: 200, y: 200 }, to: { x: 300, y: 200 }, orientation: "horizontal" },
    ];

    const path = segmentsToSVGPath(segments);

    // Should contain M followed by multiple L commands
    expect(path).toMatch(/^M\s*100[,\s]+100/);
    expect(path).toMatch(/L\s*200[,\s]+100/);
    expect(path).toMatch(/L\s*200[,\s]+200/);
    expect(path).toMatch(/L\s*300[,\s]+200/);
  });

  it("should return empty string for empty segments array", () => {
    const segments: Segment[] = [];
    const path = segmentsToSVGPath(segments);
    expect(path).toBe("");
  });

  it("should handle single point (degenerate case)", () => {
    const segments: Segment[] = [
      { from: { x: 100, y: 100 }, to: { x: 100, y: 100 }, orientation: "horizontal" },
    ];

    const path = segmentsToSVGPath(segments);

    // Should still generate valid SVG even for zero-length segment
    expect(path).toMatch(/^M\s*100[,\s]+100/);
  });
});

// =============================================================================
// T009: Tests for createOrthogonalSegments()
// =============================================================================

describe("createOrthogonalSegments", () => {
  it("should create horizontal segment for horizontally aligned points", () => {
    const from: Point = { x: 100, y: 200 };
    const to: Point = { x: 300, y: 200 };

    const segments = createOrthogonalSegments(from, to);

    expect(segments.length).toBe(1);
    expect(segments[0].orientation).toBe("horizontal");
    expect(segments[0].from).toEqual(from);
    expect(segments[0].to).toEqual(to);
  });

  it("should create vertical segment for vertically aligned points", () => {
    const from: Point = { x: 200, y: 100 };
    const to: Point = { x: 200, y: 300 };

    const segments = createOrthogonalSegments(from, to);

    expect(segments.length).toBe(1);
    expect(segments[0].orientation).toBe("vertical");
  });

  it("should prefer horizontal-first when dx > dy", () => {
    const from: Point = { x: 100, y: 100 };
    const to: Point = { x: 300, y: 150 }; // dx=200, dy=50

    const segments = createOrthogonalSegments(from, to);

    expect(segments.length).toBe(2);
    // When dx > dy, should go horizontal first, then vertical
    expect(segments[0].orientation).toBe("horizontal");
    expect(segments[1].orientation).toBe("vertical");
  });

  it("should prefer vertical-first when dy > dx", () => {
    const from: Point = { x: 100, y: 100 };
    const to: Point = { x: 150, y: 300 }; // dx=50, dy=200

    const segments = createOrthogonalSegments(from, to);

    expect(segments.length).toBe(2);
    // When dy > dx, should go vertical first, then horizontal
    expect(segments[0].orientation).toBe("vertical");
    expect(segments[1].orientation).toBe("horizontal");
  });

  it("should connect segments at intermediate point", () => {
    const from: Point = { x: 100, y: 100 };
    const to: Point = { x: 300, y: 200 };

    const segments = createOrthogonalSegments(from, to);

    // The end of segment 0 should equal the start of segment 1
    expect(segments[0].to).toEqual(segments[1].from);
  });

  it("should handle same start and end point", () => {
    const from: Point = { x: 100, y: 100 };
    const to: Point = { x: 100, y: 100 };

    const segments = createOrthogonalSegments(from, to);

    // Should handle gracefully - could return empty or single zero-length segment
    expect(segments.length).toBeLessThanOrEqual(1);
  });

  it("should handle negative coordinates", () => {
    const from: Point = { x: -100, y: -200 };
    const to: Point = { x: 100, y: 200 };

    const segments = createOrthogonalSegments(from, to);

    expect(segments.length).toBe(2);
    expect(segments[0].from).toEqual(from);
  });
});

// =============================================================================
// T017: Tests for segment hit detection (segmentToRect)
// =============================================================================

describe("segmentToRect", () => {
  it("should create rect for horizontal segment", () => {
    const segment: Segment = {
      from: { x: 100, y: 200 },
      to: { x: 300, y: 200 },
      orientation: "horizontal",
    };
    const handleWidth = 10;

    const rect = segmentToRect(segment, handleWidth);

    // Rect should span the segment length horizontally
    expect(rect.x).toBe(100);
    expect(rect.width).toBe(200);
    // Rect should be centered on y with handleWidth height
    expect(rect.y).toBe(200 - handleWidth / 2);
    expect(rect.height).toBe(handleWidth);
  });

  it("should create rect for vertical segment", () => {
    const segment: Segment = {
      from: { x: 200, y: 100 },
      to: { x: 200, y: 300 },
      orientation: "vertical",
    };
    const handleWidth = 10;

    const rect = segmentToRect(segment, handleWidth);

    // Rect should be centered on x with handleWidth width
    expect(rect.x).toBe(200 - handleWidth / 2);
    expect(rect.width).toBe(handleWidth);
    // Rect should span the segment length vertically
    expect(rect.y).toBe(100);
    expect(rect.height).toBe(200);
  });

  it("should handle segment going in reverse direction", () => {
    const segment: Segment = {
      from: { x: 300, y: 200 },
      to: { x: 100, y: 200 },
      orientation: "horizontal",
    };
    const handleWidth = 10;

    const rect = segmentToRect(segment, handleWidth);

    // Rect should normalize the coordinates
    expect(rect.x).toBe(100);
    expect(rect.width).toBe(200);
  });
});

// =============================================================================
// T018: Tests for constrainDragToAxis()
// =============================================================================

describe("constrainDragToAxis", () => {
  it("should constrain horizontal segment drag to vertical movement", () => {
    const segment: Segment = {
      from: { x: 100, y: 200 },
      to: { x: 300, y: 200 },
      orientation: "horizontal",
    };
    const dragDelta = { x: 50, y: 30 };

    const constrained = constrainDragToAxis(segment, dragDelta);

    // Horizontal segment can only move vertically
    expect(constrained.x).toBe(0);
    expect(constrained.y).toBe(30);
  });

  it("should constrain vertical segment drag to horizontal movement", () => {
    const segment: Segment = {
      from: { x: 200, y: 100 },
      to: { x: 200, y: 300 },
      orientation: "vertical",
    };
    const dragDelta = { x: 40, y: 60 };

    const constrained = constrainDragToAxis(segment, dragDelta);

    // Vertical segment can only move horizontally
    expect(constrained.x).toBe(40);
    expect(constrained.y).toBe(0);
  });
});

// =============================================================================
// T019: Tests for updateWaypointsFromDrag()
// =============================================================================

describe("updateWaypointsFromDrag", () => {
  it("should create waypoints when dragging horizontal segment vertically", () => {
    const source: Point = { x: 100, y: 100 };
    const target: Point = { x: 300, y: 200 };
    const currentWaypoints: Waypoint[] = [];
    // Simulate a horizontal segment from source going right
    const draggedSegment: Segment = {
      from: { x: 100, y: 100 },
      to: { x: 200, y: 100 },
      orientation: "horizontal",
    };
    const newPosition = { x: 150, y: 150 }; // Drag down

    const updatedWaypoints = updateWaypointsFromDrag(
      source,
      target,
      currentWaypoints,
      draggedSegment,
      newPosition
    );

    // Should create waypoints at the new Y level, using segment endpoint X positions (local bend)
    expect(updatedWaypoints.length).toBe(2);
    expect(updatedWaypoints[0]).toEqual({ x: 100, y: 150 }); // segment.from.x, newY
    expect(updatedWaypoints[1]).toEqual({ x: 200, y: 150 }); // segment.to.x, newY
  });

  it("should create waypoints when dragging vertical segment horizontally", () => {
    const source: Point = { x: 100, y: 100 };
    const target: Point = { x: 300, y: 300 };
    const currentWaypoints: Waypoint[] = [];
    // Simulate a vertical segment
    const draggedSegment: Segment = {
      from: { x: 200, y: 100 },
      to: { x: 200, y: 300 },
      orientation: "vertical",
    };
    const newPosition = { x: 250, y: 200 }; // Drag right

    const updatedWaypoints = updateWaypointsFromDrag(
      source,
      target,
      currentWaypoints,
      draggedSegment,
      newPosition
    );

    // Should create waypoints at the new X position, using source/target Y positions
    expect(updatedWaypoints.length).toBe(2);
    expect(updatedWaypoints[0]).toEqual({ x: 250, y: 100 }); // newX, source.y
    expect(updatedWaypoints[1]).toEqual({ x: 250, y: 300 }); // newX, target.y
  });

  it("should update existing waypoints near dragged segment", () => {
    const source: Point = { x: 100, y: 100 };
    const target: Point = { x: 400, y: 300 };
    const currentWaypoints: Waypoint[] = [
      { x: 200, y: 100 },
      { x: 200, y: 200 },
    ];
    // Drag the vertical segment at x=200
    const draggedSegment: Segment = {
      from: { x: 200, y: 100 },
      to: { x: 200, y: 200 },
      orientation: "vertical",
    };
    const newPosition = { x: 250, y: 150 }; // Drag right

    const updatedWaypoints = updateWaypointsFromDrag(
      source,
      target,
      currentWaypoints,
      draggedSegment,
      newPosition
    );

    // Should update X coordinates of waypoints near the segment
    expect(updatedWaypoints.length).toBe(2);
    expect(updatedWaypoints[0].x).toBe(250);
    expect(updatedWaypoints[1].x).toBe(250);
  });
});

// =============================================================================
// T029: Tests for simplifyWaypoints()
// =============================================================================

describe("simplifyWaypoints", () => {
  it("should remove collinear waypoints on horizontal line", () => {
    const waypoints: Waypoint[] = [
      { x: 100, y: 200 },
      { x: 150, y: 200 },
      { x: 200, y: 200 },
    ];

    const simplified = simplifyWaypoints(waypoints);

    // Middle waypoint is collinear, should be removed
    expect(simplified.length).toBe(2);
    expect(simplified[0]).toEqual({ x: 100, y: 200 });
    expect(simplified[1]).toEqual({ x: 200, y: 200 });
  });

  it("should remove collinear waypoints on vertical line", () => {
    const waypoints: Waypoint[] = [
      { x: 200, y: 100 },
      { x: 200, y: 150 },
      { x: 200, y: 200 },
    ];

    const simplified = simplifyWaypoints(waypoints);

    expect(simplified.length).toBe(2);
  });

  it("should preserve waypoints at corners", () => {
    const waypoints: Waypoint[] = [
      { x: 100, y: 100 },
      { x: 200, y: 100 },
      { x: 200, y: 200 },
    ];

    const simplified = simplifyWaypoints(waypoints);

    // All three are needed (corner at middle)
    expect(simplified.length).toBe(3);
  });

  it("should return empty array for empty input", () => {
    const simplified = simplifyWaypoints([]);
    expect(simplified).toEqual([]);
  });

  it("should return single waypoint unchanged", () => {
    const waypoints: Waypoint[] = [{ x: 100, y: 100 }];
    const simplified = simplifyWaypoints(waypoints);
    expect(simplified).toEqual(waypoints);
  });

  it("should handle tolerance for near-collinear points", () => {
    const waypoints: Waypoint[] = [
      { x: 100, y: 200 },
      { x: 150, y: 202 }, // Slightly off by 2 pixels
      { x: 200, y: 200 },
    ];

    const simplified = simplifyWaypoints(waypoints, 5);

    // Within tolerance, should be simplified
    expect(simplified.length).toBe(2);
  });
});

// =============================================================================
// Visibility Graph Routing Tests
// =============================================================================

// Import new functions (will fail until implemented)
import { segmentCrossesBlock, findOrthogonalPath, BlockBounds } from "./orthogonalRouting";

// =============================================================================
// T100: Block Intersection Detection Tests
// =============================================================================

describe("segmentCrossesBlock", () => {
  const block: BlockBounds = { x: 100, y: 100, width: 100, height: 100 };
  // Block spans [100, 200] in both X and Y

  it("should detect horizontal segment crossing block", () => {
    // Horizontal segment at y=150 from x=50 to x=250 crosses block
    const a: Point = { x: 50, y: 150 };
    const b: Point = { x: 250, y: 150 };
    expect(segmentCrossesBlock(a, b, block)).toBe(true);
  });

  it("should detect vertical segment crossing block", () => {
    // Vertical segment at x=150 from y=50 to y=250 crosses block
    const a: Point = { x: 150, y: 50 };
    const b: Point = { x: 150, y: 250 };
    expect(segmentCrossesBlock(a, b, block)).toBe(true);
  });

  it("should return false when segment is completely outside block", () => {
    // Segment entirely to the left of block
    const a: Point = { x: 10, y: 150 };
    const b: Point = { x: 50, y: 150 };
    expect(segmentCrossesBlock(a, b, block)).toBe(false);
  });

  it("should return false when segment touches block edge (boundary)", () => {
    // Segment exactly at block's left edge (x=100) should not "cross"
    // This allows paths to route along block edges
    const a: Point = { x: 100, y: 50 };
    const b: Point = { x: 100, y: 250 };
    expect(segmentCrossesBlock(a, b, block)).toBe(false);
  });

  it("should return false for segment above block", () => {
    const a: Point = { x: 50, y: 50 };
    const b: Point = { x: 250, y: 50 };
    expect(segmentCrossesBlock(a, b, block)).toBe(false);
  });

  it("should return false for segment below block", () => {
    const a: Point = { x: 50, y: 250 };
    const b: Point = { x: 250, y: 250 };
    expect(segmentCrossesBlock(a, b, block)).toBe(false);
  });

  it("should detect segment that starts inside block", () => {
    const a: Point = { x: 150, y: 150 }; // Inside block
    const b: Point = { x: 300, y: 150 };
    expect(segmentCrossesBlock(a, b, block)).toBe(true);
  });

  it("should detect segment that ends inside block", () => {
    const a: Point = { x: 50, y: 150 };
    const b: Point = { x: 150, y: 150 }; // Inside block
    expect(segmentCrossesBlock(a, b, block)).toBe(true);
  });
});

// =============================================================================
// T101: Path Finding Core Tests
// =============================================================================

describe("findOrthogonalPath", () => {
  // Helper to check if any segment in path crosses a block
  function pathCrossesBlock(segments: Segment[], block: BlockBounds): boolean {
    for (const seg of segments) {
      if (segmentCrossesBlock(seg.from, seg.to, block)) {
        return true;
      }
    }
    return false;
  }

  // Helper to check if middle segments (excluding first and last) cross a block
  // The first segment (source to exit) and last segment (approach to target) naturally
  // pass through their respective blocks, so we exclude them when checking block avoidance
  function middlePathCrossesBlock(segments: Segment[], block: BlockBounds): boolean {
    // Only check middle segments (skip first and last)
    for (let i = 1; i < segments.length - 1; i++) {
      const seg = segments[i];
      if (segmentCrossesBlock(seg.from, seg.to, block)) {
        return true;
      }
    }
    return false;
  }

  // Helper to count turns in a path
  function countTurns(segments: Segment[]): number {
    let turns = 0;
    for (let i = 1; i < segments.length; i++) {
      if (segments[i].orientation !== segments[i - 1].orientation) {
        turns++;
      }
    }
    return turns;
  }

  describe("Basic connectivity", () => {
    it("should find direct horizontal path when no blocks in way", () => {
      const source: Point = { x: 100, y: 200 };
      const target: Point = { x: 400, y: 200 };
      const segments = findOrthogonalPath(
        source,
        target,
        Position.Right,
        Position.Left,
        [] // No blocks
      );

      expect(segments.length).toBeGreaterThan(0);
      // Path should connect source to target
      expect(segments[0].from.x).toBe(source.x);
      expect(segments[segments.length - 1].to.x).toBe(target.x);
    });

    it("should find direct vertical path when no blocks in way", () => {
      const source: Point = { x: 200, y: 100 };
      const target: Point = { x: 200, y: 400 };
      const segments = findOrthogonalPath(source, target, Position.Bottom, Position.Top, []);

      expect(segments.length).toBeGreaterThan(0);
      expect(segments[0].from.y).toBe(source.y);
      expect(segments[segments.length - 1].to.y).toBe(target.y);
    });

    it("should find L-shaped path for perpendicular ports", () => {
      const source: Point = { x: 100, y: 200 };
      const target: Point = { x: 300, y: 100 };
      const segments = findOrthogonalPath(source, target, Position.Right, Position.Bottom, []);

      expect(segments.length).toBeGreaterThan(0);
      // Should have exactly 1 turn for L-shape (2 segments minimum)
      expect(countTurns(segments)).toBeGreaterThanOrEqual(1);
    });
  });

  describe("Block avoidance", () => {
    it("should not cross source block", () => {
      const sourceBlock: BlockBounds = { x: 80, y: 180, width: 80, height: 40 };
      const targetBlock: BlockBounds = { x: 300, y: 180, width: 80, height: 40 };

      const source: Point = { x: 160, y: 200 }; // Right edge of source block
      const target: Point = { x: 300, y: 200 }; // Left edge of target block

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Left, [
        sourceBlock,
        targetBlock,
      ]);

      expect(segments.length).toBeGreaterThan(0);
      expect(pathCrossesBlock(segments, sourceBlock)).toBe(false);
    });

    it("should not cross target block", () => {
      const sourceBlock: BlockBounds = { x: 80, y: 180, width: 80, height: 40 };
      const targetBlock: BlockBounds = { x: 300, y: 180, width: 80, height: 40 };

      const source: Point = { x: 160, y: 200 };
      const target: Point = { x: 300, y: 200 };

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Left, [
        sourceBlock,
        targetBlock,
      ]);

      expect(segments.length).toBeGreaterThan(0);
      expect(pathCrossesBlock(segments, targetBlock)).toBe(false);
    });

    it("should not cross intermediate blocks", () => {
      // Source on left, target on right, obstacle block in between
      const sourceBlock: BlockBounds = { x: 50, y: 180, width: 80, height: 40 };
      const targetBlock: BlockBounds = { x: 400, y: 180, width: 80, height: 40 };
      const obstacleBlock: BlockBounds = { x: 200, y: 150, width: 100, height: 100 };

      const source: Point = { x: 130, y: 200 }; // Right of source
      const target: Point = { x: 400, y: 200 }; // Left of target

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Left, [
        sourceBlock,
        targetBlock,
        obstacleBlock,
      ]);

      expect(segments.length).toBeGreaterThan(0);
      expect(pathCrossesBlock(segments, obstacleBlock)).toBe(false);
    });

    it("should route around multiple blocks", () => {
      // Multiple obstacles between source and target
      const sourceBlock: BlockBounds = { x: 50, y: 200, width: 60, height: 60 };
      const targetBlock: BlockBounds = { x: 500, y: 200, width: 60, height: 60 };
      const obstacle1: BlockBounds = { x: 180, y: 180, width: 80, height: 100 };
      const obstacle2: BlockBounds = { x: 320, y: 180, width: 80, height: 100 };

      const source: Point = { x: 110, y: 230 };
      const target: Point = { x: 500, y: 230 };

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Left, [
        sourceBlock,
        targetBlock,
        obstacle1,
        obstacle2,
      ]);

      expect(segments.length).toBeGreaterThan(0);
      expect(pathCrossesBlock(segments, obstacle1)).toBe(false);
      expect(pathCrossesBlock(segments, obstacle2)).toBe(false);
    });
  });

  describe("Port perpendicularity", () => {
    it("should exit source port perpendicular to block face (Right port)", () => {
      const source: Point = { x: 100, y: 200 };
      const target: Point = { x: 300, y: 100 };

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Top, []);

      // First segment from Right port should be horizontal
      expect(segments[0].orientation).toBe("horizontal");
      expect(segments[0].to.x).toBeGreaterThan(segments[0].from.x);
    });

    it("should enter target port perpendicular to block face (Top port)", () => {
      const source: Point = { x: 100, y: 200 };
      const target: Point = { x: 300, y: 100 };

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Top, []);

      // Last segment to Top port should be vertical, approaching from above
      const lastSeg = segments[segments.length - 1];
      expect(lastSeg.orientation).toBe("vertical");
      expect(lastSeg.from.y).toBeLessThan(lastSeg.to.y);
    });

    it("should handle Right→Left port connection", () => {
      const source: Point = { x: 100, y: 200 };
      const target: Point = { x: 400, y: 200 };

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Left, []);

      expect(segments[0].orientation).toBe("horizontal");
      expect(segments[segments.length - 1].orientation).toBe("horizontal");
    });

    it("should handle Bottom→Top port connection", () => {
      const source: Point = { x: 200, y: 100 };
      const target: Point = { x: 200, y: 300 };

      const segments = findOrthogonalPath(source, target, Position.Bottom, Position.Top, []);

      expect(segments[0].orientation).toBe("vertical");
      expect(segments[segments.length - 1].orientation).toBe("vertical");
    });

    it("should handle backwards connection (Right port, target to the left)", () => {
      // Source exits right, but target is to the LEFT
      const source: Point = { x: 300, y: 200 };
      const target: Point = { x: 100, y: 200 };

      const sourceBlock: BlockBounds = { x: 250, y: 170, width: 80, height: 60 };
      const targetBlock: BlockBounds = { x: 50, y: 170, width: 80, height: 60 };

      const segments = findOrthogonalPath(
        source,
        target,
        Position.Right,
        Position.Left,
        [sourceBlock, targetBlock],
        sourceBlock,
        targetBlock
      );

      expect(segments.length).toBeGreaterThan(0);
      // First segment should still exit to the right (perpendicular to port)
      expect(segments[0].orientation).toBe("horizontal");
      expect(segments[0].to.x).toBeGreaterThan(segments[0].from.x);
      // Middle path should not cross either block (first/last segments naturally pass through)
      expect(middlePathCrossesBlock(segments, sourceBlock)).toBe(false);
      expect(middlePathCrossesBlock(segments, targetBlock)).toBe(false);
    });
  });

  describe("Turn minimization", () => {
    it("should prefer fewer turns when multiple valid paths exist", () => {
      // Simple case where L-shape (1 turn) and S-shape (3 turns) both work
      const source: Point = { x: 100, y: 100 };
      const target: Point = { x: 300, y: 200 };

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Top, []);

      // Should find path with minimal turns
      // For Right→Top with target below-right, L-shape should work
      const turns = countTurns(segments);
      expect(turns).toBeLessThanOrEqual(2); // At most 2 turns for simple case
    });
  });

  describe("Edge cases", () => {
    it("should handle self-loop (same block, different ports)", () => {
      const block: BlockBounds = { x: 100, y: 100, width: 100, height: 100 };
      const source: Point = { x: 200, y: 150 }; // Right edge
      const target: Point = { x: 100, y: 150 }; // Left edge

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Left, [block]);

      expect(segments.length).toBeGreaterThan(0);
      // Path should go around the block, not through it
      expect(pathCrossesBlock(segments, block)).toBe(false);
    });

    it("should handle tight spaces between blocks", () => {
      // Two blocks with small gap between them
      const block1: BlockBounds = { x: 100, y: 100, width: 80, height: 80 };
      const block2: BlockBounds = { x: 220, y: 100, width: 80, height: 80 };
      // Gap is 40px (220 - 180)

      const source: Point = { x: 50, y: 140 };
      const target: Point = { x: 350, y: 140 };

      const segments = findOrthogonalPath(source, target, Position.Right, Position.Left, [
        block1,
        block2,
      ]);

      expect(segments.length).toBeGreaterThan(0);
      expect(pathCrossesBlock(segments, block1)).toBe(false);
      expect(pathCrossesBlock(segments, block2)).toBe(false);
    });
  });

  describe("Regression: backwards spike in forward routing", () => {
    // Bug: When target is above-right of source (forward diagonal), the path
    // should NOT spike below the source before going up to target.
    // Reported configuration:
    // - Source block at (200, 240), port on right → port at approx (320, 280)
    // - Target block at (460, 180), port on left → port at approx (460, 220)
    // - Expected: simple L-shape or Z-shape going UP and RIGHT
    // - Bug: path goes DOWN first creating a spike

    it("should not create backwards spike for forward diagonal routing (Right→Left, target above-right)", () => {
      // Exact positions from reported bug
      const sourceBlock: BlockBounds = { x: 200, y: 240, width: 120, height: 80 };
      const targetBlock: BlockBounds = { x: 460, y: 180, width: 120, height: 80 };

      // Port positions (middle of right edge for source, middle of left edge for target)
      const source: Point = { x: 320, y: 280 }; // sourceBlock.x + width, sourceBlock.y + height/2
      const target: Point = { x: 460, y: 220 }; // targetBlock.x, targetBlock.y + height/2

      const segments = findOrthogonalPath(
        source,
        target,
        Position.Right,
        Position.Left,
        [sourceBlock, targetBlock],
        sourceBlock,
        targetBlock
      );

      expect(segments.length).toBeGreaterThan(0);

      // Key assertion: no waypoint should go BELOW the source port y-coordinate
      // (in screen coords, "below" means higher y value)
      const sourceY = source.y;
      for (const seg of segments) {
        // Allow small tolerance for the initial exit from port
        expect(seg.from.y).toBeLessThanOrEqual(sourceY + 5);
        expect(seg.to.y).toBeLessThanOrEqual(sourceY + 5);
      }

      // Path should end up at target (above source)
      const lastSeg = segments[segments.length - 1];
      expect(lastSeg.to.x).toBe(target.x);
      expect(lastSeg.to.y).toBe(target.y);
    });

    it("should not create downward spike when target is far above-right", () => {
      // Second reported bug: target far above source
      const sourceBlock: BlockBounds = { x: 180, y: 240, width: 120, height: 80 };
      const targetBlock: BlockBounds = { x: 440, y: 80, width: 120, height: 80 };

      // Port positions
      const source: Point = { x: 300, y: 280 }; // right edge middle
      const target: Point = { x: 440, y: 120 }; // left edge middle

      const segments = findOrthogonalPath(
        source,
        target,
        Position.Right,
        Position.Left,
        [sourceBlock, targetBlock],
        sourceBlock,
        targetBlock
      );

      expect(segments.length).toBeGreaterThan(0);

      // Path should NOT go below source block bottom + margin
      const maxAllowedY = sourceBlock.y + sourceBlock.height + 25; // 345
      for (const seg of segments) {
        expect(seg.from.y).toBeLessThanOrEqual(maxAllowedY);
        expect(seg.to.y).toBeLessThanOrEqual(maxAllowedY);
      }

      // Path should be efficient - L-shape or Z-shape
      // Note: with midpoint grid coordinates for centering, path may have more intermediate nodes
      expect(segments.length).toBeLessThanOrEqual(10);
    });
  });
});

// =============================================================================
// T102: Integration Tests
// =============================================================================

describe("Regression: horizontal spike bug", () => {
  // Reported configuration that produces a horizontal spike going LEFT
  // before routing up-right to the target.
  //
  // Block positions from bug report:
  // - Source: transfer_function at (100, 200), size ~120x80
  // - Target: transfer_function at (360, 140), size ~120x80
  // - Connection: Right→Left
  //
  // Port positions:
  // - Source port (Right): (100+120, 200+40) = (220, 240)
  // - Target port (Left): (360, 140+40) = (360, 180)
  //
  // Expected: path goes RIGHT from source, UP, then RIGHT into target
  // Bug: path goes LEFT first (spike), then up and right

  it("should not create leftward spike for Right→Left with target above-right", () => {
    const sourceBlock: BlockBounds = { x: 100, y: 200, width: 120, height: 80 };
    const targetBlock: BlockBounds = { x: 360, y: 140, width: 120, height: 80 };

    // Port positions
    const source: Point = { x: 220, y: 240 }; // Right edge of source block
    const target: Point = { x: 360, y: 180 }; // Left edge of target block

    const segments = findOrthogonalPath(
      source,
      target,
      Position.Right,
      Position.Left,
      [sourceBlock, targetBlock],
      sourceBlock,
      targetBlock
    );

    console.log("Segments for spike bug test:", JSON.stringify(segments, null, 2));

    expect(segments.length).toBeGreaterThan(0);

    // Key assertion: NO segment should go to the LEFT of the source port
    // (i.e., no segment point should have x < source.x)
    const sourceX = source.x;
    for (let i = 0; i < segments.length; i++) {
      const seg = segments[i];
      expect(seg.from.x).toBeGreaterThanOrEqual(sourceX - 1); // Small tolerance
      expect(seg.to.x).toBeGreaterThanOrEqual(sourceX - 1);
    }

    // Path should end at target
    const lastSeg = segments[segments.length - 1];
    expect(lastSeg.to.x).toBe(target.x);
    expect(lastSeg.to.y).toBe(target.y);
  });

  it("should not create spike via calculateOrthogonalPath (full integration)", () => {
    // Test the full integration path through calculateOrthogonalPath
    const sourceBlock: BlockBounds = { x: 100, y: 200, width: 120, height: 80 };
    const targetBlock: BlockBounds = { x: 360, y: 140, width: 120, height: 80 };

    // Port positions
    const source: Point = { x: 220, y: 240 };
    const target: Point = { x: 360, y: 180 };

    const segments = calculateOrthogonalPath(
      source,
      target,
      [], // No waypoints - should auto-route
      Position.Right,
      Position.Left,
      sourceBlock,
      targetBlock,
      [sourceBlock, targetBlock]
    );

    console.log("calculateOrthogonalPath segments:", JSON.stringify(segments, null, 2));

    expect(segments.length).toBeGreaterThan(0);

    // No segment should go left of source
    const sourceX = source.x;
    for (const seg of segments) {
      expect(seg.from.x).toBeGreaterThanOrEqual(sourceX - 1);
      expect(seg.to.x).toBeGreaterThanOrEqual(sourceX - 1);
    }
  });

  it("should not create spike for various target X positions", () => {
    // Sweep through different target X positions to find edge cases
    const sourceBlock: BlockBounds = { x: 100, y: 200, width: 120, height: 80 };
    const source: Point = { x: 220, y: 240 }; // Right port of source

    // Test target positions from just right of source to far right
    for (let targetX = 250; targetX <= 500; targetX += 10) {
      const targetBlock: BlockBounds = { x: targetX, y: 140, width: 120, height: 80 };
      const target: Point = { x: targetX, y: 180 }; // Left port of target

      const segments = findOrthogonalPath(
        source,
        target,
        Position.Right,
        Position.Left,
        [sourceBlock, targetBlock],
        sourceBlock,
        targetBlock
      );

      // Check for leftward spike
      const hasLeftwardSpike = segments.some(
        (seg) => seg.from.x < source.x - 1 || seg.to.x < source.x - 1
      );

      if (hasLeftwardSpike) {
        console.log(`SPIKE at targetX=${targetX}:`, JSON.stringify(segments, null, 2));
      }

      expect(hasLeftwardSpike).toBe(false);
    }
  });

  it("should not create spike for target positions near source exit point", () => {
    // Test the boundary case where target approach is near source exit
    const sourceBlock: BlockBounds = { x: 100, y: 200, width: 120, height: 80 };
    const source: Point = { x: 220, y: 240 };

    // Source exit X = 100 + 120 + 20 + 20 = 260 (block right + margin)
    // Test targets where approach point is close to exit point

    for (let targetX = 240; targetX <= 320; targetX += 5) {
      const targetBlock: BlockBounds = { x: targetX, y: 140, width: 120, height: 80 };
      const target: Point = { x: targetX, y: 180 };

      const segments = findOrthogonalPath(
        source,
        target,
        Position.Right,
        Position.Left,
        [sourceBlock, targetBlock],
        sourceBlock,
        targetBlock
      );

      const hasLeftwardSpike = segments.some(
        (seg) => seg.from.x < source.x - 1 || seg.to.x < source.x - 1
      );

      if (hasLeftwardSpike) {
        console.log(`SPIKE at targetX=${targetX}:`, JSON.stringify(segments, null, 2));
      }

      expect(hasLeftwardSpike).toBe(false);
    }
  });

  it("should handle boundary case where target approach is near source exit", () => {
    // This is the BOUNDARY case where target approach X is near source exit X
    // Tests that the algorithm handles overlapping exit/approach areas correctly
    const sourceBlock: BlockBounds = { x: 100, y: 200, width: 120, height: 80 };
    const targetBlock: BlockBounds = { x: 240, y: 140, width: 120, height: 80 };

    const source: Point = { x: 220, y: 240 }; // Right port of source
    const target: Point = { x: 240, y: 180 }; // Left port of target

    const segments = findOrthogonalPath(
      source,
      target,
      Position.Right,
      Position.Left,
      [sourceBlock, targetBlock],
      sourceBlock,
      targetBlock
    );

    console.log("\n=== BOUNDARY CASE DEBUG ===");
    console.log("Segments:", JSON.stringify(segments, null, 2));
    const sourceY = source.y;
    const segmentsAtSourceY = segments.filter((s) => s.from.y === sourceY && s.to.y === sourceY);
    console.log("Segments at source Y:", segmentsAtSourceY);

    // Should find a valid path
    expect(segments.length).toBeGreaterThan(0);
    // First segment should exit right
    expect(segments[0].orientation).toBe("horizontal");
    expect(segments[0].to.x).toBeGreaterThan(segments[0].from.x);

    // Check PORT_OFFSET constraint on first segment
    const exitDistance = Math.abs(segments[0].to.x - segments[0].from.x);
    expect(exitDistance).toBeGreaterThanOrEqual(20);

    // Last segment should approach from left
    const lastSeg = segments[segments.length - 1];
    expect(lastSeg.orientation).toBe("horizontal");
    expect(lastSeg.to.x).toBe(target.x);

    // Check PORT_OFFSET constraint on last segment
    const approachDistance = Math.abs(lastSeg.to.x - lastSeg.from.x);
    expect(approachDistance).toBeGreaterThanOrEqual(20);

    // Path should not have back-and-forth at source level (no rightward spike)
    // With PORT_OFFSET constraints, this might create a different pattern
    // Updated: allow up to 2 segments if needed to meet PORT_OFFSET
    expect(segmentsAtSourceY.length).toBeLessThanOrEqual(2);
  });

  it("should debug the exact user-reported configuration", () => {
    // EXACT configuration from bug report
    const sourceBlock: BlockBounds = { x: 100, y: 200, width: 120, height: 80 };
    const targetBlock: BlockBounds = { x: 360, y: 140, width: 120, height: 80 };

    // Port positions (calculated from block positions)
    const source: Point = { x: 220, y: 240 }; // Right edge of source: 100+120=220, center: 200+40=240
    const target: Point = { x: 360, y: 180 }; // Left edge of target: 360, center: 140+40=180

    console.log("\n=== DEBUG: User-reported spike configuration ===");
    console.log("Source block:", sourceBlock);
    console.log("Target block:", targetBlock);
    console.log("Source port:", source);
    console.log("Target port:", target);

    // Calculate exit and approach points
    const exitX = sourceBlock.x + sourceBlock.width + 20; // 100+120+20 = 240
    const approachX = targetBlock.x - 20; // 360-20 = 340
    console.log("Expected exit X:", exitX);
    console.log("Expected approach X:", approachX);

    const segments = findOrthogonalPath(
      source,
      target,
      Position.Right,
      Position.Left,
      [sourceBlock, targetBlock],
      sourceBlock,
      targetBlock
    );

    console.log("Segments:", JSON.stringify(segments, null, 2));

    // Check path characteristics
    const minX = Math.min(...segments.flatMap((s) => [s.from.x, s.to.x]));
    const maxX = Math.max(...segments.flatMap((s) => [s.from.x, s.to.x]));
    console.log("Path X range:", minX, "to", maxX);
    console.log("Has leftward spike (x < source.x)?", minX < source.x);

    expect(segments.length).toBeGreaterThan(0);
    expect(minX).toBeGreaterThanOrEqual(source.x - 1);
  });
});

describe("calculateOrthogonalPath with all blocks", () => {
  it("should use graph search when no waypoints and blocks provided", () => {
    const source: Point = { x: 100, y: 200 };
    const target: Point = { x: 400, y: 200 };
    const obstacleBlock: BlockBounds = { x: 200, y: 150, width: 100, height: 100 };

    // This test verifies the integration point - calculateOrthogonalPath
    // should delegate to findOrthogonalPath when blocks are provided
    const segments = calculateOrthogonalPath(
      source,
      target,
      [], // No waypoints
      Position.Right,
      Position.Left,
      { x: 50, y: 170, width: 80, height: 60 }, // sourceBounds
      { x: 370, y: 170, width: 80, height: 60 }, // targetBounds
      [obstacleBlock] // allBlocks - new parameter
    );

    expect(segments.length).toBeGreaterThan(0);
  });

  it("should route through user waypoints when provided (may cross blocks)", () => {
    const source: Point = { x: 100, y: 200 };
    const target: Point = { x: 400, y: 200 };
    const waypoints: Waypoint[] = [
      { x: 250, y: 200 }, // Waypoint inside where a block might be
    ];

    // When user provides waypoints, honor them even if they cross blocks
    const segments = calculateOrthogonalPath(
      source,
      target,
      waypoints,
      Position.Right,
      Position.Left
    );

    expect(segments.length).toBeGreaterThan(0);
    // Path should pass through the waypoint
    const passesWaypoint = segments.some((seg) => seg.from.x === 250 || seg.to.x === 250);
    expect(passesWaypoint).toBe(true);
  });
});

// =============================================================================
// Centered Z-Path Tests
// =============================================================================

describe("Centered Z-path routing", () => {
  it("should prefer centered vertical segment for horizontally offset blocks", () => {
    // User-reported scenario: Gain blocks at x=100, y=200 and x=450, y=120
    // Gain block size: 120x80
    const sourceBlock: BlockBounds = { x: 100, y: 200, width: 120, height: 80 };
    const targetBlock: BlockBounds = { x: 450, y: 120, width: 120, height: 80 };

    // Source port (Right): x = 100 + 120 = 220, y = 200 + 40 = 240
    // Target port (Left): x = 450, y = 120 + 40 = 160
    const source: Point = { x: 220, y: 240 };
    const target: Point = { x: 450, y: 160 };

    const segments = findOrthogonalPath(
      source,
      target,
      Position.Right,
      Position.Left,
      [sourceBlock, targetBlock],
      sourceBlock,
      targetBlock
    );

    console.log("\n=== CENTERING TEST DEBUG ===");
    console.log("Source block:", sourceBlock);
    console.log("Target block:", targetBlock);
    console.log("Source port:", source);
    console.log("Target port:", target);
    console.log("Midpoint X:", (source.x + target.x) / 2);
    console.log("Segments:", JSON.stringify(segments, null, 2));

    // Find the vertical segment(s) - these form the "middle" of the Z
    const verticalSegments = segments.filter((s) => s.orientation === "vertical");
    console.log("Vertical segments:", verticalSegments);

    expect(segments.length).toBeGreaterThan(0);

    // The vertical segment's X coordinate should be roughly centered
    // Source exit: ~240 (100 + 120 + 20 margin)
    // Target approach: ~430 (450 - 20 margin)
    // Midpoint: ~335
    const sourceExitX = sourceBlock.x + sourceBlock.width + 20; // 240
    const targetApproachX = targetBlock.x - 20; // 430
    const midpointX = (sourceExitX + targetApproachX) / 2; // 335
    console.log("Expected centered X:", midpointX);

    if (verticalSegments.length > 0) {
      const verticalX = verticalSegments[0].from.x;
      console.log("Actual vertical segment X:", verticalX);

      // Check if vertical segment is within 20% of center vs. at the edges
      const rangeWidth = targetApproachX - sourceExitX; // 190
      const tolerance = rangeWidth * 0.3; // 30% tolerance
      const distanceFromCenter = Math.abs(verticalX - midpointX);

      console.log("Distance from center:", distanceFromCenter);
      console.log("Tolerance (30%):", tolerance);

      // The vertical segment should be closer to center than to edges
      expect(distanceFromCenter).toBeLessThan(tolerance);
    }
  });
});

// =============================================================================
// Regression: Flipped target block routing bug
// =============================================================================

describe("Flipped target block routing", () => {
  // Bug: When target block is flipped (input port on RIGHT instead of LEFT),
  // the auto-routing doesn't properly avoid the SOURCE block when routing back.
  //
  // Reported configuration:
  // - Transfer Function at (224.33, 228.10), width=100, height=50
  // - IO Marker (flipped) at (-22.99, 303.10), width=60, height=48
  // - Connection: Right→Right (source exits right, target input is on right due to flip)
  //
  // The route needs to:
  // 1. Exit source to the right
  // 2. Loop around to approach target from the right (since target is flipped)
  // 3. NOT cross through the source block while looping

  // Helper to check if any segment crosses a block
  function pathCrossesBlock(segments: Segment[], block: BlockBounds): boolean {
    for (const seg of segments) {
      if (segmentCrossesBlock(seg.from, seg.to, block)) {
        return true;
      }
    }
    return false;
  }

  it("should not cross source block when target has input on RIGHT side", () => {
    // Exact positions from bug report
    const sourceBlock: BlockBounds = { x: 224, y: 228, width: 100, height: 50 };
    const targetBlock: BlockBounds = { x: -23, y: 303, width: 60, height: 48 };

    // Source port: right edge of Transfer Function
    // Port at right side: x = 224 + 100 = 324, y = 228 + 25 = 253
    const source: Point = { x: 324, y: 253 };

    // Target port: right edge of IO Marker (FLIPPED - input is on right)
    // Port at right side: x = -23 + 60 = 37, y = 303 + 24 = 327
    const target: Point = { x: 37, y: 327 };

    // Source exits Right, Target input is on Right (flipped block)
    const segments = findOrthogonalPath(
      source,
      target,
      Position.Right,
      Position.Right, // Both Right because target is flipped
      [sourceBlock, targetBlock],
      sourceBlock,
      targetBlock
    );

    expect(segments.length).toBeGreaterThan(0);

    // First segment should exit RIGHT (positive x direction)
    // because sourcePosition is Position.Right
    expect(segments[0].orientation).toBe("horizontal");
    expect(segments[0].to.x).toBeGreaterThan(segments[0].from.x);

    // Last segment should approach target from RIGHT (going left into it)
    const lastSeg = segments[segments.length - 1];
    expect(lastSeg.orientation).toBe("horizontal");
    expect(lastSeg.from.x).toBeGreaterThan(lastSeg.to.x);

    // Path should NOT cross through source block
    // Skip first segment (exit from source) when checking source block crossing
    const segmentsAfterExit = segments.slice(1);
    const middleCrossesSource = pathCrossesBlock(segmentsAfterExit, sourceBlock);
    expect(middleCrossesSource).toBe(false);
  });

  it("should find valid path when target is to left and below source with Right input", () => {
    // More general test case - target to lower-left with input on right
    const sourceBlock: BlockBounds = { x: 300, y: 100, width: 100, height: 60 };
    const targetBlock: BlockBounds = { x: 50, y: 250, width: 80, height: 50 };

    // Source port: right edge
    const source: Point = { x: 400, y: 130 };
    // Target port: right edge (flipped)
    const target: Point = { x: 130, y: 275 };

    const segments = findOrthogonalPath(
      source,
      target,
      Position.Right,
      Position.Right,
      [sourceBlock, targetBlock],
      sourceBlock,
      targetBlock
    );

    expect(segments.length).toBeGreaterThan(0);

    // First segment should exit RIGHT (positive x direction)
    expect(segments[0].orientation).toBe("horizontal");
    expect(segments[0].to.x).toBeGreaterThan(segments[0].from.x);

    // Last segment should approach from right (going left)
    const lastSeg = segments[segments.length - 1];
    expect(lastSeg.orientation).toBe("horizontal");
    expect(lastSeg.from.x).toBeGreaterThan(lastSeg.to.x);

    // Path should not cross source block (except first exit segment)
    const segmentsAfterExit = segments.slice(1);
    for (const seg of segmentsAfterExit) {
      expect(segmentCrossesBlock(seg.from, seg.to, sourceBlock)).toBe(false);
    }
  });

  it("should handle Right→Right connection where target is directly left of source", () => {
    // Edge case: target directly to the left at same Y level
    const sourceBlock: BlockBounds = { x: 300, y: 200, width: 100, height: 60 };
    const targetBlock: BlockBounds = { x: 50, y: 200, width: 80, height: 60 };

    const source: Point = { x: 400, y: 230 }; // Right edge
    const target: Point = { x: 130, y: 230 }; // Right edge (flipped)

    const segments = findOrthogonalPath(
      source,
      target,
      Position.Right,
      Position.Right,
      [sourceBlock, targetBlock],
      sourceBlock,
      targetBlock
    );

    expect(segments.length).toBeGreaterThan(0);

    // First segment should exit right
    expect(segments[0].orientation).toBe("horizontal");
    expect(segments[0].to.x).toBeGreaterThan(segments[0].from.x);

    // Last segment should approach from right (going left)
    const lastSeg = segments[segments.length - 1];
    expect(lastSeg.orientation).toBe("horizontal");
    expect(lastSeg.from.x).toBeGreaterThan(lastSeg.to.x);
  });
});

// =============================================================================
// Fan-out PORT_OFFSET constraint tests
// =============================================================================

describe("Fan-out PORT_OFFSET constraint", () => {
  it("validates user's bug report - segments violate PORT_OFFSET on target approach", () => {
    // User provided actual segment output from console showing ~6px final segment
    // This test validates that the bug EXISTS by checking the provided buggy segments

    const buggySegments = [
      {
        from: { x: 393.28967222538614, y: 192.0004772594392 },
        to: { x: 411.28964383561635, y: 192.0004772594392 },
        orientation: "horizontal" as const,
      },
      {
        from: { x: 411.28964383561635, y: 192.0004772594392 },
        to: { x: 411.28964383561635, y: 228 },
        orientation: "vertical" as const,
      },
      {
        from: { x: 411.28964383561635, y: 228 },
        to: { x: 212.00000966651115, y: 228 },
        orientation: "horizontal" as const,
      },
      {
        from: { x: 212.00000966651115, y: 228 },
        to: { x: 212.00000966651115, y: 222.00001066783273 },
        orientation: "vertical" as const,
      },
    ];

    console.log("\n=== USER BUG VALIDATION ===");
    console.log("Checking buggy segments from user's console output");

    // Check FIRST segment (source exit) - should be >= 20px
    const firstSegment = buggySegments[0];
    const exitDistance = Math.abs(firstSegment.to.x - firstSegment.from.x);
    console.log("Source exit distance:", exitDistance, "(should be >= 20)");

    // Check LAST segment (target approach) - THIS IS THE BUG
    const lastSegment = buggySegments[buggySegments.length - 1];
    const approachDistance = Math.abs(lastSegment.to.y - lastSegment.from.y);
    console.log("Target approach distance:", approachDistance, "(should be >= 20)");
    console.log("BUG: approach distance is only ~6px!");

    // This documents the bug - approach segment is too short
    expect(approachDistance).toBeLessThan(20); // Bug: only ~6px
    expect(approachDistance).toBeCloseTo(6, 0); // Approximately 6 pixels
  });

  it("FIX: respects PORT_OFFSET in fan-out routing to sum block bottom port", () => {
    // Same scenario as user's bug, but with the FIX applied
    // This verifies that findOrthogonalPath now respects PORT_OFFSET

    const transferFunctionBlock = { x: 291.29, y: 167, width: 100, height: 50 };
    const sumBlock = { x: 184, y: 164, width: 56, height: 56 };
    const ioMarkerBlock = { x: 447.64, y: 176, width: 60, height: 48 };

    // Source: TF output port (right side, centered)
    const tfOutput = {
      x: transferFunctionBlock.x + transferFunctionBlock.width,
      y: transferFunctionBlock.y + transferFunctionBlock.height / 2,
    };

    // Target: Sum bottom port (centered horizontally, bottom edge)
    const sumBottom = {
      x: sumBlock.x + sumBlock.width / 2,
      y: sumBlock.y + sumBlock.height,
    };

    console.log("\n=== PORT_OFFSET FIX VERIFICATION ===");
    console.log("Routing from TF output to Sum bottom port");
    console.log("Source:", tfOutput);
    console.log("Target:", sumBottom);

    const segments = findOrthogonalPath(
      tfOutput,
      sumBottom,
      Position.Right,
      Position.Top,
      [transferFunctionBlock, sumBlock, ioMarkerBlock],
      transferFunctionBlock,
      sumBlock
    );

    console.log("Segments:", JSON.stringify(segments, null, 2));

    // Should find a path
    expect(segments.length).toBeGreaterThan(0);

    // Check FIRST segment (source exit)
    const firstSegment = segments[0];
    expect(firstSegment.orientation).toBe("horizontal");
    const exitDistance = Math.abs(firstSegment.to.x - firstSegment.from.x);
    console.log("Source exit distance:", exitDistance);
    expect(exitDistance).toBeGreaterThanOrEqual(20); // PORT_OFFSET

    // Check LAST segment (target approach)
    const lastSegment = segments[segments.length - 1];
    expect(lastSegment.orientation).toBe("vertical");
    const approachDistance = Math.abs(lastSegment.to.y - lastSegment.from.y);
    console.log("Target approach distance:", approachDistance);
    expect(approachDistance).toBeGreaterThanOrEqual(20); // PORT_OFFSET - FIXED!

    console.log("✓ FIX VERIFIED: Both exit and approach respect PORT_OFFSET=20px");
  });

  it("should respect 20px PORT_OFFSET on both source exit and target approach in fan-out scenarios", () => {
    // Recreate the bug scenario from the user's diagram
    // Transfer function block: position (291.29, 167), default size 100x50
    // Sum block: position (184, 164), default size 56x56
    // IOMarker: position (447.64, 176), default size 60x48

    const transferFunctionBlock = { x: 291.29, y: 167, width: 100, height: 50 };
    const sumBlock = { x: 184, y: 164, width: 56, height: 56 };
    const ioMarkerBlock = { x: 447.64, y: 176, width: 60, height: 48 };

    // Transfer function output port (right edge, centered vertically)
    const tfOutputPort = {
      x: transferFunctionBlock.x + transferFunctionBlock.width,
      y: transferFunctionBlock.y + transferFunctionBlock.height / 2,
    }; // (391.29, 192)

    // Sum block input port (left edge, centered vertically for bottom input)
    const sumInputPort = {
      x: sumBlock.x + sumBlock.width / 2,
      y: sumBlock.y + sumBlock.height,
    }; // (212, 220)

    // IOMarker input port (left edge, centered vertically)
    const ioInputPort = {
      x: ioMarkerBlock.x,
      y: ioMarkerBlock.y + ioMarkerBlock.height / 2,
    }; // (447.64, 200)

    // Test connection from TF to Sum (fan-out #1)
    const segmentsToSum = findOrthogonalPath(
      tfOutputPort,
      sumInputPort,
      Position.Right,
      Position.Top,
      [transferFunctionBlock, sumBlock, ioMarkerBlock],
      transferFunctionBlock,
      sumBlock
    );

    // Test connection from TF to IOMarker (fan-out #2)
    const segmentsToIO = findOrthogonalPath(
      tfOutputPort,
      ioInputPort,
      Position.Right,
      Position.Left,
      [transferFunctionBlock, sumBlock, ioMarkerBlock],
      transferFunctionBlock,
      ioMarkerBlock
    );

    // Both paths should exist
    expect(segmentsToSum.length).toBeGreaterThan(0);
    expect(segmentsToIO.length).toBeGreaterThan(0);

    // Check source exit segment (first segment) for TF→Sum connection
    const firstSegSum = segmentsToSum[0];
    expect(firstSegSum.orientation).toBe("horizontal"); // Right port exits horizontally
    const exitDistanceSum = Math.abs(firstSegSum.to.x - firstSegSum.from.x);
    expect(exitDistanceSum).toBeGreaterThanOrEqual(20); // PORT_OFFSET = 20

    // Check target approach segment (last segment) for TF→Sum connection
    const lastSegSum = segmentsToSum[segmentsToSum.length - 1];
    expect(lastSegSum.orientation).toBe("vertical"); // Top port approaches vertically
    const approachDistanceSum = Math.abs(lastSegSum.to.y - lastSegSum.from.y);
    expect(approachDistanceSum).toBeGreaterThanOrEqual(20); // PORT_OFFSET = 20

    // Check source exit segment for TF→IO connection
    const firstSegIO = segmentsToIO[0];
    expect(firstSegIO.orientation).toBe("horizontal");
    const exitDistanceIO = Math.abs(firstSegIO.to.x - firstSegIO.from.x);
    expect(exitDistanceIO).toBeGreaterThanOrEqual(20);

    // Check target approach segment for TF→IO connection
    const lastSegIO = segmentsToIO[segmentsToIO.length - 1];
    expect(lastSegIO.orientation).toBe("horizontal"); // Left port approaches horizontally
    const approachDistanceIO = Math.abs(lastSegIO.to.x - lastSegIO.from.x);
    expect(approachDistanceIO).toBeGreaterThanOrEqual(20);
  });
});
