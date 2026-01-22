// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for port marker geometry utilities.
 *
 * Following TDD: Tests for arrowhead line calculations and geometry.
 */

import { describe, test, expect } from "vitest";
import { Position } from "reactflow";
import { calculateArrowheadLines } from "./portMarkerGeometry";

describe("Port Marker Geometry", () => {
  describe("Arrowhead line calculation", () => {
    test("generates right-pointing arrowhead for Position.Left", () => {
      // Given: 10px arrowhead for left position (input - tip at center)
      const result = calculateArrowheadLines({
        size: 10,
        position: Position.Left,
        portType: "input",
        isFlipped: false,
        isEquilateral: true,
      });

      // Then: Isosceles arrowhead (height=60% of width), tip at center
      // heightHalf = 3, halfSize = 5
      expect(result.line1).toEqual({ x1: 0, y1: 2, x2: 5, y2: 5 });
      expect(result.line2).toEqual({ x1: 0, y1: 8, x2: 5, y2: 5 });
      expect(result.viewBox).toBe("0 0 10 10");
    });

    test("generates right-pointing arrowhead for Position.Right", () => {
      // Given: 10px arrowhead for right position (output - base at center)
      const result = calculateArrowheadLines({
        size: 10,
        position: Position.Right,
        portType: "output",
        isFlipped: false,
        isEquilateral: true,
      });

      // Then: Isosceles arrowhead, base at center, tip extends right
      expect(result.line1).toEqual({ x1: 5, y1: 2, x2: 10, y2: 5 });
      expect(result.line2).toEqual({ x1: 5, y1: 8, x2: 10, y2: 5 });
      expect(result.viewBox).toBe("0 0 10 10");
    });

    test("generates down-pointing arrowhead for Position.Top", () => {
      // Given: 10px arrowhead for top position (input - tip at center)
      const result = calculateArrowheadLines({
        size: 10,
        position: Position.Top,
        portType: "input",
        isFlipped: false,
        isEquilateral: true,
      });

      // Then: Isosceles arrowhead, tip at center
      expect(result.line1).toEqual({ x1: 2, y1: 0, x2: 5, y2: 5 });
      expect(result.line2).toEqual({ x1: 8, y1: 0, x2: 5, y2: 5 });
      expect(result.viewBox).toBe("0 0 10 10");
    });

    test("generates up-pointing arrowhead for Position.Bottom input", () => {
      // Given: 10px arrowhead for bottom position (input - points up)
      const result = calculateArrowheadLines({
        size: 10,
        position: Position.Bottom,
        portType: "input",
        isFlipped: false,
        isEquilateral: true,
      });

      // Then: Up-pointing arrowhead, tip at center, base at bottom
      expect(result.line1).toEqual({ x1: 2, y1: 10, x2: 5, y2: 5 });
      expect(result.line2).toEqual({ x1: 8, y1: 10, x2: 5, y2: 5 });
      expect(result.viewBox).toBe("0 0 10 10");
    });

    test("respects custom size parameter", () => {
      // Given: 20px arrowhead
      const result = calculateArrowheadLines({
        size: 20,
        position: Position.Left,
        portType: "input",
        isFlipped: false,
        isEquilateral: true,
      });

      // Then: Lines scaled to 20px (heightHalf = 6, halfSize = 10)
      expect(result.line1).toEqual({ x1: 0, y1: 4, x2: 10, y2: 10 });
      expect(result.line2).toEqual({ x1: 0, y1: 16, x2: 10, y2: 10 });
      expect(result.viewBox).toBe("0 0 20 20");
    });

    test("handles isosceles triangles (non-equilateral)", () => {
      // Given: 10px arrowhead (isEquilateral flag currently unused)
      const result = calculateArrowheadLines({
        size: 10,
        position: Position.Right,
        portType: "output",
        isFlipped: false,
        isEquilateral: false,
      });

      // Then: Lines are defined
      expect(result.line1).toBeDefined();
      expect(result.line2).toBeDefined();
      expect(result.viewBox).toBe("0 0 10 10");
    });

    test("validates positive size", () => {
      // Given: Invalid size (0)
      expect(() => {
        calculateArrowheadLines({
          size: 0,
          position: Position.Left,
          portType: "input",
          isFlipped: false,
          isEquilateral: true,
        });
      }).toThrow("Size must be positive");
    });

    test("validates negative size", () => {
      // Given: Invalid size (negative)
      expect(() => {
        calculateArrowheadLines({
          size: -5,
          position: Position.Left,
          portType: "input",
          isFlipped: false,
          isEquilateral: true,
        });
      }).toThrow("Size must be positive");
    });
  });

  describe("Edge cases", () => {
    test("handles very small size (1px)", () => {
      const result = calculateArrowheadLines({
        size: 1,
        position: Position.Left,
        portType: "input",
        isFlipped: false,
        isEquilateral: true,
      });

      // heightHalf = 0.3, halfSize = 0.5
      expect(result.line1).toEqual({ x1: 0, y1: 0.2, x2: 0.5, y2: 0.5 });
      expect(result.line2).toEqual({ x1: 0, y1: 0.8, x2: 0.5, y2: 0.5 });
      expect(result.viewBox).toBe("0 0 1 1");
    });

    test("handles large size (50px)", () => {
      const result = calculateArrowheadLines({
        size: 50,
        position: Position.Right,
        portType: "output",
        isFlipped: false,
        isEquilateral: true,
      });

      // heightHalf = 15, halfSize = 25
      expect(result.line1).toEqual({ x1: 25, y1: 10, x2: 50, y2: 25 });
      expect(result.line2).toEqual({ x1: 25, y1: 40, x2: 50, y2: 25 });
      expect(result.viewBox).toBe("0 0 50 50");
    });
  });
});
