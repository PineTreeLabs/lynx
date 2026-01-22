// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for port marker visibility hook.
 *
 * Following TDD: Tests for connection state detection from edges array.
 * Note: These tests use unit testing approach - testing the logic directly
 * rather than through renderHook which requires complex React Flow context setup.
 */

import { describe, test, expect } from "vitest";
import type { Edge } from "reactflow";

// Import the underlying logic (we'll export this from the hook file)
import { isPortConnected } from "./usePortMarkerVisibility";

describe("Port Connection Detection Logic", () => {
  describe("Connection detection", () => {
    test("returns false when no edges exist", () => {
      // Given: Empty edges array
      const edges: Edge[] = [];

      // When: Check if port is connected
      const result = isPortConnected("block-1", "in", edges);

      // Then: Port is not connected
      expect(result).toBe(false);
    });

    test("returns true when edge connects to input port", () => {
      // Given: Edge connected to target port
      const edges = [
        {
          id: "e1",
          source: "block-0",
          sourceHandle: "out",
          target: "block-1",
          targetHandle: "in",
        },
      ];

      // When: Check if input port is connected
      const result = isPortConnected("block-1", "in", edges);

      // Then: Port is connected
      expect(result).toBe(true);
    });

    test("returns true when edge connects to output port", () => {
      // Given: Edge connected from source port
      const edges = [
        {
          id: "e1",
          source: "block-1",
          sourceHandle: "out",
          target: "block-2",
          targetHandle: "in",
        },
      ];

      // When: Check if output port is connected
      const result = isPortConnected("block-1", "out", edges);

      // Then: Port is connected
      expect(result).toBe(true);
    });

    test("ignores edges connected to other blocks", () => {
      // Given: Edges between other blocks
      const edges = [
        {
          id: "e1",
          source: "block-0",
          sourceHandle: "out",
          target: "block-2",
          targetHandle: "in",
        },
      ];

      // When: Check if port is connected
      const result = isPortConnected("block-1", "in", edges);

      // Then: Port is not connected
      expect(result).toBe(false);
    });

    test("ignores edges connected to different ports on same block", () => {
      // Given: Edge connected to different port
      const edges = [
        {
          id: "e1",
          source: "block-0",
          sourceHandle: "out",
          target: "block-1",
          targetHandle: "in2", // Different port
        },
      ];

      // When: Check if 'in' port is connected
      const result = isPortConnected("block-1", "in", edges);

      // Then: Port is not connected
      expect(result).toBe(false);
    });

    test("returns true when multiple edges connect to same port", () => {
      // Given: Multiple edges to same input port
      const edges = [
        {
          id: "e1",
          source: "block-0",
          sourceHandle: "out",
          target: "block-1",
          targetHandle: "in",
        },
        {
          id: "e2",
          source: "block-2",
          sourceHandle: "out",
          target: "block-1",
          targetHandle: "in",
        },
      ];

      // When: Check if port is connected
      const result = isPortConnected("block-1", "in", edges);

      // Then: Port is connected (at least one edge)
      expect(result).toBe(true);
    });
  });

  describe("Edge cases", () => {
    test("handles empty string port ID", () => {
      const edges: Edge[] = [];
      const result = isPortConnected("block-1", "", edges);
      expect(result).toBe(false);
    });

    test("handles empty string block ID", () => {
      const edges: Edge[] = [];
      const result = isPortConnected("", "in", edges);
      expect(result).toBe(false);
    });

    test("handles edges with undefined handles", () => {
      const edges = [
        {
          id: "e1",
          source: "block-1",
          sourceHandle: undefined,
          target: "block-2",
          targetHandle: "in",
        },
      ];

      const result = isPortConnected("block-1", "out", edges);
      expect(result).toBe(false);
    });
  });
});
