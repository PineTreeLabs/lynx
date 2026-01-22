<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Editable Block Labels in Parameter Panel

**Feature Branch**: `013-editable-block-labels`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Replace the Type: block_type_name in the Parameter panel with the block label as an editable field.  Changes to this field must propagate to the Python Diagram object and update the UI block label if displayed, but should be independent of the Show/Hide label feature in the block right-click context menu."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Replace Type Display with Label Field (Priority: P1)

Users see an editable label field in the Parameter panel instead of the static "Type: block_type_name" text, providing a more functional use of panel space.

**Why this priority**: This is the foundational UI change that enables all other functionality. Without this structural change, users cannot edit labels via the Parameter panel. It must be completed first to provide the UI foundation for label editing workflows.

**Independent Test**: Can be fully tested by opening the Parameter panel for any block and verifying that the static "Type:" text is replaced with a labeled input field showing the block's current label. Delivers immediate value by repurposing panel space for editing rather than static display.

**Acceptance Scenarios**:

1. **Given** any block is selected, **When** the Parameter panel opens, **Then** the panel displays an editable "Label" field containing the block's current label instead of "Type: block_type_name"
2. **Given** the Parameter panel is open with a label field, **When** the user focuses on the label field, **Then** standard text input controls are available (cursor positioning, select-all, cut/copy/paste)
3. **Given** a block with no custom label set (using ID as label), **When** the Parameter panel opens, **Then** the label field displays the block's ID as the current label
4. **Given** a block with a custom label set, **When** the Parameter panel opens, **Then** the label field displays the custom label (not the block ID)

---

### User Story 2 - Edit Block Label via Parameter Panel (Priority: P1)

Users can edit a block's label by typing directly into the Parameter panel, providing an accessible way to rename blocks with standard commit actions (Enter key or blur).

**Why this priority**: This is the core editing functionality that provides the actual value of the feature. Users can rename blocks through the Parameter panel interface, offering an alternative to double-clicking labels on the canvas. This improves accessibility for users who prefer panel-based workflows.

**Independent Test**: Can be fully tested by selecting any block, opening the Parameter panel, editing the label field, and verifying the label updates both in the panel and on the canvas (if label visibility is enabled). Delivers immediate value by providing an alternative label editing method.

**Acceptance Scenarios**:

1. **Given** a block is selected and the Parameter panel is open, **When** the user types a new label name into the label field and presses Enter, **Then** the block's label is updated in the Python Diagram object and the UI reflects the new label (if label_visible is true)
2. **Given** a block is selected with the Parameter panel open, **When** the user types a new label name and clicks outside the field (blur), **Then** the block's label is updated in the Python Diagram object and the UI reflects the new label (if label_visible is true)
3. **Given** a block is selected with the Parameter panel open, **When** the user clears the label field entirely and attempts to save, **Then** the system reverts to the block's ID as the default label
4. **Given** a block is selected with the Parameter panel open, **When** the user types a label with leading/trailing whitespace, **Then** the system trims the whitespace before saving the label
5. **Given** a user is editing a label in the Parameter panel, **When** the user presses Escape, **Then** the edit is cancelled and the field reverts to the original label value

---

### User Story 3 - Label Independence from Visibility Toggle (Priority: P2)

Changes to the block label via the Parameter panel are independent of the label visibility toggle in the right-click context menu, ensuring users can set labels even when they're not displayed on the canvas.

**Why this priority**: Ensures data integrity and consistency by maintaining the block label state regardless of visibility settings. Prevents confusion when users edit labels that may not be immediately visible. This is lower priority because the core editing (US1/US2) must work first.

**Independent Test**: Can be fully tested by editing a block label while label_visible is false, then toggling visibility on to confirm the edited label appears. Delivers value by ensuring label editing works consistently regardless of visibility state.

**Acceptance Scenarios**:

1. **Given** a block with label_visible set to false, **When** the user edits the label in the Parameter panel, **Then** the block's label is updated in the Python Diagram object even though the label is not displayed on the canvas
2. **Given** a block with label_visible set to false and a recently edited label, **When** the user right-clicks and selects "Show label", **Then** the updated label (not the original label) is displayed on the canvas
3. **Given** a block with label_visible set to true, **When** the user edits the label in the Parameter panel, **Then** the displayed label on the canvas updates immediately to reflect the new value
4. **Given** a block with label_visible set to true, **When** the user right-clicks and selects "Hide label", **Then** the label disappears from the canvas but remains editable and visible in the Parameter panel

---

### Edge Cases

- What happens when two blocks are given the same label? (System allows duplicate labels; blocks remain uniquely identified by ID in Python backend)
- How does the system handle extremely long label names? (Label field in Parameter panel uses text input with horizontal scrolling; canvas display uses existing overflow handling from EditableLabel component)
- What happens when a user edits a label while the Parameter panel is open and another concurrent operation updates the same block? (Last write wins; UI reflects the final Python state after both updates via traitlet sync)
- What happens when a user enters special characters (e.g., newlines, tabs, Unicode) in the label? (System accepts printable Unicode characters; newlines and tabs are normalized to spaces; control characters are stripped)
- What happens if the label field is focused when the Parameter panel is closed? (Standard React cleanup applies; any uncommitted edits are lost unless blur event fires first)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display an editable "Label" field in the Parameter panel for all block types that use the Parameter panel (Gain, TransferFunction, StateSpace, IOMarker)
- **FR-002**: System MUST replace the existing "Type: block_type_name" static text with the editable Label field in the Parameter panel's header/top section
- **FR-003**: System MUST update the block's label in the Python Diagram object when the user commits a change via Enter key or blur event
- **FR-004**: System MUST propagate label changes from the Python backend to the frontend UI, updating the canvas label display if label_visible is true
- **FR-005**: System MUST trim leading and trailing whitespace from label input before saving to the Python backend
- **FR-006**: System MUST revert to the block's ID as the label when the user attempts to save an empty or whitespace-only label
- **FR-007**: System MUST allow label editing in the Parameter panel regardless of the label_visible state (hidden labels can still be edited)
- **FR-008**: System MUST maintain independence between label editing operations and the Show/Hide label toggle in the block context menu
- **FR-009**: System MUST support standard text editing controls (cursor positioning, text selection, cut/copy/paste) in the label field
- **FR-010**: System MUST cancel the edit and revert to the original label when the user presses Escape while editing the label field
- **FR-011**: System MUST normalize whitespace (replace newlines/tabs with spaces) and strip control characters from label input

### Key Entities

- **Block Label**: The user-facing name for a block, defaults to the block ID if not explicitly set. Stored in the Python Block object's `label` attribute and synchronized to the frontend via traitlet sync mechanism. The label value is independent from the `label_visible` boolean flag that controls whether the label is displayed on the canvas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can edit block labels through the Parameter panel with changes persisting immediately (within 50ms) to the Python Diagram object
- **SC-002**: Label changes update the canvas display (when label_visible is true) within 100ms of user commit action (Enter key or blur)
- **SC-003**: Users can edit labels for blocks with label_visible=false and see the updated label when toggling visibility on
- **SC-004**: 100% of block types that use the Parameter panel (Gain, TransferFunction, StateSpace, IOMarker) display the editable Label field instead of the static "Type:" display
- **SC-005**: The Parameter panel vertical layout remains compact with no height increase after replacing the Type display with the Label field
