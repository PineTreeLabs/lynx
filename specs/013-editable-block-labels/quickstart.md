<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart Test Scenarios: Editable Block Labels in Parameter Panel

**Date**: 2026-01-16
**Feature**: 013-editable-block-labels
**Phase**: 1 (Design & Contracts)

## Overview

This document provides concrete test scenarios for validating the editable block labels feature. Each scenario maps to acceptance criteria from the feature specification and can be executed manually or automated via Vitest/pytest.

---

## Setup Prerequisites

### Python Environment
```python
import lynx

# Create test diagram with multiple block types
diagram = lynx.Diagram()
diagram.add_block('gain', 'controller', K=5.0)
diagram.add_block('transfer_function', 'plant',
                 numerator=[1.0], denominator=[1.0, 2.0, 1.0])
diagram.add_block('state_space', 'observer',
                 A=[[0, 1], [-2, -3]], B=[[0], [1]],
                 C=[[1, 0]], D=[[0]])
diagram.add_block('io_marker', 'input', marker_type='input', label='r')

# Display widget
diagram
```

### Frontend Environment
```bash
cd js/
npm install
npm test -- --run  # Run all tests
```

---

## Test Scenarios by User Story

### US1: Replace Type Display with Label Field (Priority: P1)

#### Scenario US1-1: Label Field Appears for Gain Block
**Given**: A Gain block is selected on the canvas
**When**: The Parameter panel opens
**Then**:
- The panel displays "Label" field with an input containing "controller" (the block ID)
- The static "Type: gain" text is NOT visible
- Standard text input controls are available (cursor positioning, select-all works)

**Validation**:
```typescript
// LabelEditor.test.tsx or ParameterPanel.test.tsx
test('shows label editor for Gain block', () => {
  const block = {
    id: 'controller',
    type: 'gain',
    label: 'controller',
    parameters: [{name: 'K', value: 5.0}]
  };
  render(<ParameterPanel block={block} onUpdate={mockUpdate} onClose={mockClose} />);

  expect(screen.queryByText(/Type:/)).not.toBeInTheDocument();
  expect(screen.getByLabelText(/Label/i)).toHaveValue('controller');
  expect(screen.getByLabelText(/Label/i)).toHaveFocus(); // Optional: auto-focus
});
```

**Manual Test**:
1. Open Jupyter notebook with diagram
2. Click on "controller" Gain block
3. Verify Parameter panel shows "Label" input field at top
4. Verify "Type: gain" text is removed
5. Triple-click label input, verify text selects (select-all)

---

#### Scenario US1-2: Label Field Shows Custom Label
**Given**: A Transfer Function block with custom label "Plant Model" is selected
**When**: The Parameter panel opens
**Then**:
- Label field displays "Plant Model" (not the block ID "plant")
- Input is editable with cursor positioning working

**Setup**:
```python
# Python: Set custom label
diagram.update_block_label('plant', 'Plant Model')
```

**Validation**:
```typescript
test('shows custom label when set', () => {
  const block = {
    id: 'plant',
    type: 'transfer_function',
    label: 'Plant Model',  // Custom label ≠ id
    parameters: [...]
  };
  render(<ParameterPanel block={block} ... />);
  expect(screen.getByLabelText(/Label/i)).toHaveValue('Plant Model');
});
```

**Manual Test**:
1. Python: `diagram.update_block_label('plant', 'Plant Model')`
2. Click on Transfer Function block
3. Verify label field shows "Plant Model"
4. Click inside input, verify cursor appears at click position

---

#### Scenario US1-3: Label Field Appears for All Parameter Panel Block Types
**Given**: Gain, TransferFunction, StateSpace, and IOMarker blocks exist
**When**: Each block is selected individually
**Then**: Each block's Parameter panel shows the label editor field

**Validation**:
```typescript
test.each([
  { type: 'gain', id: 'g1' },
  { type: 'transfer_function', id: 'tf1' },
  { type: 'state_space', id: 'ss1' },
  { type: 'io_marker', id: 'io1' }
])('shows label editor for $type block', ({ type, id }) => {
  const block = { id, type, label: id, parameters: [], ports: [] };
  render(<ParameterPanel block={block} ... />);
  expect(screen.getByLabelText(/Label/i)).toBeInTheDocument();
});
```

**Manual Test**:
1. Create one of each block type
2. Click each block sequentially
3. Verify label editor appears in Parameter panel for all 4 types
4. Verify Sum block does NOT show Parameter panel (uses quadrant config)

---

### US2: Edit Block Label via Parameter Panel (Priority: P1)

#### Scenario US2-1: Edit Label with Enter Key
**Given**: Gain block "controller" selected with Parameter panel open
**When**: User types "PID Controller" and presses Enter
**Then**:
- Block label updates to "PID Controller" in Python Diagram object
- Canvas label displays "PID Controller" (if label_visible is true)
- Input blurs after Enter press

**Validation**:
```typescript
test('updates label on Enter key', async () => {
  const user = userEvent.setup();
  const mockUpdate = jest.fn();
  const block = { id: 'controller', type: 'gain', label: 'controller', ... };

  render(<ParameterPanel block={block} onUpdate={mockUpdate} ... />);
  const input = screen.getByLabelText(/Label/i);

  await user.clear(input);
  await user.type(input, 'PID Controller{Enter}');

  expect(mockUpdate).toHaveBeenCalledWith('controller', 'label', 'PID Controller');
  expect(input).not.toHaveFocus(); // Blur after Enter
});
```

**Manual Test**:
1. Click "controller" block
2. In label field, type "PID Controller" and press Enter
3. Verify label field blurs (no longer focused)
4. Python: `print(diagram._blocks['controller'].label)` → "PID Controller"
5. Verify canvas label shows "PID Controller" (if Show label was enabled)

---

#### Scenario US2-2: Edit Label with Blur
**Given**: Transfer Function block "plant" selected
**When**: User types "Second Order Plant" and clicks outside the input
**Then**:
- Block label updates to "Second Order Plant"
- UI reflects new label

**Validation**:
```typescript
test('updates label on blur', async () => {
  const user = userEvent.setup();
  const mockUpdate = jest.fn();
  const block = { id: 'plant', type: 'transfer_function', label: 'plant', ... };

  render(<ParameterPanel block={block} onUpdate={mockUpdate} ... />);
  const input = screen.getByLabelText(/Label/i);

  await user.clear(input);
  await user.type(input, 'Second Order Plant');
  await user.tab(); // Blur by tabbing away

  expect(mockUpdate).toHaveBeenCalledWith('plant', 'label', 'Second Order Plant');
});
```

**Manual Test**:
1. Click "plant" block
2. Type "Second Order Plant" in label field
3. Click on another part of the panel (e.g., numerator field)
4. Verify label saved (Python check)

---

#### Scenario US2-3: Clear Label Reverts to Block ID
**Given**: Block with custom label "My Controller"
**When**: User clears the label field and presses Enter
**Then**:
- Label reverts to block ID "controller"
- Python validation: `block.label == block.id`

**Validation**:
```python
# test_diagram.py
def test_update_block_label_empty_reverts_to_id():
    diagram = Diagram()
    diagram.add_block('gain', 'controller', K=5.0)
    diagram.update_block_label('controller', 'My Controller')

    # Clear label (empty string)
    diagram.update_block_label('controller', '')

    block = diagram._blocks['controller']
    assert block.label == 'controller'  # Reverted to ID
```

**Manual Test**:
1. Set custom label: `diagram.update_block_label('controller', 'My Controller')`
2. Click block, clear label field completely
3. Press Enter
4. Verify label field now shows "controller" (block ID)

---

#### Scenario US2-4: Trim Whitespace
**Given**: Block "controller" selected
**When**: User types "  Spaced Label  " (with leading/trailing spaces) and presses Enter
**Then**:
- Label saved as "Spaced Label" (spaces trimmed)
- Python: `block.label == 'Spaced Label'`

**Validation**:
```typescript
test('trims whitespace on save', async () => {
  const user = userEvent.setup();
  const mockUpdate = jest.fn();
  const block = { id: 'c1', type: 'gain', label: 'c1', ... };

  render(<ParameterPanel block={block} onUpdate={mockUpdate} ... />);
  const input = screen.getByLabelText(/Label/i);

  await user.clear(input);
  await user.type(input, '  Spaced Label  {Enter}');

  // Verify trimmed value sent to backend
  expect(mockUpdate).toHaveBeenCalledWith('c1', 'label', 'Spaced Label');
});
```

**Manual Test**:
1. Type "  Spaced Label  " (include spaces before and after)
2. Press Enter
3. Python: `diagram._blocks['controller'].label` → "Spaced Label" (no spaces)

---

#### Scenario US2-5: Cancel Edit with Escape
**Given**: Block with label "Original" selected, label field focused
**When**: User types "Changed" and presses Escape (without Enter/blur)
**Then**:
- Label field reverts to "Original"
- No update sent to Python
- Input remains focused (or blurs, depending on implementation choice)

**Validation**:
```typescript
test('cancels edit on Escape key', async () => {
  const user = userEvent.setup();
  const mockUpdate = jest.fn();
  const block = { id: 'c1', type: 'gain', label: 'Original', ... };

  render(<ParameterPanel block={block} onUpdate={mockUpdate} ... />);
  const input = screen.getByLabelText(/Label/i);

  await user.clear(input);
  await user.type(input, 'Changed{Escape}');

  expect(mockUpdate).not.toHaveBeenCalled();
  expect(input).toHaveValue('Original'); // Reverted
});
```

**Manual Test**:
1. Click block, focus label field
2. Type "Changed" (do not press Enter)
3. Press Escape
4. Verify label field shows original value
5. Python: Verify label unchanged in Python object

---

### US3: Label Independence from Visibility Toggle (Priority: P2)

#### Scenario US3-1: Edit Hidden Label
**Given**: Block with label_visible=false
**When**: User edits label to "Hidden Controller" in Parameter panel
**Then**:
- Python: `block.label == 'Hidden Controller'`
- Canvas does NOT show label (label_visible still false)
- Parameter panel DOES show "Hidden Controller" in label field

**Validation**:
```python
def test_update_label_when_not_visible():
    diagram = Diagram()
    diagram.add_block('gain', 'controller', K=5.0)
    block = diagram._blocks['controller']

    # Hide label
    block.label_visible = False

    # Update label
    diagram.update_block_label('controller', 'Hidden Controller')

    assert block.label == 'Hidden Controller'
    assert block.label_visible == False  # Unchanged
```

**Manual Test**:
1. Create block, ensure label_visible=false (default)
2. Click block, verify canvas has no label displayed
3. In Parameter panel, type "Hidden Controller" and press Enter
4. Python: Verify `block.label == 'Hidden Controller'`
5. Verify canvas still shows no label (visibility unchanged)

---

#### Scenario US3-2: Show Label After Editing While Hidden
**Given**: Block with label_visible=false and recently edited label "Hidden Controller"
**When**: User right-clicks block and selects "Show label"
**Then**:
- Canvas displays "Hidden Controller" (not original default ID)
- Proves label was persisted even while hidden

**Manual Test**:
1. Following US3-1, with label="Hidden Controller" and label_visible=false
2. Right-click block on canvas
3. Select "Show label" from context menu
4. Verify canvas label shows "Hidden Controller" (the edited value)

---

#### Scenario US3-3: Edit Visible Label
**Given**: Block with label_visible=true and label "Visible Controller"
**When**: User edits label to "Updated Controller" in Parameter panel
**Then**:
- Canvas label updates immediately to "Updated Controller"
- Python: `block.label == 'Updated Controller'`

**Validation**: (Integration test - requires full widget)
```typescript
test('canvas label updates when visible', async () => {
  // Mock traitlet sync round-trip
  const block = {
    id: 'c1',
    type: 'gain',
    label: 'Visible Controller',
    label_visible: true
  };

  // Render canvas + Parameter panel
  // ... simulate label edit ...
  // ... wait for state update ...

  // Verify canvas EditableLabel shows new value
  expect(screen.getByText('Updated Controller')).toBeInTheDocument();
});
```

**Manual Test**:
1. Create block with label_visible=true
2. Verify canvas shows label
3. Edit label in Parameter panel to "Updated Controller"
4. Verify canvas label changes to "Updated Controller" within 100ms

---

#### Scenario US3-4: Hide Label After Editing
**Given**: Block with label_visible=true and label "My Label"
**When**: User right-clicks and selects "Hide label"
**Then**:
- Canvas label disappears
- Parameter panel STILL shows "My Label" in label field (remains editable)

**Manual Test**:
1. Create block with label_visible=true, label="My Label"
2. Right-click, select "Hide label"
3. Verify canvas label disappears
4. Click block, verify Parameter panel label field shows "My Label"
5. Verify label field is still editable (type to confirm)

---

## Edge Case Scenarios

### Edge Case 1: Duplicate Labels
**Given**: Two blocks with labels "Controller"
**When**: User creates or edits labels so both have same text
**Then**:
- System allows duplicate labels
- Blocks remain uniquely identified by ID
- No error messages

**Manual Test**:
```python
diagram.add_block('gain', 'controller1', K=5.0)
diagram.add_block('gain', 'controller2', K=10.0)
diagram.update_block_label('controller1', 'Controller')
diagram.update_block_label('controller2', 'Controller')

# Both blocks can have same label
assert diagram._blocks['controller1'].label == 'Controller'
assert diagram._blocks['controller2'].label == 'Controller'
```

---

### Edge Case 2: Long Label with Horizontal Scroll
**Given**: Block selected with Parameter panel open
**When**: User types a very long label (100+ characters)
**Then**:
- Label field shows horizontal scrollbar or scrolls text
- No layout overflow or panel width increase

**Manual Test**:
1. Type 100-character label: `"A" * 100`
2. Verify label input scrolls horizontally
3. Verify Parameter panel width unchanged

---

### Edge Case 3: Special Characters (Unicode, Tabs, Newlines)
**Given**: Block selected
**When**: User pastes text with newlines/tabs/Unicode
**Then**:
- Newlines converted to spaces
- Tabs converted to spaces
- Unicode characters accepted
- Control characters stripped

**Validation**:
```typescript
test('normalizes newlines and tabs', async () => {
  const mockUpdate = jest.fn();
  const block = { id: 'c1', type: 'gain', label: 'c1', ... };

  render(<ParameterPanel block={block} onUpdate={mockUpdate} ... />);
  const input = screen.getByLabelText(/Label/i);

  // Simulate paste with special chars
  await user.clear(input);
  await user.type(input, 'Line1\nLine2\tTabbed{Enter}');

  // Verify normalization: newline→space, tab→space
  expect(mockUpdate).toHaveBeenCalledWith('c1', 'label', 'Line1 Line2 Tabbed');
});
```

**Manual Test**:
1. Paste multi-line text into label field:
   ```
   Line 1
   Line 2	Tabbed
   ```
2. Press Enter
3. Verify label saved as "Line 1 Line 2 Tabbed" (single line, spaces)

---

### Edge Case 4: Panel Closure Mid-Edit
**Given**: User typing in label field
**When**: Parameter panel closed (click close button) without pressing Enter/blur
**Then**:
- Uncommitted edit lost
- Block label unchanged in Python

**Manual Test**:
1. Click block, focus label field
2. Type "New Label" (do not press Enter)
3. Click X button to close panel
4. Python: Verify `block.label` unchanged (original value)

---

### Edge Case 5: Concurrent Label Edits
**Given**: Label editing in progress via Parameter panel
**When**: Python API updates same block's label concurrently
**Then**:
- Last write wins
- UI reflects final Python state after both updates

**Manual Test** (requires two cells):
```python
# Cell 1: Start editing "Controller" in Parameter panel (do not commit yet)

# Cell 2: Run Python update
diagram.update_block_label('controller', 'Python Updated')

# Cell 1: Now press Enter in Parameter panel with "UI Updated"
# Result: "UI Updated" wins (last write)
```

---

## Performance Validation Scenarios

### Performance Test 1: Persistence Latency (SC-001)
**Target**: <50ms from Enter press to Python object update

**Test**:
```typescript
test('persists label within 50ms', async () => {
  const start = performance.now();
  const mockUpdate = jest.fn(() => {
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(50);
  });

  // ... render and trigger label update ...
  // mockUpdate called → check latency
});
```

---

### Performance Test 2: Canvas Update Latency (SC-002)
**Target**: <100ms from Enter press to canvas label update (when visible)

**Test**: (Requires full widget integration test)
```python
import time

def test_canvas_update_latency():
    # Measure time from Python update to traitlet sync completion
    start = time.perf_counter()
    diagram.update_block_label('controller', 'Updated')
    # ... wait for _update_diagram_state() to complete ...
    elapsed = time.perf_counter() - start
    assert elapsed < 0.1  # 100ms
```

---

### Performance Test 3: No Layout Shift (SC-005)
**Target**: Parameter panel height unchanged after adding label editor

**Test**:
```typescript
test('no vertical height increase', () => {
  const block = { id: 'c1', type: 'gain', label: 'c1', ... };
  const { container } = render(<ParameterPanel block={block} ... />);

  const panelHeight = container.firstChild.clientHeight;

  // Compare to previous version without label editor (baseline)
  // Or verify height < max threshold (e.g., 280px from max-h-[280px] class)
  expect(panelHeight).toBeLessThanOrEqual(280);
});
```

---

## Automated Test Execution

### Run Frontend Tests
```bash
cd js/
npm test -- --run LabelEditor.test.tsx
npm test -- --run ParameterPanel.test.tsx
```

### Run Backend Tests
```bash
pytest tests/test_diagram.py::test_update_block_label_empty_reverts_to_id
pytest tests/test_diagram.py::test_update_block_label_whitespace_only_reverts_to_id
```

### Run Integration Tests
```bash
# Full widget tests (if available)
pytest tests/test_widget.py::test_update_block_label_action
```

---

## Summary

This quickstart provides:
- **13 acceptance scenarios** covering all 3 user stories
- **5 edge case scenarios** for boundary condition testing
- **3 performance validation scenarios** for success criteria
- **Code snippets** for both manual and automated testing
- **Expected outcomes** for each scenario with Python verification commands

All scenarios directly map to functional requirements (FR-001 through FR-011) and success criteria (SC-001 through SC-005) from the feature specification.
