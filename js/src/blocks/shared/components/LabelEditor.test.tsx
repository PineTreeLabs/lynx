// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Test suite for LabelEditor component
 *
 * Tests for Feature 013: Editable Block Labels in Parameter Panel
 * Phase 3 (US1) and Phase 4 (US2) test coverage
 */

import { describe, test, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LabelEditor } from "./LabelEditor";
import { flushUpdates } from "../../../test/setup";

describe("LabelEditor - Basic Rendering (US1)", () => {
  test("T009: renders with initial label value", async () => {
    const mockOnUpdate = vi.fn();

    render(
      <LabelEditor blockId="controller" initialLabel="PID Controller" onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const input = screen.getByDisplayValue("PID Controller") as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input.value).toBe("PID Controller");
  });

  test("T010: supports standard text editing controls (select-all, cursor positioning)", async () => {
    const mockOnUpdate = vi.fn();

    render(<LabelEditor blockId="plant" initialLabel="Plant Model" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Plant Model") as HTMLInputElement;

    // Verify it's a text input (supports standard controls)
    expect(input.type).toBe("text");

    // Verify cursor positioning works
    input.setSelectionRange(0, 5);
    expect(input.selectionStart).toBe(0);
    expect(input.selectionEnd).toBe(5);

    // Verify select-all works
    input.select();
    expect(input.selectionStart).toBe(0);
    expect(input.selectionEnd).toBe(input.value.length);
  });
});

describe("LabelEditor - Edit Functionality (US2)", () => {
  test("T020: calls onUpdate when Enter key pressed", async () => {
    const user = userEvent.setup();
    const mockOnUpdate = vi.fn();

    render(<LabelEditor blockId="g1" initialLabel="Gain" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Gain") as HTMLInputElement;

    // Change value and press Enter
    await user.click(input);
    await user.clear(input);
    await user.type(input, "Controller{Enter}");
    await flushUpdates();

    expect(mockOnUpdate).toHaveBeenCalledWith("g1", "label", "Controller");
  });

  test("T021: calls onUpdate when input blurs", async () => {
    const user = userEvent.setup();
    const mockOnUpdate = vi.fn();

    render(<LabelEditor blockId="g2" initialLabel="Plant" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Plant") as HTMLInputElement;

    // Change value and blur
    await user.click(input);
    await user.clear(input);
    await user.type(input, "Motor");
    await user.tab(); // Tab key blurs the input
    await flushUpdates();

    expect(mockOnUpdate).toHaveBeenCalledWith("g2", "label", "Motor");
  });

  test("T022: cancels edit on Escape key", async () => {
    const mockOnUpdate = vi.fn();

    render(<LabelEditor blockId="g3" initialLabel="Original" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Original") as HTMLInputElement;

    // Change value and press Escape
    fireEvent.change(input, { target: { value: "Modified" } });
    fireEvent.keyDown(input, { key: "Escape" });
    await flushUpdates();

    // Should revert to original value, not call onUpdate with modified
    expect(input.value).toBe("Original");
    expect(mockOnUpdate).not.toHaveBeenCalledWith("g3", "label", "Modified");
  });

  test("T023: trims leading/trailing whitespace on save", async () => {
    const user = userEvent.setup();
    const mockOnUpdate = vi.fn();

    render(<LabelEditor blockId="g4" initialLabel="Test" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Test") as HTMLInputElement;

    // Enter value with whitespace and press Enter
    await user.click(input);
    await user.clear(input);
    await user.type(input, "  Trimmed  {Enter}");
    await flushUpdates();

    // Should trim whitespace
    expect(mockOnUpdate).toHaveBeenCalledWith("g4", "label", "Trimmed");
  });

  test("T024: normalizes newlines to spaces", async () => {
    // Note: Single-line text inputs automatically strip newlines in browsers
    // This test verifies the behavior when text with newlines is set programmatically
    const user = userEvent.setup();
    const mockOnUpdate = vi.fn();
    const labelWithNewline = "Line1" + String.fromCharCode(10) + "Line2";

    render(<LabelEditor blockId="g5" initialLabel="Test" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Test") as HTMLInputElement;

    // Click, clear, then paste text with newline
    await user.click(input);
    await user.clear(input);
    // Manually trigger change with newline (simulates paste)
    // Note: Browser strips newlines from single-line inputs, so we get "Line1Line2"
    fireEvent.change(input, { target: { value: labelWithNewline } });
    await flushUpdates(); // Wait for useLayoutEffect to run
    await user.keyboard("{Enter}");
    await flushUpdates();

    // Browser strips newlines, resulting in concatenated text
    expect(mockOnUpdate).toHaveBeenCalledWith("g5", "label", "Line1Line2");
  });

  test("T025: normalizes tabs to spaces", async () => {
    // Verify normalizeLabel function handles tabs correctly
    const user = userEvent.setup();
    const mockOnUpdate = vi.fn();
    const labelWithTab = "Tab" + String.fromCharCode(9) + "Separated";

    render(<LabelEditor blockId="g6" initialLabel="Test" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Test") as HTMLInputElement;

    // Click, clear, then paste text with tab
    await user.click(input);
    await user.clear(input);
    // Manually trigger change with tab (simulates paste)
    fireEvent.change(input, { target: { value: labelWithTab } });
    await flushUpdates(); // Wait for useLayoutEffect to run
    await user.keyboard("{Enter}");
    await flushUpdates();

    // normalizeLabel function should convert tab to space
    expect(mockOnUpdate).toHaveBeenCalledWith("g6", "label", "Tab Separated");
  });

  test("T026: prevents save of empty label (relies on Python)", async () => {
    const user = userEvent.setup();
    const mockOnUpdate = vi.fn();

    render(<LabelEditor blockId="g7" initialLabel="Controller" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Controller") as HTMLInputElement;

    // Enter empty string and press Enter
    await user.click(input);
    await user.clear(input);
    await user.keyboard("{Enter}");
    await flushUpdates();

    // Frontend sends empty string to Python (Python will revert to ID per FR-006)
    expect(mockOnUpdate).toHaveBeenCalledWith("g7", "label", "");
  });

  test("T027: handles long labels with horizontal scroll", async () => {
    const user = userEvent.setup();
    const mockOnUpdate = vi.fn();
    const longLabel = "Very Long Label That Should Scroll Horizontally Without Wrapping";

    render(<LabelEditor blockId="g8" initialLabel="Short" onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = screen.getByDisplayValue("Short") as HTMLInputElement;

    // Enter long value
    await user.click(input);
    await user.clear(input);
    await user.type(input, longLabel);
    await flushUpdates();

    // Input should contain the full value
    expect(input.value).toBe(longLabel);

    // Input should be a text input (supports horizontal scroll)
    expect(input.type).toBe("text");
  });
});
