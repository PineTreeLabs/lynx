// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * GainParameterEditor - Parameter editor for Gain blocks
 *
 * Handles K parameter editing and custom LaTeX rendering
 */

import React, { useState, useEffect, useRef, useLayoutEffect } from "react";
import type { Block } from "../../utils/traitletSync";
import { useCustomLatex } from "../shared/hooks";

export interface ParameterEditorProps {
  block: Block;
  onUpdate: (blockId: string, parameterName: string, value: unknown) => void;
}

export default function GainParameterEditor({ block, onUpdate }: ParameterEditorProps) {
  // Get K parameter object (not just value)
  const kParam = block.parameters?.find((p) => p.name === "K");
  const kExpression = kParam?.expression ?? String(kParam?.value ?? 1.0);
  const kValue = kParam?.value ?? 1.0;

  // Local state for expression editing
  const [kExpressionInput, setKExpressionInput] = useState<string>(kExpression);

  // Ref to always have latest expression for event handlers
  const kExpressionRef = useRef(kExpressionInput);
  useLayoutEffect(() => {
    kExpressionRef.current = kExpressionInput;
  }, [kExpressionInput]);

  // Initialize expression when block changes
  useEffect(() => {
    const param = block.parameters?.find((p) => p.name === "K");
    setKExpressionInput(param?.expression ?? String(param?.value ?? 1.0));
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

  // Handle K expression change
  const handleKChange = (value: string) => {
    setKExpressionInput(value);
  };

  // Apply K expression (on blur or Enter)
  const handleKApply = () => {
    onUpdate(block.id, "K", kExpressionRef.current);
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
          <div>
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
              placeholder={String.raw`e.g., H(s) = \frac{1}{s+1}`}
            />
            {latexError && <div className="text-xs text-red-600 mt-1">{latexError}</div>}
          </div>
        )}
      </div>

      {/* K Parameter */}
      <div>
        <label className="block text-xs font-medium mb-1">Gain (K)</label>

        {/* Expression input */}
        <div className="mb-1">
          <div className="text-[10px] text-gray-500 mb-0.5">Expression:</div>
          <input
            type="text"
            value={kExpressionInput}
            onChange={(e) => handleKChange(e.target.value)}
            onBlur={handleKApply}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                e.stopPropagation();
                handleKApply();
                (e.target as HTMLInputElement).blur();
              }
            }}
            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
            placeholder="e.g., gain_value or 2*np.pi"
          />
        </div>

        {/* Resolved value display (read-only) */}
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Resolved Value:</div>
          <div className="px-2 py-1 text-sm bg-gray-50 rounded font-mono text-gray-700">
            {typeof kValue === "number" ? kValue.toFixed(3) : String(kValue)}
          </div>
        </div>
      </div>
    </div>
  );
}
