// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * useCustomLatex hook tests
 *
 * Tests custom LaTeX management logic extracted from ParameterPanel
 * Uses a test component wrapper for React 19 compatibility
 */

import { describe, test, expect, vi, beforeEach } from "vitest";
import { render, fireEvent } from "@testing-library/react";
import React from "react";
import { useCustomLatex } from "./useCustomLatex";
import { flushUpdates } from "../../../test/setup";

/**
 * Test component that uses the hook and exposes its state
 */
function TestCustomLatexComponent({
  blockId,
  initialValue,
  onUpdate,
}: {
  blockId: string;
  initialValue: string | undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onUpdate: (blockId: string, paramName: string, value: any) => void;
}) {
  const hook = useCustomLatex(blockId, initialValue, onUpdate);

  return (
    <div data-testid="test-wrapper">
      <div data-testid="use-custom-latex">{String(hook.useCustomLatex)}</div>
      <div data-testid="latex-value">{hook.latexValue}</div>
      <div data-testid="latex-error">{hook.latexError || "null"}</div>
      <button data-testid="toggle-btn" onClick={() => hook.handleToggle(!hook.useCustomLatex)}>
        Toggle
      </button>
      <button data-testid="toggle-off-btn" onClick={() => hook.handleToggle(false)}>
        Toggle Off
      </button>
      <button data-testid="toggle-on-btn" onClick={() => hook.handleToggle(true)}>
        Toggle On
      </button>
      <input
        data-testid="latex-input"
        value={hook.latexValue}
        onChange={(e) => hook.handleChange(e.target.value)}
      />
      <button data-testid="apply-btn" onClick={() => hook.handleApply()}>
        Apply
      </button>
    </div>
  );
}

describe("useCustomLatex - State Management", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("initializes useCustomLatex state to true when initialValue is provided", async () => {
    const initialLatex = String.raw`\alpha`; // LaTeX string with single backslash
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue={initialLatex}
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    expect(getByTestId("use-custom-latex").textContent).toBe("true");
    expect(getByTestId("latex-value").textContent).toBe(initialLatex);
    expect(getByTestId("latex-error").textContent).toBe("null");
  });

  test("initializes useCustomLatex state to false when initialValue is undefined", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue={undefined}
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    expect(getByTestId("use-custom-latex").textContent).toBe("false");
    expect(getByTestId("latex-value").textContent).toBe("");
    expect(getByTestId("latex-error").textContent).toBe("null");
  });

  test("initializes useCustomLatex state to false when initialValue is null", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        initialValue={null as any}
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    expect(getByTestId("use-custom-latex").textContent).toBe("false");
    expect(getByTestId("latex-value").textContent).toBe("");
    expect(getByTestId("latex-error").textContent).toBe("null");
  });
});

describe("useCustomLatex - Toggle Behavior", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("calls onUpdate with null when checkbox disabled", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    expect(getByTestId("use-custom-latex").textContent).toBe("true");

    fireEvent.click(getByTestId("toggle-off-btn"));
    await flushUpdates();

    expect(mockOnUpdate).toHaveBeenCalledWith("test-block-1", "custom_latex", null);
    expect(getByTestId("use-custom-latex").textContent).toBe("false");
    expect(getByTestId("latex-error").textContent).toBe("null");
  });

  test("does not call onUpdate when checkbox enabled", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue={undefined}
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    expect(getByTestId("use-custom-latex").textContent).toBe("false");

    fireEvent.click(getByTestId("toggle-on-btn"));
    await flushUpdates();

    expect(mockOnUpdate).not.toHaveBeenCalled();
    expect(getByTestId("use-custom-latex").textContent).toBe("true");
  });
});

describe("useCustomLatex - LaTeX Validation", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("sets error state for unbalanced braces (more open than close)", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    const input = getByTestId("latex-input") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "\\frac{1{2}" } });
    await flushUpdates();

    expect(getByTestId("latex-error").textContent).toBe("Unbalanced braces in LaTeX expression");
    expect(getByTestId("latex-value").textContent).toBe("\\frac{1{2}");
  });

  test("sets error state for unbalanced braces (more close than open)", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    const input = getByTestId("latex-input") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "\\frac{1}}" } });
    await flushUpdates();

    expect(getByTestId("latex-error").textContent).toBe("Unbalanced braces in LaTeX expression");
    expect(getByTestId("latex-value").textContent).toBe("\\frac{1}}");
  });

  test("clears error state when braces are balanced", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    const input = getByTestId("latex-input") as HTMLInputElement;

    // First set an error
    fireEvent.change(input, { target: { value: "\\frac{1{2}" } });
    await flushUpdates();
    expect(getByTestId("latex-error").textContent).toBe("Unbalanced braces in LaTeX expression");

    // Then fix it
    fireEvent.change(input, { target: { value: "\\frac{1}{2}" } });
    await flushUpdates();

    expect(getByTestId("latex-error").textContent).toBe("null");
    expect(getByTestId("latex-value").textContent).toBe("\\frac{1}{2}");
  });

  test("validates correctly for LaTeX with no braces", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    const input = getByTestId("latex-input") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "\\beta + \\gamma" } });
    await flushUpdates();

    expect(getByTestId("latex-error").textContent).toBe("null");
    expect(getByTestId("latex-value").textContent).toBe("\\beta + \\gamma");
  });
});

describe("useCustomLatex - Apply Behavior", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("calls onUpdate with value when LaTeX applied without errors", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    const input = getByTestId("latex-input") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "\\frac{1}{2}" } });
    await flushUpdates();

    fireEvent.click(getByTestId("apply-btn"));
    await flushUpdates();

    expect(mockOnUpdate).toHaveBeenCalledWith("test-block-1", "custom_latex", "\\frac{1}{2}");
  });

  test("calls onUpdate with null when LaTeX is empty string", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    const input = getByTestId("latex-input") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "" } });
    await flushUpdates();

    fireEvent.click(getByTestId("apply-btn"));
    await flushUpdates();

    expect(mockOnUpdate).toHaveBeenCalledWith("test-block-1", "custom_latex", null);
  });

  test("does not call onUpdate when validation error exists", async () => {
    const { getByTestId } = render(
      <TestCustomLatexComponent
        blockId="test-block-1"
        initialValue="\\alpha"
        onUpdate={mockOnUpdate}
      />
    );
    await flushUpdates();

    const input = getByTestId("latex-input") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "\\frac{1{2}" } });
    await flushUpdates();

    expect(getByTestId("latex-error").textContent).not.toBe("null");

    fireEvent.click(getByTestId("apply-btn"));
    await flushUpdates();

    expect(mockOnUpdate).not.toHaveBeenCalled();
  });
});
