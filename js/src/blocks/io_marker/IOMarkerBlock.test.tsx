// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * IOMarkerBlock tests
 *
 * Tests the IOMarker block visualization component
 */

import { describe, test, expect, vi } from "vitest";
import { render } from "@testing-library/react";
import { ReactFlowProvider } from "reactflow";
import { AnyWidgetModelContext } from "../../context/AnyWidgetModel";
import IOMarkerBlock from "./IOMarkerBlock";
import type { Block } from "../../utils/traitletSync";
import { flushUpdates } from "../../test/setup";

/**
 * Wrapper to provide ReactFlow and AnyWidget context for testing
 */
const renderIOMarkerBlock = (data: Block, props = {}) => {
  const mockModel = {
    get: vi.fn(),
    set: vi.fn(),
    save_changes: vi.fn(),
  };

  return render(
    <AnyWidgetModelContext.Provider value={mockModel}>
      <ReactFlowProvider>
        <IOMarkerBlock data={data} id={data.id} selected={false} {...props} />
      </ReactFlowProvider>
    </AnyWidgetModelContext.Provider>
  );
};

/**
 * Create a mock InputMarker block for testing
 */
const createInputMarkerBlock = (index: number = 0, customLatex?: string): Block => ({
  id: "input-1",
  type: "io_marker",
  position: { x: 0, y: 0 },
  parameters: [
    { name: "marker_type", value: "input" },
    { name: "label", value: "" },
    { name: "index", value: index },
  ],
  ports: [{ id: "out", type: "output" }],
  custom_latex: customLatex,
});

/**
 * Create a mock OutputMarker block for testing
 */
const createOutputMarkerBlock = (index: number = 0, customLatex?: string): Block => ({
  id: "output-1",
  type: "io_marker",
  position: { x: 0, y: 0 },
  parameters: [
    { name: "marker_type", value: "output" },
    { name: "label", value: "" },
    { name: "index", value: index },
  ],
  ports: [{ id: "in", type: "input" }],
  custom_latex: customLatex,
});

describe("IOMarkerBlock - Automatic Index Display (User Story 1)", () => {
  test("InputMarkers display auto-assigned indices", async () => {
    const blocks = [
      createInputMarkerBlock(0),
      createInputMarkerBlock(1),
      createInputMarkerBlock(2),
    ];

    for (let i = 0; i < blocks.length; i++) {
      const blockData = blocks[i];
      const { container } = renderIOMarkerBlock(blockData);
      await flushUpdates();

      // Additional wait for KaTeX rendering (useEffect in LaTeXRenderer)
      await new Promise((resolve) => setTimeout(resolve, 50));

      // Should display the index via LaTeXRenderer (KaTeX renders complex DOM)
      const latexRenderer = container.querySelector(".latex-renderer");
      expect(latexRenderer).not.toBeNull();

      // KaTeX content should be present with the rendered index
      // KaTeX renders the number inside .katex elements
      const katexElement = container.querySelector(".katex");
      expect(katexElement).not.toBeNull();
      expect(katexElement?.textContent).toBe(String(i));
    }
  });

  test("OutputMarkers display auto-assigned indices", async () => {
    const blocks = [
      createOutputMarkerBlock(0),
      createOutputMarkerBlock(1),
      createOutputMarkerBlock(2),
    ];

    for (let i = 0; i < blocks.length; i++) {
      const blockData = blocks[i];
      const { container } = renderIOMarkerBlock(blockData);
      await flushUpdates();

      // Additional wait for KaTeX rendering (useEffect in LaTeXRenderer)
      await new Promise((resolve) => setTimeout(resolve, 50));

      // Should display the index via LaTeXRenderer (KaTeX renders complex DOM)
      const latexRenderer = container.querySelector(".latex-renderer");
      expect(latexRenderer).not.toBeNull();

      // KaTeX content should be present with the rendered index
      // KaTeX renders the number inside .katex elements
      const katexElement = container.querySelector(".katex");
      expect(katexElement).not.toBeNull();
      expect(katexElement?.textContent).toBe(String(i));
    }
  });

  test("Index rendered via LaTeXRenderer component", async () => {
    const block = createInputMarkerBlock(5);
    const { container } = renderIOMarkerBlock(block);
    await flushUpdates();

    // LaTeXRenderer creates a div with class "latex-renderer"
    const latexRenderer = container.querySelector(".latex-renderer");
    expect(latexRenderer).toBeInTheDocument();

    // Should contain KaTeX-rendered content
    const katexContent = container.querySelector(".katex-content");
    expect(katexContent).toBeInTheDocument();
  });
});

describe("IOMarkerBlock - Custom LaTeX Override (User Story 2)", () => {
  test("Custom LaTeX overrides index display", async () => {
    const block = createInputMarkerBlock(0, "r");
    const { container } = renderIOMarkerBlock(block);
    await flushUpdates();

    // Additional wait for KaTeX rendering
    await new Promise((resolve) => setTimeout(resolve, 50));

    // Should display custom LaTeX "r" instead of index "0"
    const katexElement = container.querySelector(".katex");
    expect(katexElement).not.toBeNull();
    expect(katexElement?.textContent).toBe("r");
  });

  test("Invalid LaTeX shows error message", async () => {
    const block = createInputMarkerBlock(0, "\\invalid{");
    const { container } = renderIOMarkerBlock(block);
    await flushUpdates();

    // Additional wait for KaTeX error handling (useEffect in LaTeXRenderer)
    await new Promise((resolve) => setTimeout(resolve, 50));

    // LaTeXRenderer should show "Invalid LaTeX" for syntax errors
    expect(container.textContent).toContain("Invalid LaTeX");
  });

  test("Empty custom LaTeX shows index", async () => {
    const block = createInputMarkerBlock(3, "");
    const { container } = renderIOMarkerBlock(block);
    await flushUpdates();

    // Additional wait for KaTeX rendering
    await new Promise((resolve) => setTimeout(resolve, 50));

    // Should fall back to displaying index when custom_latex is empty
    const katexElement = container.querySelector(".katex");
    expect(katexElement).not.toBeNull();
    expect(katexElement?.textContent).toBe("3");
  });
});

/**
 * Performance Tests
 */
describe("IOMarkerBlock - Performance", () => {
  test("LaTeX rendering performance for 50 blocks", async () => {
    const blocks = Array.from({ length: 50 }, (_, i) => createInputMarkerBlock(i));

    const startTime = performance.now();

    // Render all 50 blocks
    for (const block of blocks) {
      renderIOMarkerBlock(block);
    }

    await flushUpdates();

    // Wait for KaTeX rendering
    await new Promise((resolve) => setTimeout(resolve, 100));

    const endTime = performance.now();
    const elapsed = endTime - startTime;
    const perBlock = elapsed / 50;

    // Verify <50ms per block (TS-005.1 requirement)
    expect(perBlock).toBeLessThan(50);

    // Log performance for monitoring
    console.log(
      `LaTeX rendering: ${perBlock.toFixed(2)}ms per block (50 blocks in ${elapsed.toFixed(2)}ms)`
    );
  });
});
