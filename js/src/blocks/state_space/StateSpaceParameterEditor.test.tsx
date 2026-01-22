// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * StateSpaceParameterEditor tests
 *
 * Tests the specialized parameter editor for State Space blocks
 */

import { describe, test, expect, vi, beforeEach } from "vitest";
import { render } from "@testing-library/react";
import StateSpaceParameterEditor from "./StateSpaceParameterEditor";
import type { Block } from "../../utils/traitletSync";
import { flushUpdates } from "../../test/setup";

/**
 * Create a mock State Space block for testing
 */
const createStateSpaceBlock = (customLatex?: string): Block => ({
  id: "ss-1",
  type: "state_space",
  position: { x: 0, y: 0 },
  parameters: [
    {
      name: "A",
      value: [
        [1, 0],
        [0, 1],
      ],
      expression: "np.eye(2)",
    },
    { name: "B", value: [[1], [0]], expression: "[[1], [0]]" },
    { name: "C", value: [[1, 0]], expression: "[[1, 0]]" },
    { name: "D", value: [[0]], expression: "[[0]]" },
  ],
  ports: [
    { id: "in", type: "input" },
    { id: "out", type: "output" },
  ],
  custom_latex: customLatex,
});

describe("StateSpaceParameterEditor - Matrix Display", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("renders state space equation description text", async () => {
    const block = createStateSpaceBlock();
    const { container } = render(
      <StateSpaceParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const text = container.textContent || "";
    expect(text).toContain("State Space");
  });

  test("renders 4 matrix displays (A, B, C, D)", async () => {
    const block = createStateSpaceBlock();
    const { container } = render(
      <StateSpaceParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    // MatrixDisplay components have class="matrix-display"
    const matrixDisplays = container.querySelectorAll(".matrix-display");
    expect(matrixDisplays.length).toBe(4);
  });

  test("shows matrix names A, B, C, D", async () => {
    const block = createStateSpaceBlock();
    const { container } = render(
      <StateSpaceParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const text = container.textContent || "";
    expect(text).toContain("A");
    expect(text).toContain("B");
    expect(text).toContain("C");
    expect(text).toContain("D");
  });
});

describe("StateSpaceParameterEditor - Custom LaTeX", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("shows custom LaTeX checkbox for state space blocks", async () => {
    const block = createStateSpaceBlock();
    const { container } = render(
      <StateSpaceParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(false);
  });

  test("checkbox is checked when custom_latex exists", async () => {
    const block = createStateSpaceBlock(String.raw`\dot{x} = Ax + Bu`);
    const { container } = render(
      <StateSpaceParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(true);
  });

  test("shows textarea when custom LaTeX enabled", async () => {
    const block = createStateSpaceBlock(String.raw`\dot{x} = Ax + Bu`);
    const { container } = render(
      <StateSpaceParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const textarea = container.querySelector("textarea");
    expect(textarea).not.toBeNull();
  });
});
