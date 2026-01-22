<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Editable Orthogonal Routing

**Feature Branch**: `004-editable-orthogonal-routing`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Add support for editable orthogonal routing between blocks, following the design outlined in specs/001-lynx-jupyter-widget/design-editable-routing.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Drag Connection Segments to Customize Routing (Priority: P1)

Users building control system diagrams need to manually adjust connection paths when the automatic routing creates overlapping or visually confusing connections. A user clicks on a connection to select it, then drags a horizontal segment up or down (or a vertical segment left or right) to reposition that portion of the path. The connection maintains strict orthogonal (90-degree) routing throughout the drag operation.

**Why this priority**: This is the core value proposition - without the ability to drag segments, users cannot customize routing at all. This functionality enables all other features and delivers immediate value for diagram readability.

**Independent Test**: Can be fully tested by creating two connected blocks, selecting the connection, and dragging a segment to a new position. Delivers cleaner, non-overlapping diagram layouts.

**Acceptance Scenarios**:

1. **Given** a connection is selected, **When** user drags a horizontal segment vertically, **Then** the segment moves to the new vertical position while maintaining orthogonal routing
2. **Given** a connection is selected, **When** user drags a vertical segment horizontally, **Then** the segment moves to the new horizontal position while maintaining orthogonal routing
3. **Given** user is dragging a segment, **When** drag is in progress, **Then** a real-time preview shows the new path before releasing

---

### User Story 2 - Persist Custom Routing with Diagram (Priority: P2)

Users who have spent time arranging their connections need those customizations saved when they save the diagram and restored when they reload it. After customizing connection routing, the user saves the diagram. Upon reopening the diagram later, all connection paths appear exactly as they were arranged.

**Why this priority**: Without persistence, users would lose their work every time they close the diagram. This is essential for any practical use of the routing feature.

**Independent Test**: Can be tested by customizing a connection route, saving the diagram, closing it, reopening it, and verifying the custom route is preserved.

**Acceptance Scenarios**:

1. **Given** a connection with custom waypoints, **When** user saves the diagram, **Then** waypoint coordinates are included in the saved data
2. **Given** a saved diagram with custom routing, **When** user loads the diagram, **Then** connections render with their saved custom paths
3. **Given** a connection with custom routing, **When** a connected block is moved, **Then** the waypoints remain at their absolute positions and the connection re-routes through them

---

### User Story 3 - Visual Selection and Feedback (Priority: P3)

Users need clear visual indication of which connection is selected and what actions are available. When hovering over a connection segment, the cursor changes to indicate the drag direction. When a connection is selected, it displays with visual emphasis and shows where dragging is possible.

**Why this priority**: Good visual feedback makes the feature intuitive and discoverable. Without it, users may not understand they can drag segments or which direction they can drag.

**Independent Test**: Can be tested by hovering over and clicking connections and verifying appropriate visual feedback appears.

**Acceptance Scenarios**:

1. **Given** a connection is not selected, **When** user hovers over a segment, **Then** cursor changes to indicate perpendicular drag direction (vertical arrows for horizontal segments, horizontal arrows for vertical segments)
2. **Given** user clicks on a connection, **When** connection becomes selected, **Then** it displays with increased visual emphasis (thicker line, accent color)
3. **Given** a connection is selected and being dragged, **When** drag is in progress, **Then** the new path preview is shown in accent color while original path is dimmed

---

### User Story 4 - Reset to Automatic Routing (Priority: P4)

Users who have customized a connection's routing may want to start fresh with automatic routing. A selected connection can be reset to use automatic routing, removing all manual waypoints and returning to the default path calculation.

**Why this priority**: This provides an "undo all customizations" escape hatch, but is less critical than the core drag functionality since users can manually drag segments back to approximate the auto-routed position.

**Independent Test**: Can be tested by customizing a connection route, selecting it, triggering reset, and verifying it returns to automatic routing.

**Acceptance Scenarios**:

1. **Given** a connection with custom waypoints is selected, **When** user triggers "Reset to Auto" action, **Then** all waypoints are removed and connection uses automatic routing
2. **Given** a connection is reset to auto, **When** user saves and reloads the diagram, **Then** the connection remains auto-routed (no waypoints stored)

---

### User Story 5 - Undo/Redo Routing Changes (Priority: P5)

Users may make routing adjustments they want to reverse. Routing changes integrate with the existing undo/redo system so users can step backwards and forwards through their edits.

**Why this priority**: Undo/redo is important for usability but the existing diagram infrastructure likely already supports this. Lower priority because users can manually re-drag segments.

**Independent Test**: Can be tested by making a routing change, triggering undo, verifying the change is reversed, then triggering redo and verifying it's restored.

**Acceptance Scenarios**:

1. **Given** user has dragged a segment to a new position, **When** user triggers undo, **Then** the segment returns to its previous position
2. **Given** user has undone a routing change, **When** user triggers redo, **Then** the routing change is reapplied

---

### Edge Cases

- What happens when user drags a segment that would create a path crossing through a block? The segment moves as requested; automatic block avoidance is not implemented (users manually route around blocks).
- What happens when a connected block is deleted? The entire connection is removed along with any custom waypoints.
- What happens when two waypoints would be placed at the same position? Adjacent waypoints that align are automatically merged into a single waypoint.
- What happens when user drags a segment to align with adjacent segments? The segments merge and intermediate waypoints are removed, simplifying the path.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render all connections using orthogonal (90-degree) routing only - no diagonal lines
- **FR-002**: System MUST support selecting a connection by clicking on it
- **FR-003**: System MUST allow dragging horizontal segments vertically and vertical segments horizontally
- **FR-004**: System MUST constrain segment drags to perpendicular movement only (horizontal segments cannot move horizontally, vertical segments cannot move vertically)
- **FR-005**: System MUST show real-time preview of the new path during drag operations
- **FR-006**: System MUST create waypoints automatically when segments are dragged
- **FR-007**: System MUST persist custom waypoints when saving diagrams
- **FR-008**: System MUST restore custom waypoints when loading diagrams
- **FR-009**: System MUST display appropriate cursor feedback when hovering over draggable segments
- **FR-010**: System MUST visually distinguish selected connections from unselected ones
- **FR-011**: System MUST provide a way to reset a connection to automatic routing
- **FR-012**: System MUST integrate routing changes with the existing undo/redo system
- **FR-013**: System MUST automatically merge adjacent waypoints when segments are dragged to align
- **FR-014**: System MUST snap waypoints to a grid (grid spacing consistent with existing block snapping)
- **FR-015**: System MUST use automatic orthogonal routing for new connections (no user intervention required)

### Key Entities

- **Connection**: Represents a link between two block ports; now includes an optional list of waypoints defining custom routing
- **Waypoint**: A coordinate point (x, y) that the connection path must pass through between source and target ports
- **Segment**: A horizontal or vertical line segment that is part of a connection's rendered path; segments between waypoints are computed, not stored

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can customize connection routing by dragging any segment to a new position in a single drag operation
- **SC-002**: All connections maintain strict orthogonal (90-degree) routing at all times - no diagonal segments visible
- **SC-003**: Custom routing persists correctly across save/load cycles with 100% fidelity
- **SC-004**: Routing changes integrate with undo/redo so users can reverse any routing edit
- **SC-005**: Visual feedback (cursor changes, selection highlighting, drag preview) is visible and responsive during all interactions
- **SC-006**: Diagrams with 50+ connections remain responsive during routing operations (no perceptible lag during drag)
- **SC-007**: Users report the routing interaction feels natural and intuitive (matches expectations from tools like Simulink)

## Assumptions

- Grid snapping will use the same grid size as block snapping (assumed to be 20px based on design document)
- Automatic block avoidance is out of scope - users are expected to manually route around blocks
- Parallel connections between the same blocks are handled independently (no automatic offset)
- The existing undo/redo infrastructure can be extended to support routing changes without major refactoring
- React Flow's custom edge API supports the required segment-level interaction handling

## Out of Scope

- Diagonal routing - all connections remain orthogonal
- Automatic obstacle/block avoidance during routing
- Connection bundling or automatic offset for parallel connections
- Bezier curves or smooth corners - corners remain sharp 90-degree angles
