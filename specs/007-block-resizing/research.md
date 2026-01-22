<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Block Resizing

**Feature**: 007-block-resizing
**Date**: 2026-01-12
**Status**: Complete

## Research Topics

### R1: React Flow NodeResizer vs Custom Implementation

**Decision**: Use React Flow's built-in `NodeResizer` component

**Rationale**:
- React Flow 11.11.4 includes `NodeResizer` built-in (no additional packages needed)
- Handles event propagation automatically (prevents node drag during resize)
- Provides `minWidth`/`minHeight` constraints out of the box
- Can be styled via `handleStyle` prop to match Lynx design system
- Better maintained than custom implementation

**Alternatives Considered**:
1. ~~Custom resize handles with mouse event handlers~~ - More code, harder to maintain, event propagation issues
2. `@reactflow/node-resizer` package - Not needed; NodeResizer is built into v11.x

**Implementation**:
```typescript
import { NodeResizer } from 'reactflow';

// Inside custom node component
<NodeResizer
  minWidth={MIN_WIDTH}
  minHeight={MIN_HEIGHT}
  isVisible={selected}
  handleStyle={{
    width: 8,
    height: 8,
    backgroundColor: 'var(--color-primary-600)'
  }}
/>
```

### R2: Handle Position Updates After Resize

**Decision**: Use `useUpdateNodeInternals()` hook after resize completes

**Rationale**:
- React Flow caches handle positions for performance
- When node dimensions change, handle positions must be recalculated
- `useUpdateNodeInternals(nodeId)` forces React Flow to remeasure handles

**Implementation**:
```typescript
import { useUpdateNodeInternals } from 'reactflow';

const updateInternals = useUpdateNodeInternals();

const handleResizeEnd = (nodeId: string) => {
  updateInternals(nodeId); // Recalculate handle positions
};
```

### R3: Python Sync Strategy

**Decision**: Follow existing optimistic update pattern from position/label updates

**Rationale**:
- Consistent with existing architecture in `DiagramCanvas.tsx`
- Immediate UI feedback during resize
- Python state is source of truth for persistence

**Implementation Pattern**:
```typescript
// 1. Optimistic update in React state
setNodes((nodes) =>
  nodes.map((n) =>
    n.id === nodeId ? { ...n, data: { ...n.data, width, height } } : n
  )
);

// 2. Sync to Python via existing sendAction pattern
sendAction(model, 'update_block_dimensions', {
  block_id: nodeId,
  width,
  height,
});
```

### R4: Dimension Storage in Node Data

**Decision**: Store dimensions in `node.data.width` and `node.data.height`

**Rationale**:
- Matches existing pattern for block-specific data (`flipped`, `label_visible`, etc.)
- Cannot set `node.width`/`node.height` directly (React Flow internal properties)
- Block components read from `data` props already

**Important Notes**:
- React Flow measures nodes after render and stores in `node.measured.width/height`
- Our custom dimensions override the measured values via inline CSS
- Fallback to default dimensions when `data.width/height` is undefined

### R5: Shift+Drag Aspect Ratio Lock

**Decision**: Use `onResize` callback from NodeResizer with manual aspect ratio calculation

**Rationale**:
- NodeResizer doesn't have built-in aspect lock
- Can detect Shift key in resize callback and adjust dimensions
- Matches Figma/Sketch behavior

**Implementation**:
```typescript
const onResize = (event: MouseEvent, params: ResizeParams) => {
  if (event.shiftKey) {
    // Lock aspect ratio
    const aspectRatio = originalWidth / originalHeight;
    const newHeight = params.width / aspectRatio;
    return { width: params.width, height: newHeight };
  }
  return params;
};
```

### R6: Connection Re-routing on Resize

**Decision**: Reuse existing `_clear_waypoints_for_block()` mechanism

**Rationale**:
- Block resize changes port positions (same as block move)
- Existing auto-routing infrastructure handles cleared waypoints
- Already triggers on position updates via `update_block_position()`
- New `update_block_dimensions()` can call the same waypoint clearing

**Implementation** (Python):
```python
def update_block_dimensions(self, block_id: str, width: float, height: float) -> bool:
    block = self.get_block(block_id)
    if not block:
        return False

    self._save_state()  # For undo
    block.width = width
    block.height = height

    # Force connections to auto-route
    self._clear_waypoints_for_block(block_id)

    return True
```

### R7: Minimum Size Per Block Type

**Decision**: Define constants in Python block classes, pass to frontend

**Rationale**:
- Python is source of truth for block configuration
- Minimums depend on block content (triangle shape, fraction display, etc.)
- Enforced in both frontend (NodeResizer props) and backend (validation)

| Block Type | Min Width | Min Height | Default Width | Default Height |
|------------|-----------|------------|---------------|----------------|
| Gain | 60 | 40 | 120 | 80 |
| Sum | 40 | 40 | 56 | 56 |
| TransferFunction | 80 | 40 | 100 | 50 |
| StateSpace | 80 | 40 | 100 | 60 |
| IOMarker | 60 | 40 | 60 | 48 |

## Summary

All research questions resolved. Key findings:
1. Use React Flow's built-in `NodeResizer` component
2. Call `useUpdateNodeInternals()` after resize to update handle positions
3. Follow existing optimistic update pattern for Python sync
4. Store dimensions in `node.data.width/height`
5. Manual Shift detection for aspect ratio lock
6. Reuse waypoint clearing for connection auto-route
7. Define per-block-type minimums in Python
