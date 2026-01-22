// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * ValidationStatusIcon - Compact validation status indicator for control panel
 *
 * Shows a status icon (✓/⚠/❌) in the control button stack that expands on click to show validation details.
 */

import React, { useState } from "react";

export interface ValidationStatusIconProps {
  validationResult: {
    is_valid: boolean;
    errors: string[];
    warnings: string[];
  } | null;
}

export function ValidationStatusIcon({ validationResult }: ValidationStatusIconProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Determine status based on validation result
  const hasErrors = validationResult?.errors?.length ?? 0 > 0;
  const hasWarnings = validationResult?.warnings?.length ?? 0 > 0;
  const isValid = !hasErrors && !hasWarnings;

  // Determine icon, colors based on validation state
  let iconPath: string;
  let fillColor: string;
  let panelBgColor: string;
  let panelBorderColor: string;
  let title: string;

  if (hasErrors) {
    // Red X for errors
    fillColor = "var(--color-error)";
    panelBgColor = "bg-red-50";
    panelBorderColor = "border-red-500";
    title = "Validation Errors";
    // X icon (circle with X)
    iconPath =
      "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z";
  } else if (hasWarnings) {
    // Yellow warning triangle
    fillColor = "var(--color-warning)";
    panelBgColor = "bg-yellow-50";
    panelBorderColor = "border-yellow-500";
    title = "Validation Warnings";
    // Warning triangle icon
    iconPath = "M12 2L1 21h22L12 2zm0 3.99L19.53 19H4.47L12 5.99zM11 16h2v2h-2v-2zm0-6h2v4h-2v-4z";
  } else {
    // Green checkmark
    fillColor = "var(--color-success)";
    panelBgColor = "bg-green-50";
    panelBorderColor = "border-green-500";
    title = "Valid";
    // Checkmark icon
    iconPath =
      "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z";
  }

  return (
    <>
      {/* Control Button - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="react-flow__controls-button validation-button"
        title={title}
        aria-label={title}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill={fillColor}
          style={{
            width: "100%",
            height: "100%",
          }}
        >
          <path d={iconPath} />
        </svg>
      </button>

      {/* Expanded Details Panel - positioned to the right of controls */}
      {isExpanded && (
        <div
          className={`absolute bottom-0 left-12 z-40 rounded-lg shadow-lg border-2 ${panelBorderColor} ${panelBgColor} max-w-2xl`}
          style={{ marginBottom: "10px", minWidth: "500px" }}
        >
          {/* Header */}
          <div
            className={`flex items-center justify-between px-4 py-2 border-b ${panelBorderColor}`}
          >
            <h3 className="font-semibold text-xs">{title}</h3>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-lg font-bold hover:opacity-70"
              aria-label="Close"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="px-4 py-3 space-y-2 max-h-64 overflow-y-auto">
            {/* Errors */}
            {hasErrors && validationResult && (
              <div>
                {validationResult.errors.map((error, index) => (
                  <div
                    key={`error-${index}`}
                    className="flex items-start gap-2 text-xs text-red-700 mb-2"
                  >
                    <span className="font-bold">•</span>
                    <span>{error}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Warnings */}
            {hasWarnings && validationResult && (
              <div>
                {validationResult.warnings.map((warning, index) => (
                  <div
                    key={`warning-${index}`}
                    className="flex items-start gap-2 text-xs text-yellow-700 mb-2"
                  >
                    <span className="font-bold">•</span>
                    <span>{warning}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Valid message */}
            {isValid && (
              <div className="text-xs text-green-700">No validation errors or warnings.</div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
