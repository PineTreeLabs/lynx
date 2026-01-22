// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for LaTeX generation utilities.
 *
 * Following TDD: Tests for default LaTeX generation for each block type.
 * Tests T024-T026.
 */

import { describe, test, expect } from "vitest";
import {
  generateStateSpaceLatex,
  generateTransferFunctionLatex,
  generateGainLatex,
} from "./latexGeneration";

describe("LaTeX Generation", () => {
  describe("StateSpace LaTeX generation", () => {
    test("generates symbolic state-space equations - T024", () => {
      const latex = generateStateSpaceLatex();

      // Should contain symbolic notation (not expanded matrices)
      expect(latex).toContain("\\dot{x}");
      expect(latex).toContain("Ax");
      expect(latex).toContain("Bu");
      expect(latex).toContain("y");
      expect(latex).toContain("Cx");
      expect(latex).toContain("Du");
    });

    test("returns consistent format", () => {
      const latex1 = generateStateSpaceLatex();
      const latex2 = generateStateSpaceLatex();

      // Should be deterministic
      expect(latex1).toBe(latex2);
    });
  });

  describe("TransferFunction LaTeX generation", () => {
    test("generates polynomial fraction with formatted coefficients - T025", () => {
      const latex = generateTransferFunctionLatex([1, 2.5, 0.00123], [1, 0.5, 1234]);

      // Should be a fraction
      expect(latex).toContain("\\frac{");
      expect(latex).toContain("}");

      // Should contain polynomial terms
      expect(latex).toContain("s");

      // Should handle formatting
      expect(latex).toContain("2.5");
    });

    test("handles simple transfer functions", () => {
      const latex = generateTransferFunctionLatex([1], [1, 1]);

      expect(latex).toContain("\\frac{");
      // Numerator should be constant
      expect(latex).toMatch(/\\frac\{1\}/);
    });

    test("handles exponential notation in coefficients", () => {
      const latex = generateTransferFunctionLatex([0.00456], [1234]);

      // Small and large numbers should use exponential notation with × 10^{n}
      expect(latex).toContain("\\times");
      expect(latex).toContain("10^{");
      expect(latex).toContain("-3"); // Small number exponent
      expect(latex).toContain("3}"); // Large number exponent (could be {3} or {-3})
    });

    test("handles invalid parameters", () => {
      const latex = generateTransferFunctionLatex([], []);
      expect(latex).toContain("Invalid");
    });

    test("handles zero coefficients", () => {
      const latex = generateTransferFunctionLatex([1, 0, 3], [1, 2]);

      // Should skip zero coefficient
      expect(latex).toContain("s^{2}");
      expect(latex).toContain("3");
      // Should not have "+ 0s" or similar
      expect(latex).not.toMatch(/\+ 0/);
    });

    test("handles descending powers", () => {
      const latex = generateTransferFunctionLatex([1, 2, 3], [1]);

      // Should have s^2, s, and constant
      expect(latex).toContain("s^{2}");
      expect(latex).toContain("2s");
      expect(latex).toContain("3");
    });

    test("handles scalar numerator", () => {
      const latex = generateTransferFunctionLatex(1.32, [1, 1]);

      // Should treat scalar as constant term
      expect(latex).toContain("\\frac{");
      expect(latex).toContain("1.32");
      // Should not show "0"
      expect(latex).not.toBe("\\frac{0}{s + 1}");
    });

    test("handles scalar denominator", () => {
      const latex = generateTransferFunctionLatex([1, 2], 5);

      // Should treat scalar as constant term
      expect(latex).toContain("\\frac{");
      expect(latex).toContain("5");
      // Should not show "0"
      expect(latex).not.toContain("}{0}");
    });

    test("handles both scalar numerator and denominator", () => {
      const latex = generateTransferFunctionLatex(2.5, 3.7);

      // Should treat both as constant terms
      expect(latex).toContain("\\frac{");
      expect(latex).toContain("2.5");
      expect(latex).toContain("3.7");
      // Should not show "0"
      expect(latex).not.toContain("0");
    });
  });

  describe("Gain LaTeX generation", () => {
    test("generates formatted numerical value - T026", () => {
      const latex = generateGainLatex(123.456);

      // Should be 3 significant figures
      expect(latex).toBe("123");
    });

    test("handles small gain values", () => {
      const latex = generateGainLatex(0.00456);

      // Should use exponential notation
      expect(latex).toContain("e");
    });

    test("handles large gain values", () => {
      const latex = generateGainLatex(1234);

      // Should use exponential notation
      expect(latex).toContain("e");
    });

    test("handles negative gains", () => {
      const latex = generateGainLatex(-5.5);

      expect(latex).toContain("-");
      expect(latex).toBe("-5.5");
    });

    test("handles zero gain", () => {
      const latex = generateGainLatex(0);
      expect(latex).toBe("0");
    });

    test("handles invalid parameters", () => {
      const latex = generateGainLatex(NaN);
      expect(latex).toContain("Invalid");
    });
  });

  describe("edge cases", () => {
    test("handles very long polynomials", () => {
      const latex = generateTransferFunctionLatex([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1]);

      expect(latex).toContain("s^{9}");
      expect(latex).toContain("10"); // Constant term
    });

    test("handles all-zero numerator except leading coefficient", () => {
      const latex = generateTransferFunctionLatex([1, 0, 0], [1, 1, 1]);

      expect(latex).toContain("s^{2}");
      // Should not show zero terms
      expect(latex).not.toMatch(/\+ 0/);
    });
  });
});
