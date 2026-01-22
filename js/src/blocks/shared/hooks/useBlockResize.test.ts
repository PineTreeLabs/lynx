// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for useBlockResize hook - resize geometry calculations
 *
 * Tests cover:
 * - Anchor corner calculation (opposite corner stays fixed)
 * - Aspect ratio locking with Shift key
 * - Position stability during resize
 */

import { describe, it, expect } from "vitest";
import { calculateResizedBounds, constrainAspectRatio } from "./useBlockResize";

describe("calculateResizedBounds", () => {
  const initialBounds = {
    x: 100,
    y: 100,
    width: 120,
    height: 80,
  };

  it("resizes from bottom-right corner, top-left stays fixed", () => {
    const result = calculateResizedBounds(
      initialBounds,
      "bottom-right",
      200, // new width
      120 // new height
    );

    // Top-left corner should stay at (100, 100)
    expect(result.x).toBe(100);
    expect(result.y).toBe(100);
    expect(result.width).toBe(200);
    expect(result.height).toBe(120);
  });

  it("resizes from top-left corner, bottom-right stays fixed", () => {
    const result = calculateResizedBounds(
      initialBounds,
      "top-left",
      150, // new width
      100 // new height
    );

    // Bottom-right was at (220, 180), should stay there
    // So top-left moves to (220 - 150, 180 - 100) = (70, 80)
    expect(result.x).toBe(70);
    expect(result.y).toBe(80);
    expect(result.width).toBe(150);
    expect(result.height).toBe(100);
  });

  it("resizes from top-right corner, bottom-left stays fixed", () => {
    const result = calculateResizedBounds(
      initialBounds,
      "top-right",
      150, // new width
      100 // new height
    );

    // Bottom-left was at (100, 180), should stay there
    // So x stays at 100, y moves to (180 - 100) = 80
    expect(result.x).toBe(100);
    expect(result.y).toBe(80);
    expect(result.width).toBe(150);
    expect(result.height).toBe(100);
  });

  it("resizes from bottom-left corner, top-right stays fixed", () => {
    const result = calculateResizedBounds(
      initialBounds,
      "bottom-left",
      150, // new width
      100 // new height
    );

    // Top-right was at (220, 100), should stay there
    // So x moves to (220 - 150) = 70, y stays at 100
    expect(result.x).toBe(70);
    expect(result.y).toBe(100);
    expect(result.width).toBe(150);
    expect(result.height).toBe(100);
  });
});

describe("constrainAspectRatio", () => {
  it("constrains width based on height and aspect ratio", () => {
    const originalAspectRatio = 120 / 80; // 1.5
    const result = constrainAspectRatio(100, 200, originalAspectRatio);

    // Height is 200, so width should be 200 * 1.5 = 300
    expect(result.width).toBe(300);
    expect(result.height).toBe(200);
  });

  it("constrains height based on width and aspect ratio", () => {
    const originalAspectRatio = 120 / 80; // 1.5
    const result = constrainAspectRatio(180, 50, originalAspectRatio);

    // Width is 180, height would be 180 / 1.5 = 120
    // But we take the larger dimension change, so:
    // Width 180 -> height 120
    expect(result.width).toBe(180);
    expect(result.height).toBe(120);
  });

  it("maintains exact aspect ratio for square blocks", () => {
    const originalAspectRatio = 1.0; // Square
    const result = constrainAspectRatio(150, 100, originalAspectRatio);

    // Should constrain to equal width/height
    // Takes the larger dimension (150) and applies to both
    expect(result.width).toBe(150);
    expect(result.height).toBe(150);
  });
});

describe("position stability during resize", () => {
  it("anchor corner coordinates do not change", () => {
    const initialBounds = {
      x: 100,
      y: 100,
      width: 120,
      height: 80,
    };

    // Resize from bottom-right (anchor is top-left at 100, 100)
    const result = calculateResizedBounds(initialBounds, "bottom-right", 200, 150);

    // Anchor (top-left) should be exactly (100, 100)
    expect(result.x).toBeCloseTo(100, 10);
    expect(result.y).toBeCloseTo(100, 10);
  });

  it("multiple resize operations maintain anchor stability", () => {
    let bounds = {
      x: 100,
      y: 100,
      width: 120,
      height: 80,
    };

    // First resize
    bounds = calculateResizedBounds(bounds, "bottom-right", 150, 100);
    expect(bounds.x).toBe(100);
    expect(bounds.y).toBe(100);

    // Second resize (same anchor)
    bounds = calculateResizedBounds(bounds, "bottom-right", 200, 120);
    expect(bounds.x).toBe(100);
    expect(bounds.y).toBe(100);

    // Third resize (same anchor)
    bounds = calculateResizedBounds(bounds, "bottom-right", 80, 60);
    expect(bounds.x).toBe(100);
    expect(bounds.y).toBe(100);
  });
});
