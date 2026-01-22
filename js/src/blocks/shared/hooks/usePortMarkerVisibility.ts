// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Port marker visibility hook.
 *
 * Determines if a port is connected by querying React Flow's edges array.
 */

import { useEdges, type Edge } from "reactflow";

/**
 * Core logic: Check if a specific port is connected to any edge.
 * Exported for testing purposes.
 *
 * @param blockId - Block identifier (React Flow node ID)
 * @param portId - Port identifier ("in", "out", "in1", etc.)
 * @param edges - Array of React Flow edges
 * @returns true if port is connected, false otherwise
 */
export function isPortConnected(blockId: string, portId: string, edges: Edge[]): boolean {
  // Check if any edge connects to this specific port
  return edges.some(
    (edge) =>
      (edge.source === blockId && edge.sourceHandle === portId) ||
      (edge.target === blockId && edge.targetHandle === portId)
  );
}

/**
 * React hook: Check if a specific port is connected to any edge.
 *
 * @param blockId - Block identifier (React Flow node ID)
 * @param portId - Port identifier ("in", "out", "in1", etc.)
 * @returns true if port is connected, false otherwise
 */
export function usePortConnected(blockId: string, portId: string): boolean {
  const edges = useEdges();
  return isPortConnected(blockId, portId, edges);
}
