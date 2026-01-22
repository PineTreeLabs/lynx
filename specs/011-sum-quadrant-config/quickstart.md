<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Sum Block Quadrant Configuration

**Feature**: Interactive Sign Configuration for Sum Blocks
**Status**: Implementation Ready

## Overview

Configure Sum block port signs by clicking directly on the block's quadrants. No more text string editing—just click to cycle through "+", "-", and "|" (no port).

## User Interactions

### Basic Usage

**Configure a Sum Block Port:**
1. Hover over a Sum block quadrant (top, left, or bottom)
2. Cursor changes to pointer, quadrant highlights subtly
3. Click the quadrant once
4. Port sign cycles: `"+"` → `"-"` → `"|"` → `"+"`

**Visual Feedback:**
- **Hover**: Quadrant highlights with subtle blue overlay (optional feature)
- **Click**: Sign symbol updates immediately (<100ms)
- **No Port**: When cycled to "|", port marker disappears and connections are removed

### Quadrant Mapping

```
        [TOP]
         +
         |
  [LEFT] + - [RIGHT]
         |    (output - not clickable)
         +
      [BOTTOM]
```

- **Top Quadrant**: Top port (signs[0])
- **Left Quadrant**: Left port (signs[1])
- **Bottom Quadrant**: Bottom port (signs[2])
- **Right Quadrant**: Output port (NOT configurable, clicks ignored)

### Sign States

| Symbol | Meaning | Port State |
|--------|---------|------------|
| `+` | Addition | Port visible with marker |
| `-` | Subtraction | Port visible with marker |
| `|` | No connection | Port hidden, no marker |

### Resized Sum Blocks

Feature works with any Sum block dimensions:
- **Square** (56x56): Standard circular shape
- **Wide** (80x40): Horizontal ellipse
- **Tall** (40x80): Vertical ellipse

Click detection scales correctly with block shape—always click inside the visible oval boundary.

## Edge Cases

### Accidental Clicks During Drag

If you accidentally click while dragging the Sum block:
- Click is ignored if mouse moved >5px from initial position
- Sign does NOT change during drag operations
- Use Undo (Ctrl+Z) if accidental change occurs

### Clicking Between Quadrants

If you click exactly on the boundary between two quadrants (e.g., 45° diagonal):
- System assigns click to nearest cardinal direction (top/left/bottom)
- Consistent rules apply: top-left boundary → top quadrant

### Removing Connected Ports

When you cycle a port to "|" (no connection):
- Existing connections to that port are automatically removed
- Port marker disappears
- Consistent with existing behavior when editing signs parameter manually

## Known Limitations

### No Keyboard Navigation (MVP)

**Current Version**: Mouse-only interaction
**Future**: Keyboard navigation (Tab + Arrow keys + Enter) planned for accessibility-focused iteration

**Workaround**: Use mouse or touchpad to configure Sum blocks in this version.

### No Properties Panel for Sum Blocks

**Removed**: Properties panel no longer accessible for Sum blocks
**Configuration**: All sign configuration via direct quadrant clicks only

**Migration**: Existing diagrams continue to work—signs parameter already exists in JSON format.

## Testing Scenarios

### Scenario 1: Basic Sign Cycling
1. Create new Sum block (default signs: `["+", "+", "|"]`)
2. Click top quadrant → sign changes to `"-"`
3. Click top quadrant again → sign changes to `"|"` (port disappears)
4. Click top quadrant again → sign changes to `"+"` (port reappears)

### Scenario 2: Multiple Port Configuration
1. Create Sum block with all three ports active (`["+", "+", "+"]`)
2. Click left quadrant → left port changes to `"-"`
3. Click bottom quadrant → bottom port changes to `"-"`
4. Result: Top adds, left subtracts, bottom subtracts

### Scenario 3: Removing a Port with Connection
1. Create Sum block with top port connected to another block
2. Click top quadrant twice to cycle to `"|"` (no port)
3. Connection is automatically removed
4. Port marker disappears

### Scenario 4: Resized Sum Block
1. Resize Sum block to 80x40 (wide ellipse)
2. Hover over top quadrant edge → verify highlight appears
3. Click near edge of top quadrant → verify sign cycles correctly
4. No clicks register outside oval boundary

## Performance Expectations

| Metric | Target | Typical |
|--------|--------|---------|
| Click to visual update | <100ms | <50ms |
| Hover highlight delay | <16ms (60fps) | <5ms |
| Quadrant detection | <10ms | <1ms |

## Troubleshooting

### Issue: Click doesn't register
**Possible Causes**:
- Clicked outside oval boundary (rectangular block bounds, but outside circle/ellipse)
- Clicked on right quadrant (output port not configurable)

**Solution**: Click inside the visible oval shape on top, left, or bottom quadrants only.

### Issue: Sign changed while dragging block
**Possible Causes**:
- Very small mouse movement during drag (<5px threshold)

**Solution**: Use Undo (Ctrl+Z) to revert accidental change. Future versions may increase threshold.

### Issue: Can't find properties panel for Sum block
**Expected Behavior**: Properties panel removed for Sum blocks in this version

**Solution**: Use direct quadrant clicks to configure all Sum block settings. Other block types retain properties panel.

## Development Notes

### For Implementers

**Frontend Changes**:
- New utilities: `ellipseQuadrantDetection.ts`, `ellipseQuadrantPaths.ts`
- Modified: `SumBlock.tsx` (added hover state, click handlers, overlay paths)
- Tests: `ellipseQuadrantDetection.test.ts`, `ellipseQuadrantPaths.test.ts`

**Backend Changes**:
- Verify: `diagram.py::update_block_parameter()` handles signs array (existing)
- Verify: `sum.py` port regeneration on signs change (existing)

**Test Coverage**:
- Unit tests for quadrant detection algorithm
- Unit tests for SVG path generation
- Integration tests for sign cycling
- Performance tests for <100ms latency

### For Reviewers

**Key Files to Review**:
1. `/js/src/utils/ellipseQuadrantDetection.ts` - Core algorithm
2. `/js/src/blocks/SumBlock.tsx` - UI implementation
3. `/js/src/test/ellipseQuadrantDetection.test.ts` - Test coverage

**Review Checklist**:
- [ ] Tests written FIRST (TDD compliance)
- [ ] Quadrant detection works for deformed ellipses
- [ ] Click detection prevents accidental edits during drag
- [ ] Hover highlighting performs at 60fps
- [ ] Sign cycling follows correct sequence: `"+"` → `"-"` → `"|"` → `"+"`
- [ ] Properties panel removed for Sum blocks

## See Also

- [Specification](./spec.md) - Full feature requirements
- [Implementation Plan](./plan.md) - Technical design
- [Research](./research.md) - Technical decisions and alternatives
- [Tasks](./tasks.md) - Actionable implementation tasks (generated by `/speckit.tasks`)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-14
**Status**: Ready for Implementation
