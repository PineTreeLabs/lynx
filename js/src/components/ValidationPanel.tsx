// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * ValidationPanel - Displays validation errors and warnings
 *
 * Shows validation feedback from Python backend (connection validation, etc.)
 */

import React from "react";

export interface ValidationPanelProps {
  validationResult: {
    is_valid: boolean;
    errors: string[];
    warnings: string[];
  } | null;
  onClose: () => void;
}

export function ValidationPanel({ validationResult, onClose }: ValidationPanelProps) {
  // Don't render if no validation result or no messages
  if (
    !validationResult ||
    (validationResult.errors.length === 0 && validationResult.warnings.length === 0)
  ) {
    return null;
  }

  const hasErrors = validationResult.errors.length > 0;
  const hasWarnings = validationResult.warnings.length > 0;

  return (
    <div className="absolute top-4 right-4 z-50 max-w-md">
      <div
        className={`rounded-lg shadow-lg border-2 ${hasErrors ? "border-red-500 bg-red-50" : "border-yellow-500 bg-yellow-50"}`}
      >
        {/* Header */}
        <div
          className={`flex items-center justify-between px-4 py-2 ${hasErrors ? "bg-red-100" : "bg-yellow-100"}`}
        >
          <h3 className={`font-semibold text-sm ${hasErrors ? "text-red-800" : "text-yellow-800"}`}>
            {hasErrors ? "Validation Errors" : "Validation Warnings"}
          </h3>
          <button
            onClick={onClose}
            className={`text-lg font-bold ${hasErrors ? "text-red-600 hover:text-red-800" : "text-yellow-600 hover:text-yellow-800"}`}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div className="px-4 py-3 space-y-2">
          {/* Errors */}
          {hasErrors && (
            <div>
              {validationResult.errors.map((error, index) => (
                <div
                  key={`error-${index}`}
                  className="flex items-start gap-2 text-sm text-red-700 mb-2"
                >
                  <span className="font-bold">•</span>
                  <span>{error}</span>
                </div>
              ))}
            </div>
          )}

          {/* Warnings */}
          {hasWarnings && (
            <div>
              {validationResult.warnings.map((warning, index) => (
                <div
                  key={`warning-${index}`}
                  className="flex items-start gap-2 text-sm text-yellow-700 mb-2"
                >
                  <span className="font-bold">•</span>
                  <span>{warning}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
