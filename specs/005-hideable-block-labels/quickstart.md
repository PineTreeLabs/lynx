<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Hideable Block Labels

**Feature**: 005-hideable-block-labels
**Date**: 2026-01-12

## Test Scenarios

### Scenario 1: Show Label via Context Menu (P1)

**Steps**:
1. Create a new diagram with a Gain block
2. Observe that the block has no visible label (hidden by default)
3. Right-click on the block
4. Verify the context menu shows "Show Label" option
5. Click "Show Label"
6. Verify the label appears below the block

**Expected Result**: Label displays below the block showing the block ID (e.g., "gain_1")

### Scenario 2: Hide Label via Context Menu (P2)

**Steps**:
1. Continue from Scenario 1 (block has visible label)
2. Right-click on the block
3. Verify the context menu shows "Hide Label" option (not "Show Label")
4. Click "Hide Label"
5. Verify the label disappears

**Expected Result**: Label is no longer visible

### Scenario 3: Edit Visible Label (P3)

**Steps**:
1. Show a block's label via context menu
2. Double-click on the label
3. Verify an inline text editor appears with current text selected
4. Type a new name (e.g., "MyGain")
5. Press Enter
6. Verify the label updates to the new text

**Expected Result**: Label shows "MyGain"

### Scenario 4: Cancel Label Edit (P3)

**Steps**:
1. Show a block's label via context menu
2. Double-click on the label
3. Type some text
4. Press Escape
5. Verify the original label is restored

**Expected Result**: Label shows original text

### Scenario 5: Persistence (P4)

**Steps**:
1. Create a diagram with multiple blocks
2. Show labels on some blocks (not all)
3. Save the diagram to file
4. Close and reopen the diagram
5. Verify label visibility states are preserved

**Expected Result**: Same blocks have visible labels as before save

### Scenario 6: Undo/Redo

**Steps**:
1. Start with a block (label hidden)
2. Show the label via context menu
3. Press Ctrl+Z (undo)
4. Verify label is hidden again
5. Press Ctrl+Y (redo)
6. Verify label is visible again

**Expected Result**: Label visibility toggles with undo/redo

### Scenario 7: All Block Types

**Steps**:
1. Create one of each block type: Gain, Sum, TransferFunction, StateSpace, IOMarker
2. For each block:
   - Verify label is hidden by default
   - Right-click and show label
   - Verify label appears
   - Right-click and hide label
   - Verify label disappears

**Expected Result**: All 5 block types support label show/hide consistently

### Scenario 8: Copy/Paste with Visible Label

**Steps**:
1. Create a Gain block
2. Show its label via context menu
3. Copy the block (Ctrl+C)
4. Paste (Ctrl+V)
5. Verify the pasted block also has a visible label

**Expected Result**: Pasted block preserves `label_visible = true`

### Scenario 9: New Block Default

**Steps**:
1. Add a new block via keyboard shortcut (e.g., 'g' for Gain)
2. Verify the new block has no visible label

**Expected Result**: New blocks start with `label_visible = false`

## Manual Verification Checklist

- [ ] Labels hidden by default for all block types
- [ ] Context menu shows "Show Label" when hidden
- [ ] Context menu shows "Hide Label" when visible
- [ ] Label appears/disappears on toggle
- [ ] Double-click editing works on visible labels
- [ ] Escape cancels edit
- [ ] Enter saves edit
- [ ] Save/load preserves visibility
- [ ] Undo/redo works for toggle
- [ ] Copy/paste preserves visibility
- [ ] All 5 block types work consistently
