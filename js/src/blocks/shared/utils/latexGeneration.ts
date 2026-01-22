// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * LaTeX generation utilities for block default rendering.
 *
 * Generates LaTeX strings for StateSpace, TransferFunction, and Gain blocks
 * based on their parameters. Uses formatNumber for consistent numerical display.
 */

import { formatNumber } from "../../../utils/numberFormatting";

/**
 * Generate default LaTeX for StateSpace block.
 * Shows symbolic state-space equations: ẋ = Ax + Bu, y = Cx + Du
 *
 * @returns LaTeX string for state-space representation
 *
 * @example
 * generateStateSpaceLatex()
 * // Returns: "\\dot{x} = Ax + Bu \\\\ y = Cx + Du"
 */
export function generateStateSpaceLatex(): string {
  // Always symbolic notation (not expanded matrices per research.md)
  return String.raw`\dot{x} = Ax + Bu \\ y = Cx + Du`;
}

/**
 * Generate default LaTeX for TransferFunction block.
 * Shows polynomial fraction with formatted coefficients.
 *
 * @param numerator - Numerator coefficients (descending powers) or scalar
 * @param denominator - Denominator coefficients (descending powers) or scalar
 * @returns LaTeX string for transfer function
 *
 * @example
 * generateTransferFunctionLatex([1, 2.5, 0.00123], [1, 0.5, 1234])
 * // Returns: "\\frac{s^2 + 2.5s + 1.23 \\times 10^{-3}}{s^2 + 0.5s + 1.23 \\times 10^3}"
 */
export function generateTransferFunctionLatex(
  numerator: number[] | number,
  denominator: number[] | number
): string {
  // Normalize scalars to arrays
  const numArray = Array.isArray(numerator) ? numerator : [numerator];
  const denArray = Array.isArray(denominator) ? denominator : [denominator];

  if (!numArray || numArray.length === 0 || !denArray || denArray.length === 0) {
    return "Invalid parameters";
  }

  const numLatex = formatPolynomial(numArray);
  const denLatex = formatPolynomial(denArray);

  return String.raw`\frac{${numLatex}}{${denLatex}}`;
}

/**
 * Generate default LaTeX for Gain block.
 * Shows formatted numerical value.
 *
 * @param K - Gain value
 * @returns LaTeX string for gain value
 *
 * @example
 * generateGainLatex(123.456)
 * // Returns: "123"
 */
export function generateGainLatex(K: number): string {
  if (K === null || K === undefined || isNaN(K)) {
    return "Invalid parameters";
  }
  return formatNumber(K);
}

/**
 * Format polynomial coefficients as LaTeX.
 * Handles descending powers, sign formatting, and coefficient display.
 *
 * @param coeffs - Polynomial coefficients [highest power ... constant]
 * @returns LaTeX string for polynomial
 *
 * @example
 * formatPolynomial([1, 2.5, 0.00123])
 * // Returns: "s^2 + 2.5s + 1.23 \\times 10^{-3}"
 */
function formatPolynomial(coeffs: number[]): string {
  if (!coeffs || coeffs.length === 0) {
    return "0";
  }

  const degree = coeffs.length - 1;
  const terms: string[] = [];

  for (let i = 0; i < coeffs.length; i++) {
    const coeff = coeffs[i];
    const power = degree - i;

    // Skip zero coefficients
    if (coeff === 0) {
      continue;
    }

    let term = "";

    // Format coefficient
    const absCoeff = Math.abs(coeff);
    const sign = coeff < 0 ? "-" : "+";

    // Coefficient display (skip "1" for s terms unless it's the constant)
    let coeffStr = "";
    if (power === 0 || absCoeff !== 1) {
      coeffStr = formatNumber(absCoeff);
      // Handle exponential notation in LaTeX
      coeffStr = coeffStr.replace(/e([+-])0?(\d+)/g, (_, sign, exp) => {
        return String.raw` \times 10^{${sign}${exp}}`;
      });
    }

    // Variable and power
    if (power === 0) {
      // Constant term
      term = coeffStr;
    } else if (power === 1) {
      // Linear term
      term = coeffStr ? `${coeffStr}s` : "s";
    } else {
      // Higher powers
      term = coeffStr ? `${coeffStr}s^{${power}}` : `s^{${power}}`;
    }

    // Add sign (except for first term if positive)
    if (terms.length === 0) {
      if (sign === "-") {
        term = `-${term}`;
      }
    } else {
      term = ` ${sign} ${term}`;
    }

    terms.push(term);
  }

  // Handle all-zero polynomial
  if (terms.length === 0) {
    return "0";
  }

  return terms.join("");
}
