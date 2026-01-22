<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Editable Orthogonal Routing

**Feature**: 004-editable-orthogonal-routing
**Date**: 2026-01-06

## Overview

This document captures technical research and design decisions for implementing editable orthogonal connection routing in Lynx.

---

## Decision 1: Custom Edge Component Architecture

**Decision**: Create a new `OrthogonalEditableEdge` component using React Flow's `BaseEdge` with custom path calculation.

**Rationale**:
- React Flow's built-in `smoothstep` edge doesn't support waypoints or segment dragging
- The existing `EditableEdge.tsx` in Lynx provides a starting point but only has a single control point
- `BaseEdge` handles the invisible interaction layer and markers automatically
- Custom path calculation allows full control over orthogonal segment generation

**Alternatives Considered**:
1. **Modify smoothstep path**: Rejected - smoothstep uses internal algorithms we can't intercept
2. **Use React Flow Pro editable edge**: Rejected - requires paid subscription, adds dependency
3. **Third-party routing library**: Rejected - adds complexity, may not integrate well

**Implementation Pattern**:
```typescript
// OrthogonalEditableEdge.tsx
function OrthogonalEditableEdge({
  id, sourceX, sourceY, targetX, targetY, data, selected, ...props
}: EdgeProps<EdgeData>) {
  const waypoints = data?.waypoints || [];
  const segments = calculateOrthogonalPath(
    { x: sourceX, y: sourceY },
    { x: targetX, y: targetY },
    waypoints
  );
  const pathString = segmentsToSVGPath(segments);

  return (
    <>
      <BaseEdge path={pathString} markerEnd={props.markerEnd} />
      {selected && <SegmentHandles segments={segments} onDrag={...} />}
    </>
  );
}
```

---

## Decision 2: Path Calculation Algorithm

**Decision**: Use a simple 2-segment (H-V or V-H) approach for routing between points.

**Rationale**:
- Matches the design document recommendation for Phase 1
- Simple algorithm is easier to test and debug
- Can be upgraded to smarter routing later if needed
- Users have manual control via waypoints, reducing need for automatic avoidance

**Algorithm**:
```typescript
function createOrthogonalSegments(from: Point, to: Point): Segment[] {
  const dx = Math.abs(to.x - from.x);
  const dy = Math.abs(to.y - from.y);

  if (dx > dy) {
    // Horizontal first, then vertical
    const mid = { x: to.x, y: from.y };
    return [
      { from, to: mid, orientation: 'horizontal' },
      { from: mid, to, orientation: 'vertical' }
    ];
  } else {
    // Vertical first, then horizontal
    const mid = { x: from.x, y: to.y };
    return [
      { from, to: mid, orientation: 'vertical' },
      { from: mid, to, orientation: 'horizontal' }
    ];
  }
}
```

**Alternatives Considered**:
1. **A* pathfinding with obstacle avoidance**: Rejected for MVP - adds significant complexity
2. **Always H-then-V routing**: Rejected - sometimes produces unnecessarily long paths

---

## Decision 3: Segment Interaction Handling

**Decision**: Use overlay `<rect>` elements positioned over each segment for hit detection and drag handling.

**Rationale**:
- SVG paths are difficult to hit-test at specific segment locations
- Overlay rectangles provide reliable mouse event handling
- Can apply cursor styles directly to rectangles
- Works well with React's event system

**Implementation Pattern**:
```typescript
function SegmentHandle({ segment, onDrag }: SegmentHandleProps) {
  const isHorizontal = segment.orientation === 'horizontal';
  const cursor = isHorizontal ? 'ns-resize' : 'ew-resize';

  // Calculate rect bounds from segment
  const rect = segmentToRect(segment, HANDLE_WIDTH);

  return (
    <rect
      x={rect.x}
      y={rect.y}
      width={rect.width}
      height={rect.height}
      fill="transparent"
      cursor={cursor}
      onMouseDown={handleDragStart}
    />
  );
}
```

**Alternatives Considered**:
1. **Path element with pointer-events**: Rejected - hard to identify which segment was clicked
2. **EdgeLabelRenderer for handles**: Considered for visual handles, but rect overlay better for segments

---

## Decision 4: State Management for Waypoints

**Decision**: Store waypoints in edge data, sync to Python via action messages (same pattern as other diagram changes).

**Rationale**:
- Follows existing Lynx architecture for state synchronization
- Python backend remains the source of truth
- Undo/redo works through existing infrastructure
- Persistence handled by existing save/load code

**Data Flow**:
```
1. User drags segment → local React state update (immediate feedback)
2. Drag ends → sendAction(model, 'updateConnectionRouting', { connectionId, waypoints })
3. Python handler → diagram.update_connection_waypoints()
4. Python saves state → undo stack
5. Python syncs → React Flow updates from traitlet change
```

**Alternatives Considered**:
1. **React-only state with periodic sync**: Rejected - loses undo/redo consistency
2. **Direct traitlet mutation**: Rejected - doesn't integrate with undo system

---

## Decision 5: Waypoint Coordinate System

**Decision**: Store waypoints as absolute canvas coordinates.

**Rationale**:
- Matches React Flow's coordinate system
- Simpler than relative coordinates (no reference point calculations)
- When blocks move, waypoints stay in place (desired Simulink-like behavior)
- Design document specifies this approach

**Data Model**:
```typescript
interface Waypoint {
  x: number;  // Absolute canvas X coordinate
  y: number;  // Absolute canvas Y coordinate
}

interface EdgeData {
  waypoints?: Waypoint[];
}
```

**Alternatives Considered**:
1. **Relative to source/target**: Rejected - waypoints should stay fixed when blocks move
2. **Percentages along path**: Rejected - doesn't work well for arbitrary orthogonal paths

---

## Decision 6: Grid Snapping for Waypoints

**Decision**: Snap waypoints to the existing 20px grid (same as block snapping).

**Rationale**:
- Maintains visual consistency with block positions
- Grid is already implemented and tested in DiagramCanvas (GRID_SIZE = 20)
- Matches design document recommendation
- Prevents messy, misaligned routing

**Implementation**:
```typescript
// Reuse existing snapToGrid function
function snapToGrid(position: { x: number; y: number }, gridSize = 20) {
  return {
    x: Math.round(position.x / gridSize) * gridSize,
    y: Math.round(position.y / gridSize) * gridSize,
  };
}
```

---

## Decision 7: Visual Feedback Approach

**Decision**: Use CSS-based visual states with Tailwind variables for consistency.

**States**:
| State | Visual Treatment |
|-------|------------------|
| Default | 2px stroke, primary-600 color |
| Hover (segment) | Cursor changes to ns-resize/ew-resize |
| Selected | 3px stroke, primary-500 color, optional waypoint handles |
| Dragging | Ghost preview in primary-400, original dimmed |

**Rationale**:
- Matches existing Lynx design system (colors.md)
- CSS cursor changes are performant and native
- No additional dependencies needed

---

## Decision 8: Waypoint Auto-Merge

**Decision**: Automatically merge adjacent waypoints when segments align (within grid tolerance).

**Rationale**:
- Prevents accumulation of redundant waypoints
- Simplifies paths when user drags segment back
- Design document specifies this behavior

**Algorithm**:
```typescript
function simplifyWaypoints(waypoints: Waypoint[], tolerance = 5): Waypoint[] {
  if (waypoints.length < 2) return waypoints;

  return waypoints.filter((wp, i, arr) => {
    if (i === 0 || i === arr.length - 1) return true;
    const prev = arr[i - 1];
    const next = arr[i + 1];

    // Remove if this waypoint is collinear with prev and next
    const collinearH = Math.abs(prev.y - wp.y) < tolerance && Math.abs(wp.y - next.y) < tolerance;
    const collinearV = Math.abs(prev.x - wp.x) < tolerance && Math.abs(wp.x - next.x) < tolerance;

    return !(collinearH || collinearV);
  });
}
```

---

## Decision 9: Reset to Auto Routing

**Decision**: Implement reset via context menu item or keyboard shortcut that clears waypoints array.

**Rationale**:
- Design document recommends "Reset to Auto" button
- Clearing waypoints triggers default routing algorithm
- Simple implementation: `waypoints = []`

**UI Location**: Block context menu (existing `BlockContextMenu.tsx`) extended to edge context menu, or toolbar button when connection is selected.

---

## Technical Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Performance with many connections | Limit re-renders using React.memo; only update changed edges |
| Complex drag state management | Use useReducer for drag state; test edge cases thoroughly |
| Waypoint persistence edge cases | Unit tests for save/load with various waypoint configurations |
| React Flow version compatibility | Pin React Flow 11.11.4; document API usage |

---

## References

- [React Flow EdgeProps API](https://reactflow.dev/api-reference/types/edge-props)
- [React Flow BaseEdge Component](https://reactflow.dev/api-reference/components/base-edge)
- [React Flow useReactFlow Hook](https://reactflow.dev/api-reference/hooks/use-react-flow)
- [Design Document](../001-lynx-jupyter-widget/design-editable-routing.md)
