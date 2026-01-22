<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Sum Block Quadrant Configuration

**Feature Branch**: `011-sum-quadrant-config`
**Created**: 2026-01-14
**Status**: Draft
**Input**: User description: "The Sum block is currently configured with a text string that specifies "+/-/|" for each of the Top, Left, Bottom ports. Remove the block properties panel for the Sum and instead support configuration by double-clicking in the appropriate quadrant of the Sum block to cycle through the options from "+" -> "-" -> "|" (no port). The result should be the same as editing the current properties panel, but without the need to edit a string. The quadrant click detection should scale and deform with the block dimensions and should not extend outside of the circle/oval SVG region."

## Clarifications

### Session 2026-01-14

- Q: Should keyboard-only users be able to configure Sum block port signs without a mouse? → A: Yes - Tab to block + Arrow keys to select quadrant + Enter to cycle (standard accessibility pattern)
- Q: What specific visual feedback should appear when hovering over or focusing on an interactive quadrant? → A: Cursor change + subtle hover highlight on the quadrant region (Note: cursor-only is acceptable fallback if quadrant highlighting proves more difficult than anticipated)
- Q: Should the entire properties panel be removed for Sum blocks, or just the signs parameter editor? → A: Remove entire properties panel for Sum blocks (no panel access at all)
- Q: Should double-click configuration be disabled during or immediately after drag operations? → A: No - allow double-clicks at all times (user must be careful not to double-click while dragging)
- Q: What is the maximum acceptable response time from double-click to visual update? → A: 100 milliseconds or less

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Port Sign by Quadrant Click (Priority: P1)

Users can configure Sum block port signs by double-clicking directly on the visual representation of the block rather than editing text strings in a properties panel. Each quadrant of the Sum block (top, left, bottom) responds to double-clicks by cycling through sign options (+, -, |), making configuration intuitive and visual. Keyboard-only users can tab to the block, use arrow keys to select a quadrant, and press Enter to cycle the port sign.

**Why this priority**: This is the core functionality that replaces text-based configuration with direct manipulation. It provides immediate value by simplifying the most common Sum block configuration task and ensures accessibility compliance.

**Independent Test**: Can be fully tested by creating a Sum block, double-clicking each quadrant (top, left, bottom), and verifying that the signs cycle correctly through +, -, and | (no port), with the same underlying configuration as the current text-based system. Also testable using keyboard-only navigation (Tab + Arrow keys + Enter).

**Acceptance Scenarios**:

1. **Given** a Sum block with default configuration, **When** user double-clicks the top quadrant, **Then** the top port sign cycles from its current value to the next in sequence (+ → - → | → +)
2. **Given** a Sum block with a "+" top port, **When** user double-clicks the top quadrant twice, **Then** the top port changes to "|" (no port) and the port marker disappears
3. **Given** a Sum block with all ports configured, **When** user double-clicks the left quadrant, **Then** only the left port sign changes while other ports remain unchanged
4. **Given** a Sum block, **When** user double-clicks the bottom quadrant to cycle through all options, **Then** the block updates visually and functionally equivalent to manually editing the signs parameter string
5. **Given** a Sum block with focus, **When** keyboard user presses Up arrow then Enter, **Then** the top port sign cycles identically to a double-click interaction
6. **Given** a Sum block with focus, **When** keyboard user presses Left arrow then Enter twice, **Then** the left port sign advances by two steps in the cycle sequence
7. **Given** a Sum block on the canvas, **When** user hovers mouse over the top quadrant, **Then** cursor changes to pointer and the top quadrant displays a subtle highlight (Note: quadrant highlight is optional; cursor change is minimum requirement)
8. **Given** a Sum block with keyboard focus and arrow key selection, **When** user selects the left quadrant with arrow keys, **Then** the left quadrant displays a subtle highlight as focus indicator (Note: some visual indicator required for accessibility; implementation may be simplified if needed)
9. **Given** a Sum block on the canvas, **When** user attempts to open the properties panel (via any interaction that would normally open it for other block types), **Then** no properties panel appears for the Sum block

---

### User Story 2 - Accurate Click Detection with Block Scaling (Priority: P2)

When Sum blocks are resized or have non-square dimensions, the quadrant click detection accurately follows the deformed circle/oval shape boundaries. Users can confidently click within the visible block shape without accidentally triggering configuration changes from clicks outside the shape.

**Why this priority**: This ensures the interaction works correctly with the existing block resizing feature. While less critical than basic functionality, it prevents user frustration from unexpected behavior with non-default block sizes.

**Independent Test**: Can be tested by resizing a Sum block to various non-square dimensions (e.g., 80x40, 40x80), double-clicking at the edges of the oval, and verifying that clicks inside the oval boundary trigger configuration while clicks outside do not.

**Acceptance Scenarios**:

1. **Given** a Sum block resized to 80x40 pixels (wide oval), **When** user double-clicks at the edge of the visible oval in the top quadrant, **Then** the top port sign cycles correctly
2. **Given** a Sum block resized to 40x80 pixels (tall oval), **When** user double-clicks just outside the oval boundary but within the block's rectangular bounds, **Then** no configuration change occurs
3. **Given** a Sum block with non-square dimensions, **When** user double-clicks near the center dividing lines between quadrants, **Then** the correct quadrant is detected based on geometric division of the oval
4. **Given** a Sum block at any size, **When** user clicks in the right quadrant (where output port is located), **Then** no configuration change occurs (output port is not configurable)

---

### Edge Cases

- What happens when a user double-clicks rapidly on the same quadrant?
  - System should handle each double-click as a discrete cycle event (if user triggers two double-clicks quickly, the sign should advance by two steps)

- What happens when a user clicks exactly on the boundary line between two quadrants?
  - System should assign the click to one quadrant using consistent geometric rules (e.g., top-left boundary belongs to top quadrant, left-bottom boundary belongs to left quadrant)

- What happens when a Sum block is resized to minimum dimensions (close to 40x40)?
  - Click detection should still work accurately within the oval boundary, even at minimum size

- What happens when a port is cycled to "|" (no port) and the block already has connections to that port?
  - The port and its connections should be removed, consistent with current behavior when editing the signs parameter

- What happens when a user accidentally double-clicks while dragging a Sum block?
  - System will process the double-click as a configuration change if it occurs within a quadrant. Users must be careful to avoid double-clicking during drag operations

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect double-click events on the Sum block visual region and map them to specific quadrants (top, left, bottom, right)
- **FR-002**: System MUST cycle the port sign for the clicked quadrant through the sequence: "+" → "-" → "|" → "+" (where "|" means no port)
- **FR-003**: System MUST NOT trigger configuration changes for double-clicks in the right quadrant (output port is fixed and not configurable)
- **FR-004**: System MUST completely remove the properties panel for Sum blocks (users configure signs exclusively through quadrant clicks, no properties panel access)
- **FR-005**: Quadrant click detection MUST respect the circular/oval SVG boundary, not triggering for clicks outside the visible shape but within the rectangular block bounds
- **FR-006**: Quadrant click detection MUST scale and deform correctly when the Sum block is resized to non-square dimensions
- **FR-007**: System MUST update the underlying block configuration (signs parameter) identically to the current text-based editing approach
- **FR-008**: When a port is set to "|" (no port), the system MUST remove the port marker and any existing connections, consistent with current port regeneration behavior
- **FR-009**: System MUST provide visual feedback when hovering over or focusing on an interactive quadrant: cursor changes to pointer, and the quadrant region displays a subtle highlight (Note: cursor change only is acceptable if quadrant highlighting implementation complexity exceeds expectations)
- **FR-010**: System MUST persist the sign configuration through save/load operations, maintaining compatibility with existing diagram files
- **FR-011**: System MUST support keyboard-only navigation: Tab to focus block, arrow keys (Up/Left/Down/Right) to select quadrant, Enter to cycle the selected quadrant's port sign
- **FR-012**: System MUST respond to double-click or keyboard input with visual update within 100 milliseconds to ensure interactions feel instant

### Key Entities

- **Sum Block**: A diagram block with configurable input ports (top, left, bottom) that can have signs (+, -, or no port) and a fixed output port (right)
- **Quadrant**: A geometric region of the Sum block corresponding to one of the four cardinal directions (top, left, bottom, right), used for click detection
- **Port Sign**: A configuration value for an input port that determines whether it adds (+), subtracts (-), or doesn't exist (|)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can configure all three Sum block input ports (top, left, bottom) through double-click interactions (or keyboard navigation for accessibility) without opening a properties panel
- **SC-002**: Click detection accuracy is 100% within the oval boundary and 0% outside the oval boundary for blocks of any size between minimum (40x40) and maximum tested dimensions
- **SC-003**: Configuration changes through quadrant clicking produce identical functional results (port signs, port regeneration, connection cleanup) as the current text-based parameter editing
- **SC-004**: Users can resize a Sum block to non-square dimensions and successfully configure ports at the first attempt, without misclicks or confusion about interactive regions
- **SC-005**: Visual updates appear within 100 milliseconds of user interaction (double-click or keyboard input), ensuring interactions feel instant and responsive
