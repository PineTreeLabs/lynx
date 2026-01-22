// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Collinear Snapping Utility
 *
 * Snaps blocks to create straight connections instead of grid alignment.
 * When a block is dropped, if any connected port is nearly aligned with its
 * paired port, the block snaps to create a perfectly straight connection.
 */

import type { Node, Edge } from "reactflow";

/** Default block dimensions (matches orthogonalRouting.ts defaults) */
const DEFAULT_WIDTH = 120;
const DEFAULT_HEIGHT = 80;

/** Known block dimensions by type */
const BLOCK_DIMENSIONS: Record<string, { width: number; height: number }> = {
  gain: { width: 120, height: 80 },
  transfer_function: { width: 120, height: 80 },
  state_space: { width: 120, height: 80 },
  sum: { width: 56, height: 56 },
  io_marker: { width: 100, height: 60 },
};

interface SnapCandidate {
  axis: "x" | "y";
  adjustment: number; // How much to move the block
  distance: number; // How far from perfect alignment (for sorting)
}

/**
 * Get the dimensions of a node, using known defaults or React Flow's measured values
 */
function getNodeDimensions(node: Node): { width: number; height: number } {
  // Prefer measured dimensions from React Flow
  if (node.width && node.height) {
    return { width: node.width, height: node.height };
  }
  // Fall back to known dimensions by type
  const typeDimensions = BLOCK_DIMENSIONS[node.type || ""];
  if (typeDimensions) {
    return typeDimensions;
  }
  // Default
  return { width: DEFAULT_WIDTH, height: DEFAULT_HEIGHT };
}

/**
 * Calculate the absolute canvas position of a port on a block.
 *
 * For most blocks, ports are centered vertically on left/right edges.
 * Sum blocks have ports on top/bottom as well.
 *
 * @param blockPosition - Block's top-left position
 * @param blockDimensions - Block's width and height
 * @param portId - Port identifier (e.g., "in", "out", "in1", "in2")
 * @param portType - "input" or "output"
 * @param blockType - Block type for special handling
 * @param isFlipped - Whether the block is horizontally flipped
 */
function getPortPosition(
  blockPosition: { x: number; y: number },
  blockDimensions: { width: number; height: number },
  portId: string,
  portType: "input" | "output",
  blockType: string,
  isFlipped: boolean
): { x: number; y: number } {
  const { width, height } = blockDimensions;
  const centerY = blockPosition.y + height / 2;

  // Sum block has special port positions (top, bottom inputs)
  if (blockType === "sum") {
    // Output is always on the right (or left if flipped)
    if (portType === "output") {
      return {
        x: isFlipped ? blockPosition.x : blockPosition.x + width,
        y: centerY,
      };
    }

    // For sum inputs, we need to determine position based on port id
    // Sum blocks can have ports on left (default input), top, or bottom
    // Port IDs are "in1", "in2", "in3" mapping to active quadrants
    // For simplicity, assume most inputs are on left/right edges (centered Y)
    // Top/bottom ports would have different Y positions but same X
    return {
      x: isFlipped ? blockPosition.x + width : blockPosition.x,
      y: centerY,
    };
  }

  // IO markers can have input OR output depending on configuration
  if (blockType === "io_marker") {
    // IO markers are circular, port is on the edge
    if (portType === "input") {
      return {
        x: isFlipped ? blockPosition.x + width : blockPosition.x,
        y: centerY,
      };
    } else {
      return {
        x: isFlipped ? blockPosition.x : blockPosition.x + width,
        y: centerY,
      };
    }
  }

  // Standard blocks (gain, transfer_function, state_space): input left, output right
  if (portType === "input") {
    return {
      x: isFlipped ? blockPosition.x + width : blockPosition.x,
      y: centerY,
    };
  } else {
    return {
      x: isFlipped ? blockPosition.x : blockPosition.x + width,
      y: centerY,
    };
  }
}

/**
 * Find the best collinear snap position for a dragged block.
 *
 * Examines all edges connected to the block and checks if any port
 * is nearly aligned (within threshold) with its connected port.
 * Returns the position that would create the straightest connection.
 *
 * @param draggedNodeId - ID of the block being dragged
 * @param currentPosition - Current position of the dragged block
 * @param nodes - All nodes in the diagram
 * @param edges - All edges in the diagram
 * @param threshold - Maximum distance to consider for snapping (default 20px)
 * @returns Snapped position (or original if no snap found)
 */
export function findCollinearSnap(
  draggedNodeId: string,
  currentPosition: { x: number; y: number },
  nodes: Node[],
  edges: Edge[],
  threshold: number = 20
): { x: number; y: number } {
  // Find the dragged node to get its dimensions and type
  const draggedNode = nodes.find((n) => n.id === draggedNodeId);
  if (!draggedNode) {
    return currentPosition;
  }

  const draggedDimensions = getNodeDimensions(draggedNode);
  const draggedType = draggedNode.type || "";
  const draggedFlipped = draggedNode.data?.flipped || false;

  // Find all edges connected to this node
  const connectedEdges = edges.filter(
    (e) => e.source === draggedNodeId || e.target === draggedNodeId
  );

  if (connectedEdges.length === 0) {
    return currentPosition;
  }

  const candidates: SnapCandidate[] = [];

  for (const edge of connectedEdges) {
    // Determine which end of the edge is the dragged node
    const isDraggedSource = edge.source === draggedNodeId;
    const otherNodeId = isDraggedSource ? edge.target : edge.source;

    // Find the other node
    const otherNode = nodes.find((n) => n.id === otherNodeId);
    if (!otherNode) continue;

    const otherDimensions = getNodeDimensions(otherNode);
    const otherType = otherNode.type || "";
    const otherFlipped = otherNode.data?.flipped || false;

    // Determine port types and IDs
    const draggedPortId = isDraggedSource ? edge.sourceHandle || "out" : edge.targetHandle || "in";
    const otherPortId = isDraggedSource ? edge.targetHandle || "in" : edge.sourceHandle || "out";

    // Port types: source is output, target is input
    const draggedPortType: "input" | "output" = isDraggedSource ? "output" : "input";
    const otherPortType: "input" | "output" = isDraggedSource ? "input" : "output";

    // Calculate port positions
    const draggedPortPos = getPortPosition(
      currentPosition,
      draggedDimensions,
      draggedPortId,
      draggedPortType,
      draggedType,
      draggedFlipped
    );

    const otherPortPos = getPortPosition(
      otherNode.position,
      otherDimensions,
      otherPortId,
      otherPortType,
      otherType,
      otherFlipped
    );

    // Check horizontal alignment (same Y = straight horizontal line)
    const yDiff = Math.abs(draggedPortPos.y - otherPortPos.y);
    if (yDiff < threshold && yDiff > 0) {
      candidates.push({
        axis: "y",
        adjustment: otherPortPos.y - draggedPortPos.y,
        distance: yDiff,
      });
    }

    // Check vertical alignment (same X = straight vertical line)
    const xDiff = Math.abs(draggedPortPos.x - otherPortPos.x);
    if (xDiff < threshold && xDiff > 0) {
      candidates.push({
        axis: "x",
        adjustment: otherPortPos.x - draggedPortPos.x,
        distance: xDiff,
      });
    }
  }

  if (candidates.length === 0) {
    return currentPosition;
  }

  // Sort by distance (nearest alignment wins)
  candidates.sort((a, b) => a.distance - b.distance);
  const bestSnap = candidates[0];

  // Apply the snap
  return {
    x: bestSnap.axis === "x" ? currentPosition.x + bestSnap.adjustment : currentPosition.x,
    y: bestSnap.axis === "y" ? currentPosition.y + bestSnap.adjustment : currentPosition.y,
  };
}
