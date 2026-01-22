// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * OrthogonalEditableEdge - Custom edge component with orthogonal routing
 *
 * Renders connections as orthogonal (90-degree) paths that can be customized
 * by dragging segments. Supports waypoints for custom routing.
 */

import React, { useState, useCallback, useContext, useMemo } from "react";
import {
  BaseEdge,
  EdgeProps,
  EdgeLabelRenderer,
  getSmoothStepPath,
  useReactFlow,
  useNodes,
} from "reactflow";
import { AnyWidgetModelContext } from "../index";
import type { OrthogonalEdgeData, Waypoint } from "../utils/traitletSync";
import { sendAction } from "../utils/traitletSync";
import { EditableLabel } from "../blocks/shared/components";
import {
  calculateOrthogonalPath,
  segmentsToSVGPath,
  segmentToRect,
  updateWaypointsFromDrag,
  simplifyWaypoints,
  extractWaypointsFromSegments,
  type Segment,
  type Point,
  type BlockBounds,
} from "../utils/orthogonalRouting";
import { calculateConnectionLabelPosition } from "../utils/connectionLabelPosition";
import { getBlockDimensions } from "../blocks/shared/utils/blockDefaults";

/** Width of draggable segment handles in pixels */
const HANDLE_WIDTH = 10;

/**
 * Segment handle component for dragging individual segments
 */
interface SegmentHandleProps {
  segment: Segment;
  index: number;
  onDragStart: (index: number, segment: Segment, startPos: Point) => void;
  isDragging: boolean;
}

function SegmentHandle({ segment, index, onDragStart, isDragging }: SegmentHandleProps) {
  const [isHovered, setIsHovered] = useState(false);
  const rect = segmentToRect(segment, HANDLE_WIDTH);
  const isHorizontal = segment.orientation === "horizontal";
  const cursor = isHorizontal ? "ns-resize" : "ew-resize";

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      const startPos = { x: e.clientX, y: e.clientY };
      onDragStart(index, segment, startPos);
    },
    [index, segment, onDragStart]
  );

  return (
    <rect
      x={rect.x}
      y={rect.y}
      width={Math.max(rect.width, HANDLE_WIDTH)}
      height={Math.max(rect.height, HANDLE_WIDTH)}
      fill={isHovered ? "var(--color-primary-200)" : "transparent"}
      stroke={isHovered ? "var(--color-primary-400)" : "transparent"}
      strokeWidth={1}
      rx={2}
      cursor={cursor}
      onMouseDown={handleMouseDown}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        pointerEvents: isDragging ? "none" : "all",
        transition: "fill 0.15s ease, stroke 0.15s ease",
      }}
    />
  );
}

/**
 * Custom edge that renders orthogonal paths through waypoints
 */
export default function OrthogonalEditableEdge({
  id,
  source: sourceNodeId,
  target: targetNodeId,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  markerEnd,
  style,
}: EdgeProps<OrthogonalEdgeData>) {
  const model = useContext(AnyWidgetModelContext);
  const { getViewport } = useReactFlow();
  const nodes = useNodes();

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const waypoints = data?.waypoints || [];
  const labelText = data?.label ?? id; // Default to connection ID if no label set
  const labelVisible = data?.label_visible || false;
  const sourcePoint = useMemo(() => ({ x: sourceX, y: sourceY }), [sourceX, sourceY]);
  const targetPoint = useMemo(() => ({ x: targetX, y: targetY }), [targetX, targetY]);

  // Get block bounds for source and target nodes
  // Use actual block dimensions from data (excluding labels) instead of measured dimensions
  const { sourceBounds, targetBounds } = useMemo(() => {
    const sourceNode = nodes.find((n) => n.id === sourceNodeId);
    const targetNode = nodes.find((n) => n.id === targetNodeId);

    const srcBounds: BlockBounds | undefined = sourceNode
      ? {
          x: sourceNode.position.x,
          y: sourceNode.position.y,
          ...getBlockDimensions(
            sourceNode.type || "gain",
            sourceNode.data?.width,
            sourceNode.data?.height
          ),
        }
      : undefined;

    const tgtBounds: BlockBounds | undefined = targetNode
      ? {
          x: targetNode.position.x,
          y: targetNode.position.y,
          ...getBlockDimensions(
            targetNode.type || "gain",
            targetNode.data?.width,
            targetNode.data?.height
          ),
        }
      : undefined;

    return { sourceBounds: srcBounds, targetBounds: tgtBounds };
  }, [nodes, sourceNodeId, targetNodeId]);

  // Get ALL block bounds for collision avoidance routing
  // Use actual block dimensions from data (excluding labels) instead of measured dimensions
  const allBlocks = useMemo(() => {
    return nodes.map((node) => ({
      x: node.position.x,
      y: node.position.y,
      ...getBlockDimensions(node.type || "gain", node.data?.width, node.data?.height),
    }));
  }, [nodes]);

  // Drag state
  const [dragState, setDragState] = useState<{
    segmentIndex: number;
    segment: Segment;
    startPos: Point;
    startWaypoints: Waypoint[];
    previewWaypoints: Waypoint[];
  } | null>(null);

  // Calculate segments for the current path
  const segments = useMemo(() => {
    const activeWaypoints = dragState?.previewWaypoints ?? waypoints;
    const result = calculateOrthogonalPath(
      sourcePoint,
      targetPoint,
      activeWaypoints,
      sourcePosition,
      targetPosition,
      sourceBounds,
      targetBounds,
      allBlocks
    );

    console.log("[OrthogonalEditableEdge] Calculated segments:", {
      waypoints: activeWaypoints,
      resultSegments: result,
      sourcePoint,
      targetPoint,
    });

    return result;
  }, [
    sourcePoint,
    targetPoint,
    waypoints,
    dragState?.previewWaypoints,
    sourcePosition,
    targetPosition,
    sourceBounds,
    targetBounds,
    allBlocks,
  ]);

  // Generate path string
  const edgePath = useMemo(() => {
    if (segments.length > 0) {
      return segmentsToSVGPath(segments);
    }
    // Fall back to React Flow's smoothstep for auto-routing
    const [path] = getSmoothStepPath({
      sourceX,
      sourceY,
      sourcePosition,
      targetX,
      targetY,
      targetPosition,
    });
    return path;
  }, [segments, sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition]);

  // Calculate label position using smart positioning algorithm
  // Positions at horizontal center, shifting to avoid corner waypoints
  const labelPosition = useMemo(() => {
    if (!labelVisible) return { x: 0, y: 0 };

    // Convert segments to the format expected by the positioning algorithm
    const positioningSegments = segments.map((seg) => ({
      from: seg.from,
      to: seg.to,
      orientation: seg.orientation,
    }));

    return calculateConnectionLabelPosition(positioningSegments, labelText);
  }, [labelVisible, segments, labelText]);

  // Handle label save (for editable labels)
  const handleLabelSave = useCallback(
    (newLabel: string) => {
      if (model) {
        sendAction(model, "updateConnectionLabel", {
          connectionId: id,
          label: newLabel,
        });
      }
    },
    [model, id]
  );

  // Handle drag start
  const handleDragStart = useCallback(
    (index: number, segment: Segment, startPos: Point) => {
      // If waypoints are empty (auto-routed path), extract waypoints from current segments
      // This preserves the auto-routed shape when the user starts editing
      const effectiveWaypoints =
        waypoints.length === 0 ? extractWaypointsFromSegments(segments) : waypoints;

      console.log("[OrthogonalEditableEdge] handleDragStart:", {
        segmentIndex: index,
        segment,
        currentSegments: segments,
        storedWaypoints: waypoints,
        effectiveWaypoints,
        sourcePoint,
        targetPoint,
      });

      setDragState({
        segmentIndex: index,
        segment,
        startPos,
        startWaypoints: effectiveWaypoints,
        previewWaypoints: effectiveWaypoints,
      });

      // Add global mouse event listeners
      const handleMouseMove = (e: MouseEvent) => {
        const viewport = getViewport();

        // Convert screen delta to canvas delta (accounting for zoom)
        const screenDelta = {
          x: e.clientX - startPos.x,
          y: e.clientY - startPos.y,
        };
        const canvasDelta = {
          x: screenDelta.x / viewport.zoom,
          y: screenDelta.y / viewport.zoom,
        };

        // Calculate constrained new position based on segment orientation
        let newPosition: Point;
        if (segment.orientation === "horizontal") {
          // Horizontal segment moves vertically only
          newPosition = {
            x: segment.from.x,
            y: segment.from.y + canvasDelta.y,
          };
        } else {
          // Vertical segment moves horizontally only
          newPosition = {
            x: segment.from.x + canvasDelta.x,
            y: segment.from.y,
          };
        }

        console.log("[OrthogonalEditableEdge] handleMouseMove:", {
          canvasDelta,
          segmentBeingDragged: segment,
          newPosition,
          effectiveWaypoints,
        });

        // Update waypoints based on drag
        const updatedWaypoints = updateWaypointsFromDrag(
          sourcePoint,
          targetPoint,
          effectiveWaypoints,
          segment,
          newPosition,
          sourcePosition,
          targetPosition
        );

        console.log("[OrthogonalEditableEdge] Updated waypoints from drag:", updatedWaypoints);

        setDragState((prev) =>
          prev
            ? {
                ...prev,
                previewWaypoints: updatedWaypoints,
              }
            : null
        );
      };

      const handleMouseUp = () => {
        // Remove listeners
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);

        // Get final waypoints from state
        setDragState((prev) => {
          if (!prev || !model) return null;

          // Don't snap waypoints to grid - they should align with source/target positions
          // Only simplify to remove collinear waypoints
          const simplifiedWaypoints = simplifyWaypoints(prev.previewWaypoints);

          // Send action to Python backend
          sendAction(model, "updateConnectionRouting", {
            connectionId: id,
            waypoints: simplifiedWaypoints,
          });

          return null;
        });
      };

      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [waypoints, segments, sourcePoint, targetPoint, id, model, getViewport]
  );

  // Calculate edge styling based on selection and drag state
  const isDragging = dragState !== null;
  const edgeStyle = {
    ...style,
    stroke: isDragging
      ? "var(--color-primary-400)"
      : selected
        ? "var(--color-primary-500)"
        : "var(--color-primary-600)",
    strokeWidth: selected || isDragging ? 2 : 1.5,
    opacity: isDragging ? 0.7 : 1,
  };

  return (
    <>
      <BaseEdge id={id} path={edgePath} markerEnd={markerEnd} style={edgeStyle} />
      {/* Render draggable segment handles when selected */}
      {selected && !isDragging && segments.length > 0 && (
        <g className="segment-handles">
          {segments.map((segment, index) => (
            <SegmentHandle
              key={`segment-${index}`}
              segment={segment}
              index={index}
              onDragStart={handleDragStart}
              isDragging={isDragging}
            />
          ))}
        </g>
      )}
      {/* Render connection label when visible */}
      {labelVisible && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${labelPosition.x}px, ${labelPosition.y}px)`,
              pointerEvents: "all",
            }}
          >
            <EditableLabel
              value={labelText}
              onSave={handleLabelSave}
              className="text-xs font-mono text-slate-600 whitespace-nowrap"
            />
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
