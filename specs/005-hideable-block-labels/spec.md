<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Hideable Block Labels

**Feature Branch**: `005-hideable-block-labels`
**Created**: 2026-01-12
**Status**: Draft
**Input**: User description: "Currently block labels are on by default. This feature should make block labels hideable (hidden by default), and add an option to the right-click block context menu to show labels. The context menu item should be "Show Label" if the label is hidden, or "Hide Label" if the label is shown. All default + editable label behavior should be the same, and the shown/hidden state should be stored in the Python Diagram object (the source of truth)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Show Label via Context Menu (Priority: P1)

A user working with a block diagram wants to display a label on a specific block to identify it. The user right-clicks on the block and sees a "Show Label" option in the context menu. After clicking this option, the block's label becomes visible below the block.

**Why this priority**: This is the primary interaction method for revealing labels. Without this, users cannot show labels at all since they are hidden by default.

**Independent Test**: Can be fully tested by right-clicking any block, selecting "Show Label", and observing that the label appears. The label displays the block's name (which defaults to the block ID if not customized).

**Acceptance Scenarios**:

1. **Given** a block with its label hidden (default state), **When** the user right-clicks the block and selects "Show Label", **Then** the label appears below the block
2. **Given** a block with its label hidden, **When** the user opens the context menu, **Then** the menu displays "Show Label" as an option

---

### User Story 2 - Hide Label via Context Menu (Priority: P2)

A user has previously shown a label on a block but now wants to hide it to reduce visual clutter. The user right-clicks on the block with a visible label and sees a "Hide Label" option. After clicking this option, the label is no longer displayed.

**Why this priority**: Complements P1 by providing the inverse operation. Users need to be able to hide labels they've shown, but showing labels comes first since labels start hidden.

**Independent Test**: Can be fully tested by first showing a label on a block, then right-clicking and selecting "Hide Label", observing that the label disappears.

**Acceptance Scenarios**:

1. **Given** a block with its label visible, **When** the user right-clicks the block and selects "Hide Label", **Then** the label disappears from view
2. **Given** a block with its label visible, **When** the user opens the context menu, **Then** the menu displays "Hide Label" (not "Show Label")

---

### User Story 3 - Edit Visible Labels (Priority: P3)

A user with a visible label wants to customize the label text. The user double-clicks the label and can edit it inline, just as labels work today. The edited label persists.

**Why this priority**: Maintains existing label editing functionality. This is important but only relevant after labels are visible, hence lower priority than show/hide.

**Independent Test**: Can be fully tested by showing a label, double-clicking it, typing a new name, pressing Enter, and verifying the new name is displayed.

**Acceptance Scenarios**:

1. **Given** a block with a visible label, **When** the user double-clicks the label, **Then** an inline text editor appears with the current label text selected
2. **Given** the user is editing a label, **When** the user types a new name and presses Enter, **Then** the label updates to the new text
3. **Given** the user is editing a label, **When** the user presses Escape, **Then** the edit is cancelled and the original label is restored

---

### User Story 4 - Persist Label Visibility (Priority: P4)

A user saves a diagram with some labels shown and others hidden. When the diagram is reopened, the label visibility states are preserved exactly as saved.

**Why this priority**: Persistence ensures user work is not lost between sessions. Lower priority because it's about data persistence rather than interactive functionality.

**Independent Test**: Can be fully tested by showing labels on some blocks, saving the diagram, reopening it, and verifying the same labels are visible.

**Acceptance Scenarios**:

1. **Given** a diagram with mixed label visibility states, **When** the user saves the diagram, **Then** the visibility state for each block is stored
2. **Given** a saved diagram with mixed label visibility states, **When** the user opens the diagram, **Then** each block displays labels according to its saved visibility state

---

### Edge Cases

- What happens when a new block is added? The label starts hidden (default behavior).
- What happens when the user copies/pastes a block with a visible label? The pasted block should preserve the label visibility state of the source block.
- What happens if a block has no label text set? The label still shows/hides correctly, displaying the default text (block ID).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST hide block labels by default when blocks are created or added to the diagram
- **FR-002**: System MUST display a "Show Label" option in the block context menu when the label is hidden
- **FR-003**: System MUST display a "Hide Label" option in the block context menu when the label is visible
- **FR-004**: System MUST show the block label when the user selects "Show Label" from the context menu
- **FR-005**: System MUST hide the block label when the user selects "Hide Label" from the context menu
- **FR-006**: System MUST persist the label visibility state in the Python Diagram object (source of truth)
- **FR-007**: System MUST preserve existing label editing behavior (double-click to edit) for visible labels
- **FR-008**: System MUST persist label visibility state when diagrams are saved and loaded
- **FR-009**: System MUST preserve label visibility state when blocks are copied and pasted

### Key Entities

- **Block**: Existing entity representing a diagram block; gains a new `label_visible` attribute (boolean, defaults to false)
- **Label Visibility State**: Boolean property per block indicating whether the label should be displayed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of newly created blocks start with labels hidden
- **SC-002**: Users can toggle label visibility in under 3 seconds (right-click, select option)
- **SC-003**: Context menu correctly reflects current label state (shows appropriate "Show/Hide" text) 100% of the time
- **SC-004**: Diagram save/load preserves label visibility with 100% accuracy
- **SC-005**: All 5 existing block types support label show/hide functionality consistently

## Assumptions

- Label position (below the block) remains unchanged from current implementation
- The label text value itself is unchanged by show/hide operations (editing works the same as before)
- All block types (Gain, TransferFunction, StateSpace, Sum, IOMarker) share the same label show/hide behavior
- Undo/redo should capture label visibility changes as part of existing undo/redo infrastructure
