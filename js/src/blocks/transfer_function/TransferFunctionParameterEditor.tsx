// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * TransferFunctionParameterEditor - Parameter editor for Transfer Function blocks
 *
 * Handles numerator and denominator parameter editing and custom LaTeX rendering
 */

import React, { useState, useEffect } from "react";
import type { Block } from "../../utils/traitletSync";
import { useCustomLatex } from "../shared/hooks";

export interface ParameterEditorProps {
  block: Block;
  onUpdate: (blockId: string, parameterName: string, value: unknown) => void;
}

export default function TransferFunctionParameterEditor({ block, onUpdate }: ParameterEditorProps) {
  // Get parameter objects
  const numParam = block.parameters?.find((p) => p.name === "numerator");
  const denParam = block.parameters?.find((p) => p.name === "denominator");

  // Extract expressions (fallback to stringified values for old diagrams)
  const numExpression =
    numParam?.expression ??
    (Array.isArray(numParam?.value) ? numParam.value.join(",") : String(numParam?.value ?? "[1]"));
  const denExpression =
    denParam?.expression ??
    (Array.isArray(denParam?.value)
      ? denParam.value.join(",")
      : String(denParam?.value ?? "[1,1]"));

  // Extract resolved values for display
  const numValue = numParam?.value ?? [1];
  const denValue = denParam?.value ?? [1, 1];

  // Local state for expression editing
  const [numExpressionInput, setNumExpressionInput] = useState<string>(numExpression);
  const [denExpressionInput, setDenExpressionInput] = useState<string>(denExpression);

  // Initialize expressions when block changes
  useEffect(() => {
    const param = block.parameters?.find((p) => p.name === "numerator");
    const expr =
      param?.expression ??
      (Array.isArray(param?.value) ? param.value.join(",") : String(param?.value ?? "[1]"));
    setNumExpressionInput(expr);
  }, [block.parameters]);

  useEffect(() => {
    const param = block.parameters?.find((p) => p.name === "denominator");
    const expr =
      param?.expression ??
      (Array.isArray(param?.value) ? param.value.join(",") : String(param?.value ?? "[1,1]"));
    setDenExpressionInput(expr);
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

  // Handle numerator expression change
  const handleNumChange = (value: string) => {
    setNumExpressionInput(value);
  };

  // Apply numerator expression
  const handleNumApply = () => {
    onUpdate(block.id, "numerator", numExpressionInput);
  };

  // Handle denominator expression change
  const handleDenChange = (value: string) => {
    setDenExpressionInput(value);
  };

  // Apply denominator expression
  const handleDenApply = () => {
    onUpdate(block.id, "denominator", denExpressionInput);
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

      {/* Numerator Parameter */}
      <div>
        <label className="block text-xs font-medium mb-1">Numerator</label>

        {/* Expression input */}
        <div className="mb-1">
          <div className="text-[10px] text-gray-500 mb-0.5">Expression:</div>
          <input
            type="text"
            value={numExpressionInput}
            onChange={(e) => handleNumChange(e.target.value)}
            onBlur={() => handleNumApply()}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                e.stopPropagation();
                handleNumApply();
                (e.target as HTMLInputElement).blur();
              }
            }}
            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
            placeholder="e.g., [1, 2, 3] or num_coeffs"
          />
        </div>

        {/* Resolved value display */}
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Resolved Value:</div>
          <div className="px-2 py-1 text-sm bg-gray-50 rounded font-mono text-gray-700">
            {formatArray(numValue)}
          </div>
        </div>
      </div>

      {/* Denominator Parameter */}
      <div>
        <label className="block text-xs font-medium mb-1">Denominator</label>

        {/* Expression input */}
        <div className="mb-1">
          <div className="text-[10px] text-gray-500 mb-0.5">Expression:</div>
          <input
            type="text"
            value={denExpressionInput}
            onChange={(e) => handleDenChange(e.target.value)}
            onBlur={() => handleDenApply()}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                e.stopPropagation();
                handleDenApply();
                (e.target as HTMLInputElement).blur();
              }
            }}
            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
            placeholder={String.raw`e.g., [1, 2*zeta, 1] or den_coeffs`}
          />
        </div>

        {/* Resolved value display */}
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Resolved Value:</div>
          <div className="px-2 py-1 text-sm bg-gray-50 rounded font-mono text-gray-700">
            {formatArray(denValue)}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Format array for display (e.g., [1.000, 2.000, 3.000])
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function formatArray(value: any): string {
  if (Array.isArray(value)) {
    return `[${value.map((v) => (typeof v === "number" ? v.toFixed(3) : String(v))).join(", ")}]`;
  }
  return String(value);
}
