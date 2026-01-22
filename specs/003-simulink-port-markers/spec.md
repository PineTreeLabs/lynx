<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Simulink-Style Port Markers

**Feature Branch**: `003-simulink-port-markers`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "Modify the block port markers (currently dots) to follow the visual style of Simulink.  Specifically, input ports should have a 'sideways carat' pointing into the block and output ports should have a 'sideways carat' poiting out of the block.  These symbols should obey the standard 'flip horizontal' semantics, and should disappear when a connection to that port is made.  Finally, these markers should appear on the edge of the visible block and should be centered on the block geometry."

## Clarifications

### Session 2026-01-05

- Q: Multiple ports on same edge - how should markers be spaced/arranged? → A: Not an issue for current block library. Only the Sum block has multiple ports, arranged in a circular pattern where ports aren't near each other.
- Q: How are port markers displayed on blocks with very small dimensions where markers might overlap with block content? → A: Render markers at full fixed size regardless of block dimensions (may overlap block content if block is very small).
- Q: How do port markers behave during drag-and-drop connection operations (before connection is finalized)? → A: Destination port marker disappears when drag operation hovers over it; source port marker remains until drop.
- Q: What happens when a user rapidly connects and disconnects ports (marker visibility toggling)? → A: Markers update immediately on each connect/disconnect action with no debouncing (may flicker if very rapid).
- Q: Triangle marker exact dimensions and shape? → A: Start with 10px equilateral triangle, but make this flexible so we can adjust to isosceles with different scale if needed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visual Port Identification on Unconnected Blocks (Priority: P1)

Users building block diagrams need to quickly identify input and output ports on unconnected blocks without having to consult documentation or hover for tooltips. The Simulink-style port markers provide immediate visual feedback about port direction through standardized symbols.

**Why this priority**: This is the core value of the feature - enabling users to distinguish port types at a glance, which is essential for efficient diagram construction. Without this, users must rely on less intuitive visual cues or trial-and-error when connecting blocks.

**Independent Test**: Can be fully tested by placing an unconnected block on the canvas and verifying that input ports show inward-pointing triangular markers and output ports show outward-pointing triangular markers. Delivers immediate value by improving visual clarity.

**Acceptance Scenarios**:

1. **Given** a new block is placed on the canvas with no connections, **When** the user views the block, **Then** each input port displays a triangular marker (sideways carat) pointing toward the block interior
2. **Given** a new block is placed on the canvas with no connections, **When** the user views the block, **Then** each output port displays a triangular marker (sideways carat) pointing away from the block
3. **Given** an unconnected block on the canvas, **When** the user views the block, **Then** all port markers are positioned on the block's edge and centered on their respective port geometry

---

### User Story 2 - Port Marker Visibility Based on Connection State (Priority: P2)

Users connecting blocks together need port markers to disappear once a connection is established, reducing visual clutter and clearly distinguishing connected ports from unconnected ones.

**Why this priority**: While important for visual clarity and following Simulink conventions, users can still build functional diagrams without this behavior. It primarily enhances the user experience by reducing visual noise.

**Independent Test**: Can be fully tested by connecting two blocks and verifying that the port markers disappear at both the source and destination ports of the connection, while markers remain visible on unconnected ports.

**Acceptance Scenarios**:

1. **Given** two unconnected blocks with visible port markers, **When** the user creates a connection between an output port and an input port, **Then** the port markers disappear on both the connected output port and the connected input port
2. **Given** a block with both connected and unconnected ports, **When** the user views the block, **Then** only the unconnected ports display port markers
3. **Given** a connection between two blocks, **When** the user deletes the connection, **Then** the port markers reappear on both previously connected ports

---

### User Story 3 - Port Marker Orientation with Horizontal Flip (Priority: P3)

Users who flip blocks horizontally need port markers to maintain correct directional semantics - input markers should always point into the block and output markers should always point out of the block, regardless of block orientation.

**Why this priority**: This is a refinement that ensures consistency when blocks are manipulated. While helpful for maintaining visual clarity during diagram rearrangement, it's not essential for basic diagram functionality.

**Independent Test**: Can be fully tested by placing a block, flipping it horizontally, and verifying that input port markers continue pointing into the block and output port markers continue pointing out of the block (with markers on opposite physical sides after the flip).

**Acceptance Scenarios**:

1. **Given** a block with visible port markers in default orientation, **When** the user flips the block horizontally, **Then** input port markers remain pointing toward the block interior and output port markers remain pointing away from the block
2. **Given** a horizontally-flipped block, **When** the user views the port markers, **Then** the markers are positioned on the opposite edge from their pre-flip positions but maintain correct directional semantics
3. **Given** a horizontally-flipped block with connections, **When** the user views the block, **Then** only unconnected ports show markers with correct orientation

---

### Edge Cases

- No critical edge cases remain unresolved. All identified scenarios have been clarified in the Clarifications section.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display triangular markers (sideways carats) on all unconnected input ports, with the triangle pointing toward the block interior
- **FR-002**: System MUST display triangular markers (sideways carats) on all unconnected output ports, with the triangle pointing away from the block
- **FR-003**: System MUST position port markers on the edge of the visible block boundary
- **FR-004**: System MUST center port markers on the geometric center of each port
- **FR-005**: System MUST hide port markers when a connection is made to that port
- **FR-006**: System MUST show port markers when a connection is removed from that port
- **FR-007**: System MUST maintain correct directional semantics for port markers when blocks are horizontally flipped (input markers point in, output markers point out)
- **FR-008**: System MUST update port marker positions and orientations in real-time during block transformations (flip operations)
- **FR-009**: Port markers MUST be visually distinguishable from the current dot-based markers, using theme colors (primary-600, same as block borders) with fixed size that does not scale with block dimensions
- **FR-010**: Port markers MUST render at full fixed size regardless of block dimensions (markers may overlap block content on very small blocks)
- **FR-011**: During drag-and-drop connection operations, the destination port marker MUST disappear when the drag operation hovers over it, while the source port marker MUST remain visible until the connection is finalized

### Key Entities

- **Port Marker**: A triangular visual indicator associated with a block port, having properties for position (edge-aligned, centered on port), orientation (inward/outward), and visibility state (shown/hidden based on connection status)
- **Block Port**: A connection point on a block with a type (input/output) and connection state (connected/unconnected) that determines marker rendering

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify port direction (input vs output) on unconnected blocks without tooltips or documentation in under 1 second
- **SC-002**: Port markers disappear within 100ms of connection creation
- **SC-003**: Port markers correctly maintain directional semantics on 100% of blocks after horizontal flip operations
- **SC-004**: Visual clarity of diagrams improves, measured by 30% reduction in user errors when connecting incompatible ports (if telemetry available)

## Assumptions *(include if you made informed guesses)*

- **Port marker size and shape**: Markers are 10px equilateral triangles (fixed size, does not scale with block dimensions), with flexibility to adjust to isosceles proportions if needed during implementation
- **Marker color**: Markers use theme color primary-600, matching the existing block border color scheme for visual consistency
- **Flip semantics**: Assuming "flip horizontal" refers to the existing block flip functionality in the application
- **Connection detection**: Assuming the application already has a mechanism to detect when ports are connected/disconnected that can trigger marker visibility changes
- **Rendering performance**: Assuming marker rendering should have negligible performance impact (same order of magnitude as current dot markers)

## Dependencies

- Requires access to the current block rendering system to replace dot markers
- Requires access to block flip transformation logic
- Requires access to connection state management to toggle marker visibility
- May depend on existing visual design guidelines or theming system

## Out of Scope

- Changing port functionality or connection behavior (only visual markers are affected)
- Adding new port types beyond existing input/output ports
- Customizing marker appearance per-block or per-user
- Animated transitions for marker appearance/disappearance (unless trivial to implement)
- Tooltips or additional information displays on port hover
