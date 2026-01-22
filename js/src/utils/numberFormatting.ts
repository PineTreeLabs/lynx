// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { NUMBER_FORMAT } from "../config/constants";

/**
 * Number formatting utilities for LaTeX rendering.
 *
 * Mirrors Python implementation in src/lynx/utils/latex_formatting.py
 * for consistent display across backend and frontend.
 */

/**
 * Format number to N significant figures with exponential notation for extremes.
 *
 * @param value - Number to format
 * @param sigFigs - Number of significant figures (default from NUMBER_FORMAT)
 * @returns Formatted string (e.g., "1.23", "4.56e-3", "1.23e+3")
 *
 * Exponential notation used based on NUMBER_FORMAT thresholds
 *
 * @example
 * formatNumber(0.00456) // '4.56e-3'
 * formatNumber(1234) // '1.23e+3'
 * formatNumber(123.456) // '123'
 * formatNumber(0) // '0'
 */
export function formatNumber(value: number, sigFigs: number = NUMBER_FORMAT.sigFigs): string {
  if (value === 0) {
    return "0";
  }

  const absValue = Math.abs(value);

  // Use exponential notation for very small or large numbers
  if (absValue < NUMBER_FORMAT.expNotationMin || absValue >= NUMBER_FORMAT.expNotationMax) {
    // Format in scientific notation with sigFigs-1 decimal places
    // Use LaTeX format: 1.23 × 10^{3} instead of 1.23e+3
    const expStr = value.toExponential(sigFigs - 1);
    const [mantissa, exponent] = expStr.split("e");
    const expInt = parseInt(exponent, 10);
    return `${mantissa} \\times 10^{${expInt}}`;
  } else {
    // For mid-range numbers, round to sigFigs significant figures
    // Calculate the magnitude (position of first significant digit)
    const magnitude = Math.floor(Math.log10(absValue));

    // Round to the appropriate decimal place
    const decimalPlaces = sigFigs - magnitude - 1;

    // Round the value
    if (decimalPlaces >= 0) {
      // Positive decimal places (e.g., 1.234 → 1.23)
      const formatted = value.toFixed(decimalPlaces);
      // Strip trailing zeros ONLY if there's a decimal point
      if (formatted.includes(".")) {
        return formatted.replace(/\.?0+$/, "");
      } else {
        return formatted;
      }
    } else {
      // Negative decimal places (e.g., 123.456 with 2 sig figs → 120)
      const roundedValue =
        Math.round(value * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces);
      // No stripping for integers
      return roundedValue.toFixed(0);
    }
  }
}
