// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * MatrixDisplay - Component for displaying matrix parameters with hybrid storage
 *
 * Shows both the expression and the resolved value for State Space matrices.
 * Supports inline editing of the expression.
 */

import React from "react";

interface MatrixDisplayProps {
  /** Parameter name (A, B, C, or D) */
  name: string;
  /** Current expression (e.g., "A_matrix" or "np.eye(2)") */
  expression: string | null;
  /** Resolved value (2D array) */
  value: number[][] | null;
  /** Whether the field is currently being edited */
  isEditing: boolean;
  /** Callback when user starts editing */
  onEdit: () => void;
  /** Callback when user finishes editing */
  onSave: (newExpression: string) => void;
  /** Callback when user cancels editing */
  onCancel: () => void;
}

export function MatrixDisplay({
  name,
  expression,
  value,
  isEditing,
  onEdit,
  onSave,
  onCancel,
}: MatrixDisplayProps) {
  const [editValue, setEditValue] = React.useState(expression || "");

  // Update edit value when expression changes
  React.useEffect(() => {
    setEditValue(expression || "");
  }, [expression]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSave(editValue);
    } else if (e.key === "Escape") {
      e.preventDefault();
      onCancel();
    }
  };

  return (
    <div className="matrix-display border border-gray-300 rounded p-1.5 mb-1.5">
      {/* Parameter name header */}
      <div className="font-semibold text-xs text-gray-700 mb-1">{name}</div>

      {/* Expression input/display */}
      <div className="mb-1">
        <div className="text-[10px] text-gray-500 mb-0.5">Expression:</div>
        {isEditing ? (
          <div>
            <input
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={() => onSave(editValue)}
              className="w-full px-1.5 py-0.5 text-xs border border-blue-500 rounded font-mono"
              placeholder="e.g., A_matrix or np.eye(2)"
              autoFocus
            />
            <div className="text-[10px] text-gray-400 mt-0.5">Enter to save, Esc to cancel</div>
          </div>
        ) : (
          <div
            onClick={onEdit}
            className="px-1.5 py-0.5 text-xs bg-gray-50 rounded font-mono cursor-pointer hover:bg-gray-100"
          >
            {expression || <span className="text-gray-400 italic text-[10px]">Click to add</span>}
          </div>
        )}
      </div>

      {/* Resolved value display */}
      {value && value.length > 0 && (
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Value:</div>
          <div className="matrix-value bg-blue-50 p-1 rounded text-[10px] font-mono overflow-auto max-h-20">
            {formatMatrix(value)}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Format a 2D array as a matrix string for display
 */
function formatMatrix(matrix: number[][]): string {
  if (!matrix || matrix.length === 0) {
    return "[]";
  }

  // Find max width for each column
  const numCols = Math.max(...matrix.map((row) => row.length));
  const colWidths: number[] = [];

  for (let col = 0; col < numCols; col++) {
    let maxWidth = 0;
    for (const row of matrix) {
      if (col < row.length) {
        const str = formatNumber(row[col]);
        maxWidth = Math.max(maxWidth, str.length);
      }
    }
    colWidths.push(maxWidth);
  }

  // Format each row
  const lines = matrix.map((row) => {
    const cells = row.map((val, col) => {
      const str = formatNumber(val);
      return str.padStart(colWidths[col], " ");
    });
    return `[${cells.join("  ")}]`;
  });

  return lines.join("\n");
}

/**
 * Format a number for display (handle scientific notation, etc.)
 */
function formatNumber(num: number): string {
  // Handle special values
  if (!isFinite(num)) {
    return String(num);
  }

  // Use fixed-point for small numbers, scientific for very large/small
  if (Math.abs(num) < 0.001 && num !== 0) {
    return num.toExponential(2);
  } else if (Math.abs(num) > 1000) {
    return num.toExponential(2);
  } else {
    // Round to 3 decimal places
    return num.toFixed(3);
  }
}
