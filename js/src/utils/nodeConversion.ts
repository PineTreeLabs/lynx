// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Shared node/edge conversion utilities
 *
 * Ensures identical conversion between DiagramCanvas and CaptureCanvas
 */

import type { Node, Edge } from "reactflow";
import type { Block as DiagramBlock, Connection as DiagramConnection } from "./traitletSync";

/**
 * Convert backend block to React Flow node
 *
 * Matches DiagramCanvas's original implementation.
 * Width/height are stored in data for component rendering.
 *
 * @param block - Backend block from Python
 * @returns React Flow node
 */
export function blockToNode(block: DiagramBlock): Node {
  return {
    id: block.id,
    type: block.type,
    position: block.position,
    data: {
      parameters: block.parameters,
      ports: block.ports,
      label: block.label,
      flipped: block.flipped || false,
      custom_latex: block.custom_latex,
      label_visible: block.label_visible || false,
      width: block.width,
      height: block.height,
    },
  };
}

/**
 * Convert backend connection to React Flow edge
 *
 * @param conn - Backend connection from Python
 * @param markerColor - Color for edge stroke and marker
 * @returns React Flow edge
 */
export function connectionToEdge(conn: DiagramConnection, markerColor: string): Edge {
  return {
    id: conn.id,
    source: conn.source_block_id,
    sourceHandle: conn.source_port_id,
    target: conn.target_block_id,
    targetHandle: conn.target_port_id,
    type: "orthogonal",
    data: {
      waypoints: conn.waypoints || [],
      label: conn.label,
      label_visible: conn.label_visible || false,
    },
    style: { stroke: markerColor, strokeWidth: 2.5 },
    markerEnd: {
      type: "arrowclosed",
      width: 14,
      height: 14,
      color: markerColor,
    },
  };
}
