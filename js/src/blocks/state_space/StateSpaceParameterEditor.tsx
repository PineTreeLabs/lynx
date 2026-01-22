// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * StateSpaceParameterEditor - Parameter editor for State Space blocks
 *
 * Handles A, B, C, D matrix parameter editing via MatrixDisplay and custom LaTeX rendering
 */

import React, { useState } from "react";
import type { Block } from "../../utils/traitletSync";
import { useCustomLatex } from "../shared/hooks";
import { MatrixDisplay } from "./MatrixDisplay";

export interface ParameterEditorProps {
  block: Block;
  onUpdate: (blockId: string, parameterName: string, value: unknown) => void;
}

export default function StateSpaceParameterEditor({ block, onUpdate }: ParameterEditorProps) {
  // Track which matrix is being edited (only one at a time)
  const [editingMatrix, setEditingMatrix] = useState<string | null>(null);

  // Custom LaTeX hook
  const {
    useCustomLatex: useCustomLatexState,
    latexValue,
    latexError,
    handleToggle,
    handleChange,
    handleApply,
  } = useCustomLatex(block.id, block.custom_latex, onUpdate);

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
              placeholder={String.raw`e.g., \dot{x} = Ax + Bu`}
            />
            {latexError && <div className="text-xs text-red-600 mt-1">{latexError}</div>}
          </div>
        )}
      </div>

      {/* State Space Equation */}
      <div className="text-[10px] text-gray-600 mb-1">State Space: x' = Ax + Bu, y = Cx + Du</div>

      {/* Matrix Parameters */}
      <div>
        {["A", "B", "C", "D"].map((matrixName) => {
          const param = block.parameters.find((p) => p.name === matrixName);
          return (
            <MatrixDisplay
              key={matrixName}
              name={matrixName}
              expression={param?.expression || null}
              value={param?.value || null}
              isEditing={editingMatrix === matrixName}
              onEdit={() => setEditingMatrix(matrixName)}
              onSave={(newExpression) => {
                onUpdate(block.id, matrixName, newExpression);
                setEditingMatrix(null);
              }}
              onCancel={() => setEditingMatrix(null)}
            />
          );
        })}
      </div>
    </div>
  );
}
