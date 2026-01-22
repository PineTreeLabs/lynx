<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Collapsible Block Library

**Feature Branch**: `009-collapsible-block-library`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "The block library should by default be collapsed to a single icon with the same styling that says 'Blocks' in the upper left corner. When the cursor hovers over this icon it should expand into the full library panel. When the cursor leaves the library panel it should shrink back to the library icon."

## Clarifications

### Session 2026-01-13

- Q: What is the panel expansion direction/behavior? → A: Icon stays fixed, panel grows downward from it (like a dropdown)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Collapsed Library Icon (Priority: P1)

When a user opens a diagram, they see a compact "Blocks" icon in the upper left corner instead of the full block library panel. This gives them more canvas space by default while maintaining easy access to the block palette.

**Why this priority**: This is the default state users see on every diagram. The collapsed state maximizes canvas real estate for the most common activity (viewing and editing diagrams).

**Independent Test**: Can be fully tested by opening any diagram and verifying the collapsed icon appears in the upper left corner with consistent styling.

**Acceptance Scenarios**:

1. **Given** a user opens a diagram, **When** the diagram loads, **Then** they see a compact "Blocks" icon in the upper left corner (not the expanded panel)
2. **Given** a user views the collapsed icon, **When** they inspect its appearance, **Then** it has the same visual styling (colors, border, shadow) as the expanded panel

---

### User Story 2 - Expand Library on Hover (Priority: P1)

When a user hovers their cursor over the collapsed "Blocks" icon, the full block library panel smoothly expands, giving them immediate access to all available block types.

**Why this priority**: Equal to P1 because hover-to-expand is the primary interaction mechanism. Without this, users cannot add blocks to their diagram.

**Independent Test**: Can be fully tested by hovering over the collapsed icon and verifying the full panel appears with all block buttons.

**Acceptance Scenarios**:

1. **Given** the block library is collapsed, **When** the user hovers their cursor over the "Blocks" icon, **Then** the full library panel expands showing all block buttons
2. **Given** the user is hovering over the icon, **When** the panel expands, **Then** all block buttons (Gain, Input, Output, Sum, TF, SS) are visible and clickable
3. **Given** the library is expanding, **When** the user observes the transition, **Then** the expansion is smooth (not instant/jarring)

---

### User Story 3 - Collapse Library on Mouse Leave (Priority: P1)

When a user moves their cursor away from the expanded library panel, the panel collapses back to the compact "Blocks" icon.

**Why this priority**: Equal to P1 because auto-collapse is essential for the space-saving behavior. The feature doesn't deliver value without proper collapse behavior.

**Independent Test**: Can be fully tested by hovering to expand, then moving the cursor away and verifying the panel collapses.

**Acceptance Scenarios**:

1. **Given** the library panel is expanded, **When** the user moves their cursor outside the panel boundaries, **Then** the panel collapses back to the "Blocks" icon
2. **Given** the user's cursor leaves the panel, **When** the collapse occurs, **Then** the transition is smooth (not instant/jarring)
3. **Given** the library is collapsing, **When** the animation completes, **Then** only the compact "Blocks" icon remains visible

---

### User Story 4 - Add Block While Panel is Expanded (Priority: P2)

When a user clicks a block button while the library is expanded, the block is added to the diagram and the library remains accessible for adding more blocks.

**Why this priority**: Secondary to core expand/collapse behavior but essential for usability. Users need to be able to add multiple blocks in succession.

**Independent Test**: Can be fully tested by expanding the library, clicking a block button, and verifying the block appears on the canvas.

**Acceptance Scenarios**:

1. **Given** the library panel is expanded, **When** the user clicks a block button (e.g., "Gain"), **Then** a new block of that type is added to the diagram
2. **Given** the user has just clicked a block button, **When** they want to add another block, **Then** the panel remains expanded and accessible (does not immediately collapse)
3. **Given** the user is actively interacting with the panel, **When** they move their cursor between buttons, **Then** the panel remains expanded

---

### Edge Cases

- What happens when the user rapidly moves their cursor in and out of the panel? The panel should not flicker; a small delay before collapse prevents accidental closures.
- What happens when the user clicks a block button and their cursor exits the panel during the click? The click should complete successfully before any collapse occurs.
- What happens on touch devices without hover capability? The collapsed icon should be tappable to toggle expansion, with a tap outside to collapse.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a collapsed "Blocks" icon as the default state when a diagram loads
- **FR-002**: System MUST position the collapsed icon in the upper left corner of the canvas
- **FR-003**: System MUST expand the full library panel when the user hovers over the collapsed icon
- **FR-004**: System MUST collapse the library panel when the user's cursor leaves the panel area
- **FR-005**: System MUST apply consistent visual styling between the collapsed icon and expanded panel (same border, shadow, and color scheme)
- **FR-006**: System MUST animate the expand/collapse transitions smoothly, with the collapsed icon remaining fixed in position while the panel grows downward (dropdown-style expansion)
- **FR-007**: System MUST display all existing block buttons (Gain, Input, Output, Sum, TF, SS) in the expanded panel
- **FR-008**: System MUST maintain all existing block-adding functionality when expanded
- **FR-009**: System MUST include a brief delay (approximately 150-300ms) before collapsing to prevent accidental closures from brief cursor movements
- **FR-010**: System MUST keep the panel expanded while the user is actively interacting with it (clicking buttons, moving between elements)

### Key Entities

- **Block Library Panel**: The UI component containing block-adding buttons. Has two states: collapsed (icon only) and expanded (full panel with buttons).
- **Collapsed State**: Compact icon showing "Blocks" text, matching panel styling
- **Expanded State**: Full panel with all block type buttons visible and clickable

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify the block library location within 2 seconds of viewing a new diagram
- **SC-002**: Library expands to full panel within 200ms of hover initiation
- **SC-003**: Library collapses to icon within 200ms of cursor leaving (after delay period)
- **SC-004**: Users can add a new block within 1 second of deciding to add one (hover + click)
- **SC-005**: Panel does not collapse during normal interaction patterns (moving between buttons, clicking)
- **SC-006**: Collapsed icon occupies less than 25% of the horizontal space compared to the expanded panel

## Assumptions

- The existing block palette styling (colors, borders, shadows) will be preserved for both states
- Animation duration of approximately 150-200ms provides smooth but responsive transitions
- A collapse delay of 150-300ms is sufficient to prevent accidental closures while not feeling sluggish
- The text "Blocks" is clear and recognizable as the library access point
- Existing block-adding functionality and button order will remain unchanged
