// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * TransferFunctionParameterEditor tests
 *
 * Tests the specialized parameter editor for Transfer Function blocks
 */

import { describe, test, expect, vi, beforeEach } from "vitest";
import { render } from "@testing-library/react";
import TransferFunctionParameterEditor from "./TransferFunctionParameterEditor";
import type { Block } from "../../utils/traitletSync";
import { flushUpdates } from "../../test/setup";

/**
 * Create a mock Transfer Function block for testing
 */
const createTransferFunctionBlock = (
  numerator: number[] = [1],
  denominator: number[] = [1, 1],
  customLatex?: string
): Block => ({
  id: "tf-1",
  type: "transfer_function",
  position: { x: 0, y: 0 },
  parameters: [
    { name: "numerator", value: numerator },
    { name: "denominator", value: denominator },
  ],
  ports: [
    { id: "in", type: "input" },
    { id: "out", type: "output" },
  ],
  custom_latex: customLatex,
});

describe("TransferFunctionParameterEditor - Parameters", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("renders numerator input with correct initial value", async () => {
    const block = createTransferFunctionBlock([1, 2], [1, 3, 2]);
    const { container } = render(
      <TransferFunctionParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const inputs = container.querySelectorAll('input[type="text"]');
    expect(inputs.length).toBeGreaterThanOrEqual(2);
    // First input is numerator
    expect((inputs[0] as HTMLInputElement).value).toBe("1,2");
  });

  test("renders numerator with default 1 when no value", async () => {
    const block = createTransferFunctionBlock();
    const { container } = render(
      <TransferFunctionParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const inputs = container.querySelectorAll('input[type="text"]');
    expect((inputs[0] as HTMLInputElement).value).toBe("1");
  });

  test("renders denominator input with correct initial value", async () => {
    const block = createTransferFunctionBlock([1, 2], [1, 3, 2]);
    const { container } = render(
      <TransferFunctionParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const inputs = container.querySelectorAll('input[type="text"]');
    // Second input is denominator
    expect((inputs[1] as HTMLInputElement).value).toBe("1,3,2");
  });

  test("renders denominator with default [1, 1] when no value", async () => {
    const block = createTransferFunctionBlock();
    const { container } = render(
      <TransferFunctionParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const inputs = container.querySelectorAll('input[type="text"]');
    expect((inputs[1] as HTMLInputElement).value).toBe("1,1");
  });
});

describe("TransferFunctionParameterEditor - Custom LaTeX", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("shows custom LaTeX checkbox for transfer function blocks", async () => {
    const block = createTransferFunctionBlock();
    const { container } = render(
      <TransferFunctionParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(false); // Initially unchecked when no custom_latex
  });

  test("checkbox is checked when custom_latex exists", async () => {
    const block = createTransferFunctionBlock([1], [1, 1], String.raw`\frac{1}{s+1}`);
    const { container } = render(
      <TransferFunctionParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(true);
  });

  test("shows textarea when custom LaTeX enabled", async () => {
    const block = createTransferFunctionBlock([1], [1, 1], String.raw`\frac{1}{s+1}`);
    const { container } = render(
      <TransferFunctionParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const textarea = container.querySelector("textarea");
    expect(textarea).not.toBeNull();
  });
});
