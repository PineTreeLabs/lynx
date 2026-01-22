// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * PortMarker - Triangular port direction indicator
 *
 * Displays Simulink-style triangular markers on block ports to indicate
 * signal flow direction. Markers are visible only on unconnected ports.
 */

import React from "react";
import { Position } from "reactflow";
import { calculateArrowheadLines } from "../utils/portMarkerGeometry";

export interface PortMarkerProps {
  /** Handle position - determines triangle orientation */
  position: Position;
  /** Port type - determines tip vs base positioning */
  portType: "input" | "output";
  /** Connection state - controls visibility */
  isConnected: boolean;
  /** Block flip state - inherited from parent (affects arrow direction) */
  isFlipped?: boolean;
  /** Whether port is drag target during connection operation */
  isDragTarget?: boolean;
  /** Triangle size in pixels (default: 10) */
  size?: number;
  /** Additional CSS classes */
  className?: string;
}

/**
 * PortMarker component renders an arrowhead SVG marker for block ports.
 *
 * Arrowheads consist of two angled lines (no base) forming a V-shape.
 * - Input ports: arrow tip at block border, base extends outward
 * - Output ports: arrow base at block border, tip extends outward
 *
 * Visibility rules:
 * - VISIBLE: !isConnected && !isDragTarget
 * - HIDDEN: isConnected || isDragTarget
 *
 * @param props - PortMarker component props
 * @returns SVG arrowhead or null when hidden
 */
const PortMarker: React.FC<PortMarkerProps> = ({
  position,
  portType,
  isConnected,
  isFlipped = false,
  isDragTarget = false,
  size = 10,
  className = "",
}) => {
  // Visibility logic: hide if connected or drag target
  const isVisible = !isConnected && !isDragTarget;

  if (!isVisible) {
    return null;
  }

  // Calculate arrowhead line geometry based on handle position, type, and flip state
  const { line1, line2, viewBox } = calculateArrowheadLines({
    size,
    position,
    portType,
    isFlipped,
    isEquilateral: true,
  });

  // Position the SVG centered on the handle, with input positions shifted outward by 3px
  let svgLeft = "50%";
  let svgTop = "50%";

  if (position === Position.Left) {
    // Input: shift left by 3px to prevent penetration
    svgLeft = "calc(50% - 3px)";
  } else if (position === Position.Top) {
    // Input: shift up by 3px to prevent penetration
    svgTop = "calc(50% - 3px)";
  } else if (position === Position.Bottom) {
    // Input: shift down by 3px to prevent penetration
    svgTop = "calc(50% + 3px)";
  } else if (position === Position.Right) {
    // Output: shift right by 3px to prevent penetration
    svgLeft = "calc(50% + 3px)";
  }

  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      className={`port-marker ${className}`}
      style={{
        position: "absolute",
        left: svgLeft,
        top: svgTop,
        transform: "translate(-50%, -50%)", // Center the SVG on the handle
        pointerEvents: "none", // Don't interfere with Handle interaction
        zIndex: 20, // Above Handle (which is z-10)
      }}
    >
      <line
        x1={line1.x1}
        y1={line1.y1}
        x2={line1.x2}
        y2={line1.y2}
        stroke="var(--color-primary-600)"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <line
        x1={line2.x1}
        y1={line2.y1}
        x2={line2.x2}
        y2={line2.y2}
        stroke="var(--color-primary-600)"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default PortMarker;
