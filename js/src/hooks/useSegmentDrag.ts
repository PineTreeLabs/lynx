// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * useSegmentDrag - Hook for managing segment drag interactions
 *
 * Handles the state and logic for dragging connection segments to create/update waypoints.
 */

import { useState, useCallback, useRef } from "react";
import type { Segment, Point, Waypoint } from "../utils/orthogonalRouting";
import {
  constrainDragToAxis,
  updateWaypointsFromDrag,
  simplifyWaypoints,
} from "../utils/orthogonalRouting";

/**
 * State for an active drag operation
 */
export interface DragState {
  /** Index of the segment being dragged */
  segmentIndex: number;
  /** The segment being dragged */
  segment: Segment;
  /** Starting mouse position */
  startPosition: Point;
  /** Current mouse position */
  currentPosition: Point;
  /** Preview waypoints (not yet committed) */
  previewWaypoints: Waypoint[];
}

/**
 * Return value from useSegmentDrag hook
 */
export interface UseSegmentDragResult {
  /** Current drag state (null if not dragging) */
  dragState: DragState | null;
  /** Whether a drag is in progress */
  isDragging: boolean;
  /** Start dragging a segment */
  startDrag: (
    segmentIndex: number,
    segment: Segment,
    startPosition: Point,
    source: Point,
    target: Point,
    currentWaypoints: Waypoint[]
  ) => void;
  /** Update drag position */
  updateDrag: (currentPosition: Point, source: Point, target: Point) => void;
  /** End drag and return final waypoints */
  endDrag: (gridSize?: number) => Waypoint[];
  /** Cancel drag without committing */
  cancelDrag: () => void;
}

/**
 * Hook for managing segment drag state and logic.
 *
 * Provides methods to start, update, and end segment drags,
 * with real-time preview waypoint calculation.
 *
 * @returns Drag state and control methods
 */
export function useSegmentDrag(): UseSegmentDragResult {
  const [dragState, setDragState] = useState<DragState | null>(null);

  // Store current waypoints ref for calculations during drag
  const currentWaypointsRef = useRef<Waypoint[]>([]);

  const startDrag = useCallback(
    (
      segmentIndex: number,
      segment: Segment,
      startPosition: Point,
      source: Point,
      target: Point,
      currentWaypoints: Waypoint[]
    ) => {
      currentWaypointsRef.current = currentWaypoints;

      setDragState({
        segmentIndex,
        segment,
        startPosition,
        currentPosition: startPosition,
        previewWaypoints: currentWaypoints,
      });
    },
    []
  );

  const updateDrag = useCallback((currentPosition: Point, source: Point, target: Point) => {
    setDragState((prev) => {
      if (!prev) return null;

      // Calculate constrained delta
      const rawDelta = {
        x: currentPosition.x - prev.startPosition.x,
        y: currentPosition.y - prev.startPosition.y,
      };
      const constrainedDelta = constrainDragToAxis(prev.segment, rawDelta);

      // Calculate new position for the segment
      const newPosition = {
        x: prev.segment.from.x + constrainedDelta.x,
        y: prev.segment.from.y + constrainedDelta.y,
      };

      // Update waypoints based on drag
      const updatedWaypoints = updateWaypointsFromDrag(
        source,
        target,
        currentWaypointsRef.current,
        prev.segment,
        newPosition
      );

      return {
        ...prev,
        currentPosition,
        previewWaypoints: updatedWaypoints,
      };
    });
  }, []);

  const endDrag = useCallback(
    (gridSize: number = 20): Waypoint[] => {
      if (!dragState) return [];

      // Snap waypoints to grid
      const snappedWaypoints = dragState.previewWaypoints.map((wp) => ({
        x: Math.round(wp.x / gridSize) * gridSize,
        y: Math.round(wp.y / gridSize) * gridSize,
      }));

      // Simplify to remove collinear waypoints
      const simplifiedWaypoints = simplifyWaypoints(snappedWaypoints);

      // Clear drag state
      setDragState(null);
      currentWaypointsRef.current = [];

      return simplifiedWaypoints;
    },
    [dragState]
  );

  const cancelDrag = useCallback(() => {
    setDragState(null);
    currentWaypointsRef.current = [];
  }, []);

  return {
    dragState,
    isDragging: dragState !== null,
    startDrag,
    updateDrag,
    endDrag,
    cancelDrag,
  };
}
