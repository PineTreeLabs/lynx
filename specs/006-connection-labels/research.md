<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Connection Labels

**Feature**: 006-connection-labels
**Date**: 2026-01-12

## Overview

This feature extends the existing label system from blocks to connections. Research focused on:
1. Existing block label implementation patterns
2. React Flow edge label positioning
3. Smart positioning algorithm design

## Research Findings

### R1: Existing Block Label Pattern

**Decision**: Follow the exact same pattern as block labels (005-hideable-block-labels)

**Rationale**:
- Consistency with existing UX
- Proven implementation in production
- Minimal new code (reuse `EditableLabel` component)
- Same data model pattern (`label`, `label_visible` fields)

**Alternatives Considered**:
- Custom label implementation: Rejected - unnecessary complexity, already have working component
- Always-visible labels: Rejected - user explicitly requested hidden-by-default behavior

**Implementation Reference**:
- `js/src/components/EditableLabel.tsx` - Reusable double-click edit component
- `js/src/blocks/GainBlock.tsx:124-130` - Example of conditional label rendering
- `src/lynx/schema.py:44` - `label_visible: bool = False` pattern

### R2: React Flow EdgeLabelRenderer

**Decision**: Use `EdgeLabelRenderer` component for label positioning

**Rationale**:
- Already imported in `OrthogonalEditableEdge.tsx` (line 8)
- Renders labels in a separate layer (doesn't interfere with edge interaction)
- Provides absolute positioning within the flow viewport
- Standard React Flow pattern for edge labels

**Alternatives Considered**:
- SVG text element: Rejected - harder to make interactive, doesn't support React components
- Custom portal: Rejected - EdgeLabelRenderer already solves this problem

**Implementation Reference**:
- `js/src/connections/OrthogonalEditableEdge.tsx:68-92` - Existing EdgeLabelRenderer usage (control point)

### R3: Label Positioning Algorithm

**Decision**: Compute position client-side based on path segments

**Rationale**:
- Position depends on current connection geometry (source/target positions, waypoints)
- Geometry changes when blocks move - persisting position would be stale
- Simple algorithm: find horizontal center, adjust to avoid corners

**Algorithm**:
```typescript
function calculateConnectionLabelPosition(
  segments: Segment[],
  labelText: string,
  charWidth: number = 7  // text-xs font-mono
): { x: number; y: number } {
  // 1. Find bounding box of all segments
  const allPoints = segments.flatMap(s => [s.from, s.to]);
  const minX = Math.min(...allPoints.map(p => p.x));
  const maxX = Math.max(...allPoints.map(p => p.x));

  // 2. Calculate ideal center position
  const centerX = (minX + maxX) / 2;

  // 3. Find segment at centerX
  const segment = findSegmentAtX(segments, centerX);
  const centerY = segment ? (segment.from.y + segment.to.y) / 2 : allPoints[0].y;

  // 4. Calculate label bounds
  const labelWidth = labelText.length * charWidth;
  let labelLeft = centerX - labelWidth / 2;
  let labelRight = centerX + labelWidth / 2;

  // 5. Find nearest corner waypoints
  const corners = findCornerWaypoints(segments);

  // 6. Adjust position if overlapping corners
  for (const corner of corners) {
    if (labelLeft < corner.x && labelRight > corner.x) {
      // Label overlaps this corner - shift away
      const shiftLeft = corner.x - labelRight;
      const shiftRight = labelLeft - corner.x;
      // Use minimum shift
      if (Math.abs(shiftLeft) < Math.abs(shiftRight)) {
        labelLeft += shiftLeft - 5; // 5px padding
        labelRight += shiftLeft - 5;
      } else {
        labelLeft += shiftRight + 5;
        labelRight += shiftRight + 5;
      }
    }
  }

  return {
    x: labelLeft + labelWidth / 2,
    y: centerY - 10  // Position above the line
  };
}
```

**Alternatives Considered**:
- Persist position in data model: Rejected - would be stale when blocks move
- Center of longest segment: Rejected - spec says "horizontal center of connection"
- No corner avoidance: Rejected - spec explicitly requires smart positioning

### R4: Context Menu Extension

**Decision**: Extend existing `EdgeContextMenu` component

**Rationale**:
- Already has the right structure and styling
- Same pattern as `BlockContextMenu` (which has Show/Hide Label)
- Minimal change - just add new menu item

**Implementation Reference**:
- `js/src/components/EdgeContextMenu.tsx` - Current edge context menu
- `js/src/components/BlockContextMenu.tsx:86-98` - Show/Hide Label pattern

### R5: Data Synchronization

**Decision**: Follow existing traitletSync pattern for state synchronization

**Rationale**:
- Consistent with all other diagram state
- Undo/redo support via existing history mechanism
- Python as source of truth, React as view

**Actions Needed**:
| Action | Payload | Handler |
|--------|---------|---------|
| `toggleConnectionLabelVisibility` | `{ connectionId }` | `diagram.toggle_connection_label_visibility()` |
| `updateConnectionLabel` | `{ connectionId, label }` | `diagram.update_connection_label()` |

**Implementation Reference**:
- `src/lynx/widget.py:140-141` - Existing toggleLabelVisibility action
- `src/lynx/diagram.py:804-822` - Existing toggle_label_visibility method

## Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Label overlaps edge during editing | Low | Low | Position label above line with offset |
| Performance with many labels | Low | Medium | Labels are text-only; React optimizes rendering |
| Position calculation edge cases | Medium | Low | Unit tests for positioning algorithm |

## Dependencies

No external dependencies. All required infrastructure exists:
- EditableLabel component (reuse)
- EdgeLabelRenderer (React Flow built-in)
- Pydantic schema validation (existing)
- traitletSync action dispatch (existing)

## Conclusion

Research complete. All technical decisions follow existing patterns with minimal new code. The only new utility function needed is `calculateConnectionLabelPosition()` for smart label positioning.
