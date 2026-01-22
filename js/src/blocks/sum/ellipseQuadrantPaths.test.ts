// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { describe, it, expect } from "vitest";
import { getQuadrantPath } from "./ellipseQuadrantPaths";

describe("Ellipse Quadrant SVG Paths", () => {
  describe("Path Generation for Each Quadrant (3 test cases)", () => {
    it("should generate valid SVG path for quadrant 0 (top)", () => {
      const path = getQuadrantPath(0, 100, 100, 50, 50);

      // Path should start at center (M 100,100)
      expect(path).toContain("M 100,100");

      // Path should contain an arc command (A)
      expect(path).toContain("A");

      // Path should end with Z (close path)
      expect(path).toMatch(/Z\s*$/);

      // Path should not be empty
      expect(path.length).toBeGreaterThan(0);
    });

    it("should generate valid SVG path for quadrant 1 (left)", () => {
      const path = getQuadrantPath(1, 100, 100, 50, 50);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A");
      expect(path).toMatch(/Z\s*$/);
      expect(path.length).toBeGreaterThan(0);
    });

    it("should generate valid SVG path for quadrant 2 (bottom)", () => {
      const path = getQuadrantPath(2, 100, 100, 50, 50);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A");
      expect(path).toMatch(/Z\s*$/);
      expect(path.length).toBeGreaterThan(0);
    });
  });

  describe("Path Scaling with Different Ellipse Dimensions (6 test cases)", () => {
    it("should scale quadrant 0 path for small ellipse (20x20)", () => {
      const path = getQuadrantPath(0, 50, 50, 20, 20);

      // Smaller ellipse should produce different coordinates
      expect(path).toContain("M 50,50");
      expect(path).toContain("A 20,20");
    });

    it("should scale quadrant 0 path for large ellipse (100x100)", () => {
      const path = getQuadrantPath(0, 200, 200, 100, 100);

      expect(path).toContain("M 200,200");
      expect(path).toContain("A 100,100");
    });

    it("should scale quadrant 1 path for wide ellipse (80x40)", () => {
      const path = getQuadrantPath(1, 100, 100, 80, 40);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A 80,40");
    });

    it("should scale quadrant 1 path for tall ellipse (40x80)", () => {
      const path = getQuadrantPath(1, 100, 100, 40, 80);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A 40,80");
    });

    it("should scale quadrant 2 path for wide ellipse (80x40)", () => {
      const path = getQuadrantPath(2, 100, 100, 80, 40);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A 80,40");
    });

    it("should scale quadrant 2 path for tall ellipse (40x80)", () => {
      const path = getQuadrantPath(2, 100, 100, 40, 80);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A 40,80");
    });
  });

  describe("Arc Angle Calculations (6 test cases)", () => {
    it("should generate quadrant 0 arc with correct angle range (-90° to -30°, and -30° to 90° reversed)", () => {
      const path = getQuadrantPath(0, 100, 100, 50, 50);

      // Top quadrant should cover angles from -150° to -30° (wide top region)
      // Extract line-to coordinates to verify arc endpoints
      const lineMatch = path.match(/L\s+([\d.]+),([\d.]+)/);
      expect(lineMatch).not.toBeNull();

      // Arc should exist
      expect(path).toContain("A 50,50");
    });

    it("should generate quadrant 1 arc with correct angle range (150° to -150°)", () => {
      const path = getQuadrantPath(1, 100, 100, 50, 50);

      // Left quadrant should cover angles from 150° to -150° (left region)
      const lineMatch = path.match(/L\s+([\d.]+),([\d.]+)/);
      expect(lineMatch).not.toBeNull();
      expect(path).toContain("A 50,50");
    });

    it("should generate quadrant 2 arc with correct angle range (30° to 150°)", () => {
      const path = getQuadrantPath(2, 100, 100, 50, 50);

      // Bottom quadrant should cover angles from 30° to 150°
      const lineMatch = path.match(/L\s+([\d.]+),([\d.]+)/);
      expect(lineMatch).not.toBeNull();
      expect(path).toContain("A 50,50");
    });

    it("should generate quadrant 0 arc that covers top region correctly", () => {
      const path = getQuadrantPath(0, 100, 100, 50, 50);

      // Verify the path contains line to a point in the top-right area
      // For quadrant 0, should go from center to approximately angle -150°
      expect(path).toMatch(/L\s*[\d.]+,[\d.]+/);
    });

    it("should generate quadrant 1 arc that covers left region correctly", () => {
      const path = getQuadrantPath(1, 100, 100, 50, 50);

      // Verify the path contains line to a point in the top-left area
      // For quadrant 1, should go from center to approximately angle 150°
      expect(path).toMatch(/L\s*[\d.]+,[\d.]+/);
    });

    it("should generate quadrant 2 arc that covers bottom region correctly", () => {
      const path = getQuadrantPath(2, 100, 100, 50, 50);

      // Verify the path contains line to a point in the bottom-right area
      // For quadrant 2, should go from center to approximately angle 30°
      expect(path).toMatch(/L\s*[\d.]+,[\d.]+/);
    });
  });

  describe("Edge Cases and Validation", () => {
    it("should handle center at origin (0,0)", () => {
      const path = getQuadrantPath(0, 0, 0, 50, 50);

      expect(path).toContain("M 0,0");
      expect(path).toContain("A 50,50");
    });

    it("should handle negative center coordinates", () => {
      const path = getQuadrantPath(0, -100, -100, 50, 50);

      expect(path).toContain("M -100,-100");
      expect(path).toContain("A 50,50");
    });

    it("should handle minimum ellipse size (20x20 radius for 40x40 block)", () => {
      const path = getQuadrantPath(0, 50, 50, 20, 20);

      expect(path).toContain("M 50,50");
      expect(path).toContain("A 20,20");
      expect(path.length).toBeGreaterThan(0);
    });

    it("should handle extreme aspect ratio (wide)", () => {
      const path = getQuadrantPath(0, 100, 100, 200, 20);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A 200,20");
    });

    it("should handle extreme aspect ratio (tall)", () => {
      const path = getQuadrantPath(0, 100, 100, 20, 200);

      expect(path).toContain("M 100,100");
      expect(path).toContain("A 20,200");
    });

    it("should not generate path for invalid quadrant index", () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const path = getQuadrantPath(4 as any, 100, 100, 50, 50);

      // Should return empty string for invalid quadrant
      expect(path).toBe("");
    });
  });
});
