// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * GainBlock - React component for Gain blocks
 *
 * Displays a simple scalar gain block: y = K * u
 */

import React from "react";
import { Handle, Position, NodeProps, NodeResizer } from "reactflow";
import { EditableLabel, LaTeXRenderer, PortMarker } from "../shared/components";
import {
  useBlockLabel,
  useFlippableBlock,
  useBlockResize,
  usePortConnected,
} from "../shared/hooks";
import { generateGainLatex, getBlockDimensions, getBlockMinDimensions } from "../shared/utils";

interface GainBlockData {
  parameters: Array<{ name: string; value: unknown }>;
  ports: Array<{ id: string; type: string }>;
  label?: string;
  flipped?: boolean;
  custom_latex?: string;
  label_visible?: boolean;
  width?: number;
  height?: number;
}

export default function GainBlock({ data, id, selected }: NodeProps<GainBlockData>) {
  // Get K parameter value
  const K = data.parameters?.find((p) => p.name === "K")?.value ?? 1.0;
  const customLatex = data.custom_latex;
  const isFlipped = data.flipped || false;

  // Get dimensions (custom or default)
  const { width, height } = getBlockDimensions("gain", data.width, data.height);
  const { minWidth, minHeight } = getBlockMinDimensions("gain");

  // Use shared hooks
  const { blockLabel, handleLabelSave } = useBlockLabel(id, data);
  const { getHandlePosition, getFlipTransform } = useFlippableBlock(isFlipped);
  const { handleResizeStart, handleResize, handleResizeEnd } = useBlockResize(
    id,
    "gain",
    width,
    height
  );

  // Check port connection status for markers
  const inputConnected = usePortConnected(id, "in");
  const outputConnected = usePortConnected(id, "out");

  // Generate LaTeX for display
  const latex = customLatex || generateGainLatex(K);

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
        {/* Input handle - swaps to right side when flipped */}
        <Handle
          type="target"
          position={getHandlePosition(Position.Left)}
          id="in"
          style={{
            position: "absolute",
            left: isFlipped ? "91.67%" : "8.33%", // Flipped: right edge at 91.67%, unflipped: left edge at 8.33%
            top: "50%", // 40px/80px = 50%
            transform: "translate(-50%, -50%)",
          }}
        >
          <PortMarker
            position={getHandlePosition(Position.Left)}
            portType="input"
            isConnected={inputConnected}
            isFlipped={isFlipped}
          />
        </Handle>

        {/* Triangle SVG - flip the visual to point the other direction */}
        <svg
          width={width}
          height={height}
          className="drop-shadow-md"
          style={{ transform: getFlipTransform() }}
        >
          {/* Triangle pointing right (gain amplifier symbol) - scales with dimensions */}
          <polygon
            points={`${width * 0.083},0 ${width * 0.083},${height} ${width},${height / 2}`}
            fill="var(--color-slate-200)"
            stroke="var(--color-primary-600)"
            strokeWidth="2"
          />

          {/* Gain value with LaTeX rendering - fixed font size, centered */}
          <foreignObject
            x={width * 0.083}
            y={height * 0.2}
            width={width * 0.75}
            height={height * 0.6}
          >
            <div
              style={{
                transform: getFlipTransform(),
                transformOrigin: "center",
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: isFlipped ? "flex-end" : "flex-start",
                paddingLeft: isFlipped ? "5px" : "10px",
                paddingRight: isFlipped ? "10px" : "5px",
              }}
            >
              <LaTeXRenderer
                latex={latex}
                className="text-primary-600"
                align={isFlipped ? "right" : "left"}
              />
            </div>
          </foreignObject>
        </svg>

        {/* Output handle - swaps to left side when flipped */}
        <Handle
          type="source"
          position={getHandlePosition(Position.Right)}
          id="out"
          style={{
            position: "absolute",
            left: isFlipped ? "calc(0% + 1px)" : "100%", // Flipped: left tip at 0%, unflipped: right tip at 100%
            top: "50%",
            transform: "translate(-50%, -50%)",
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
