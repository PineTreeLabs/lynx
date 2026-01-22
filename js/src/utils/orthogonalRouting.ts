// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Orthogonal routing utilities for connection paths
 *
 * Provides functions for calculating orthogonal (90-degree) paths between points,
 * routing through waypoints, and converting to SVG path strings.
 */

import { Position } from "reactflow";

/**
 * A point in 2D canvas coordinate space
 */
export interface Point {
  x: number;
  y: number;
}

/**
 * A waypoint for custom connection routing
 */
export interface Waypoint {
  x: number;
  y: number;
}

/**
 * Orientation of a path segment
 */
export type SegmentOrientation = "horizontal" | "vertical";

/**
 * A line segment with known orientation
 */
export interface Segment {
  from: Point;
  to: Point;
  orientation: SegmentOrientation;
}

/**
 * Bounding box for a block (position + dimensions)
 */
export interface BlockBounds {
  x: number; // left edge
  y: number; // top edge
  width: number;
  height: number;
}

/** Clearance margin around blocks for routing */
const BLOCK_MARGIN = 20;

/** Turn penalty for path finding (equivalent distance in pixels) */
const TURN_PENALTY = 50;

/** Minimum offset distance from port for routing */
const PORT_OFFSET = 20;

// =============================================================================
// Visibility Graph Routing Algorithm
// =============================================================================

/**
 * Check if an orthogonal segment (horizontal or vertical) crosses through a block.
 *
 * A segment "crosses" a block if it passes through the interior.
 * Touching the boundary exactly does NOT count as crossing (allows routing along edges).
 *
 * @param a - Start point of segment
 * @param b - End point of segment
 * @param block - Block bounds to check against
 * @returns true if segment crosses through block interior
 */
export function segmentCrossesBlock(a: Point, b: Point, block: BlockBounds): boolean {
  const minX = Math.min(a.x, b.x);
  const maxX = Math.max(a.x, b.x);
  const minY = Math.min(a.y, b.y);
  const maxY = Math.max(a.y, b.y);

  const blockLeft = block.x;
  const blockRight = block.x + block.width;
  const blockTop = block.y;
  const blockBottom = block.y + block.height;

  // For horizontal segment (same Y)
  if (a.y === b.y) {
    const y = a.y;
    // Segment must be strictly inside block's Y range
    if (y <= blockTop || y >= blockBottom) {
      return false;
    }
    // Segment X range must overlap with block X range (strictly inside)
    if (maxX <= blockLeft || minX >= blockRight) {
      return false;
    }
    return true;
  }

  // For vertical segment (same X)
  if (a.x === b.x) {
    const x = a.x;
    // Segment must be strictly inside block's X range
    if (x <= blockLeft || x >= blockRight) {
      return false;
    }
    // Segment Y range must overlap with block Y range (strictly inside)
    if (maxY <= blockTop || minY >= blockBottom) {
      return false;
    }
    return true;
  }

  // Non-orthogonal segment - shouldn't happen in our routing, but handle gracefully
  return false;
}

/**
 * Check if a segment crosses any of the given blocks
 */
function segmentCrossesAnyBlock(a: Point, b: Point, blocks: BlockBounds[]): boolean {
  for (const block of blocks) {
    if (segmentCrossesBlock(a, b, block)) {
      return true;
    }
  }
  return false;
}

/**
 * Node in the routing graph
 */
interface RouteNode {
  id: string;
  point: Point;
  type: "source" | "target" | "corner";
}

/**
 * Edge in the routing graph
 */
interface RouteEdge {
  to: RouteNode;
  distance: number;
  orientation: SegmentOrientation;
}

/**
 * State for Dijkstra search (includes direction for turn penalty)
 */
interface SearchState {
  node: RouteNode;
  direction: SegmentOrientation | "start";
  distance: number;
}

/**
 * Generate route nodes from source, target, and block corners.
 *
 * Creates a grid of potential waypoints at the intersections of:
 * - Exit/approach X and Y coordinates
 * - Block corner X and Y coordinates (with margin)
 *
 * This ensures there's always a path if one exists.
 */

// Unused helper function - kept for potential future use
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function generateRouteNodes(
  source: Point,
  target: Point,
  sourcePosition: Position,
  targetPosition: Position,
  blocks: BlockBounds[]
): RouteNode[] {
  // Collect all unique X and Y coordinates for the grid
  const xCoords = new Set<number>();
  const yCoords = new Set<number>();

  // Calculate exit point (clears source block in exit direction)
  const exitPoint = getExitPoint(source, sourcePosition);
  xCoords.add(exitPoint.x);
  yCoords.add(exitPoint.y);

  // Calculate approach point (outside target block)
  const approachPoint = getApproachPoint(target, targetPosition);
  xCoords.add(approachPoint.x);
  yCoords.add(approachPoint.y);

  // Add block corner coordinates (with margin)
  for (const block of blocks) {
    const expanded = expandBounds(block, BLOCK_MARGIN);
    xCoords.add(expanded.x);
    xCoords.add(expanded.x + expanded.width);
    yCoords.add(expanded.y);
    yCoords.add(expanded.y + expanded.height);
  }

  // Generate nodes at all grid intersections
  const nodes: RouteNode[] = [];
  let nodeId = 0;

  const xArray = Array.from(xCoords);
  const yArray = Array.from(yCoords);

  for (const x of xArray) {
    for (const y of yArray) {
      // Determine node type
      let type: "source" | "target" | "corner" = "corner";
      if (x === exitPoint.x && y === exitPoint.y) {
        type = "source";
      } else if (x === approachPoint.x && y === approachPoint.y) {
        type = "target";
      }

      nodes.push({
        id: `node_${nodeId++}`,
        point: { x, y },
        type,
      });
    }
  }

  return nodes;
}

/**
 * Get the exit point for a source port (offset from port in exit direction)
 */
function getExitPoint(source: Point, position: Position): Point {
  switch (position) {
    case Position.Right:
      return { x: source.x + BLOCK_MARGIN, y: source.y };
    case Position.Left:
      return { x: source.x - BLOCK_MARGIN, y: source.y };
    case Position.Bottom:
      return { x: source.x, y: source.y + BLOCK_MARGIN };
    case Position.Top:
      return { x: source.x, y: source.y - BLOCK_MARGIN };
    default:
      return source;
  }
}

/**
 * Get the approach point for a target port (offset from port in approach direction)
 */
function getApproachPoint(target: Point, position: Position): Point {
  switch (position) {
    case Position.Left:
      return { x: target.x - BLOCK_MARGIN, y: target.y };
    case Position.Right:
      return { x: target.x + BLOCK_MARGIN, y: target.y };
    case Position.Top:
      return { x: target.x, y: target.y - BLOCK_MARGIN };
    case Position.Bottom:
      return { x: target.x, y: target.y + BLOCK_MARGIN };
    default:
      return target;
  }
}

/**
 * Build visibility graph from nodes.
 * Creates edges between nodes that can be connected with orthogonal segments
// eslint-disable-next-line @typescript-eslint/no-unused-vars

 * without crossing any blocks.
 */
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
function buildVisibilityGraph(nodes: RouteNode[], blocks: BlockBounds[]): Map<string, RouteEdge[]> {
  const graph = new Map<string, RouteEdge[]>();

  // Initialize adjacency list for each node
  for (const node of nodes) {
    graph.set(node.id, []);
  }

  // Check all pairs of nodes
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i];
      const b = nodes[j];

      // Only consider orthogonal connections (same X or same Y)
      const isHorizontal = a.point.y === b.point.y;
      const isVertical = a.point.x === b.point.x;

      if (!isHorizontal && !isVertical) {
        continue;
      }

      // Check if segment crosses any block
      if (segmentCrossesAnyBlock(a.point, b.point, blocks)) {
        continue;
      }

      // Add bidirectional edge
      const distance = Math.abs(a.point.x - b.point.x) + Math.abs(a.point.y - b.point.y);
      const orientation: SegmentOrientation = isHorizontal ? "horizontal" : "vertical";

      graph.get(a.id)!.push({ to: b, distance, orientation });
      graph.get(b.id)!.push({ to: a, distance, orientation });
    }
  }

  return graph;
}

/**
 * Dijkstra's algorithm with turn penalty.
 * Searches over (node, direction) pairs to properly penalize turns.
 *
 * @param sourceOrientation - Expected orientation of the first edge (matches initial segment)
 * @param targetOrientation - Expected orientation of the last edge (matches final segment)
 */
function dijkstraWithTurns(
  graph: Map<string, RouteEdge[]>,
  startNode: RouteNode,
  endNode: RouteNode,
  turnPenalty: number,
  sourceOrientation?: SegmentOrientation,
  targetOrientation?: SegmentOrientation
): RouteNode[] {
  // State key: "nodeId:direction"
  const stateKey = (node: RouteNode, dir: SegmentOrientation | "start") => `${node.id}:${dir}`;

  // Distance to each state
  const dist = new Map<string, number>();
  // Previous state for path reconstruction
  const prev = new Map<string, { node: RouteNode; direction: SegmentOrientation | "start" }>();

  // Priority queue (simple array, sorted on pop)
  const queue: SearchState[] = [];

  // Initialize with start state - use source orientation if provided to penalize misalignment
  const initialDir: SegmentOrientation | "start" = sourceOrientation || "start";
  const startKey = stateKey(startNode, initialDir);
  dist.set(startKey, 0);
  queue.push({ node: startNode, direction: initialDir, distance: 0 });

  while (queue.length > 0) {
    // Get state with minimum distance
    queue.sort((a, b) => a.distance - b.distance);
    const current = queue.shift()!;
    const currentKey = stateKey(current.node, current.direction);

    // Skip if we've already found a better path to this state
    if (dist.has(currentKey) && dist.get(currentKey)! < current.distance) {
      continue;
    }

    // Check if we've reached the target
    if (current.node.id === endNode.id) {
      // Reconstruct path
      const path: RouteNode[] = [];
      let state: { node: RouteNode; direction: SegmentOrientation | "start" } | undefined = {
        node: current.node,
        direction: current.direction,
      };

      while (state) {
        path.unshift(state.node);
        const key = stateKey(state.node, state.direction);
        state = prev.get(key);
      }

      return path;
    }

    // Explore neighbors
    const edges = graph.get(current.node.id) || [];
    for (const edge of edges) {
      const nextDir = edge.orientation;

      // Calculate turn cost from current direction
      const turnCost =
        current.direction !== "start" && current.direction !== nextDir ? turnPenalty : 0;

      // Add penalty if arriving at target with wrong direction for final segment alignment
      const targetAlignmentCost =
        edge.to.id === endNode.id && targetOrientation && nextDir !== targetOrientation
          ? turnPenalty
          : 0;

      const newDist = current.distance + edge.distance + turnCost + targetAlignmentCost;
      const nextKey = stateKey(edge.to, nextDir);

      if (!dist.has(nextKey) || newDist < dist.get(nextKey)!) {
        dist.set(nextKey, newDist);
        prev.set(nextKey, { node: current.node, direction: current.direction });
        queue.push({ node: edge.to, direction: nextDir, distance: newDist });
      }
    }
  }

  // No path found
  return [];
}

/**
 * Convert a path of nodes to segments.
 */
function pathToSegments(path: RouteNode[]): Segment[] {
  if (path.length < 2) {
    return [];
  }

  const segments: Segment[] = [];

  for (let i = 0; i < path.length - 1; i++) {
    const from = path[i].point;
    const to = path[i + 1].point;
    const orientation: SegmentOrientation = from.y === to.y ? "horizontal" : "vertical";
    segments.push({ from, to, orientation });
  }

  return segments;
}

/**
 * Check if two segments are going in the same direction.
 * For horizontal: both going right (dx > 0) or both going left (dx < 0)
 * For vertical: both going down (dy > 0) or both going up (dy < 0)
 */
function sameDirection(a: Segment, b: Segment): boolean {
  if (a.orientation !== b.orientation) return false;

  if (a.orientation === "horizontal") {
    const aDx = a.to.x - a.from.x;
    const bDx = b.to.x - b.from.x;
    return (aDx > 0 && bDx > 0) || (aDx < 0 && bDx < 0);
  } else {
    const aDy = a.to.y - a.from.y;
    const bDy = b.to.y - b.from.y;
    return (aDy > 0 && bDy > 0) || (aDy < 0 && bDy < 0);
  }
}

/**
 * Simplify path by merging consecutive collinear segments going the same direction.
 * This removes intermediate grid nodes that don't change direction.
 */
function simplifyPath(segments: Segment[]): Segment[] {
  if (segments.length <= 1) return segments;

  const simplified: Segment[] = [];
  let current = segments[0];

  for (let i = 1; i < segments.length; i++) {
    const next = segments[i];
    if (sameDirection(current, next)) {
      // Merge collinear segments going the same direction
      current = { from: current.from, to: next.to, orientation: current.orientation };
    } else {
      simplified.push(current);
      current = next;
    }
  }
  simplified.push(current);

  return simplified;
}

/**
 * Center a Z-shaped path by moving the middle segment to the midpoint.
 *
 * A Z-path has pattern: H-V-H (horizontal-vertical-horizontal) or V-H-V.
 * This function shifts the middle segment's position to be centered between
 * the fixed endpoints.
 *
 * @param segments - Simplified path segments
 * @param blocks - Blocks to avoid (for collision checking)
 * @returns Centered segments if valid, or original segments if centering not possible
 */
function centerZPath(segments: Segment[], blocks: BlockBounds[]): Segment[] {
  // Must have exactly 3 segments for a Z-path
  if (segments.length !== 3) return segments;

  const [first, middle, last] = segments;

  // Check for H-V-H pattern (horizontal-vertical-horizontal)
  if (
    first.orientation === "horizontal" &&
    middle.orientation === "vertical" &&
    last.orientation === "horizontal"
  ) {
    // Current middle X is where the vertical segment is
    const currentMiddleX = middle.from.x;

    // Calculate centered X position
    const startX = first.from.x;
    const endX = last.to.x;
    const centeredX = (startX + endX) / 2;

    // If already centered (within 5px), no change needed
    if (Math.abs(currentMiddleX - centeredX) < 5) return segments;

    // Check if centering would reverse the direction of first or last segment
    // This preserves exit/approach direction constraints from the routing algorithm
    const originalFirstDx = first.to.x - first.from.x;
    const centeredFirstDx = centeredX - first.from.x;
    const originalLastDx = last.to.x - last.from.x;
    const centeredLastDx = last.to.x - centeredX;

    // Skip centering if it would reverse direction of first segment
    if (
      (originalFirstDx > 0 && centeredFirstDx <= 0) ||
      (originalFirstDx < 0 && centeredFirstDx >= 0)
    ) {
      return segments;
    }

    // Skip centering if it would reverse direction of last segment
    if (
      (originalLastDx > 0 && centeredLastDx <= 0) ||
      (originalLastDx < 0 && centeredLastDx >= 0)
    ) {
      return segments;
    }

    // Create new centered path
    const newFirst: Segment = {
      from: first.from,
      to: { x: centeredX, y: first.from.y },
      orientation: "horizontal",
    };
    const newMiddle: Segment = {
      from: { x: centeredX, y: first.from.y },
      to: { x: centeredX, y: last.to.y },
      orientation: "vertical",
    };
    const newLast: Segment = {
      from: { x: centeredX, y: last.to.y },
      to: last.to,
      orientation: "horizontal",
    };

    // Check if the centered vertical segment crosses any blocks
    if (!segmentCrossesAnyBlock(newMiddle.from, newMiddle.to, blocks)) {
      return [newFirst, newMiddle, newLast];
    }
  }

  // Check for V-H-V pattern (vertical-horizontal-vertical)
  if (
    first.orientation === "vertical" &&
    middle.orientation === "horizontal" &&
    last.orientation === "vertical"
  ) {
    // Current middle Y is where the horizontal segment is
    const currentMiddleY = middle.from.y;

    // Calculate centered Y position
    const startY = first.from.y;
    const endY = last.to.y;
    const centeredY = (startY + endY) / 2;

    // If already centered (within 5px), no change needed
    if (Math.abs(currentMiddleY - centeredY) < 5) return segments;

    // Check if centering would reverse the direction of first or last segment
    const originalFirstDy = first.to.y - first.from.y;
    const centeredFirstDy = centeredY - first.from.y;
    const originalLastDy = last.to.y - last.from.y;
    const centeredLastDy = last.to.y - centeredY;

    // Skip centering if it would reverse direction of first segment
    if (
      (originalFirstDy > 0 && centeredFirstDy <= 0) ||
      (originalFirstDy < 0 && centeredFirstDy >= 0)
    ) {
      return segments;
    }

    // Skip centering if it would reverse direction of last segment
    if (
      (originalLastDy > 0 && centeredLastDy <= 0) ||
      (originalLastDy < 0 && centeredLastDy >= 0)
    ) {
      return segments;
    }

    // Create new centered path
    const newFirst: Segment = {
      from: first.from,
      to: { x: first.from.x, y: centeredY },
      orientation: "vertical",
    };
    const newMiddle: Segment = {
      from: { x: first.from.x, y: centeredY },
      to: { x: last.to.x, y: centeredY },
      orientation: "horizontal",
    };
    const newLast: Segment = {
      from: { x: last.to.x, y: centeredY },
      to: last.to,
      orientation: "vertical",
    };

    // Check if the centered horizontal segment crosses any blocks
    if (!segmentCrossesAnyBlock(newMiddle.from, newMiddle.to, blocks)) {
      return [newFirst, newMiddle, newLast];
    }
  }

  // Return original if centering not applicable or blocked
  return segments;
}

/**
 * Find orthogonal path from source to target avoiding all blocks.
 *
 * Uses visibility graph + Dijkstra with turn penalty.
 *
 * @param source - Source port position
 * @param target - Target port position
 * @param sourcePosition - Which side the source port is on
 * @param targetPosition - Which side the target port is on
 * @param blocks - All blocks to avoid
 * @param sourceBounds - Optional: source block bounds (for proper exit point calculation)
 * @param targetBounds - Optional: target block bounds (for proper approach point calculation)
 * @returns Array of segments forming the path
 */
export function findOrthogonalPath(
  source: Point,
  target: Point,
  sourcePosition: Position,
  targetPosition: Position,
  blocks: BlockBounds[],
  sourceBounds?: BlockBounds,
  targetBounds?: BlockBounds
): Segment[] {
  const sourceOrientation = isHorizontalPosition(sourcePosition) ? "horizontal" : "vertical";
  const targetOrientation = isHorizontalPosition(targetPosition) ? "horizontal" : "vertical";

  // Generate route nodes including source, target, and grid coordinates
  // Exit and approach point coordinates are included in the grid generation
  const nodes = generateRouteNodesWithSourceTarget(
    source,
    target,
    sourcePosition,
    targetPosition,
    blocks,
    sourceBounds,
    targetBounds
  );

  if (nodes.length < 2) {
    return [];
  }

  // Find source and target nodes
  const sourceNode = nodes.find((n) => n.type === "source");
  const targetNode = nodes.find((n) => n.type === "target");

  if (!sourceNode || !targetNode) {
    return [];
  }

  // Build visibility graph with directional constraints for source/target
  const graph = buildVisibilityGraphWithConstraints(
    nodes,
    blocks,
    sourceNode,
    targetNode,
    sourcePosition,
    targetPosition
  );

  // Find shortest path with turn minimization
  const path = dijkstraWithTurns(
    graph,
    sourceNode,
    targetNode,
    TURN_PENALTY,
    sourceOrientation,
    targetOrientation
  );

  if (path.length === 0) {
    return [];
  }

  // Convert path to segments
  const segments = pathToSegments(path);

  // Post-process: simplify path (merge collinear segments) and center Z-paths
  const simplified = simplifyPath(segments);
  const centered = centerZPath(simplified, blocks);

  return centered;
}

/**
 * Get exit point at the block's expanded edge (for proper clearing)
 * Ensures the exit point is at least PORT_OFFSET away from the source
 */
function getBlockExitPoint(source: Point, position: Position, bounds: BlockBounds): Point {
  const expanded = expandBounds(bounds, BLOCK_MARGIN);
  switch (position) {
    case Position.Right:
      // Use the further of: expanded block edge OR source + PORT_OFFSET
      return { x: Math.max(expanded.x + expanded.width, source.x + PORT_OFFSET), y: source.y };
    case Position.Left:
      // Use the closer of: expanded block edge OR source - PORT_OFFSET
      return { x: Math.min(expanded.x, source.x - PORT_OFFSET), y: source.y };
    case Position.Bottom:
      return { x: source.x, y: Math.max(expanded.y + expanded.height, source.y + PORT_OFFSET) };
    case Position.Top:
      return { x: source.x, y: Math.min(expanded.y, source.y - PORT_OFFSET) };
    default:
      return source;
  }
}

/**
 * Get approach point at the block's expanded edge (for proper clearing)
 * Ensures the approach point is at least PORT_OFFSET away from the target
 */
function getBlockApproachPoint(target: Point, position: Position, bounds: BlockBounds): Point {
  const expanded = expandBounds(bounds, BLOCK_MARGIN);
  switch (position) {
    case Position.Left:
      // Port faces left, approach from left: target.x - PORT_OFFSET
      return { x: Math.min(expanded.x, target.x - PORT_OFFSET), y: target.y };
    case Position.Right:
      // Port faces right, approach from right: target.x + PORT_OFFSET
      return { x: Math.max(expanded.x + expanded.width, target.x + PORT_OFFSET), y: target.y };
    case Position.Top:
      // Port faces up, approach from above: target.y - PORT_OFFSET
      return { x: target.x, y: Math.min(expanded.y, target.y - PORT_OFFSET) };
    case Position.Bottom:
      // Port faces down, approach from below: target.y + PORT_OFFSET
      return { x: target.x, y: Math.max(expanded.y + expanded.height, target.y + PORT_OFFSET) };
    default:
      return target;
  }
}

/**
 * Generate route nodes with source and target as actual endpoints.
 * Grid coordinates are based on block corners to allow proper routing.
 */
function generateRouteNodesWithSourceTarget(
  source: Point,
  target: Point,
  sourcePosition: Position,
  targetPosition: Position,
  blocks: BlockBounds[],
  sourceBounds?: BlockBounds,
  targetBounds?: BlockBounds
): RouteNode[] {
  // Collect all unique X and Y coordinates for the grid
  const xCoords = new Set<number>();
  const yCoords = new Set<number>();

  // Add source and target coordinates
  xCoords.add(source.x);
  yCoords.add(source.y);
  xCoords.add(target.x);
  yCoords.add(target.y);

  // Add midpoint coordinates for centered routing (bias toward symmetric Z-paths)
  const midX = (source.x + target.x) / 2;
  const midY = (source.y + target.y) / 2;
  xCoords.add(midX);
  yCoords.add(midY);

  // Add exit and approach point coordinates
  // This ensures the grid has points where the path can exit/approach properly
  const sourceExt = getExitPoint(source, sourcePosition);
  const targetExt = getApproachPoint(target, targetPosition);
  xCoords.add(sourceExt.x);
  yCoords.add(sourceExt.y);
  xCoords.add(targetExt.x);
  yCoords.add(targetExt.y);

  // Add block-based exit/approach coordinates if bounds provided
  // These are at the expanded block edge OR PORT_OFFSET (whichever is further)
  // This ensures paths clear blocks while respecting PORT_OFFSET minimum
  if (sourceBounds) {
    const blockExit = getBlockExitPoint(source, sourcePosition, sourceBounds);
    xCoords.add(blockExit.x);
    yCoords.add(blockExit.y);
  }
  if (targetBounds) {
    const blockApproach = getBlockApproachPoint(target, targetPosition, targetBounds);
    xCoords.add(blockApproach.x);
    yCoords.add(blockApproach.y);
  }

  // Add block corner coordinates (with margin) for routing around blocks
  for (const block of blocks) {
    const expanded = expandBounds(block, BLOCK_MARGIN);
    xCoords.add(expanded.x);
    xCoords.add(expanded.x + expanded.width);
    yCoords.add(expanded.y);
    yCoords.add(expanded.y + expanded.height);
  }

  // Generate nodes at all grid intersections
  const nodes: RouteNode[] = [];
  let nodeId = 0;

  const xArray = Array.from(xCoords);
  const yArray = Array.from(yCoords);

  for (const x of xArray) {
    for (const y of yArray) {
      // Determine node type
      let type: "source" | "target" | "corner" = "corner";
      if (x === source.x && y === source.y) {
        type = "source";
      } else if (x === target.x && y === target.y) {
        type = "target";
      }

      nodes.push({
        id: `node_${nodeId++}`,
        point: { x, y },
        type,
      });
    }
  }

  return nodes;
}

/**
 * Build visibility graph with directional constraints for source and target.
 * - Source can only connect to edges going in the exit direction
 * - Target can only be reached from edges coming from the approach direction
 */
function buildVisibilityGraphWithConstraints(
  nodes: RouteNode[],
  blocks: BlockBounds[],
  sourceNode: RouteNode,
  targetNode: RouteNode,
  sourcePosition: Position,
  targetPosition: Position
): Map<string, RouteEdge[]> {
  const graph = new Map<string, RouteEdge[]>();

  // Identify which blocks contain source and target (these can be traversed by edges from/to source/target)
  const sourceBlockIndex = blocks.findIndex((b) => pointInsideBlock(sourceNode.point, b));
  const targetBlockIndex = blocks.findIndex((b) => pointInsideBlock(targetNode.point, b));

  // Initialize adjacency list for each node
  for (const node of nodes) {
    graph.set(node.id, []);
  }

  // Check all pairs of nodes
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i];
      const b = nodes[j];

      // Only consider orthogonal connections (same X or same Y)
      const isHorizontal = a.point.y === b.point.y;
      const isVertical = a.point.x === b.point.x;

      if (!isHorizontal && !isVertical) {
        continue;
      }

      const distance = Math.abs(a.point.x - b.point.x) + Math.abs(a.point.y - b.point.y);
      const orientation: SegmentOrientation = isHorizontal ? "horizontal" : "vertical";

      // Check directional constraints for source (direction + minimum distance)
      // This ensures the first segment is at least PORT_OFFSET long
      const canExitFromA =
        a.id !== sourceNode.id ||
        (isValidExitDirection(a.point, b.point, sourcePosition) &&
          meetsMinimumExitDistance(a.point, b.point, sourcePosition, PORT_OFFSET));
      const canExitFromB =
        b.id !== sourceNode.id ||
        (isValidExitDirection(b.point, a.point, sourcePosition) &&
          meetsMinimumExitDistance(b.point, a.point, sourcePosition, PORT_OFFSET));

      // Check directional constraints for target (direction + minimum distance)
      // This ensures the last segment is at least PORT_OFFSET long
      const canEnterA =
        a.id !== targetNode.id ||
        (isValidApproachDirection(b.point, a.point, targetPosition) &&
          meetsMinimumApproachDistance(b.point, a.point, targetPosition, PORT_OFFSET));
      const canEnterB =
        b.id !== targetNode.id ||
        (isValidApproachDirection(a.point, b.point, targetPosition) &&
          meetsMinimumApproachDistance(a.point, b.point, targetPosition, PORT_OFFSET));

      // For edges from source, exclude source's block from collision check
      // For edges to target, exclude target's block from collision check
      const isFromSource = a.id === sourceNode.id || b.id === sourceNode.id;
      const isToTarget = a.id === targetNode.id || b.id === targetNode.id;

      const blocksToCheck = blocks.filter((_, idx) => {
        if (isFromSource && idx === sourceBlockIndex) return false;
        if (isToTarget && idx === targetBlockIndex) return false;
        return true;
      });

      // Check if segment crosses any remaining block
      if (segmentCrossesAnyBlock(a.point, b.point, blocksToCheck)) {
        continue;
      }

      // Add edge A→B if valid
      if (canExitFromA && canEnterB) {
        graph.get(a.id)!.push({ to: b, distance, orientation });
      }

      // Add edge B→A if valid
      if (canExitFromB && canEnterA) {
        graph.get(b.id)!.push({ to: a, distance, orientation });
      }
    }
  }

  return graph;
}

/**
 * Check if a point is inside a block (including on the boundary)
 */
function pointInsideBlock(point: Point, block: BlockBounds): boolean {
  return (
    point.x >= block.x &&
    point.x <= block.x + block.width &&
    point.y >= block.y &&
    point.y <= block.y + block.height
  );
}

/**
 * Check if moving from 'from' to 'to' is a valid exit direction for a port.
 * E.g., a Right port can only exit by moving to the right (increasing X).
 */
function isValidExitDirection(from: Point, to: Point, position: Position): boolean {
  switch (position) {
    case Position.Right:
      return to.x > from.x; // Must go right
    case Position.Left:
      return to.x < from.x; // Must go left
    case Position.Bottom:
      return to.y > from.y; // Must go down
    case Position.Top:
      return to.y < from.y; // Must go up
    default:
      return true;
  }
}

/**
 * Check if the distance from 'from' to 'to' meets the minimum offset requirement.
 * Only checks distance in the direction of movement (horizontal or vertical).
 * For EXIT (source) positions - measures distance in exit direction.
 */
function meetsMinimumExitDistance(
  from: Point,
  to: Point,
  position: Position,
  minDistance: number
): boolean {
  switch (position) {
    case Position.Right:
      return to.x - from.x >= minDistance;
    case Position.Left:
      return from.x - to.x >= minDistance;
    case Position.Bottom:
      return to.y - from.y >= minDistance;
    case Position.Top:
      return from.y - to.y >= minDistance;
    default:
      return true;
  }
}

/**
 * Check if the distance from 'from' to 'to' meets the minimum offset requirement.
 * For APPROACH (target) positions - measures distance in approach direction.
 * Follows same convention as isValidApproachDirection:
 * - Position.Left: approach from left (from.x < to.x), distance = to.x - from.x
 * - Position.Right: approach from right (from.x > to.x), distance = from.x - to.x
 * - Position.Top: approach from above (from.y < to.y), distance = to.y - from.y
 * - Position.Bottom: approach from below (from.y > to.y), distance = from.y - to.y
 */
function meetsMinimumApproachDistance(
  from: Point,
  to: Point,
  position: Position,
  minDistance: number
): boolean {
  switch (position) {
    case Position.Left:
      return to.x - from.x >= minDistance; // Approach from left
    case Position.Right:
      return from.x - to.x >= minDistance; // Approach from right
    case Position.Top:
      return to.y - from.y >= minDistance; // Approach from above
    case Position.Bottom:
      return from.y - to.y >= minDistance; // Approach from below
    default:
      return true;
  }
}

/**
 * Check if moving from 'from' to 'to' is a valid approach direction for a port.
 * E.g., a Left port must be approached from the left (segment going right into it).
 */
function isValidApproachDirection(from: Point, to: Point, position: Position): boolean {
  switch (position) {
    case Position.Left:
      return from.x < to.x; // Must approach from left (from.x < to.x)
    case Position.Right:
      return from.x > to.x; // Must approach from right
    case Position.Top:
      return from.y < to.y; // Must approach from above
    case Position.Bottom:
      return from.y > to.y; // Must approach from below
    default:
      return true;
  }
}

/**
 * Expand bounds by a margin on all sides
 */
function expandBounds(bounds: BlockBounds, margin: number): BlockBounds {
  return {
    x: bounds.x - margin,
    y: bounds.y - margin,
    width: bounds.width + 2 * margin,
    height: bounds.height + 2 * margin,
  };
}

/**
 * Get the edges of a bounds box
 */
function getBoundsEdges(bounds: BlockBounds) {
  return {
    left: bounds.x,
    right: bounds.x + bounds.width,
    top: bounds.y,
    bottom: bounds.y + bounds.height,
  };
}

/**
 * Check if two bounds boxes overlap
 */
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
function boundsOverlap(a: BlockBounds, b: BlockBounds): boolean {
  const aEdges = getBoundsEdges(a);
  const bEdges = getBoundsEdges(b);
  return !(
    aEdges.right < bEdges.left ||
    aEdges.left > bEdges.right ||
    aEdges.bottom < bEdges.top ||
    aEdges.top > bEdges.bottom
  );
}

/**
 * Check if a point is inside a bounds box (using edges)
 */
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
function isPointInsideBounds(
  point: Point,
  edges: { left: number; right: number; top: number; bottom: number }
): boolean {
  return (
    point.x > edges.left && point.x < edges.right && point.y > edges.top && point.y < edges.bottom
  );
}

/**
 * Filter out zero-length segments (where from and to are the same point)
 */
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
function filterZeroLengthSegments(segments: Segment[]): Segment[] {
  return segments.filter((seg) => seg.from.x !== seg.to.x || seg.from.y !== seg.to.y);
}

/**
 * Create orthogonal segments between two points using H-V or V-H routing.
 *
 * Uses a simple 2-segment approach:
 * - If horizontal distance > vertical distance: go horizontal first, then vertical
 * - Otherwise: go vertical first, then horizontal
 *
 * @param from - Starting point
 * @param to - Ending point
 * @returns Array of segments connecting the points
 */
export function createOrthogonalSegments(from: Point, to: Point): Segment[] {
  const dx = to.x - from.x;
  const dy = to.y - from.y;

  // Handle same point - no segments needed
  if (dx === 0 && dy === 0) {
    return [];
  }

  // Horizontally aligned - single horizontal segment
  if (dy === 0) {
    return [{ from, to, orientation: "horizontal" }];
  }

  // Vertically aligned - single vertical segment
  if (dx === 0) {
    return [{ from, to, orientation: "vertical" }];
  }

  // Need two segments
  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);

  if (absDx > absDy) {
    // Horizontal first, then vertical
    const mid: Point = { x: to.x, y: from.y };
    return [
      { from, to: mid, orientation: "horizontal" },
      { from: mid, to, orientation: "vertical" },
    ];
  } else {
    // Vertical first, then horizontal
    const mid: Point = { x: from.x, y: to.y };
    return [
      { from, to: mid, orientation: "vertical" },
      { from: mid, to, orientation: "horizontal" },
    ];
  }
}

/**
 * Check if a position is horizontal (Left or Right)
 */
function isHorizontalPosition(position: Position): boolean {
  return position === Position.Left || position === Position.Right;
}

/**
 * Get extension point away from port in the direction the port faces
 */
function getExtensionPoint(point: Point, position: Position, offset: number): Point {
  switch (position) {
    case Position.Right:
      return { x: point.x + offset, y: point.y };
    case Position.Left:
      return { x: point.x - offset, y: point.y };
    case Position.Top:
      return { x: point.x, y: point.y - offset };
    case Position.Bottom:
      return { x: point.x, y: point.y + offset };
    default:
      return point;
  }
}

/**
 * Calculate orthogonal path from source to target, routing through waypoints.
 *
 * Creates a connected path: source -> waypoint[0] -> waypoint[1] -> ... -> target
 * When port positions are provided, ensures perpendicular connections at both ends.
 * When block bounds are provided, routes around all blocks in the diagram.
 *
 * @param source - Starting point (output port position)
 * @param target - Ending point (input port position)
 * @param waypoints - Ordered list of intermediate points to route through
 * @param sourcePosition - Optional: which side the source port is on
 * @param targetPosition - Optional: which side the target port is on
 * @param sourceBounds - Optional: source block bounding box for exit point calculation
 * @param targetBounds - Optional: target block bounding box for approach point calculation
 * @param allBlocks - Optional: all blocks in the diagram for collision avoidance
 * @returns Array of segments forming the complete path
 */
export function calculateOrthogonalPath(
  source: Point,
  target: Point,
  waypoints: Waypoint[],
  sourcePosition?: Position,
  targetPosition?: Position,
  sourceBounds?: BlockBounds,
  targetBounds?: BlockBounds,
  allBlocks?: BlockBounds[]
): Segment[] {
  console.log("[calculateOrthogonalPath] Called with:", {
    source,
    target,
    waypoints,
    sourcePosition,
    targetPosition,
  });

  // If no waypoints and positions provided, use visibility graph routing
  if (waypoints.length === 0 && sourcePosition && targetPosition) {
    return findOrthogonalPath(
      source,
      target,
      sourcePosition,
      targetPosition,
      allBlocks || [],
      sourceBounds,
      targetBounds
    );
  }

  // With waypoints, use position-aware routing for first and last legs
  if (waypoints.length > 0 && sourcePosition && targetPosition) {
    const allSegments: Segment[] = [];

    // First leg: source to first waypoint (perpendicular to source port)
    const firstWaypoint = waypoints[0];
    const sourceExt = getExtensionPoint(source, sourcePosition, PORT_OFFSET);
    const sourceOrientation = isHorizontalPosition(sourcePosition) ? "horizontal" : "vertical";

    console.log("[calculateOrthogonalPath] First leg routing:", {
      source,
      sourceExt,
      firstWaypoint,
      sourceOrientation,
    });

    // Add perpendicular exit from source
    if (source.x !== sourceExt.x || source.y !== sourceExt.y) {
      const exitSegment = { from: source, to: sourceExt, orientation: sourceOrientation };
      console.log("[calculateOrthogonalPath] Adding source exit segment:", exitSegment);
      allSegments.push(exitSegment);
    }

    // Connect to first waypoint
    const toFirstWaypoint = createOrthogonalSegments(sourceExt, firstWaypoint);
    console.log(
      "[calculateOrthogonalPath] Segments from sourceExt to firstWaypoint:",
      toFirstWaypoint
    );
    allSegments.push(...toFirstWaypoint);

    // Middle legs: between waypoints
    for (let i = 0; i < waypoints.length - 1; i++) {
      const segments = createOrthogonalSegments(waypoints[i], waypoints[i + 1]);
      allSegments.push(...segments);
    }

    // Last leg: last waypoint to target (perpendicular to target port)
    const lastWaypoint = waypoints[waypoints.length - 1];
    const targetExt = getExtensionPoint(target, targetPosition, PORT_OFFSET);
    const targetOrientation = isHorizontalPosition(targetPosition) ? "horizontal" : "vertical";

    console.log("[calculateOrthogonalPath] Last leg routing:", {
      lastWaypoint,
      targetExt,
      target,
      targetOrientation,
    });

    // Connect from last waypoint to target approach point
    const toTargetExt = createOrthogonalSegments(lastWaypoint, targetExt);
    console.log("[calculateOrthogonalPath] Segments from lastWaypoint to targetExt:", toTargetExt);
    allSegments.push(...toTargetExt);

    // Add perpendicular entry to target
    if (targetExt.x !== target.x || targetExt.y !== target.y) {
      const entrySegment = { from: targetExt, to: target, orientation: targetOrientation };
      console.log("[calculateOrthogonalPath] Adding target entry segment:", entrySegment);
      allSegments.push(entrySegment);
    }

    console.log("[calculateOrthogonalPath] Final segments array:", allSegments);
    return allSegments;
  }

  // Fallback: Build list of all points in order and use simple routing
  const points: Point[] = [source, ...waypoints, target];

  // Generate segments between each consecutive pair of points
  const allSegments: Segment[] = [];

  for (let i = 0; i < points.length - 1; i++) {
    const from = points[i];
    const to = points[i + 1];
    const segments = createOrthogonalSegments(from, to);
    allSegments.push(...segments);
  }

  return allSegments;
}

/**
 * Extract waypoints from segments.
 *
 * Waypoints are the intermediate corner points where segments meet,
 * excluding the source (first segment start) and target (last segment end).
 *
 * @param segments - Array of segments from the path
 * @returns Array of waypoints (corner points)
 */
export function extractWaypointsFromSegments(segments: Segment[]): Waypoint[] {
  if (segments.length <= 1) {
    console.log("[extractWaypointsFromSegments] Too few segments, returning empty");
    return [];
  }

  // Waypoints are the "to" points of all segments except the last one
  // (which ends at the target)
  const waypoints: Waypoint[] = [];
  for (let i = 0; i < segments.length - 1; i++) {
    waypoints.push({ x: segments[i].to.x, y: segments[i].to.y });
  }

  console.log("[extractWaypointsFromSegments] Extracted waypoints from segments:", {
    inputSegments: segments,
    extractedWaypoints: waypoints,
  });

  return waypoints;
}

/**
 * Convert segments to an SVG path string.
 *
 * Generates a path using M (moveto) and L (lineto) commands.
 *
 * @param segments - Array of segments to convert
 * @returns SVG path string (e.g., "M 100 100 L 200 100 L 200 200")
 */
export function segmentsToSVGPath(segments: Segment[]): string {
  if (segments.length === 0) {
    return "";
  }

  // Start with moveto for first segment's start
  const parts: string[] = [`M ${segments[0].from.x} ${segments[0].from.y}`];

  // Add lineto for each segment's end
  for (const segment of segments) {
    parts.push(`L ${segment.to.x} ${segment.to.y}`);
  }

  return parts.join(" ");
}

/**
 * Rectangle bounds for hit detection
 */
export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Convert a segment to a rectangle for hit detection.
 *
 * Creates a rect that overlays the segment with the specified width
 * (for horizontal segments, height is handleWidth; for vertical, width is handleWidth).
 *
 * @param segment - The segment to convert
 * @param handleWidth - Width of the clickable/draggable area
 * @returns Rectangle bounds
 */
export function segmentToRect(segment: Segment, handleWidth: number): Rect {
  const minX = Math.min(segment.from.x, segment.to.x);
  const maxX = Math.max(segment.from.x, segment.to.x);
  const minY = Math.min(segment.from.y, segment.to.y);
  const maxY = Math.max(segment.from.y, segment.to.y);

  if (segment.orientation === "horizontal") {
    return {
      x: minX,
      y: minY - handleWidth / 2,
      width: maxX - minX,
      height: handleWidth,
    };
  } else {
    return {
      x: minX - handleWidth / 2,
      y: minY,
      width: handleWidth,
      height: maxY - minY,
    };
  }
}

/**
 * Constrain a drag delta to the axis perpendicular to the segment.
 *
 * - Horizontal segments can only be moved vertically (x delta = 0)
 * - Vertical segments can only be moved horizontally (y delta = 0)
 *
 * @param segment - The segment being dragged
 * @param dragDelta - The raw drag delta from mouse movement
 * @returns Constrained delta
 */
export function constrainDragToAxis(segment: Segment, dragDelta: Point): Point {
  if (segment.orientation === "horizontal") {
    // Horizontal segment moves vertically
    return { x: 0, y: dragDelta.y };
  } else {
    // Vertical segment moves horizontally
    return { x: dragDelta.x, y: 0 };
  }
}

/**
 * Update waypoints based on dragging a segment to a new position.
 *
 * This is the core logic for creating/updating waypoints when the user
 * drags a segment. Uses the segment's actual rendered coordinates as the
 * source of truth (no recalculation needed).
 *
 * @param source - Source point (output port) - kept for signature compatibility
 * @param target - Target point (input port) - kept for signature compatibility
 * @param currentWaypoints - Current waypoints (may be empty)
 * @param draggedSegment - The segment being dragged (from rendered segments array)
 * @param newPosition - The new position (only perpendicular axis matters)
 * @param sourcePosition - Optional: kept for signature compatibility
 * @param targetPosition - Optional: kept for signature compatibility
 * @returns Updated waypoints array
 */
export function updateWaypointsFromDrag(
  source: Point,
  target: Point,
  currentWaypoints: Waypoint[],
  draggedSegment: Segment,
  newPosition: Point,
  sourcePosition?: Position,
  targetPosition?: Position
): Waypoint[] {
  console.log("[updateWaypointsFromDrag] Called with:", {
    source,
    target,
    currentWaypoints,
    draggedSegment,
    newPosition,
    sourcePosition,
    targetPosition,
  });

  // ============================================================================
  // Calculate Extension Points
  // ============================================================================
  const sourceExt = sourcePosition
    ? getExtensionPoint(source, sourcePosition, PORT_OFFSET)
    : source;
  const targetExt = targetPosition
    ? getExtensionPoint(target, targetPosition, PORT_OFFSET)
    : target;

  // Helper to compare points with tolerance
  const pointsEqual = (p1: Point, p2: Point, tolerance = 1) => {
    return Math.abs(p1.x - p2.x) < tolerance && Math.abs(p1.y - p2.y) < tolerance;
  };

  // ============================================================================
  // Find Position of Dragged Segment in Waypoints Array
  // ============================================================================
  // The segment endpoints can be:
  // - sourceExt, waypoint[i], targetExt (not in waypoints array)
  // - Existing waypoints in the array

  const fromWpIndex = currentWaypoints.findIndex((wp) => pointsEqual(wp, draggedSegment.from));
  const toWpIndex = currentWaypoints.findIndex((wp) => pointsEqual(wp, draggedSegment.to));
  const fromIsSourceExt = pointsEqual(draggedSegment.from, sourceExt);
  const toIsTargetExt = pointsEqual(draggedSegment.to, targetExt);

  console.log("[updateWaypointsFromDrag] Segment position analysis:", {
    fromWpIndex,
    toWpIndex,
    fromIsSourceExt,
    toIsTargetExt,
    sourceExt,
    targetExt,
  });

  // ============================================================================
  // Adjust Segment Endpoints for PORT_OFFSET
  // ============================================================================
  // Auto-routed segments have endpoints at raw port positions (source/target)
  // We need to use sourceExt/targetExt instead for correct waypoint placement
  let adjustedFrom = draggedSegment.from;
  let adjustedTo = draggedSegment.to;

  if (pointsEqual(draggedSegment.from, source)) {
    adjustedFrom = sourceExt;
    console.log("[updateWaypointsFromDrag] Adjusted segment start from source to sourceExt");
  }
  if (pointsEqual(draggedSegment.to, target)) {
    adjustedTo = targetExt;
    console.log("[updateWaypointsFromDrag] Adjusted segment end from target to targetExt");
  }

  // ============================================================================
  // Create New Bend Waypoints
  // ============================================================================
  // When dragging a segment, we insert waypoints to create a perpendicular bend
  let newBendWaypoints: Waypoint[];
  if (draggedSegment.orientation === "horizontal") {
    newBendWaypoints = [
      { x: adjustedFrom.x, y: newPosition.y },
      { x: adjustedTo.x, y: newPosition.y },
    ];
  } else {
    newBendWaypoints = [
      { x: newPosition.x, y: adjustedFrom.y },
      { x: newPosition.x, y: adjustedTo.y },
    ];
  }

  console.log("[updateWaypointsFromDrag] New bend waypoints:", newBendWaypoints);

  // ============================================================================
  // Insert New Waypoints at Correct Position
  // ============================================================================

  // Case 1: Segment connects two existing waypoints (fromWpIndex and toWpIndex)
  if (fromWpIndex >= 0 && toWpIndex >= 0 && toWpIndex > fromWpIndex) {
    // Replace the waypoints at fromWpIndex and toWpIndex with new bend waypoints
    const result = [...currentWaypoints];
    result.splice(fromWpIndex, toWpIndex - fromWpIndex + 1, ...newBendWaypoints);
    console.log("[updateWaypointsFromDrag] Case 1: Between waypoints", {
      fromWpIndex,
      toWpIndex,
      result,
    });
    return result;
  }

  // Case 2: Segment connects sourceExt to first waypoint
  if (fromIsSourceExt && currentWaypoints.length > 0) {
    // Insert new waypoints before the first waypoint
    const result = [...newBendWaypoints, ...currentWaypoints.slice(1)];
    console.log("[updateWaypointsFromDrag] Case 2: SourceExt to first waypoint", result);
    return result;
  }

  // Case 3: Segment connects a waypoint to targetExt
  if (toIsTargetExt && fromWpIndex >= 0) {
    // Insert new waypoints after the waypoint
    const result = [...currentWaypoints];
    result.splice(fromWpIndex + 1, 0, ...newBendWaypoints);
    console.log("[updateWaypointsFromDrag] Case 3: Waypoint to targetExt", { fromWpIndex, result });
    return result;
  }

  // Case 4: Segment connects sourceExt to targetExt (no existing waypoints, or first drag)
  if ((fromIsSourceExt && toIsTargetExt) || currentWaypoints.length === 0) {
    console.log(
      "[updateWaypointsFromDrag] Case 4: SourceExt to targetExt (no existing waypoints)",
      newBendWaypoints
    );
    return newBendWaypoints;
  }

  // Fallback: Return new waypoints (should not reach here in normal operation)
  console.warn("[updateWaypointsFromDrag] Fallback case - segment position not identified clearly");
  return newBendWaypoints;
}

/**
 * Simplify waypoints by aligning near-identical coordinates and removing collinear points.
 *
 * Two-step process:
 * 1. Align coordinates that are within tolerance (makes segments merge cleanly)
 * 2. Remove waypoints that are collinear with their neighbors
 *
 * @param waypoints - Array of waypoints to simplify
 * @param tolerance - Tolerance in pixels for alignment/collinearity (default 15)
 * @returns Simplified waypoints array
 */
export function simplifyWaypoints(waypoints: Waypoint[], tolerance: number = 15): Waypoint[] {
  if (waypoints.length <= 1) {
    return [...waypoints];
  }

  // Step 1: Align coordinates that are nearly the same
  // This helps segments "snap" together when close
  const aligned = waypoints.map((wp, i) => {
    if (i === 0) return { ...wp };

    const prev = waypoints[i - 1];
    return {
      // If X coords are close, align to previous X
      x: Math.abs(wp.x - prev.x) < tolerance ? prev.x : wp.x,
      // If Y coords are close, align to previous Y
      y: Math.abs(wp.y - prev.y) < tolerance ? prev.y : wp.y,
    };
  });

  // Step 2: Remove collinear points
  if (aligned.length <= 2) {
    return aligned;
  }

  const result: Waypoint[] = [aligned[0]];

  for (let i = 1; i < aligned.length - 1; i++) {
    const prev = aligned[i - 1];
    const curr = aligned[i];
    const next = aligned[i + 1];

    // Check if current point is collinear (on same horizontal or vertical line)
    const collinearH =
      Math.abs(prev.y - curr.y) < tolerance && Math.abs(curr.y - next.y) < tolerance;
    const collinearV =
      Math.abs(prev.x - curr.x) < tolerance && Math.abs(curr.x - next.x) < tolerance;

    if (!collinearH && !collinearV) {
      // Not collinear - keep this waypoint
      result.push(curr);
    }
  }

  // Always keep the last waypoint
  result.push(aligned[aligned.length - 1]);

  return result;
}
