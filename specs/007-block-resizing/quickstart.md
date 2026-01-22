<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Block Resizing

**Feature**: 007-block-resizing
**Date**: 2026-01-12

## Test Scenarios

### Scenario 1: Basic Resize

**Setup**:
1. Create a new diagram
2. Add a Gain block

**Steps**:
1. Single-click the Gain block
2. Observe resize handles at all four corners
3. Drag the bottom-right handle outward
4. Release the mouse

**Expected**:
- Handles appear as 8x8 squares at corners
- Block grows smoothly during drag
- Top-left corner stays fixed
- New size persists (visible after deselecting and reselecting)

### Scenario 2: Free-form vs Constrained Resize

**Setup**:
1. Create a diagram with a Sum block

**Steps**:
1. Select the Sum block
2. Drag a corner handle diagonally WITHOUT holding Shift
3. Observe width and height change independently (circle becomes ellipse)
4. Reset by pressing Ctrl+Z
5. Hold Shift and drag the same handle
6. Observe aspect ratio is preserved (circle stays circular, just scaled)

**Expected**:
- Free-form: Can create ellipse from circle
- Shift+drag: Circle remains circular, scales uniformly

### Scenario 3: Minimum Size Enforcement

**Setup**:
1. Create a Gain block

**Steps**:
1. Select the block
2. Drag a corner handle to shrink the block as small as possible
3. Continue dragging past the minimum

**Expected**:
- Block stops shrinking at minimum size (60x40 for Gain)
- Cannot go smaller regardless of drag distance

### Scenario 4: Connection Re-routing

**Setup**:
1. Create two Gain blocks
2. Connect them with an edge
3. Manually edit the edge path (drag a segment to create custom waypoints)

**Steps**:
1. Select one of the Gain blocks
2. Resize it

**Expected**:
- Connection waypoints are cleared
- Edge auto-routes to new port positions
- Route updates in real-time during resize drag

### Scenario 5: Persistence

**Setup**:
1. Create a diagram with multiple blocks
2. Resize several blocks to custom sizes

**Steps**:
1. Save the diagram to JSON file
2. Close and reopen the diagram

**Expected**:
- All custom block sizes are preserved
- Blocks render at saved dimensions, not defaults

### Scenario 6: SVG Scaling (Gain Block)

**Setup**:
1. Create a Gain block with value K=2

**Steps**:
1. Resize the block to 180x120 (1.5x larger)

**Expected**:
- Triangle fills the new 180x120 bounding box
- "K=2" LaTeX stays same font size, remains centered
- Ports remain at correct positions (left edge center, right tip)

### Scenario 7: SVG Scaling (Sum Block)

**Setup**:
1. Create a Sum block with signs ["+", "+", "-"]

**Steps**:
1. Resize to 80x50 (non-uniform)

**Expected**:
- Circle becomes ellipse fitting 80x50
- X lines scale proportionally inside ellipse
- +/- symbols stay positioned near their ports (top, left, bottom)
- Output port stays at right center of ellipse

### Scenario 8: Flipped Block Resize

**Setup**:
1. Create a Gain block
2. Flip it horizontally (via context menu or parameter panel)

**Steps**:
1. Select the flipped block
2. Observe handle positions
3. Drag bottom-right handle

**Expected**:
- Handles appear at visual corners (same as unflipped)
- Resize behavior matches unflipped block
- Flip state is preserved after resize

### Scenario 9: Undo/Redo

**Setup**:
1. Create a block at default size

**Steps**:
1. Resize the block
2. Press Ctrl+Z (undo)
3. Press Ctrl+Y (redo)

**Expected**:
- Undo restores original size
- Redo restores resized size
- Multiple resize operations create separate undo states

### Scenario 10: Block Label Position

**Setup**:
1. Create a block
2. Make block label visible

**Steps**:
1. Resize the block

**Expected**:
- Label stays below the block shape
- Resize handles are on block shape only, not on label
- Label does not interfere with resize interaction

## Manual Verification Checklist

- [ ] Handles visible on selection
- [ ] Handles disappear on deselection
- [ ] Free-form resize works (independent width/height)
- [ ] Shift+drag locks aspect ratio
- [ ] Opposite corner stays fixed
- [ ] Minimum size enforced
- [ ] No position snapping during resize
- [ ] Connections re-route on resize
- [ ] Real-time visual feedback
- [ ] Dimensions persist to Python
- [ ] Save/load preserves dimensions
- [ ] Undo/redo works for resize
- [ ] All 5 block types resize correctly
- [ ] SVG shapes scale properly
- [ ] Text/LaTeX font size unchanged
- [ ] Content alignment preserved
- [ ] Works with flipped blocks
- [ ] No console errors during resize
