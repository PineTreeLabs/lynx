// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * IOMarkerBlock - React component for Input/Output marker blocks
 *
 * Displays input or output boundary markers
 */

import React from "react";
import { Handle, Position, NodeProps, NodeResizer } from "reactflow";
import { EditableLabel, PortMarker, LaTeXRenderer } from "../shared/components";
import {
  useBlockLabel,
  useFlippableBlock,
  useBlockResize,
  usePortConnected,
} from "../shared/hooks";
import { getBlockDimensions, getBlockMinDimensions } from "../shared/utils";

interface IOMarkerData {
  parameters: Array<{ name: string; value: unknown }>;
  ports: Array<{ id: string; type: string }>;
  label?: string;
  flipped?: boolean;
  label_visible?: boolean;
  width?: number;
  height?: number;
  custom_latex?: string;
}

export default function IOMarkerBlock({ data, id, selected }: NodeProps<IOMarkerData>) {
  // Get label parameter if present (signal label, displayed inside block)
  const index = data.parameters?.find((p) => p.name === "index")?.value ?? 0;
  const customLatex = data.custom_latex;
  const isFlipped = data.flipped || false;

  // Determine if this is an input or output marker based on ports
  const isInput = data.ports?.some((p) => p.type === "output");
  const isOutput = data.ports?.some((p) => p.type === "input");

  // Get dimensions (custom or default)
  const { width, height } = getBlockDimensions("io_marker", data.width, data.height);
  const { minWidth, minHeight } = getBlockMinDimensions("io_marker");

  // Use shared hooks
  const { blockLabel, handleLabelSave } = useBlockLabel(id, data);
  const { getHandlePosition } = useFlippableBlock(isFlipped);
  const { handleResizeStart, handleResize, handleResizeEnd } = useBlockResize(
    id,
    "io_marker",
    width,
    height
  );

  // Check port connection status for markers
  const inputConnected = usePortConnected(id, "in");
  const outputConnected = usePortConnected(id, "out");

  // Generate LaTeX for display
  const latex = customLatex || String.raw`${index}`;

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
        <div
          className="bg-slate-200 border-2 border-primary-600 rounded-full shadow-md relative flex items-center justify-center"
          style={{ width: `${width}px`, height: `${height}px` }}
        >
          {/* Output marker has INPUT handle */}
          {isOutput && (
            <Handle
              type="target"
              position={getHandlePosition(Position.Left)}
              id="in"
              style={{
                position: "absolute",
                left: isFlipped ? "100%" : "0",
                top: "50%",
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
          )}

          {/* Block content - LaTeX-rendered (custom or index) */}
          <div className="text-center px-2">
            <LaTeXRenderer
              latex={latex}
              autoScale={true}
              displayMode={true}
              className="text-primary-600"
            />
          </div>

          {/* Input marker has OUTPUT handle */}
          {isInput && (
            <Handle
              type="source"
              position={getHandlePosition(Position.Right)}
              id="out"
              style={{
                position: "absolute",
                left: isFlipped ? "0" : "100%",
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
          )}
        </div>

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
