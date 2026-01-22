<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Block Drag Detection

**Feature Branch**: `015-block-drag-detection`
**Created**: 2026-01-18
**Status**: Draft
**Input**: User description: "Implement drag detection for block movement.  The intended behavior is that if a block is clicked and moved less than 5px, it is selected (+highlight, +resize handles displayed, no movement), but if it is clicked and dragged further, then it is moved *without* being selected (no highlight, no resize handles).  Block movement 'live previews' should not show resize handles."

## Clarifications

### Session 2026-01-18

- Q: When a user clicks on empty canvas space (not on any block), what should happen to the currently selected block? → A: Clicking empty canvas deselects the current block (standard diagram tool behavior)
- Q: When a block with connections is being dragged, should the connected edges update in real-time to follow the block, or should they update only after the drag completes? → A: Edges update in real-time during drag (preserve existing behavior exactly)
- Q: When dragging a block, should the block be constrained to stay within the visible canvas boundaries, or can it be dragged partially or fully outside the canvas area? → A: Blocks can be dragged outside canvas boundaries (preserve existing behavior exactly)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Click to Select (Priority: P1)

Users need to select blocks with a click to access editing controls (resize handles, parameter panel) without accidentally moving the block. When a user clicks on a block and releases without moving (or moves less than 5 pixels), the block should become selected, showing highlight and resize handles, but should not change position.

**Why this priority**: This is the foundation of block interaction - users must be able to select blocks reliably to access all editing features. Without this, users cannot resize blocks, edit parameters, or perform any selection-based operations.

**Independent Test**: Can be fully tested by clicking various blocks on the canvas and verifying that they become selected (highlighted with resize handles visible) without moving from their original position. Delivers immediate value by enabling all selection-dependent features.

**Acceptance Scenarios**:

1. **Given** an unselected block on the canvas, **When** user clicks the block and releases without moving the mouse, **Then** the block becomes selected with highlight and resize handles visible, and the block position remains unchanged
2. **Given** an unselected block on the canvas, **When** user clicks the block, moves mouse less than 5 pixels in any direction, and releases, **Then** the block becomes selected with highlight and resize handles visible, and the block position remains unchanged
3. **Given** a selected block on the canvas, **When** user clicks a different block without moving the mouse, **Then** the first block becomes unselected and the second block becomes selected with highlight and resize handles visible
4. **Given** a selected block on the canvas, **When** user clicks on empty canvas space (not on any block), **Then** the block becomes unselected and no selection indicators are displayed

---

### User Story 2 - Drag to Move Without Selection (Priority: P2)

Users need to quickly reposition blocks by dragging them across the canvas without triggering selection behavior. When a user clicks on a block and drags it more than 5 pixels, the block should move in real-time following the cursor, but should not show selection indicators (highlight, resize handles) during or after the drag operation.

**Why this priority**: Once users can select blocks (P1), they need efficient repositioning without extra clicks. This streamlines the workflow by allowing direct dragging without needing to deselect or manage selection state during movement.

**Independent Test**: Can be fully tested by dragging blocks across the canvas and verifying that they follow the cursor without showing resize handles during the drag, and that they remain unselected after being released. Delivers value by enabling fluid block repositioning.

**Acceptance Scenarios**:

1. **Given** an unselected block on the canvas, **When** user clicks the block and drags more than 5 pixels, **Then** the block moves in real-time following the cursor without showing highlight or resize handles during the drag
2. **Given** a selected block on the canvas, **When** user clicks the block and drags more than 5 pixels, **Then** the block moves following the cursor, the selection state is cleared (no highlight or resize handles), and the block remains unselected after release
3. **Given** a block being dragged across the canvas, **When** user releases the mouse button, **Then** the block is placed at the final position without becoming selected (no highlight or resize handles appear)

---

### User Story 3 - Clear Visual Feedback During Movement (Priority: P3)

Users need clear visual feedback during block dragging to understand the block's position without confusion from selection indicators. During the drag operation, the block should show a "live preview" of its position without displaying resize handles, ensuring the user can see the block bounds clearly without visual clutter.

**Why this priority**: After basic selection (P1) and movement (P2) work, polished visual feedback prevents user confusion and creates a professional experience. This is lower priority because the core functionality works without it, but it significantly improves usability.

**Independent Test**: Can be fully tested by dragging blocks while observing the visual presentation - the block should be visible and positioned correctly throughout the drag without resize handles appearing. Delivers value by reducing visual noise and improving spatial awareness during repositioning.

**Acceptance Scenarios**:

1. **Given** a user dragging a block across the canvas, **When** the block is in motion, **Then** the block's visual representation (shape, label, content) is clearly visible without resize handles or selection highlight
2. **Given** multiple blocks on the canvas with one being dragged, **When** the dragged block passes over or near other blocks, **Then** the dragged block's preview remains visually distinct and the absence of resize handles makes the block bounds clear
3. **Given** a user dragging a block near the canvas edge, **When** the block approaches the boundary, **Then** the block preview position updates smoothly without resize handles obscuring the visual feedback

---

### Edge Cases

- What happens when a user clicks and holds on a block for an extended time (>2 seconds) without moving? (Expected: block should be selected when mouse is released, similar to a normal click)
- How does the system handle rapid click-drag-release sequences (e.g., user quickly clicks and drags multiple blocks in succession)? (Expected: each interaction should be evaluated independently based on the 5-pixel threshold)
- What happens when a user starts dragging a block, crosses the 5-pixel threshold, but then drags back to near the original position before releasing? (Expected: block should move to the final cursor position and remain unselected, even if final position is close to original)
- How does the system handle dragging on touchscreen devices where pointer precision may vary? (Expected: 5-pixel threshold should still apply based on actual touch movement delta)
- What happens when a user drags a selected block? (Expected: selection should be cleared and block should move without showing selection indicators)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect when a user clicks on a block and distinguish between a click-to-select action (movement < 5 pixels) and a drag-to-move action (movement ≥ 5 pixels)
- **FR-002**: System MUST select a block (display highlight and resize handles) when the user clicks and releases with less than 5 pixels of movement in any direction
- **FR-003**: System MUST NOT change a block's position when the interaction qualifies as a click-to-select (movement < 5 pixels)
- **FR-004**: System MUST deselect the currently selected block when the user clicks on empty canvas space (not on any block)
- **FR-005**: System MUST move a block in real-time following the cursor when the user drags more than 5 pixels from the initial click position
- **FR-006**: System MUST NOT display selection indicators (highlight, resize handles) on a block during a drag-to-move operation (movement ≥ 5 pixels)
- **FR-007**: System MUST NOT select a block after a drag-to-move operation completes (block remains unselected after release)
- **FR-008**: System MUST clear existing selection state when a selected block is dragged (movement ≥ 5 pixels)
- **FR-009**: System MUST calculate movement distance using Euclidean distance from the initial click position: `distance = sqrt((x_current - x_initial)² + (y_current - y_initial)²)`
- **FR-010**: System MUST show the block's visual representation (shape, content, label) during a drag operation without displaying resize handles
- **FR-011**: System MUST update connected edges in real-time as a block is dragged, preserving existing edge routing behavior
- **FR-012**: System MUST allow blocks to be dragged outside the visible canvas boundaries without constraint
- **FR-013**: System MUST maintain consistent drag detection behavior across all block types (Gain, Sum, TransferFunction, StateSpace, IOMarker)

### Key Entities

- **Block**: Represents a diagram block that can be selected or moved. Key attributes include position (x, y coordinates), selection state (boolean), and visual bounds (width, height)
- **Drag Interaction**: Represents a user's click-and-drag action. Key attributes include initial click position, current cursor position, movement distance (calculated), and interaction state (pending, selecting, moving)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select any block on the canvas with a single click (movement < 5 pixels) and see selection indicators appear within 50 milliseconds
- **SC-002**: Users can drag any block across the canvas (movement ≥ 5 pixels) and see real-time position updates with latency under 16 milliseconds (60 FPS)
- **SC-003**: Block movement "live previews" display no resize handles during drag operations 100% of the time
- **SC-004**: Drag detection correctly distinguishes between click-to-select and drag-to-move actions with 100% accuracy based on the 5-pixel movement threshold
- **SC-005**: Users can perform 10 consecutive block selection and movement operations without any incorrect behavior (false positives/negatives in drag detection)

## Assumptions *(optional)*

- The 5-pixel movement threshold is measured in screen pixels (not canvas coordinates accounting for zoom)
- Movement distance is calculated as Euclidean distance from the initial click point to the current cursor position
- Drag detection applies to primary mouse button interactions (left-click on most systems)
- The existing block selection system already supports programmatic selection/deselection via state management
- React Flow's existing drag handlers can be extended or replaced to implement custom drag detection logic
- Resize handles are controlled by the same selection state that controls highlight/selection indicators
- The existing canvas allows blocks to be positioned anywhere, including outside visible boundaries (users can pan to retrieve)
- The existing edge routing system updates connections in real-time during block movement
