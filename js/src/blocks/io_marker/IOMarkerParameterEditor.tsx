// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * IOMarkerParameterEditor - Parameter editor for IO Marker blocks
 *
 * Handles parameter editing and custom LaTeX rendering
 */

import React, { useState, useEffect, useRef, useLayoutEffect } from "react";
import type { Block } from "../../utils/traitletSync";
import { useCustomLatex } from "../shared/hooks";

export interface ParameterEditorProps {
  block: Block;
  onUpdate: (blockId: string, parameterName: string, value: unknown) => void;
}

export default function IOMarkerParameterEditor({ block, onUpdate }: ParameterEditorProps) {
  // Get parameter values
  const indexParam = block.parameters?.find((p) => p.name === "index");
  const index = indexParam?.value ?? 0;

  // Local state for index (as string to allow deletion)
  const [indexValue, setIndexValue] = useState<string>(String(index));

  // Ref to always have latest index value for event handlers
  const indexValueRef = useRef(indexValue);
  useLayoutEffect(() => {
    indexValueRef.current = indexValue;
  }, [indexValue]);

  // Initialize index values when block changes
  useEffect(() => {
    const param = block.parameters?.find((p) => p.name === "index");
    setIndexValue(String(param?.value ?? 0));
  }, [block.parameters]);

  // Custom LaTeX hook
  const {
    useCustomLatex: useCustomLatexState,
    latexValue,
    latexError,
    handleToggle,
    handleChange,
    handleApply,
  } = useCustomLatex(block.id, block.custom_latex, onUpdate);

  // Handle index value change
  const handleIndexChange = (value: string) => {
    // Allow any string input (including empty for deletion)
    setIndexValue(value);
  };

  // Apply index value (on blur or Enter)
  const handleIndexApply = () => {
    // Parse and validate on apply using ref to get latest value
    const currentValue = indexValueRef.current;
    const numValue = currentValue === "" ? 0 : parseInt(currentValue, 10);
    const validValue = isNaN(numValue) || numValue < 0 ? 0 : numValue;
    onUpdate(block.id, "index", validValue);
    // Don't update local state here - wait for backend to send clamped value
    // (backend clamps to [0, N-1] range, which we don't know here)
  };

  return (
    <div className="space-y-2">
      {/* Custom LaTeX Section */}
      <div className="mb-3 pb-3 border-b">
        <label className="flex items-center text-xs font-medium mb-2 cursor-pointer">
          <input
            type="checkbox"
            checked={useCustomLatexState}
            onChange={(e) => handleToggle(e.target.checked)}
            className="mr-2"
          />
          Render custom block contents
        </label>

        {useCustomLatexState && (
          <div style={{ display: useCustomLatexState ? "block" : "none" }}>
            <label className="block text-xs font-medium mb-1">Custom LaTeX Expression</label>
            <textarea
              value={latexValue}
              onChange={(e) => handleChange(e.target.value)}
              onBlur={() => handleApply()}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  e.stopPropagation();
                  handleApply();
                  e.currentTarget.blur();
                }
              }}
              className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono resize-none"
              rows={3}
              placeholder={String.raw`e.g., r, \theta, \dot{x}`}
            />
            {latexError && <div className="text-xs text-red-600 mt-1">{latexError}</div>}
          </div>
        )}
      </div>

      {/* Index Parameter */}
      <div>
        <label className="block text-xs font-medium mb-1">Index</label>
        <input
          type="text"
          value={indexValue}
          onChange={(e) => handleIndexChange(e.target.value)}
          onBlur={() => handleIndexApply()}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              (e.target as HTMLInputElement).blur();
            }
          }}
          className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="0"
        />
      </div>
    </div>
  );
}
