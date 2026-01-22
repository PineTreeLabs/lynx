<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Block Resizing

**Feature Branch**: `007-block-resizing`
**Created**: 2026-01-12
**Status**: Draft
**Input**: User description: "Add support for manually resizing blocks. When a block is selected with a single click, small handle markers should appear on all 4 corners. Dragging any of these should have the expected behavior per standard UX best practices. In particular, the block should not move by applying collinearity snapping regardless of the resize. Also, in keeping with the Python as source of truth principle, the block size should be stored in the Python object. SVG-based blocks should scale and deform smoothly, including the X lines in the Sum block. Resizing will change port locations accordingly, so all connections should be auto-routed as part of the resize operation. Rendered labels and LaTeX inside the blocks should preserve font size and aspect ratio and should not stretch or otherwise deform. This block content should also preserve alignment including the block-relative location of the plus/minus symbols in the Sum block."

## Clarifications

### Session 2026-01-12

- Q: Should resizing be constrained to maintain aspect ratio or allow free-form resizing? → A: Free-form default - Free resize by default; hold Shift to lock aspect ratio.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resize Block via Corner Handles (Priority: P1)

A user working on a control system diagram wants to resize a block to better fit the layout or accommodate longer parameter labels. They click once on the block to select it, and small resize handles appear at all four corners. They drag any corner handle to resize the block, with the opposite corner remaining fixed. The block shape deforms smoothly as they drag.

**Why this priority**: This is the core interaction that enables all resizing functionality. Without corner handles and smooth resize behavior, the feature cannot exist.

**Independent Test**: Can be fully tested by selecting any block and dragging a corner handle. Delivers immediate value by allowing users to customize block sizes to fit their diagram layouts.

**Acceptance Scenarios**:

1. **Given** a diagram with a Gain block, **When** the user single-clicks the block, **Then** small square handles appear at all four corners of the block.
2. **Given** a selected block with visible corner handles, **When** the user drags the bottom-right handle diagonally outward, **Then** the block grows proportionally while the top-left corner remains fixed.
3. **Given** a selected block with visible corner handles, **When** the user drags the top-left handle diagonally inward, **Then** the block shrinks proportionally while the bottom-right corner remains fixed.
4. **Given** a selected block, **When** the user clicks elsewhere on the canvas, **Then** the resize handles disappear.
5. **Given** a user dragging a resize handle, **When** they release the mouse, **Then** the new block size is immediately persisted to the Python object.
6. **Given** a user dragging a corner handle without holding Shift, **When** they move diagonally, **Then** width and height change independently (free-form resize).
7. **Given** a user holding Shift while dragging a corner handle, **When** they resize the block, **Then** the original aspect ratio is preserved.

---

### User Story 2 - SVG Block Shape Scaling (Priority: P2)

A user resizes an SVG-based block (Gain triangle or Sum circle) and the shape scales smoothly with the new dimensions. The Gain block's triangle deforms to fit the new bounding box. The Sum block's circle deforms to an ellipse if resized non-uniformly. The X lines inside the Sum block scale proportionally to stay within the shape.

**Why this priority**: SVG blocks (Gain and Sum) have geometric shapes that must deform correctly. This is essential for visual consistency but depends on the basic resize handles being functional.

**Independent Test**: Can be tested by selecting a Gain block and resizing it to various aspect ratios, observing that the triangle fills the new bounding box. Similarly for Sum blocks.

**Acceptance Scenarios**:

1. **Given** a Gain block at default size (120x80), **When** the user resizes it to 180x120, **Then** the triangle scales to fill the new 180x120 bounding box.
2. **Given** a Sum block at default size (56x56), **When** the user resizes it to 80x60, **Then** the circle becomes an ellipse fitting the 80x60 bounding box.
3. **Given** a Sum block with an elliptical shape, **When** the block is displayed, **Then** the X lines inside scale proportionally and remain within the ellipse.

---

### User Story 3 - Block Content Preserves Font Size and Alignment (Priority: P2)

When a user resizes a block, the text and LaTeX content inside should not stretch or deform. Instead, the content maintains its original font size and aspect ratio, staying centered or aligned according to the block's style. The +/- symbols in the Sum block remain positioned relative to their input ports.

**Why this priority**: Maintaining readable, undistorted content is critical for diagram usability. This depends on resize functionality but is equally important for a complete feature.

**Independent Test**: Can be tested by resizing a TransferFunction block with a long equation and verifying the LaTeX remains readable at the same font size.

**Acceptance Scenarios**:

1. **Given** a Gain block displaying "K=1.5", **When** the user doubles the block size, **Then** the "K=1.5" text remains the same font size and stays centered within the larger block.
2. **Given** a TransferFunction block with a fraction equation, **When** the user resizes the block, **Then** the LaTeX fraction maintains its aspect ratio and font size.
3. **Given** a Sum block with +/- symbols in quadrants, **When** the user resizes the block, **Then** each symbol remains positioned near its corresponding input port, maintaining relative placement within each quadrant.

---

### User Story 4 - Connection Auto-Routing on Resize (Priority: P3)

When a user resizes a block, the port locations change. All connections attached to the block automatically re-route to accommodate the new port positions, just as they would when moving a block.

**Why this priority**: Connections must remain valid after resizing, but this leverages existing auto-routing infrastructure and is less novel than the resize interaction itself.

**Independent Test**: Can be tested by creating a diagram with connected blocks, resizing one block, and observing that all connections update to the new port locations.

**Acceptance Scenarios**:

1. **Given** a Gain block connected to another block, **When** the user resizes the Gain block, **Then** the connection re-routes to connect to the port at its new location.
2. **Given** a Sum block with three input connections, **When** the user resizes the Sum block, **Then** all three input connections update to the new input port positions.
3. **Given** a resize operation in progress (user dragging handle), **When** the handle position changes, **Then** connections update in real-time as the block resizes.

---

### User Story 5 - Block Position Stability During Resize (Priority: P3)

When a user drags a corner handle to resize a block, the opposite corner of the block remains stationary. The block's position does not jump due to collinearity snapping or any other automatic positioning feature.

**Why this priority**: Position stability is expected UX behavior but is listed separately to emphasize the explicit requirement to disable snapping during resize.

**Independent Test**: Can be tested by observing that the non-dragged corner of a block stays pixel-perfect stationary during resize.

**Acceptance Scenarios**:

1. **Given** a block positioned at (100, 100), **When** the user drags the bottom-right corner outward, **Then** the top-left corner remains at exactly (100, 100).
2. **Given** a block in a diagram with other aligned blocks that would normally trigger snapping, **When** the user resizes the block, **Then** no snapping occurs and the block resizes freely.

---

### Edge Cases

- What happens when resizing a block below a minimum size? (Block should have a minimum size threshold to remain usable)
- How does resize handle appear when block is flipped? (Handles should always appear at the visual corners regardless of flip state)
- What happens if the user resizes a block to a very large size? (No explicit maximum, but the block should remain usable)
- How do resize handles interact with block labels below the block? (Handles are on the block shape, not the label)
- What happens when resizing during an active drag-to-connect operation? (Should not interfere; resize only activates on single-click selection)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display resize handles at all four corners of a block when the block is selected with a single click.
- **FR-002**: Resize handles MUST be small square markers (approximately 8x8 pixels) visually distinct from the block shape.
- **FR-003**: System MUST allow dragging any corner handle to resize the block, keeping the opposite corner fixed. By default, width and height resize independently (free-form). When the user holds Shift while dragging, the original aspect ratio MUST be preserved.
- **FR-004**: System MUST persist block dimensions (width and height) in the Python Block object.
- **FR-005**: System MUST serialize block dimensions to the diagram JSON format.
- **FR-006**: SVG-based blocks (Gain triangle, Sum circle) MUST scale their shapes to fit the new block dimensions.
- **FR-007**: The Sum block's X lines MUST scale proportionally with the block shape.
- **FR-008**: Text and LaTeX content inside blocks MUST NOT stretch or deform during resize.
- **FR-009**: Text and LaTeX content MUST maintain their alignment (centered, etc.) within the resized block.
- **FR-010**: The +/- symbols in Sum blocks MUST remain positioned relative to their corresponding input ports.
- **FR-011**: System MUST re-route all connections when block port positions change due to resize.
- **FR-012**: Connection re-routing MUST occur in real-time during the resize drag operation.
- **FR-013**: System MUST NOT apply collinearity snapping or any position-adjusting behavior during resize.
- **FR-014**: System MUST enforce a minimum block size to ensure blocks remain usable (handles accessible, content visible).
- **FR-015**: Resize handles MUST appear at visual corners regardless of block flip state.
- **FR-016**: Each block type MUST have sensible default dimensions that match current behavior when no custom size is specified.

### Key Entities

- **Block Dimensions**: Width and height values (in pixels) stored as block attributes, used to render the block shape and position ports.
- **Resize Handle**: A small visual marker at each corner of a selected block that enables drag-to-resize interaction.
- **Anchor Corner**: The corner opposite to the handle being dragged, which remains fixed during resize.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can resize any block type by dragging corner handles with smooth, real-time visual feedback.
- **SC-002**: Block dimensions persist correctly through save/load cycles of the diagram.
- **SC-003**: SVG shapes scale smoothly without visual artifacts during and after resize.
- **SC-004**: Text and LaTeX content remains readable at consistent font size regardless of block dimensions.
- **SC-005**: All connected edges update correctly when blocks are resized, with no orphaned or misaligned connections.
- **SC-006**: The non-dragged corner of a block remains stationary during resize operations.
- **SC-007**: Resize operations complete without perceptible lag for diagrams with up to 50 blocks.

## Assumptions

- Resize handles are only visible when a block is selected (single-click selection).
- Double-click continues to trigger other interactions (e.g., parameter editing) and does not show resize handles.
- The existing auto-routing infrastructure for connections will be reused for resize-triggered re-routing.
- Default block dimensions match current hardcoded values to maintain backward compatibility.
- Blocks without explicit dimensions in saved diagrams use default sizes on load.
- Minimum block size is determined per block type to ensure usability (handles accessible, content visible).
