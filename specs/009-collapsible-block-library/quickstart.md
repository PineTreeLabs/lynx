<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Collapsible Block Library

**Feature**: 009-collapsible-block-library
**Date**: 2026-01-13

## Test Scenarios

### Scenario 1: Default Collapsed State

**Steps**:
1. Open any diagram in Jupyter notebook
2. Observe the upper left corner

**Expected**:
- A compact "Blocks" label is visible
- The label has the same styling as the expanded panel (white background, border, shadow)
- Block buttons are NOT visible
- The collapsed element is small and unobtrusive

### Scenario 2: Expand on Hover

**Steps**:
1. Move cursor over the "Blocks" label
2. Observe the panel

**Expected**:
- Panel smoothly expands downward
- All 6 block buttons become visible (Gain, Input, Output, Sum, TF, SS)
- Animation completes in under 200ms
- Expansion feels smooth, not jarring

### Scenario 3: Collapse on Mouse Leave

**Steps**:
1. Hover to expand the panel
2. Move cursor away from the panel (to the canvas)
3. Wait briefly

**Expected**:
- After ~200ms delay, panel collapses
- Animation is smooth
- Only the "Blocks" label remains visible

### Scenario 4: No Flickering on Quick Movement

**Steps**:
1. Rapidly move cursor in and out of the panel area
2. Move cursor back in before collapse completes

**Expected**:
- Panel does NOT flicker
- If cursor returns before collapse delay, panel stays expanded
- Smooth visual experience

### Scenario 5: Add Block While Expanded

**Steps**:
1. Hover to expand the panel
2. Click "Gain" button
3. Observe diagram

**Expected**:
- A new Gain block appears on the canvas
- Panel remains expanded (does not collapse during click)
- User can add multiple blocks without re-hovering

### Scenario 6: Move Between Buttons

**Steps**:
1. Hover to expand the panel
2. Move cursor between different buttons
3. Observe panel state

**Expected**:
- Panel stays expanded the entire time
- No collapse occurs while cursor is within panel bounds

## Development Verification

### Build & Test Commands

```bash
# Navigate to frontend directory
cd js

# Run tests (should all pass)
npm test

# Build for production
npm run build

# Start dev server for interactive testing
npm run dev
```

### Files to Inspect

1. **`js/src/palette/BlockPalette.tsx`** - Main component with collapse logic
2. **`js/src/palette/BlockPalette.test.tsx`** - Test file (to be created)

### Visual Checks

- [ ] Collapsed label matches expanded panel styling
- [ ] Animation is smooth (150-200ms)
- [ ] No layout shift during expand/collapse
- [ ] Z-index remains above canvas but below modals
- [ ] Works in both light canvas and over blocks
