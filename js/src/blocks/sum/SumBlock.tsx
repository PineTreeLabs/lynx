// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * SumBlock - React component for Sum junction blocks
 *
 * Displays a sum junction that adds/subtracts multiple inputs
 * Classic control system style: circle/ellipse with X inside
 * Follows Simulink convention: signs = [top, left, bottom], "|" = no connection
 *
 * Features quadrant-based configuration: double-click quadrants to cycle through "+", "-", "|"
 */

import React, { useCallback, useContext } from "react";
import { Handle, Position, NodeProps, NodeResizer } from "reactflow";
import { AnyWidgetModelContext } from "../../context/AnyWidgetModel";
import { sendAction } from "../../utils/traitletSync";
import { EditableLabel, PortMarker } from "../shared/components";
import {
  useBlockLabel,
  useFlippableBlock,
  useBlockResize,
  usePortConnected,
} from "../shared/hooks";
import { getBlockDimensions, getBlockMinDimensions } from "../shared/utils";
import { getQuadrantPath } from "./ellipseQuadrantPaths";

interface SumBlockData {
  parameters: Array<{ name: string; value: unknown }>;
  ports: Array<{ id: string; type: string }>;
  label?: string;
  flipped?: boolean;
  label_visible?: boolean;
  width?: number;
  height?: number;
}

// Helper component for input handle with marker
function InputHandleWithMarker({
  blockId,
  portId,
  position,
  style,
  isFlipped,
}: {
  blockId: string;
  portId: string;
  position: Position;
  style: React.CSSProperties;
  isFlipped: boolean;
}) {
  const isConnected = usePortConnected(blockId, portId);

  return (
    <Handle type="target" position={position} id={portId} style={style}>
      <PortMarker
        position={position}
        portType="input"
        isConnected={isConnected}
        isFlipped={isFlipped}
      />
    </Handle>
  );
}

export default function SumBlock({ data, id, selected }: NodeProps<SumBlockData>) {
  // Get signs parameter - Simulink convention: [top, left, bottom]
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const signs = data.parameters?.find((p) => p.name === "signs")?.value ?? ["+", "+", "|"];
  const isFlipped = data.flipped || false;

  // Get dimensions (custom or default)
  const { width, height } = getBlockDimensions("sum", data.width, data.height);
  const { minWidth, minHeight } = getBlockMinDimensions("sum");

  // Use shared hooks
  const { blockLabel, handleLabelSave } = useBlockLabel(id, data);
  const { getHandlePosition } = useFlippableBlock(isFlipped);
  const { handleResizeStart, handleResize, handleResizeEnd } = useBlockResize(
    id,
    "sum",
    width,
    height
  );

  // Check output port connection status
  const outputConnected = usePortConnected(id, "out");

  // Ellipse dimensions - use half of width/height as radii
  const centerX = width / 2;
  const centerY = height / 2;
  const radiusX = (width - 4) / 2; // Subtract stroke width
  const radiusY = (height - 4) / 2;

  // Get anywidget model for sending actions to Python backend
  const model = useContext(AnyWidgetModelContext);

  // Helper: Cycle sign through states: "+" → "-" → "|" → "+"
  const cycleSign = (currentSign: string): string => {
    switch (currentSign) {
      case "+":
        return "-";
      case "-":
        return "|";
      case "|":
        return "+";
      default:
        return "+";
    }
  };

  // Handle quadrant double-click - use data attribute from SVG path
  const handleQuadrantDoubleClick = useCallback(
    (e: React.MouseEvent<SVGPathElement>) => {
      e.stopPropagation(); // Prevent canvas-level double-click
      e.preventDefault(); // Prevent default

      // Get quadrant from the path element's data attribute
      const quadrant = parseInt(e.currentTarget.getAttribute("data-quadrant") || "-1", 10);

      // Only process double-clicks on input quadrants (0, 1, 2)
      if (quadrant < 0 || quadrant > 2) {
        return;
      }

      // Cycle the sign for this quadrant
      const currentSign = signs[quadrant] || "+";
      const nextSign = cycleSign(currentSign);

      // Update signs array
      const newSigns = [...signs];
      newSigns[quadrant] = nextSign;

      // Send action to Python backend
      if (model) {
        sendAction(model, "updateParameter", {
          blockId: id,
          parameterName: "signs",
          value: newSigns,
        });
      }
    },
    [signs, id, model]
  );

  // Define quadrant positions and their corresponding signs
  // Simulink convention: signs[0]=top, signs[1]=left, signs[2]=bottom
  // Use ellipse radii for handle positioning
  const quadrants = [
    {
      position: "top",
      angle: -Math.PI / 2, // -90 degrees (up)
      sign: signs[0] || "+",
      handlePosition: Position.Top,
      rx: radiusX,
      ry: radiusY,
    },
    {
      position: "left",
      angle: Math.PI, // 180 degrees
      sign: signs[1] || "+",
      handlePosition: Position.Left,
      rx: radiusX,
      ry: radiusY,
    },
    {
      position: "bottom",
      angle: Math.PI / 2, // 90 degrees (down)
      sign: signs[2] || "|",
      handlePosition: Position.Bottom,
      rx: radiusX,
      ry: radiusY,
    },
  ];

  // Map active quadrants (not "|") to sequential port IDs (in1, in2, in3)
  // Python backend creates ports sequentially: in1, in2, in3, etc.
  const activeQuadrants = quadrants
    .map((q, idx) => ({ ...q, originalIndex: idx }))
    .filter((q) => q.sign !== "|");

  // Assign sequential port IDs to active quadrants
  const quadrantsWithPorts = activeQuadrants.map((q, idx) => ({
    ...q,
    portId: `in${idx + 1}`,
  }));

  return (
    <>
      {/* NodeResizer for corner handles - must be at root level */}
      <NodeResizer
        minWidth={minWidth}
        minHeight={minHeight}
        isVisible={selected}
        onResizeStart={handleResizeStart}
        onResize={handleResize}
        onResizeEnd={handleResizeEnd}
        handleStyle={{
          width: 8,
          height: 8,
          backgroundColor: "var(--color-primary-600)",
          borderRadius: 2,
        }}
        lineStyle={{
          borderColor: "var(--color-primary-400)",
          borderWidth: 1,
        }}
      />
      {/* Wrapper constrained to block dimensions only (excludes label from measured bounds) */}
      <div className="relative" style={{ width: `${width}px`, height: `${height}px` }}>
        {/* Ellipse-X SVG - classic sum junction symbol (scales to ellipse for non-square) */}
        <svg width={width} height={height} className="drop-shadow-md">
          {/* Ellipse (circle when width === height) */}
          <ellipse
            cx={centerX}
            cy={centerY}
            rx={radiusX}
            ry={radiusY}
            fill="var(--color-slate-200)"
            stroke="var(--color-primary-600)"
            strokeWidth="2"
          />

          {/* X inside ellipse - two diagonal lines extending to edges */}
          <line
            x1={centerX - radiusX * 0.707}
            y1={centerY - radiusY * 0.707}
            x2={centerX + radiusX * 0.707}
            y2={centerY + radiusY * 0.707}
            stroke="var(--color-primary-600)"
            strokeWidth="2"
          />
          <line
            x1={centerX + radiusX * 0.707}
            y1={centerY - radiusY * 0.707}
            x2={centerX - radiusX * 0.707}
            y2={centerY + radiusY * 0.707}
            stroke="var(--color-primary-600)"
            strokeWidth="2"
          />

          {/* Quadrant overlays - clickable regions for sign configuration */}
          {/* Render AFTER ellipse and X, BEFORE signs text */}
          <style>
            {`
              .sum-quadrant {
                fill: transparent;
                cursor: pointer;
                pointer-events: auto;
                transition: fill 0.15s ease, opacity 0.15s ease;
              }
              .sum-quadrant:hover {
                fill: var(--color-primary-200);
                opacity: 0.5;
              }
            `}
          </style>
          {[0, 1, 2].map((quadrantIndex) => {
            const quadrantPathData = getQuadrantPath(
              quadrantIndex as 0 | 1 | 2,
              centerX,
              centerY,
              radiusX,
              radiusY
            );

            return (
              <path
                key={`quadrant-${quadrantIndex}`}
                className="sum-quadrant"
                d={quadrantPathData}
                data-quadrant={quadrantIndex}
                onDoubleClick={(e) => {
                  handleQuadrantDoubleClick(e);
                }}
              />
            );
          })}

          {/* Signs in quadrants - positioned closer to center to avoid port dots */}
          {quadrants.map((quadrant, i) => {
            if (quadrant.sign === "|") return null;

            // Position sign inside ellipse, aligned with port but closer to center
            const signDistanceX = radiusX * 0.55;
            const signDistanceY = radiusY * 0.55;
            const baseX = signDistanceX * Math.cos(quadrant.angle);
            const y = centerY + signDistanceY * Math.sin(quadrant.angle);

            // Mirror X position when flipped
            const x = centerX + (isFlipped ? -baseX : baseX);

            return (
              <text
                key={i}
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  fontFamily: "monospace",
                  pointerEvents: "none", // Allow clicks to pass through to quadrant paths
                }}
                fill="var(--color-primary-600)"
              >
                {quadrant.sign}
              </text>
            );
          })}
        </svg>

        {/* Input handles - positioned ON the ellipse at quadrant midpoints, rendered AFTER SVG */}
        {quadrantsWithPorts.map((quadrant) => {
          // Position on ellipse edge using parametric equation
          const baseX = radiusX * Math.cos(quadrant.angle);
          const y = centerY + radiusY * Math.sin(quadrant.angle);

          // Mirror X position when flipped
          const x = centerX + (isFlipped ? -baseX : baseX);

          return (
            <InputHandleWithMarker
              key={quadrant.portId}
              blockId={id}
              portId={quadrant.portId}
              position={getHandlePosition(quadrant.handlePosition)}
              style={{
                position: "absolute",
                left: `${x}px`,
                top: `${y}px`,
                transform: "translate(-50%, -50%)",
                zIndex: 10,
              }}
              isFlipped={isFlipped}
            />
          );
        })}

        {/* Output handle - positioned ON the ellipse at right quadrant */}
        <Handle
          type="source"
          position={getHandlePosition(Position.Right)}
          id="out"
          style={{
            position: "absolute",
            left: `${centerX + (isFlipped ? -radiusX : radiusX)}px`,
            top: `${centerY}px`,
            transform: "translate(-50%, -50%)",
            zIndex: 10,
          }}
        >
          <PortMarker
            position={getHandlePosition(Position.Right)}
            portType="output"
            isConnected={outputConnected}
            isFlipped={isFlipped}
          />
        </Handle>

        {/* Block name label - positioned absolutely below block (excluded from measured bounds) */}
        {data.label_visible && (
          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-1">
            <EditableLabel
              value={blockLabel}
              onSave={handleLabelSave}
              className="text-xs text-slate-600 font-mono whitespace-nowrap"
            />
          </div>
        )}
      </div>
    </>
  );
}
