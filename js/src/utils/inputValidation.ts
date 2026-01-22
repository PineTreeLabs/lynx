// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Input validation utilities for user-provided data
 */

import { VALIDATION } from "../config/constants";

export interface ValidationResult<T> {
  isValid: boolean;
  value: T;
  error?: string;
}

export class InputValidator {
  validateLabel(label: string, fieldName = "Label"): ValidationResult<string> {
    const sanitized = label.trim();

    if (sanitized.length > VALIDATION.maxLabelLength) {
      return {
        isValid: false,
        value: sanitized.substring(0, VALIDATION.maxLabelLength),
        error: `${fieldName} exceeds ${VALIDATION.maxLabelLength} characters`,
      };
    }

    if (/[\n\r\0]/.test(sanitized)) {
      return {
        isValid: false,
        value: sanitized.replace(/[\n\r\0]/g, " "),
        error: `${fieldName} contains invalid characters`,
      };
    }

    return { isValid: true, value: sanitized };
  }

  validateNumber(value: string, fieldName = "Value"): ValidationResult<number> {
    const trimmed = value.trim();

    if (trimmed === "") {
      return { isValid: false, value: 0, error: `${fieldName} cannot be empty` };
    }

    const num = parseFloat(trimmed);

    if (isNaN(num)) {
      return { isValid: false, value: 0, error: `${fieldName} must be a number` };
    }

    if (!isFinite(num)) {
      return { isValid: false, value: 0, error: `${fieldName} must be finite` };
    }

    return { isValid: true, value: num };
  }

  validateLatex(latex: string): ValidationResult<string> {
    const sanitized = latex.trim();

    if (sanitized.length > VALIDATION.maxLatexLength) {
      return {
        isValid: false,
        value: sanitized.substring(0, VALIDATION.maxLatexLength),
        error: `LaTeX exceeds ${VALIDATION.maxLatexLength} characters`,
      };
    }

    const openBraces = (sanitized.match(/{/g) || []).length;
    const closeBraces = (sanitized.match(/}/g) || []).length;

    if (openBraces !== closeBraces) {
      return { isValid: false, value: sanitized, error: "Unbalanced braces" };
    }

    return { isValid: true, value: sanitized };
  }
}

export const validator = new InputValidator();
