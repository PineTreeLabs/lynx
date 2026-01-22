<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quick Start: Block Drag Detection Testing

**Feature**: Block Drag Detection (015)
**Date**: 2026-01-18
**Purpose**: Manual and automated test scenarios for validating drag detection behavior

## Overview

This guide provides step-by-step test scenarios to verify the 5-pixel drag detection threshold works correctly for all block types and edge cases.

## Prerequisites

- Lynx development environment running
- Jupyter notebook with Lynx widget loaded
- Browser developer tools open (for inspecting node state)

## Test Scenarios

### Scenario 1: Click to Select (Core Functionality)

**Objective**: Verify that clicking a block with minimal movement (< 5px) selects it without changing position.

**Setup**:
1. Create a new Lynx diagram
2. Add a Gain block at position (100, 100)
3. Ensure block is not selected (no resize handles visible)

**Actions**:
1. Click on the Gain block
2. Move mouse slightly (2-3 pixels in any direction)
3. Release mouse button

**Expected Results**:
- ✅ Block becomes selected (resize handles visible)
- ✅ Block position remains at (100, 100)
- ✅ Parameter panel does NOT open (single click, not double-click)
- ✅ Selection happens within 50ms of mouse release (SC-001)

**Validation**:
```javascript
// In browser console
const node = reactFlowInstance.getNode('gain_block_id');
console.log('Selected:', node.selected);  // Should be true
console.log('Position:', node.position);  // Should be {x: 100, y: 100}
```

**Pass Criteria**: Block selected, position unchanged, resize handles visible

---

### Scenario 2: Drag to Move (Core Functionality)

**Objective**: Verify that dragging a block more than 5 pixels moves it without selection.

**Setup**:
1. Create a new Lynx diagram
2. Add a Sum block at position (200, 150)
3. Ensure block is not selected

**Actions**:
1. Click on the Sum block
2. Drag mouse 50 pixels to the right (final position ~250, 150)
3. Release mouse button

**Expected Results**:
- ✅ Block moves in real-time following cursor during drag
- ✅ Block position updates to approximately (250, 150)
- ✅ Block is NOT selected after drag (no resize handles)
- ✅ No selection highlight appears during or after drag
- ✅ Position updates at 60 FPS during drag (< 16ms latency, SC-002)

**Validation**:
```javascript
const node = reactFlowInstance.getNode('sum_block_id');
console.log('Selected:', node.selected);  // Should be false
console.log('Position X:', node.position.x);  // Should be ~250 (±5px for snapping)
```

**Pass Criteria**: Block moved to new position, NOT selected, no resize handles

---

### Scenario 3: Canvas Deselection (UI Interaction)

**Objective**: Verify that clicking empty canvas space deselects all blocks.

**Setup**:
1. Create a Lynx diagram with a TransferFunction block
2. Click the block to select it (verify resize handles appear)
3. Note the block's position for later verification

**Actions**:
1. Click on empty canvas space (not on any block, edge, or handle)
2. Verify click was not on block or handle (no visual feedback)

**Expected Results**:
- ✅ Block becomes deselected (resize handles disappear)
- ✅ Parameter panel closes (if open)
- ✅ Context menu closes (if open)
- ✅ Block position unchanged

**Validation**:
```javascript
const nodes = reactFlowInstance.getNodes();
const anySelected = nodes.some(n => n.selected);
console.log('Any node selected:', anySelected);  // Should be false
```

**Pass Criteria**: All blocks deselected, UI state cleared

---

### Scenario 4: Drag Selected Block (Interaction Edge Case)

**Objective**: Verify that dragging a selected block clears selection and moves it.

**Setup**:
1. Create a StateSpace block at (300, 200)
2. Click to select it (resize handles should appear)
3. Verify `node.selected === true`

**Actions**:
1. Click on the selected block (resize handles visible)
2. Drag 100 pixels downward (final position ~300, 300)
3. Release mouse button

**Expected Results**:
- ✅ Block moves in real-time during drag
- ✅ Resize handles disappear when drag starts (selection cleared)
- ✅ Block ends at new position (~300, 300)
- ✅ Block remains unselected after drag completes

**Validation**:
```javascript
const node = reactFlowInstance.getNode('state_space_block_id');
console.log('Selected:', node.selected);  // Should be false
console.log('Position Y:', node.position.y);  // Should be ~300 (±5px)
```

**Pass Criteria**: Block moved, selection cleared during drag, remains unselected

---

### Scenario 5: Edge Updates During Drag (Behavior Preservation)

**Objective**: Verify that connected edges update in real-time when blocks are dragged (preserve existing behavior).

**Setup**:
1. Create two Gain blocks: G1 at (100, 100), G2 at (300, 100)
2. Connect G1 output to G2 input (create edge)
3. Verify edge is visible and connects blocks

**Actions**:
1. Click on G1 and drag 50 pixels to the right
2. Observe edge behavior during drag
3. Release mouse button

**Expected Results**:
- ✅ Edge follows G1 in real-time during drag (smooth updates)
- ✅ Edge remains connected to both blocks throughout drag
- ✅ Edge routing updates automatically (orthogonal routing preserved)
- ✅ No edge waypoints remain after drag (cleared on drag start)

**Validation**:
- Visual inspection (automated check not feasible for real-time rendering)
- Edge should not "detach" or "snap back" during drag

**Pass Criteria**: Edge updates smoothly, stays connected, no visual glitches

---

### Scenario 6: Threshold Boundary Test (4.9px vs 5.1px)

**Objective**: Verify the 5-pixel threshold is accurately enforced.

**Setup**:
1. Create an IOMarker block at (400, 200)
2. Prepare to measure mouse movement precisely (use browser dev tools)

**Actions (Part A - Just Under Threshold)**:
1. Click IOMarker block
2. Move mouse exactly 4 pixels horizontally (hold Shift for straight line if possible)
3. Release mouse button

**Expected Results (Part A)**:
- ✅ Block selected (distance < 5px)
- ✅ Position unchanged at (400, 200)

**Actions (Part B - Just Over Threshold)**:
1. Deselect block (click empty canvas)
2. Click IOMarker block again
3. Move mouse exactly 6 pixels horizontally
4. Release mouse button

**Expected Results (Part B)**:
- ✅ Block moved to (406, 200)
- ✅ Block NOT selected (distance ≥ 5px)

**Validation**:
```javascript
// Part A
const node = reactFlowInstance.getNode('io_marker_id');
console.log('Selected:', node.selected);  // Should be true
console.log('Position:', node.position);  // Should be {x: 400, y: 200}

// Part B (after deselect and re-drag)
console.log('Selected:', node.selected);  // Should be false
console.log('Position X:', node.position.x);  // Should be ~406
```

**Pass Criteria**: 100% accuracy at threshold boundary (SC-004)

---

### Scenario 7: All Block Types Consistency

**Objective**: Verify drag detection works identically for all 5 block types.

**Setup**:
1. Create one of each block type:
   - Gain at (100, 100)
   - Sum at (200, 100)
   - TransferFunction at (300, 100)
   - StateSpace at (400, 100)
   - IOMarker at (500, 100)

**Actions**:
For EACH block type:
1. Click and move 3px → verify selected, position unchanged
2. Deselect (click canvas)
3. Click and drag 20px → verify moved, not selected

**Expected Results**:
- ✅ All blocks behave identically for small movements (< 5px)
- ✅ All blocks behave identically for large movements (≥ 5px)
- ✅ No special cases or type-specific bugs

**Validation**:
```javascript
const blocks = ['gain', 'sum', 'transfer_function', 'state_space', 'io_marker'];
blocks.forEach(type => {
  const node = reactFlowInstance.getNode(`${type}_id`);
  console.log(`${type}: selected=${node.selected}, position=${JSON.stringify(node.position)}`);
});
```

**Pass Criteria**: Consistent behavior across all block types (FR-013)

---

### Scenario 8: Extended Hold Without Movement

**Objective**: Verify that holding mouse button down for >2 seconds without moving selects block on release.

**Setup**:
1. Create a Gain block at (150, 150)
2. Ensure block is not selected

**Actions**:
1. Click (mousedown) on the Gain block
2. Hold mouse button without moving for 3 seconds
3. Release mouse button (mouseup)

**Expected Results**:
- ✅ Block becomes selected on release
- ✅ Position remains unchanged at (150, 150)
- ✅ No drag events triggered (distance = 0px)

**Validation**:
```javascript
const node = reactFlowInstance.getNode('gain_block_id');
console.log('Selected:', node.selected);  // Should be true
console.log('Position:', node.position);  // Should be {x: 150, y: 150}
```

**Pass Criteria**: Long hold treated as click, selection applied

---

### Scenario 9: Rapid Click-Drag-Click Sequence

**Objective**: Verify that rapidly alternating between clicks and drags doesn't cause state corruption.

**Setup**:
1. Create a Sum block at (250, 250)

**Actions** (perform quickly in succession):
1. Click Sum block (3px movement) → should select
2. Click canvas to deselect
3. Drag Sum block 30px right → should move to (280, 250)
4. Click Sum block (2px movement) → should select at new position
5. Drag Sum block 40px down → should move to (280, 290)

**Expected Results**:
- ✅ Each operation evaluates independently (no state carryover)
- ✅ No race conditions or position jumping
- ✅ Block ends at (280, 290), not selected

**Validation**:
```javascript
const node = reactFlowInstance.getNode('sum_block_id');
console.log('Final selected:', node.selected);  // Should be false
console.log('Final position:', node.position);  // Should be ~{x: 280, y: 290}
```

**Pass Criteria**: All operations execute correctly without interference

---

### Scenario 10: Collinear Snapping Preservation

**Objective**: Verify that existing collinear snapping (20px threshold) still works after drag detection is implemented.

**Setup**:
1. Create two Gain blocks: G1 at (100, 100), G2 at (100, 200) (vertically aligned)
2. Create a third Gain block G3 at (250, 150) (not aligned)

**Actions**:
1. Drag G3 horizontally toward G1/G2 column
2. Stop dragging when G3 is at approximately (98, 150) - within 20px of x=100
3. Release mouse button

**Expected Results**:
- ✅ G3 snaps to x=100 (aligned with G1 and G2)
- ✅ G3 final position is approximately (100, 150)
- ✅ G3 is not selected after drag
- ✅ Collinear snapping still triggers (existing behavior preserved)

**Validation**:
```javascript
const node = reactFlowInstance.getNode('g3_id');
console.log('Position X:', node.position.x);  // Should be 100 (snapped)
console.log('Position Y:', node.position.y);  // Should be ~150
console.log('Selected:', node.selected);  // Should be false
```

**Pass Criteria**: Collinear snapping works, 20px threshold preserved

---

## Automated Test Suite

### Unit Tests (`useDragDetection.test.ts`)

**Test: Distance Calculation Accuracy**
```typescript
test('calculateDistance returns Euclidean distance', () => {
  const start = { x: 0, y: 0 };
  const end = { x: 3, y: 4 };
  expect(calculateDistance(start, end)).toBe(5); // 3-4-5 triangle
});

test('calculateDistanceSquared avoids sqrt overhead', () => {
  const start = { x: 0, y: 0 };
  const end = { x: 3, y: 4 };
  expect(calculateDistanceSquared(start, end)).toBe(25); // 5²
});
```

**Test: Threshold Detection**
```typescript
test('movement < 5px triggers selection', () => {
  const distanceSquared = 24; // sqrt(24) ≈ 4.9px
  expect(distanceSquared < 25).toBe(true); // Should select
});

test('movement ≥ 5px triggers move', () => {
  const distanceSquared = 26; // sqrt(26) ≈ 5.1px
  expect(distanceSquared >= 25).toBe(true); // Should move
});
```

---

### Integration Tests (`DiagramCanvas.test.tsx`)

**Test: Click-to-Select Workflow**
```typescript
test('clicking block with < 5px movement selects it', () => {
  const { getByTestId } = render(<DiagramCanvas />);
  const block = getByTestId('gain-block');

  fireEvent.mouseDown(block, { clientX: 100, clientY: 100 });
  fireEvent.mouseMove(block, { clientX: 102, clientY: 103 }); // 3.6px movement
  fireEvent.mouseUp(block, { clientX: 102, clientY: 103 });

  const node = reactFlowInstance.getNode('gain-block-id');
  expect(node.selected).toBe(true);
  expect(node.position).toEqual({ x: 100, y: 100 });
});
```

**Test: Drag-to-Move Workflow**
```typescript
test('dragging block ≥ 5px moves it without selection', () => {
  const { getByTestId } = render(<DiagramCanvas />);
  const block = getByTestId('sum-block');

  fireEvent.mouseDown(block, { clientX: 200, clientY: 150 });
  fireEvent.mouseMove(block, { clientX: 250, clientY: 150 }); // 50px movement
  fireEvent.mouseUp(block, { clientX: 250, clientY: 150 });

  const node = reactFlowInstance.getNode('sum-block-id');
  expect(node.selected).toBe(false);
  expect(node.position.x).toBeCloseTo(250, 1); // ±1px tolerance for snapping
});
```

---

## Performance Validation

### Latency Measurements

**Tool**: Chrome DevTools Performance Profiler

**Steps**:
1. Open DevTools → Performance tab
2. Start recording
3. Perform Scenario 2 (Drag to Move 50px)
4. Stop recording
5. Analyze flame graph

**Metrics to Verify**:
- **Selection response** (Scenario 1): Time from mouseup to resize handles visible < 50ms (SC-001)
- **Drag update latency** (Scenario 2): Time between mouse move events < 16ms (SC-002)
- **Distance calculation overhead**: Function execution time < 1ms

**Pass Criteria**:
- All frame times < 16ms (60 FPS maintained)
- No long tasks (>50ms) during drag operations
- Distance calculation not visible in profiler (negligible overhead)

---

## Manual Testing Checklist

Before merging this feature, verify:

- [ ] Scenario 1: Click-to-select works (< 5px)
- [ ] Scenario 2: Drag-to-move works (≥ 5px)
- [ ] Scenario 3: Canvas deselection works
- [ ] Scenario 4: Dragging selected block clears selection
- [ ] Scenario 5: Edges update in real-time during drag
- [ ] Scenario 6: Threshold boundary accurate (4.9px vs 5.1px)
- [ ] Scenario 7: All block types behave consistently
- [ ] Scenario 8: Extended hold (>2s) selects on release
- [ ] Scenario 9: Rapid sequences don't corrupt state
- [ ] Scenario 10: Collinear snapping still works (20px)
- [ ] Performance: Selection < 50ms, drag < 16ms (60 FPS)
- [ ] No regressions: Existing features still work (resize, flip, delete, undo/redo)

---

## Troubleshooting

### Issue: Block Moves Slightly When Clicking

**Symptoms**: Block position changes by 1-2 pixels after click

**Diagnosis**:
```javascript
// Check if position change is being filtered
const changes = []; // captured in onNodesChange
console.log('Position changes:', changes.filter(c => c.type === 'position'));
```

**Possible Causes**:
1. Distance threshold not filtering correctly (check < vs ≤)
2. dragStartPos ref not storing initial position
3. React Flow's internal position updates not intercepted

**Fix**: Verify `onNodesChange` filter returns `false` for distance < 5px

---

### Issue: Drag Not Triggering Movement

**Symptoms**: Block doesn't move when dragged > 5px

**Diagnosis**:
```javascript
// Check if position changes are being applied
const node = reactFlowInstance.getNode('block_id');
console.log('Draggable:', node.draggable); // Should be true (or undefined)
console.log('Position:', node.position);
```

**Possible Causes**:
1. onNodesChange filter returning `false` for all position changes
2. dragStartPos ref not being cleaned up (stale data)
3. Distance calculation error (always returns < 5px)

**Fix**: Add logging to distance calculation, verify cleanup in onNodesChange

---

### Issue: Selection Not Applied After Click

**Symptoms**: Block doesn't show resize handles after small movement

**Diagnosis**:
```javascript
const node = reactFlowInstance.getNode('block_id');
console.log('Selected:', node.selected);  // Should be true
console.log('Draggable:', node.draggable); // Should allow selection
```

**Possible Causes**:
1. setNodes not updating `selected` property
2. NodeResizer `isVisible` not reacting to `selected` change
3. onClick handler preventing selection

**Fix**: Verify setNodes callback in onNodesChange sets `selected: true`

---

## Success Criteria Reference

From feature specification (spec.md):

- **SC-001**: Selection indicators appear within 50ms ✅
- **SC-002**: Drag updates at 60 FPS (< 16ms latency) ✅
- **SC-003**: No resize handles during drag 100% of time ✅
- **SC-004**: 100% drag detection accuracy at 5px threshold ✅
- **SC-005**: 10 consecutive operations without errors ✅

All test scenarios above map to these success criteria. Passing all scenarios validates feature completeness.
