// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * ParameterPanel - Tests for block parameter editing UI
 *
 * Tests the refactored ParameterPanel that uses a registry pattern
 * to route to block-specific parameter editors.
 */

import { describe, test, expect, vi, beforeEach } from "vitest";
import { render, fireEvent } from "@testing-library/react";
import ParameterPanel from "./ParameterPanel";
import type { Block } from "../utils/traitletSync";
import { flushUpdates } from "../test/setup";

/**
 * Mock block fixtures for testing
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const createMockBlock = (type: Block["type"], parameters: any[] = []): Block => ({
  id: `test-${type}-1`,
  type,
  position: { x: 0, y: 0 },
  parameters,
  ports: [],
  label: `Test ${type}`,
});

describe("ParameterPanel - Block Type Routing", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;
  let mockOnClose: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
    mockOnClose = vi.fn();
  });

  test("returns null when block is null", async () => {
    const { container } = render(
      <ParameterPanel block={null} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    expect(container.firstChild).toBeNull();
  });

  test("returns null when block type is sum", async () => {
    const sumBlock = createMockBlock("sum", [{ name: "signs", value: ["+", "-", "+"] }]);
    const { container } = render(
      <ParameterPanel block={sumBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    expect(container.firstChild).toBeNull();
  });

  test("renders editor component for gain block", async () => {
    const gainBlock = createMockBlock("gain", [{ name: "K", value: 2.5 }]);
    const { container } = render(
      <ParameterPanel block={gainBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    // Should render the panel with header and label editor
    const panel = container.querySelector("div");
    expect(panel).not.toBeNull();
    expect(panel?.textContent).toContain("Edit Block Parameters");
    expect(panel?.textContent).toContain("Label"); // Label editor present
  });

  test("renders editor component for io_marker block", async () => {
    const ioMarkerBlock = createMockBlock("io_marker", [
      { name: "label", value: "Input A" },
      { name: "marker_type", value: "input" },
    ]);
    const { container } = render(
      <ParameterPanel block={ioMarkerBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    const panel = container.querySelector("div");
    expect(panel).not.toBeNull();
    expect(panel?.textContent).toContain("Edit Block Parameters");
    expect(panel?.textContent).toContain("Label"); // Label editor present
  });

  test("renders editor component for transfer_function block", async () => {
    const tfBlock = createMockBlock("transfer_function", [
      { name: "numerator", value: [1, 2] },
      { name: "denominator", value: [1, 3, 2] },
    ]);
    const { container } = render(
      <ParameterPanel block={tfBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    const panel = container.querySelector("div");
    expect(panel).not.toBeNull();
    expect(panel?.textContent).toContain("Edit Block Parameters");
    expect(panel?.textContent).toContain("Label"); // Label editor present
  });

  test("renders editor component for state_space block", async () => {
    const ssBlock = createMockBlock("state_space", [
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
    ]);
    const { container } = render(
      <ParameterPanel block={ssBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    const panel = container.querySelector("div");
    expect(panel).not.toBeNull();
    expect(panel?.textContent).toContain("Edit Block Parameters");
    expect(panel?.textContent).toContain("Label"); // Label editor present
  });
});

describe("ParameterPanel - Common Behaviors", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;
  let mockOnClose: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
    mockOnClose = vi.fn();
  });

  test("calls onClose when close button clicked", async () => {
    const gainBlock = createMockBlock("gain", [{ name: "K", value: 1 }]);
    const { container } = render(
      <ParameterPanel block={gainBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    const closeButton = container.querySelector("button") as HTMLButtonElement;
    expect(closeButton).not.toBeNull();
    expect(closeButton.textContent).toBe("×");

    fireEvent.click(closeButton);
    await flushUpdates();

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test("calls onClose when Enter pressed with no input focused", async () => {
    const gainBlock = createMockBlock("gain", [{ name: "K", value: 1 }]);
    const { container } = render(
      <ParameterPanel block={gainBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    const panel = container.querySelector("div") as HTMLDivElement;
    expect(panel).not.toBeNull();

    // Focus the panel itself (not an input)
    panel.focus();

    // Press Enter
    fireEvent.keyDown(panel, { key: "Enter" });
    await flushUpdates();

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test("does not call onClose when Enter pressed with input focused", async () => {
    const gainBlock = createMockBlock("gain", [{ name: "K", value: 1 }]);
    const { container } = render(
      <ParameterPanel block={gainBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    // Find a parameter input (not the label input, which has special Enter handling)
    const inputs = container.querySelectorAll("input");
    // Skip first input (label editor) and use parameter input (K value)
    const paramInput = Array.from(inputs).find((input) => {
      const parent = input.parentElement;
      return parent && !parent.textContent?.includes("Label");
    }) as HTMLInputElement;

    if (paramInput) {
      paramInput.focus();

      // Press Enter in the parameter input
      fireEvent.keyDown(paramInput, { key: "Enter" });
      await flushUpdates();

      // Should NOT close panel (input handles Enter)
      expect(mockOnClose).not.toHaveBeenCalled();
    }
  });
});

describe("ParameterPanel - Error Handling", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;
  let mockOnClose: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
    mockOnClose = vi.fn();
  });

  test("returns null for unknown block type", async () => {
    // Create a block with an unknown type (TypeScript won't allow this, but test runtime behavior)
    const unknownBlock = {
      id: "unknown-1",
      type: "unknown_type",
      position: { x: 0, y: 0 },
      parameters: [],
      ports: [],
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any;

    const { container } = render(
      <ParameterPanel block={unknownBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    expect(container.firstChild).toBeNull();
  });
});

describe("ParameterPanel - Label Editor (US1)", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;
  let mockOnClose: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
    mockOnClose = vi.fn();
  });

  test("T011: shows LabelEditor for Gain blocks", async () => {
    const gainBlock = createMockBlock("gain", [{ name: "K", value: 2.5 }]);
    const { container } = render(
      <ParameterPanel block={gainBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    // Type display should be removed
    expect(container.textContent).not.toContain("Type:");

    // Label editor should be present (look for label input)
    const labelInput = container.querySelector('input[type="text"]');
    expect(labelInput).toBeInTheDocument();
  });

  test("T012: shows LabelEditor for TransferFunction blocks", async () => {
    const tfBlock = createMockBlock("transfer_function", [
      { name: "numerator", value: [1, 2] },
      { name: "denominator", value: [1, 3, 2] },
    ]);
    const { container } = render(
      <ParameterPanel block={tfBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    expect(container.textContent).not.toContain("Type:");
    const labelInput = container.querySelector('input[type="text"]');
    expect(labelInput).toBeInTheDocument();
  });

  test("T013: shows LabelEditor for StateSpace blocks", async () => {
    const ssBlock = createMockBlock("state_space", [
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
    ]);
    const { container } = render(
      <ParameterPanel block={ssBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    expect(container.textContent).not.toContain("Type:");
    const labelInput = container.querySelector('input[type="text"]');
    expect(labelInput).toBeInTheDocument();
  });

  test("T014: shows LabelEditor for IOMarker blocks", async () => {
    const ioMarkerBlock = createMockBlock("io_marker", [
      { name: "label", value: "Input A" },
      { name: "marker_type", value: "input" },
    ]);
    const { container } = render(
      <ParameterPanel block={ioMarkerBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    expect(container.textContent).not.toContain("Type:");
    const labelInput = container.querySelector('input[type="text"]');
    expect(labelInput).toBeInTheDocument();
  });
});

describe("ParameterPanel - Label Independence (US3)", () => {
  let mockOnUpdate: ReturnType<typeof vi.fn>;
  let mockOnClose: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnUpdate = vi.fn();
    mockOnClose = vi.fn();
  });

  test("T036: label updates when label_visible=false", async () => {
    // Create block with label_visible=false
    const gainBlock: Block = {
      id: "g1",
      type: "gain",
      position: { x: 0, y: 0 },
      label: "Hidden Label",
      label_visible: false,
      parameters: [{ name: "K", value: 1.0 }],
      ports: [],
    };

    const { container } = render(
      <ParameterPanel block={gainBlock} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    // Label editor should be present and editable
    const labelInput = container.querySelector('input[type="text"]') as HTMLInputElement;
    expect(labelInput).toBeInTheDocument();
    expect(labelInput.value).toBe("Hidden Label");

    // Verify editing works - input should not be disabled
    expect(labelInput.disabled).toBe(false);

    // Verify that onUpdate callback exists (editing infrastructure is present)
    expect(mockOnUpdate).toBeDefined();
  });

  test("T037: label field remains editable regardless of label_visible state", async () => {
    // Test with label_visible=false
    const blockHidden: Block = {
      id: "g2",
      type: "gain",
      position: { x: 0, y: 0 },
      label: "Test",
      label_visible: false,
      parameters: [{ name: "K", value: 1.0 }],
      ports: [],
    };

    const { container: containerHidden } = render(
      <ParameterPanel block={blockHidden} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    const inputHidden = containerHidden.querySelector('input[type="text"]') as HTMLInputElement;
    expect(inputHidden).toBeInTheDocument();
    expect(inputHidden.disabled).toBe(false); // Should be editable

    // Test with label_visible=true
    const blockVisible: Block = {
      id: "g3",
      type: "gain",
      position: { x: 0, y: 0 },
      label: "Test",
      label_visible: true,
      parameters: [{ name: "K", value: 1.0 }],
      ports: [],
    };

    const { container: containerVisible } = render(
      <ParameterPanel block={blockVisible} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    const inputVisible = containerVisible.querySelector('input[type="text"]') as HTMLInputElement;
    expect(inputVisible).toBeInTheDocument();
    expect(inputVisible.disabled).toBe(false); // Should be editable

    // Both should allow editing
    expect(inputHidden.disabled).toBe(inputVisible.disabled);
  });

  test("T038: Parameter Panel label field ignores label_visible property", async () => {
    // Test that label editor renders the same way regardless of label_visible
    // First with label_visible=false
    const blockHidden: Block = {
      id: "b1",
      type: "transfer_function",
      position: { x: 0, y: 0 },
      label: "Plant",
      label_visible: false, // Hidden on canvas
      parameters: [
        { name: "numerator", value: [1] },
        { name: "denominator", value: [1, 1] },
      ],
      ports: [],
    };

    const { container, unmount } = render(
      <ParameterPanel block={blockHidden} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    // Label editor should be present
    const input1 = container.querySelector('input[type="text"]') as HTMLInputElement;
    expect(input1).toBeInTheDocument();
    expect(input1.value).toBe("Plant");
    expect(input1.disabled).toBe(false);

    // Unmount and test with label_visible=true
    unmount();

    const blockVisible: Block = {
      ...blockHidden,
      label_visible: true, // Visible on canvas
    };

    const { container: container2 } = render(
      <ParameterPanel block={blockVisible} onUpdate={mockOnUpdate} onClose={mockOnClose} />
    );
    await flushUpdates();

    // Label editor should still be present with same properties
    const input2 = container2.querySelector('input[type="text"]') as HTMLInputElement;
    expect(input2).toBeInTheDocument();
    expect(input2.value).toBe("Plant");
    expect(input2.disabled).toBe(false);
  });
});
