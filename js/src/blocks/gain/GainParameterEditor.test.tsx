// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * GainParameterEditor tests
 *
 * Tests the specialized parameter editor for Gain blocks
 */

import { describe, test, expect, vi, beforeEach } from "vitest";
import { render, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GainParameterEditor from "./GainParameterEditor";
import type { Block } from "../../utils/traitletSync";
import { flushUpdates } from "../../test/setup";

/**
 * Create a mock Gain block for testing
 */
const createGainBlock = (K: number = 1, customLatex?: string): Block => ({
  id: "gain-1",
  type: "gain",
  position: { x: 0, y: 0 },
  parameters: [{ name: "K", value: K }],
  ports: [
    { id: "in", type: "input" },
    { id: "out", type: "output" },
  ],
  custom_latex: customLatex,
});

describe("GainParameterEditor - K Parameter", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("renders K parameter input with correct initial value", async () => {
    const block = createGainBlock(2.5);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = container.querySelector('input[type="text"]') as HTMLInputElement;
    expect(input).not.toBeNull();
    expect(input.value).toBe("2.5");
  });

  test("renders K parameter with default 1 when no value", async () => {
    const block = createGainBlock();
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = container.querySelector('input[type="text"]') as HTMLInputElement;
    expect(input).not.toBeNull();
    expect(input.value).toBe("1");
  });

  test("calls onUpdate when K input blurred", async () => {
    const user = userEvent.setup();
    const block = createGainBlock(1);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = container.querySelector('input[type="text"]') as HTMLInputElement;
    expect(input).not.toBeNull();

    await user.click(input);
    await user.clear(input);
    await user.type(input, "3.5");
    await user.tab(); // Tab away to blur

    expect(mockOnUpdate).toHaveBeenCalledWith("gain-1", "K", "3.5");
  });

  test("calls onUpdate when Enter pressed in K input", async () => {
    const user = userEvent.setup();
    const block = createGainBlock(1);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = container.querySelector('input[type="text"]') as HTMLInputElement;
    expect(input).not.toBeNull();

    await user.click(input);
    await user.clear(input);
    await user.type(input, "2*np.pi{Enter}");

    // Enter should call onUpdate directly
    expect(mockOnUpdate).toHaveBeenCalledWith("gain-1", "K", "2*np.pi");
  });
});

describe("GainParameterEditor - Custom LaTeX", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("shows custom LaTeX checkbox for gain blocks", async () => {
    const block = createGainBlock(1);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(false); // Initially unchecked when no custom_latex
  });

  test("checkbox is checked when custom_latex exists", async () => {
    const block = createGainBlock(1, String.raw`\alpha`);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(true);
  });

  test("toggles custom LaTeX section when checkbox clicked", async () => {
    const block = createGainBlock(1);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    // Initially, textarea should not be visible
    let textarea = container.querySelector("textarea");
    expect(textarea).toBeNull();

    // Click checkbox to enable
    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    fireEvent.click(checkbox);
    await flushUpdates();

    // Now textarea should be visible
    textarea = container.querySelector("textarea");
    expect(textarea).not.toBeNull();
  });

  test("updates custom LaTeX textarea value on change", async () => {
    const block = createGainBlock(1, String.raw`\alpha`);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    expect(textarea).not.toBeNull();

    const newLatex = String.raw`\beta`;
    fireEvent.change(textarea, { target: { value: newLatex } });
    await flushUpdates();

    expect(textarea.value).toBe(newLatex);
  });

  test("validates LaTeX - unbalanced braces shows error", async () => {
    const block = createGainBlock(1, String.raw`\alpha`);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    const invalidLatex = String.raw`\frac{1{2}`;
    fireEvent.change(textarea, { target: { value: invalidLatex } });
    await flushUpdates();

    // Should show error message
    const errorText = container.textContent;
    expect(errorText).toContain("Unbalanced braces");
  });

  test("applies custom LaTeX on blur", async () => {
    const block = createGainBlock(1, String.raw`\alpha`);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    const newLatex = String.raw`\frac{1}{2}`;
    fireEvent.change(textarea, { target: { value: newLatex } });
    fireEvent.blur(textarea);
    await flushUpdates();

    expect(mockOnUpdate).toHaveBeenCalledWith("gain-1", "custom_latex", newLatex);
  });

  test("does not apply custom LaTeX if validation error exists", async () => {
    const block = createGainBlock(1, String.raw`\alpha`);
    const { container } = render(<GainParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    const invalidLatex = String.raw`\frac{1{2}`;

    fireEvent.change(textarea, { target: { value: invalidLatex } });
    await flushUpdates();

    // Clear any previous calls
    mockOnUpdate.mockClear();

    // Try to apply (blur)
    fireEvent.blur(textarea);
    await flushUpdates();

    // Should NOT call onUpdate because of validation error
    expect(mockOnUpdate).not.toHaveBeenCalled();
  });
});
