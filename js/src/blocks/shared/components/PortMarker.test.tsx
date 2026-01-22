// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Tests for PortMarker component.
 *
 * Following TDD: Write tests FIRST, ensure they FAIL, then implement.
 * Tests T009-T012 combined in this file.
 */

import { describe, test, expect } from "vitest";
import { render } from "@testing-library/react";
import { Position } from "reactflow";
import PortMarker from "./PortMarker";
import { flushUpdates } from "../../../test/setup";

describe("PortMarker Component", () => {
  describe("Visibility Logic (T010)", () => {
    test("renders arrowhead when isConnected=false", async () => {
      // Given: Unconnected port
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Two line elements form arrowhead
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
    });

    test("hides triangle when isConnected=true", async () => {
      // Given: Connected port
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={true} />
      );
      await flushUpdates();

      // Then: No triangle rendered (returns null)
      const svg = container.querySelector("svg");
      expect(svg).not.toBeInTheDocument();
    });

    test("hides triangle when isDragTarget=true", async () => {
      // Given: Port is drag target during connection operation
      const { container } = render(
        <PortMarker position={Position.Left} isConnected={false} isDragTarget={true} />
      );
      await flushUpdates();

      // Then: No triangle rendered
      const svg = container.querySelector("svg");
      expect(svg).not.toBeInTheDocument();
    });

    test("hides triangle when both isConnected and isDragTarget are true", async () => {
      // Given: Port is connected AND drag target (edge case)
      const { container } = render(
        <PortMarker
          position={Position.Left}
          portType="input"
          isConnected={true}
          isDragTarget={true}
        />
      );
      await flushUpdates();

      // Then: No triangle rendered
      const svg = container.querySelector("svg");
      expect(svg).not.toBeInTheDocument();
    });

    test("shows arrowhead when isConnected=false and isDragTarget=false", async () => {
      // Given: Explicit false values
      const { container } = render(
        <PortMarker position={Position.Left} isConnected={false} isDragTarget={false} />
      );
      await flushUpdates();

      // Then: Arrowhead is visible
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
    });
  });

  describe("Geometry - Arrowhead Direction (T011)", () => {
    test("generates right-pointing arrowhead for Position.Left", async () => {
      // Given: Left position marker (input - tip at center)
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Isosceles arrowhead with tip at center (heightHalf=3)
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
      expect(lines[0]).toHaveAttribute("x1", "0");
      expect(lines[0]).toHaveAttribute("y1", "2");
      expect(lines[0]).toHaveAttribute("x2", "5");
      expect(lines[0]).toHaveAttribute("y2", "5");
      expect(lines[1]).toHaveAttribute("x1", "0");
      expect(lines[1]).toHaveAttribute("y1", "8");
      expect(lines[1]).toHaveAttribute("x2", "5");
      expect(lines[1]).toHaveAttribute("y2", "5");
    });

    test("generates right-pointing arrowhead for Position.Right", async () => {
      // Given: Right position marker (output - base at center)
      const { container } = render(
        <PortMarker position={Position.Right} portType="output" isConnected={false} />
      );
      await flushUpdates();

      // Then: Isosceles arrowhead with base at center
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
      expect(lines[0]).toHaveAttribute("x1", "5");
      expect(lines[0]).toHaveAttribute("y1", "2");
      expect(lines[0]).toHaveAttribute("x2", "10");
      expect(lines[0]).toHaveAttribute("y2", "5");
    });

    test("generates down-pointing arrowhead for Position.Top", async () => {
      // Given: Top position marker (input - tip at center)
      const { container } = render(
        <PortMarker position={Position.Top} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Isosceles arrowhead with tip at center
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
      expect(lines[0]).toHaveAttribute("x1", "2");
      expect(lines[0]).toHaveAttribute("y1", "0");
      expect(lines[0]).toHaveAttribute("x2", "5");
      expect(lines[0]).toHaveAttribute("y2", "5");
    });

    test("generates up-pointing arrowhead for Position.Bottom input", async () => {
      // Given: Bottom position marker (input - points up, like Sum block bottom)
      const { container } = render(
        <PortMarker position={Position.Bottom} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Up-pointing arrowhead, tip at center, base at bottom
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
      expect(lines[0]).toHaveAttribute("x1", "2");
      expect(lines[0]).toHaveAttribute("y1", "10");
      expect(lines[0]).toHaveAttribute("x2", "5");
      expect(lines[0]).toHaveAttribute("y2", "5");
    });

    test("uses custom size when provided", async () => {
      // Given: 20px marker size
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} size={20} />
      );
      await flushUpdates();

      // Then: Arrowhead scaled to 20px (heightHalf=6, halfSize=10)
      const lines = container.querySelectorAll("line");
      expect(lines[0]).toHaveAttribute("x2", "10");
      expect(lines[0]).toHaveAttribute("y2", "10");
    });

    test("uses default 10px size when not provided", async () => {
      // Given: No size prop
      const { container } = render(
        <PortMarker position={Position.Right} portType="output" isConnected={false} />
      );
      await flushUpdates();

      // Then: Default 10px arrowhead (base at center for output)
      const lines = container.querySelectorAll("line");
      expect(lines[0]).toHaveAttribute("x1", "5");
      expect(lines[0]).toHaveAttribute("x2", "10");
      expect(lines[0]).toHaveAttribute("y2", "5");
    });
  });

  describe("Styling (T012)", () => {
    test("applies primary-600 stroke color", async () => {
      // Given: PortMarker rendered
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Stroke uses theme color variable
      const lines = container.querySelectorAll("line");
      expect(lines[0]).toHaveAttribute("stroke", "var(--color-primary-600)");
      expect(lines[1]).toHaveAttribute("stroke", "var(--color-primary-600)");
    });

    test("applies correct stroke width", async () => {
      // Given: PortMarker rendered
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Stroke width is 2px (matches blocks and edges)
      const lines = container.querySelectorAll("line");
      expect(lines[0]).toHaveAttribute("stroke-width", "2");
      expect(lines[1]).toHaveAttribute("stroke-width", "2");
    });

    test("applies rounded line caps", async () => {
      // Given: PortMarker rendered
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Lines have round caps for smooth arrowhead appearance
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2); // Ensure lines exist
      expect(lines[0]).toBeTruthy(); // Ensure element is valid
      expect(lines[1]).toBeTruthy(); // Ensure element is valid
      expect(lines[0]).toHaveAttribute("stroke-linecap", "round");
      expect(lines[1]).toHaveAttribute("stroke-linecap", "round");
    });

    test("accepts custom className", async () => {
      // Given: Custom class provided
      const { container } = render(
        <PortMarker position={Position.Left} isConnected={false} className="custom-marker" />
      );
      await flushUpdates();

      // Then: SVG has custom class
      const svg = container.querySelector("svg");
      expect(svg).toHaveClass("custom-marker");
    });

    test("sets correct viewBox for SVG", async () => {
      // Given: Default size marker
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: ViewBox matches size
      const svg = container.querySelector("svg");
      expect(svg).toHaveAttribute("viewBox", "0 0 10 10");
    });

    test("sets correct viewBox for custom size", async () => {
      // Given: 20px marker
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} size={20} />
      );
      await flushUpdates();

      // Then: ViewBox scales
      const svg = container.querySelector("svg");
      expect(svg).toHaveAttribute("viewBox", "0 0 20 20");
    });
  });

  describe("Edge Cases", () => {
    test("handles isFlipped prop (inherits block transform)", async () => {
      // Given: Flipped block marker
      const { container } = render(
        <PortMarker
          position={Position.Left}
          portType="input"
          isConnected={false}
          isFlipped={true}
        />
      );
      await flushUpdates();

      // Then: Marker still renders (flip handled by parent block scaleX)
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
    });

    test("handles very small size (1px)", async () => {
      // Given: 1px marker
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} size={1} />
      );
      await flushUpdates();

      // Then: Arrowhead still renders with correct coordinates
      const lines = container.querySelectorAll("line");
      expect(lines[0]).toHaveAttribute("x2", "0.5");
      expect(lines[0]).toHaveAttribute("y2", "0.5");
    });

    test("handles large size (50px)", async () => {
      // Given: 50px marker
      const { container } = render(
        <PortMarker position={Position.Right} portType="output" isConnected={false} size={50} />
      );
      await flushUpdates();

      // Then: Arrowhead scales correctly (base at center for output)
      const lines = container.querySelectorAll("line");
      expect(lines[0]).toHaveAttribute("x1", "25");
      expect(lines[0]).toHaveAttribute("x2", "50");
      expect(lines[0]).toHaveAttribute("y2", "25");
    });
  });

  describe("Component Props Interface", () => {
    test("renders with all optional props omitted", async () => {
      // Given: Only required props
      const { container } = render(
        <PortMarker position={Position.Left} portType="input" isConnected={false} />
      );
      await flushUpdates();

      // Then: Renders successfully
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
    });

    test("renders with all optional props provided", async () => {
      // Given: All props specified
      const { container } = render(
        <PortMarker
          position={Position.Right}
          isConnected={false}
          isFlipped={true}
          isDragTarget={false}
          size={15}
          className="test-class"
        />
      );
      await flushUpdates();

      // Then: Renders successfully
      const lines = container.querySelectorAll("line");
      expect(lines).toHaveLength(2);
    });
  });
});
