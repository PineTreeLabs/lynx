// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * useCustomLatex - Hook for managing custom LaTeX input
 *
 * Extracted from ParameterPanel to be reused by multiple block editors
 * (Gain, TransferFunction, StateSpace).
 */

import { useState, useCallback } from "react";

export interface UseCustomLatexResult {
  /** Whether custom LaTeX is enabled */
  useCustomLatex: boolean;
  /** Current LaTeX value */
  latexValue: string;
  /** Validation error message, null if valid */
  latexError: string | null;
  /** Toggle custom LaTeX on/off */
  handleToggle: (checked: boolean) => void;
  /** Update LaTeX value and validate */
  handleChange: (value: string) => void;
  /** Apply LaTeX value (calls onUpdate if valid) */
  handleApply: () => void;
}

/**
 * Hook for managing custom LaTeX state and validation
 *
 * @param blockId - The ID of the block being edited
 * @param initialValue - Initial custom LaTeX value from block
 * @param onUpdate - Callback to update block parameter
 * @returns Custom LaTeX state and handlers
 */
export function useCustomLatex(
  blockId: string,
  initialValue: string | undefined,
  onUpdate: (blockId: string, paramName: string, value: unknown) => void
): UseCustomLatexResult {
  // Initialize checkbox state based on whether initialValue exists
  const [useCustomLatex, setUseCustomLatex] = useState(!!initialValue);

  // Initialize LaTeX value
  const [latexValue, setLatexValue] = useState(initialValue || "");

  // Track validation error
  const [latexError, setLatexError] = useState<string | null>(null);

  /**
   * Toggle custom LaTeX on/off
   * When disabled, clear the custom LaTeX value in the backend
   */
  const handleToggle = useCallback(
    (checked: boolean) => {
      setUseCustomLatex(checked);
      if (!checked) {
        // Clear custom LaTeX when checkbox is disabled
        onUpdate(blockId, "custom_latex", null);
        setLatexError(null);
      }
    },
    [blockId, onUpdate]
  );

  /**
   * Update LaTeX value and validate
   * Checks for balanced braces
   */
  const handleChange = useCallback((value: string) => {
    setLatexValue(value);

    // Basic validation - check if LaTeX has balanced braces
    const openBraces = (value.match(/\{/g) || []).length;
    const closeBraces = (value.match(/\}/g) || []).length;

    if (openBraces !== closeBraces) {
      setLatexError("Unbalanced braces in LaTeX expression");
    } else {
      setLatexError(null);
    }
  }, []);

  /**
   * Apply custom LaTeX value
   * Only calls onUpdate if validation passes
   */
  const handleApply = useCallback(() => {
    if (latexError) return; // Don't apply if there's an error

    // Send null for empty strings, otherwise send the value
    onUpdate(blockId, "custom_latex", latexValue || null);
  }, [blockId, latexValue, latexError, onUpdate]);

  return {
    useCustomLatex,
    latexValue,
    latexError,
    handleToggle,
    handleChange,
    handleApply,
  };
}
