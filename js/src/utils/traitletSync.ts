// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Traitlet synchronization utilities
 *
 * Helpers for syncing state between Python (anywidget model) and React
 */

import type { AnyModel } from "@anywidget/types";
import type { BlockType } from "../config/constants";

/**
 * Diagram state from Python (read-only in frontend)
 */
export interface DiagramState {
  version: string;
  blocks: Block[];
  connections: Connection[];
}

export interface Block {
  id: string;
  type: BlockType;
  position: { x: number; y: number };
  parameters: Parameter[];
  ports: Port[];
  label?: string;
  flipped?: boolean;
  custom_latex?: string;
  label_visible?: boolean;
  width?: number;
  height?: number;
}

export interface Parameter {
  name: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  value: any; // Can be any JSON-serializable type from Python
  expression?: string;
}

export interface Port {
  id: string;
  type: "input" | "output";
  label?: string;
}

/**
 * Waypoint for custom connection routing (absolute canvas coordinates)
 */
export interface Waypoint {
  x: number;
  y: number;
}

export interface Connection {
  id: string;
  source_block_id: string;
  source_port_id: string;
  target_block_id: string;
  target_port_id: string;
  waypoints?: Waypoint[];
  label?: string;
  label_visible?: boolean;
}

/**
 * Edge data passed to OrthogonalEditableEdge component
 */
export interface OrthogonalEdgeData {
  waypoints?: Waypoint[];
  label?: string;
  label_visible?: boolean;
}

/**
 * Action payload sent to Python
 */
export interface Action {
  type: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  payload: any; // Can be any JSON-serializable data from actions
  timestamp: number;
}

/**
 * Send action to Python backend via anywidget traitlet synchronization.
 *
 * Actions are sent through the `_action` traitlet with a timestamp for deduplication.
 * Python's `_on_action` handler processes these actions and updates the diagram state.
 *
 * @param model - anywidget model instance (provides set/save_changes methods)
 * @param type - Action type string (e.g., "addBlock", "deleteBlock", "updateParameter")
 * @param payload - Action-specific data (e.g., { blockId: "g1", position: { x: 100, y: 200 } })
 *
 * @example
 * ```ts
 * sendAction(model, "addBlock", {
 *   blockType: "gain",
 *   id: "g1",
 *   position: { x: 100, y: 200 },
 *   K: 1.0
 * });
 * ```
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function sendAction(model: AnyModel, type: string, payload: any): void {
  const action: Action = {
    type,
    payload,
    timestamp: Date.now(),
  };

  // Logging will be added in Phase 2.2
  model.set("_action", action);
  model.save_changes();
}

/**
 * Retrieve current diagram state from Python via anywidget model.
 *
 * Reads the `diagram_state` traitlet which contains blocks and connections.
 * Returns empty diagram if state not yet initialized.
 *
 * @param model - anywidget model instance
 * @returns Current diagram state with blocks, connections, and version
 *
 * @example
 * ```ts
 * const state = getDiagramState(model);
 * console.log(`Diagram has ${state.blocks.length} blocks`);
 * ```
 */
export function getDiagramState(model: AnyModel): DiagramState {
  return model.get("diagram_state") || { version: "1.0.0", blocks: [], connections: [] };
}

/**
 * Subscribe to diagram state changes from Python.
 *
 * Sets up an event listener on the `diagram_state` traitlet that fires whenever
 * Python updates the diagram (after add/delete/undo operations, etc.).
 *
 * Returns cleanup function to unsubscribe - MUST be called on component unmount
 * to prevent memory leaks.
 *
 * @param model - anywidget model instance
 * @param callback - Function called with new state on each change
 * @returns Cleanup function to remove event listener
 *
 * @example
 * ```ts
 * useEffect(() => {
 *   const unsubscribe = onDiagramStateChange(model, (state) => {
 *     setNodes(state.blocks.map(blockToNode));
 *     setEdges(state.connections.map(connectionToEdge));
 *   });
 *   return unsubscribe; // Cleanup on unmount
 * }, [model]);
 * ```
 */
export function onDiagramStateChange(
  model: AnyModel,
  callback: (state: DiagramState) => void
): () => void {
  const handler = () => {
    callback(getDiagramState(model));
  };

  model.on("change:diagram_state", handler);

  // Return cleanup function
  return () => {
    model.off("change:diagram_state", handler);
  };
}
