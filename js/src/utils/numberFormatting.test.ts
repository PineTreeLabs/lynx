// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for number formatting utilities.
 *
 * Following TDD: These tests mirror Python tests and validate TypeScript implementation.
 * Tests T018-T020.
 */

import { describe, test, expect } from "vitest";
import { formatNumber } from "./numberFormatting";

describe("formatNumber", () => {
  describe("exponential notation for small numbers", () => {
    test("formats small positive numbers (<0.01) - T018", () => {
      expect(formatNumber(0.00456)).toBe("4.56 \\times 10^{-3}");
      expect(formatNumber(0.00123)).toBe("1.23 \\times 10^{-3}");
      expect(formatNumber(0.001)).toBe("1.00 \\times 10^{-3}");
    });

    test("formats very small numbers", () => {
      expect(formatNumber(0.000001)).toBe("1.00 \\times 10^{-6}");
    });

    test("formats negative small numbers", () => {
      expect(formatNumber(-0.00789)).toBe("-7.89 \\times 10^{-3}");
    });
  });

  describe("exponential notation for large numbers", () => {
    test("formats large positive numbers (>=1000) - T019", () => {
      expect(formatNumber(1234)).toBe("1.23 \\times 10^{3}");
      expect(formatNumber(5678.9)).toBe("5.68 \\times 10^{3}");
      expect(formatNumber(1000)).toBe("1.00 \\times 10^{3}");
    });

    test("formats very large numbers", () => {
      expect(formatNumber(1000000)).toBe("1.00 \\times 10^{6}");
    });

    test("formats negative large numbers", () => {
      expect(formatNumber(-12345)).toBe("-1.23 \\times 10^{4}");
    });
  });

  describe("fixed notation for mid-range numbers", () => {
    test("formats mid-range numbers (0.01 to 999) - T020", () => {
      expect(formatNumber(123.456)).toBe("123");
      expect(formatNumber(12.3456)).toBe("12.3");
      expect(formatNumber(1.23456)).toBe("1.23");
      expect(formatNumber(0.123456)).toBe("0.123");
      expect(formatNumber(0.0123456)).toBe("0.0123");
    });

    test("formats edge cases at boundaries", () => {
      expect(formatNumber(0.01)).toBe("0.01"); // Lower boundary
      expect(formatNumber(999)).toBe("999"); // Upper boundary
      expect(formatNumber(999.9)).toBe("1000"); // Rounds to 1000
    });

    test("formats negative mid-range numbers", () => {
      expect(formatNumber(-45.678)).toBe("-45.7");
    });
  });

  describe("zero handling", () => {
    test("formats zero", () => {
      expect(formatNumber(0)).toBe("0");
      expect(formatNumber(0.0)).toBe("0");
      expect(formatNumber(-0.0)).toBe("0");
    });
  });

  describe("custom significant figures", () => {
    test("formats with 2 significant figures", () => {
      expect(formatNumber(123.456, 2)).toBe("120");
    });

    test("formats with 4 significant figures", () => {
      expect(formatNumber(12.3456, 4)).toBe("12.35");
    });

    test("formats with 5 significant figures", () => {
      expect(formatNumber(0.123456, 5)).toBe("0.12346");
    });
  });
});
