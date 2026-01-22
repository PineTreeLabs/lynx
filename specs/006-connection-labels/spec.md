<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Connection Labels

**Feature Branch**: `006-connection-labels`
**Created**: 2026-01-12
**Status**: Draft
**Input**: User description: "Add support for editable labels to connections. The behavior should mimic the behavior of blocks - label hidden by default, but toggleable via context menu, truth stored in the Python diagram, and edits persist over save/load via JSON. In terms of graphical appearance, the font and size should match block labels, and the position should be as close to the center of the connection (halfway between the extrema on the x-direction) as possible without the text extending past a corner waypoint. If text would extend past a corner waypoint it should be moved left or right (whichever is the least distance) until it does not."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Show Label via Context Menu (Priority: P1)

A user working with a block diagram wants to label a connection to indicate what signal flows through it. The user right-clicks on the connection and sees a "Show Label" option in the context menu. After clicking this option, the connection's label becomes visible along the connection path.

**Why this priority**: This is the primary interaction method for revealing labels. Without this, users cannot show labels at all since they are hidden by default. Mirrors the established block label workflow.

**Independent Test**: Can be fully tested by right-clicking any connection, selecting "Show Label", and observing that the label appears along the connection path. The label displays the connection's name (which defaults to the connection ID if not customized).

**Acceptance Scenarios**:

1. **Given** a connection with its label hidden (default state), **When** the user right-clicks the connection and selects "Show Label", **Then** the label appears along the connection path
2. **Given** a connection with its label hidden, **When** the user opens the context menu, **Then** the menu displays "Show Label" as an option

---

### User Story 2 - Hide Label via Context Menu (Priority: P2)

A user has previously shown a label on a connection but now wants to hide it to reduce visual clutter. The user right-clicks on the connection with a visible label and sees a "Hide Label" option. After clicking this option, the label is no longer displayed.

**Why this priority**: Complements P1 by providing the inverse operation. Users need to be able to hide labels they've shown, but showing labels comes first since labels start hidden.

**Independent Test**: Can be fully tested by first showing a label on a connection, then right-clicking and selecting "Hide Label", observing that the label disappears.

**Acceptance Scenarios**:

1. **Given** a connection with its label visible, **When** the user right-clicks the connection and selects "Hide Label", **Then** the label disappears from view
2. **Given** a connection with its label visible, **When** the user opens the context menu, **Then** the menu displays "Hide Label" (not "Show Label")

---

### User Story 3 - Edit Visible Labels (Priority: P3)

A user with a visible label wants to customize the label text to describe the signal (e.g., "velocity", "error", "control input"). The user double-clicks the label and can edit it inline. The edited label persists.

**Why this priority**: Maintains consistency with existing block label editing functionality. This is important but only relevant after labels are visible, hence lower priority than show/hide.

**Independent Test**: Can be fully tested by showing a label, double-clicking it, typing a new name, pressing Enter, and verifying the new name is displayed.

**Acceptance Scenarios**:

1. **Given** a connection with a visible label, **When** the user double-clicks the label, **Then** an inline text editor appears with the current label text selected
2. **Given** the user is editing a label, **When** the user types a new name and presses Enter, **Then** the label updates to the new text
3. **Given** the user is editing a label, **When** the user presses Escape, **Then** the edit is cancelled and the original label is restored

---

### User Story 4 - Persist Label Visibility and Text (Priority: P4)

A user saves a diagram with some connection labels shown and others hidden. When the diagram is reopened, the label visibility states and custom text are preserved exactly as saved.

**Why this priority**: Persistence ensures user work is not lost between sessions. Lower priority because it's about data persistence rather than interactive functionality.

**Independent Test**: Can be fully tested by showing labels on some connections, editing their text, saving the diagram, reopening it, and verifying the same labels are visible with their custom text.

**Acceptance Scenarios**:

1. **Given** a diagram with mixed connection label visibility states, **When** the user saves the diagram, **Then** the visibility state and label text for each connection is stored
2. **Given** a saved diagram with mixed connection label visibility states, **When** the user opens the diagram, **Then** each connection displays labels according to its saved visibility state and text

---

### User Story 5 - Smart Label Positioning (Priority: P5)

A user shows a label on a connection that has corner waypoints (non-straight path). The label appears as close to the horizontal center of the connection as possible, but if the label text would extend past a corner waypoint, the label shifts left or right by the minimum distance necessary to avoid overlapping the corner.

**Why this priority**: Visual polish and edge case handling. Core functionality works without this, but it improves usability for complex diagrams with routed connections.

**Independent Test**: Can be fully tested by creating a connection with waypoints, showing its label, and observing that the label does not overlap corner waypoints.

**Acceptance Scenarios**:

1. **Given** a straight connection (no waypoints), **When** the label is shown, **Then** the label is centered horizontally along the connection
2. **Given** a connection with waypoints, **When** the label is shown, **Then** the label appears near the horizontal center without extending past any corner waypoints
3. **Given** a connection where the centered label would extend past a corner, **When** the label is shown, **Then** the label shifts by the minimum distance needed to avoid the corner

---

### Edge Cases

- What happens when a new connection is created? The label starts hidden (default behavior).
- What happens when a connection has no label text set? The label still shows/hides correctly, displaying the default text (connection ID).
- What happens with very long label text? The label renders completely but may extend beyond its segment boundaries for extremely long text.
- What happens when the connection's routing changes (waypoints added/removed)? The label repositions according to the new path geometry.
- What happens with a very short connection segment? The label renders but may extend beyond the segment; this is acceptable for very short segments.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST hide connection labels by default when connections are created
- **FR-002**: System MUST display a "Show Label" option in the connection context menu when the label is hidden
- **FR-003**: System MUST display a "Hide Label" option in the connection context menu when the label is visible
- **FR-004**: System MUST show the connection label when the user selects "Show Label" from the context menu
- **FR-005**: System MUST hide the connection label when the user selects "Hide Label" from the context menu
- **FR-006**: System MUST persist the label visibility state in the Python Diagram object (source of truth)
- **FR-007**: System MUST allow editing visible labels via double-click inline editing (same as block labels)
- **FR-008**: System MUST persist label text and visibility state when diagrams are saved and loaded
- **FR-009**: System MUST match the font family and size of connection labels to existing block labels
- **FR-010**: System MUST position labels as close to the horizontal center of the connection as possible
- **FR-011**: System MUST shift label position left or right (minimum distance) if the label would extend past a corner waypoint

### Key Entities

- **Connection**: Existing entity representing a diagram edge between two ports; gains `label` (string, defaults to connection ID) and `label_visible` (boolean, defaults to false) attributes
- **Label Visibility State**: Boolean property per connection indicating whether the label should be displayed
- **Label Position**: Computed position based on connection geometry and waypoints

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of newly created connections start with labels hidden
- **SC-002**: Users can toggle connection label visibility in under 3 seconds (right-click, select option)
- **SC-003**: Context menu correctly reflects current label state (shows appropriate "Show/Hide" text) 100% of the time
- **SC-004**: Diagram save/load preserves connection label visibility and text with 100% accuracy
- **SC-005**: Connection labels use identical font styling to block labels (visual consistency)
- **SC-006**: Label positioning never causes text to overlap corner waypoints on standard-length connection segments

## Assumptions

- Label position is computed on the frontend based on connection geometry; position is not persisted (only text and visibility are stored)
- The label text value defaults to the connection ID if not customized (same pattern as block labels)
- Inline editing uses the same keyboard shortcuts as block labels (Enter to save, Escape to cancel)
- The existing `EditableLabel` component can be reused or adapted for connection labels
- Label vertical positioning places the label slightly above or below the connection line to avoid obscuring it
- "Horizontal center" refers to the midpoint between the minimum and maximum x-coordinates of the connection path
- The smart positioning algorithm handles the common case; extremely short segments or very long text may still have visual overlap
