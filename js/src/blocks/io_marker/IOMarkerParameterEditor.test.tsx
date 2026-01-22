// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * IOMarkerParameterEditor tests
 *
 * Tests the specialized parameter editor for IO Marker blocks
 */

import { describe, test, expect, vi, beforeEach } from "vitest";
import { render, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import IOMarkerParameterEditor from "./IOMarkerParameterEditor";
import type { Block } from "../../utils/traitletSync";
import { flushUpdates } from "../../test/setup";

/**
 * Create a mock IO Marker block for testing
 */
const createIOMarkerBlock = (index: number = 0, markerType: string = "input"): Block => ({
  id: "io-marker-1",
  type: "io_marker",
  position: { x: 0, y: 0 },
  parameters: [
    { name: "index", value: index },
    { name: "marker_type", value: markerType },
  ],
  ports: [{ id: "port", type: markerType === "input" ? "output" : "input" }],
});

describe("IOMarkerParameterEditor - Index Parameter", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("renders index input with correct initial value", async () => {
    const block: Block = {
      id: "io-marker-1",
      type: "io_marker",
      position: { x: 0, y: 0 },
      parameters: [
        { name: "index", value: 2 },
        { name: "marker_type", value: "input" },
      ],
      ports: [{ id: "out", type: "output" }],
    };
    const { container } = render(<IOMarkerParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = container.querySelector(
      'input[type="text"][placeholder="0"]'
    ) as HTMLInputElement;
    expect(input).not.toBeNull();
    expect(input.value).toBe("2");
  });

  test("renders index input with 0 when no value", async () => {
    const block = createIOMarkerBlock(0);
    const { container } = render(<IOMarkerParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = container.querySelector(
      'input[type="text"][placeholder="0"]'
    ) as HTMLInputElement;
    expect(input).not.toBeNull();
    expect(input.value).toBe("0");
  });

  test("index input allows deletion and defaults to 0 on blur", async () => {
    const user = userEvent.setup();

    const block: Block = {
      id: "io-marker-1",
      type: "io_marker",
      position: { x: 0, y: 0 },
      parameters: [
        { name: "index", value: 5 },
        { name: "marker_type", value: "input" },
      ],
      ports: [{ id: "out", type: "output" }],
    };
    const { container } = render(<IOMarkerParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const input = container.querySelector(
      'input[type="text"][placeholder="0"]'
    ) as HTMLInputElement;
    expect(input.value).toBe("5");

    mockOnUpdate.mockClear(); // Clear calls from initialization

    // Clear the input and blur
    await user.click(input);
    await user.clear(input);
    await user.tab(); // Tab away to blur

    // Should call onUpdate with 0 when empty value is applied
    expect(mockOnUpdate).toHaveBeenCalledWith("io-marker-1", "index", 0);
  });

  test("index input updates to show backend-clamped value", async () => {
    const user = userEvent.setup();

    // Start with a block at index 0
    const block: Block = {
      id: "io-marker-1",
      type: "io_marker",
      position: { x: 0, y: 0 },
      parameters: [
        { name: "index", value: 0 },
        { name: "marker_type", value: "input" },
      ],
      ports: [{ id: "out", type: "output" }],
    };

    const { container, rerender } = render(
      <IOMarkerParameterEditor block={block} onUpdate={mockOnUpdate} />
    );
    await flushUpdates();

    const input = container.querySelector(
      'input[type="text"][placeholder="0"]'
    ) as HTMLInputElement;
    expect(input.value).toBe("0");

    mockOnUpdate.mockClear(); // Clear calls from initialization

    // User enters "5" (out of range - suppose there are only 2 markers, valid range [0,1])
    await user.click(input);
    await user.clear(input);
    await user.type(input, "5");
    await user.tab(); // Tab away to blur

    // Should call onUpdate with 5 (frontend doesn't know it's out of range)
    expect(mockOnUpdate).toHaveBeenCalledWith("io-marker-1", "index", 5);

    // Simulate backend clamping to 1 and sending back updated block
    // (backend clamped 5 to 1 because there are only 2 markers, max index is 1)
    const updatedBlock: Block = {
      ...block,
      parameters: [
        { name: "index", value: 1 }, // Backend clamped 5 to 1
        { name: "marker_type", value: "input" },
      ],
    };

    rerender(<IOMarkerParameterEditor block={updatedBlock} onUpdate={mockOnUpdate} />);

    // Wait for the input to show the backend's clamped value (1)
    await waitFor(() => {
      const updatedInput = container.querySelector(
        'input[type="text"][placeholder="0"]'
      ) as HTMLInputElement;
      expect(updatedInput.value).toBe("1");
    });
  });
});

describe("IOMarkerParameterEditor - Marker Type Parameter (REMOVED - User Story 2)", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("Type dropdown removed from parameter panel (FR-004)", async () => {
    const block = createIOMarkerBlock(0, "input");
    const { container } = render(<IOMarkerParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    // Type dropdown should NOT exist (marker type is visually obvious from port orientation)
    const select = container.querySelector("select") as HTMLSelectElement;
    expect(select).toBeNull();
  });
});

describe("IOMarkerParameterEditor - Custom LaTeX (User Story 2)", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
  });

  test("Custom LaTeX checkbox and textarea rendering", async () => {
    const block = createIOMarkerBlock(0, "input");
    const { container } = render(<IOMarkerParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    // Should have custom LaTeX checkbox
    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(false); // Unchecked by default

    // Textarea should NOT exist initially (conditionally rendered)
    let textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    expect(textarea).toBeNull();

    // Check the checkbox to make textarea appear
    fireEvent.click(checkbox);
    await flushUpdates();

    // Now textarea should exist
    textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    expect(textarea).not.toBeNull();
  });

  test("LaTeX field only visible when checkbox enabled", async () => {
    const block = createIOMarkerBlock(0, "input");
    const { container } = render(<IOMarkerParameterEditor block={block} onUpdate={mockOnUpdate} />);
    await flushUpdates();

    const checkbox = container.querySelector('input[type="checkbox"]') as HTMLInputElement;

    // Initially checkbox unchecked, textarea should NOT exist
    expect(checkbox.checked).toBe(false);
    let textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    expect(textarea).toBeNull();

    // Check the checkbox
    fireEvent.click(checkbox);
    await flushUpdates();

    // Textarea should now exist and be visible
    expect(checkbox.checked).toBe(true);
    textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    expect(textarea).not.toBeNull();
    expect(textarea.parentElement?.style.display).toBe("block");
  });
});
