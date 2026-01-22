// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * BlockPalette - UI for adding blocks to the diagram
 *
 * All 5 block types: Gain, I/O markers, Sum, Transfer Function, State Space
 *
 * Collapsible by default - expands on hover, collapses on mouse leave.
 */

import React, { useContext, useState, useRef, useEffect, useCallback } from "react";
import { AnyWidgetModelContext } from "../context/AnyWidgetModel";
import { sendAction } from "../utils/traitletSync";
import { BLOCK_TYPES } from "../config/constants";

// Collapse delay in milliseconds - prevents accidental closures
const COLLAPSE_DELAY_MS = 200;

export default function BlockPalette() {
  const model = useContext(AnyWidgetModelContext);

  // Expand/collapse state - collapsed by default
  const [isExpanded, setIsExpanded] = useState(false);

  // Ref to track collapse timeout for cancellation
  const collapseTimeoutRef = useRef<number | null>(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (collapseTimeoutRef.current) {
        clearTimeout(collapseTimeoutRef.current);
      }
    };
  }, []);

  // Handle mouse enter - expand immediately, cancel any pending collapse
  const handleMouseEnter = useCallback(() => {
    if (collapseTimeoutRef.current) {
      clearTimeout(collapseTimeoutRef.current);
      collapseTimeoutRef.current = null;
    }
    setIsExpanded(true);
  }, []);

  // Handle mouse leave - collapse after delay
  const handleMouseLeave = useCallback(() => {
    collapseTimeoutRef.current = window.setTimeout(() => {
      setIsExpanded(false);
    }, COLLAPSE_DELAY_MS);
  }, []);

  const addBlock = (blockType: string, defaultParams: Record<string, unknown> = {}) => {
    if (!model) return;

    const id = `${blockType}_${Date.now()}`;

    // Use center of viewport for new blocks (cleaner than random)
    // User can drag to desired position
    const position = {
      x: 250, // Center of typical viewport
      y: 200,
    };

    sendAction(model, "addBlock", {
      blockType,
      id,
      position,
      ...defaultParams,
    });
  };

  return (
    <div
      data-testid="block-palette"
      className="absolute top-2 left-2 z-10 bg-slate-100 border-2 border-slate-300 rounded-lg shadow-lg"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Always visible: Collapsed header with "Library" text */}
      <div className="px-3 py-1.5 text-xs font-semibold text-slate-600 cursor-default">Library</div>

      {/* Collapsible button panel */}
      <div
        data-testid="button-panel"
        className={`flex flex-col gap-1 transition-all duration-150 ease-in-out ${
          isExpanded ? "max-h-96 opacity-100 p-2 pt-0" : "max-h-0 opacity-0 overflow-hidden"
        }`}
      >
        {/* Gain Block */}
        <button
          onClick={() => addBlock(BLOCK_TYPES.GAIN, { K: 1.0 })}
          disabled={!model}
          className="palette-button w-full px-3 py-1.5 bg-slate-600 text-slate-50 text-xs rounded hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          title="Add Gain Block (K)"
        >
          Gain
        </button>

        {/* Input Marker */}
        <button
          onClick={() => addBlock(BLOCK_TYPES.IO_MARKER, { marker_type: "input", label: "u" })}
          disabled={!model}
          className="palette-button w-full px-3 py-1.5 bg-slate-600 text-slate-50 text-xs rounded hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          title="Add Input Marker"
        >
          Input
        </button>

        {/* Output Marker */}
        <button
          onClick={() => addBlock(BLOCK_TYPES.IO_MARKER, { marker_type: "output", label: "y" })}
          disabled={!model}
          className="palette-button w-full px-3 py-1.5 bg-slate-600 text-slate-50 text-xs rounded hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          title="Add Output Marker"
        >
          Output
        </button>

        {/* Sum Block */}
        <button
          onClick={() => addBlock(BLOCK_TYPES.SUM, { signs: ["+", "+", "|"] })}
          disabled={!model}
          className="palette-button w-full px-3 py-1.5 bg-slate-600 text-slate-50 text-xs rounded hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          title="Add Sum Block (top, left, bottom quadrants)"
        >
          Sum
        </button>

        {/* Transfer Function Block */}
        <button
          onClick={() =>
            addBlock(BLOCK_TYPES.TRANSFER_FUNCTION, { numerator: [1], denominator: [1, 1] })
          }
          disabled={!model}
          className="palette-button w-full px-3 py-1.5 bg-slate-600 text-slate-50 text-xs rounded hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          title="Add Transfer Function Block"
        >
          TF
        </button>

        {/* State Space Block */}
        <button
          onClick={() =>
            addBlock(BLOCK_TYPES.STATE_SPACE, {
              A: [
                [0, 1],
                [-1, -1],
              ],
              B: [[0], [1]],
              C: [[1, 0]],
              D: [[0]],
            })
          }
          disabled={!model}
          className="palette-button w-full px-3 py-1.5 bg-slate-600 text-slate-50 text-xs rounded hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          title="Add State Space Block"
        >
          SS
        </button>
      </div>
    </div>
  );
}
