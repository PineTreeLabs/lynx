<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Design: Simulink-Style Editable Orthogonal Routing

**Feature**: 001-lynx-jupyter-widget
**Date**: 2025-12-31
**Status**: Design Phase (Post-Phase 8)
**Priority**: Nice-to-have enhancement

## Overview

Enable users to customize connection routing by dragging segments to create/move waypoints, while maintaining orthogonal (90-degree) routing like Simulink.

## Current State (Phase 7)

- React Flow's `smoothstep` edge type provides automatic orthogonal routing
- Users cannot customize routing - all connections auto-routed
- Works well for simple diagrams but can create overlapping connections in complex layouts

## Goal

Allow users to manually adjust connection paths while maintaining professional orthogonal routing, matching Simulink's interaction model.

## Design Principles

1. **Orthogonal routing only** - No diagonal lines, all segments horizontal or vertical
2. **Automatic by default** - New connections use smart auto-routing
3. **Manual override** - Users can drag segments to customize routing
4. **Intuitive constraints** - Horizontal segments only move vertically, vertical only horizontally
5. **Persistent** - Custom routing saved/loaded with diagram

## User Interaction Model

### Creating Connections (No change from current)

1. User drags from output port to input port
2. System creates connection with automatic orthogonal routing
3. **Default routing strategy:**
   - Simple L-shape for straight horizontal/vertical connections
   - S-shape for connections requiring direction changes
   - Z-shape for feedback loops
   - Minimize segment count while avoiding block overlaps

### Editing Routing (New functionality)

**Selection:**
- Click on connection line to select it
- Selected connection highlights (thicker line, different color)
- Shows draggable segment handles

**Dragging segments:**
- Hover over segment → cursor changes to perpendicular arrows (↕ for horizontal, ↔ for vertical)
- Click and drag segment perpendicular to its orientation
- Dragging automatically creates waypoints at segment endpoints
- Real-time preview of new path during drag

**Waypoint management:**
- Waypoints are implicit (defined by segment positions)
- Waypoints automatically created when segment is dragged
- Adjacent waypoints automatically merge if segments align
- Waypoints stored as (x, y) coordinates in edge data

### Visual Feedback

**Default state (not selected):**
- Normal connection line with arrow
- No visible waypoints

**Hovered:**
- Slight highlight
- Cursor changes to indicate drag direction

**Selected:**
- Thicker line with accent color
- Small circular handles at waypoints (optional - could be implicit)
- Segment hover zones visible

**Dragging:**
- Preview of new path in accent color
- Original path shown dimmed
- Snap guides for alignment with blocks/grid (optional)

## Technical Implementation

### Data Model

```typescript
interface Connection {
  id: string;
  source_block_id: string;
  source_port_id: string;
  target_block_id: string;
  target_port_id: string;
  waypoints?: Array<{ x: number; y: number }>; // NEW: Custom routing
}
```

**Waypoint coordinate system:**
- Absolute canvas coordinates
- Waypoints are intermediate points between source and target ports
- Path = [source port] → waypoint₁ → waypoint₂ → ... → [target port]

### Routing Algorithm

**Path calculation:**
1. Start at source port position
2. For each waypoint:
   - Calculate orthogonal path from current position to waypoint
   - Use alternating H-V or V-H segments
3. End at target port position

**Segment generation:**
```typescript
function calculateOrthogonalPath(
  start: Point,
  end: Point,
  waypoints: Point[]
): Segment[] {
  const segments: Segment[] = [];
  let current = start;

  for (const waypoint of waypoints) {
    segments.push(...createOrthogonalSegments(current, waypoint));
    current = waypoint;
  }

  segments.push(...createOrthogonalSegments(current, end));
  return segments;
}

function createOrthogonalSegments(from: Point, to: Point): Segment[] {
  // Simple 2-segment approach: H then V, or V then H
  // Choose based on which direction has larger delta
  const dx = Math.abs(to.x - from.x);
  const dy = Math.abs(to.y - from.y);

  if (dx > dy) {
    // Horizontal first
    const mid = { x: to.x, y: from.y };
    return [
      { from, to: mid, orientation: 'horizontal' },
      { from: mid, to, orientation: 'vertical' }
    ];
  } else {
    // Vertical first
    const mid = { x: from.x, y: to.y };
    return [
      { from, to: mid, orientation: 'vertical' },
      { from: mid, to, orientation: 'horizontal' }
    ];
  }
}
```

### Drag Handling

**Segment drag constraints:**
```typescript
function handleSegmentDrag(
  segment: Segment,
  dragDelta: { x: number, y: number }
): void {
  if (segment.orientation === 'horizontal') {
    // Can only move vertically
    const newY = segment.from.y + dragDelta.y;
    updateWaypoint(segment, { y: newY });
  } else {
    // Can only move horizontally
    const newX = segment.from.x + dragDelta.x;
    updateWaypoint(segment, { x: newX });
  }
}
```

**Waypoint creation:**
- When dragging segment, create waypoints at segment endpoints if they don't exist
- Store in edge data
- Sync to Python backend

### React Flow Integration

**Custom edge component:**
```typescript
// js/src/connections/OrthogonalEditableEdge.tsx
function OrthogonalEditableEdge({
  id,
  source,
  target,
  sourceX,
  sourceY,
  targetX,
  targetY,
  data, // Contains waypoints
  selected,
}: EdgeProps) {
  const waypoints = data?.waypoints || [];
  const segments = calculateOrthogonalPath(
    { x: sourceX, y: sourceY },
    { x: targetX, y: targetY },
    waypoints
  );

  return (
    <g>
      {/* Render path */}
      <path d={segmentsToSVGPath(segments)} />

      {/* Render draggable segment handles if selected */}
      {selected && segments.map((segment, i) => (
        <SegmentHandle
          key={i}
          segment={segment}
          onDrag={(delta) => handleSegmentDrag(segment, delta)}
        />
      ))}
    </g>
  );
}
```

### Python Backend Changes

**Diagram model:**
```python
# lynx/diagram.py
class Connection:
    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: List[Dict[str, float]] = []  # NEW: [{"x": 100, "y": 200}, ...]
```

**Action handler:**
```python
# lynx/widget.py
def _handle_update_connection_routing(self, payload: Dict[str, Any]) -> None:
    """Handle connection routing update from frontend."""
    connection_id = payload.get("connectionId", "")
    waypoints = payload.get("waypoints", [])

    if self.diagram.update_connection_waypoints(connection_id, waypoints):
        self._save_state()  # For undo/redo
        self._update_diagram_state()
```

**Persistence:**
```json
{
  "connections": [
    {
      "id": "conn_1",
      "source_block_id": "block_1",
      "source_port_id": "out",
      "target_block_id": "block_2",
      "target_port_id": "in",
      "waypoints": [
        {"x": 250, "y": 150},
        {"x": 350, "y": 150}
      ]
    }
  ]
}
```

## Open Questions & Design Decisions

### Q1: Waypoint visibility
**Options:**
- A) Always show waypoint handles when connection selected
- B) Only show on segment hover
- C) Never show explicit handles, just allow segment dragging

**Recommendation:** Option A (always show when selected) - clearest UX

### Q2: Waypoint deletion
**Options:**
- A) Double-click waypoint to delete
- B) Right-click menu with "Delete Waypoint"
- C) Drag waypoint to align with adjacent waypoints (auto-merge)
- D) Button in selected connection toolbar to "Reset to Auto"

**Recommendation:** Combination of C (auto-merge) and D (reset button)

### Q3: Auto-routing algorithm
**Options:**
- A) Simple 2-segment (H-V or V-H)
- B) Smart multi-segment avoiding block overlaps
- C) A* pathfinding with obstacle avoidance

**Recommendation:** Start with A, optionally upgrade to B later

### Q4: Grid snapping
**Options:**
- A) Waypoints always snap to grid (20px)
- B) Waypoints free-form (no snapping)
- C) Configurable via settings

**Recommendation:** Option A (snap to grid) - maintains clean diagrams

### Q5: Simultaneous multi-connection routing
**Scenario:** Multiple connections between same two blocks
**Options:**
- A) Each connection routes independently (may overlap)
- B) Automatically offset parallel connections
- C) User manually routes each

**Recommendation:** Start with A, optionally add B later

## Implementation Phases

### Phase 1: Foundation (2-3 tasks)
- [T146] Design and implement orthogonal path calculation algorithm
- [T147] Create custom OrthogonalEditableEdge component with rendering
- [T148] Add waypoints field to Connection model (Python + TypeScript)

### Phase 2: Basic Editing (3-4 tasks)
- [T149] Implement segment selection and hover detection
- [T150] Implement segment dragging with orthogonal constraints
- [T151] Implement waypoint creation/update on drag
- [T152] Add updateConnectionRouting action handler in Python

### Phase 3: Polish & UX (2-3 tasks)
- [T153] Add visual feedback (hover, selection, drag preview)
- [T154] Implement waypoint auto-merge when segments align
- [T155] Add "Reset to Auto" button for selected connections
- [T156] Add grid snapping for waypoints

### Phase 4: Testing & Refinement (2-3 tasks)
- [T157] Write tests for path calculation algorithm
- [T158] Write tests for drag constraints
- [T159] Test persistence (save/load with custom routing)
- [T160] User testing and iteration

**Total estimated tasks:** 10-13 tasks
**Estimated complexity:** Medium-High (requires custom React Flow edge implementation)

## Success Criteria

1. ✅ Users can drag connection segments perpendicular to their orientation
2. ✅ All connections maintain orthogonal (90-degree) routing
3. ✅ Custom routing persists across save/load
4. ✅ Routing supports undo/redo
5. ✅ Visual feedback clearly indicates editable segments
6. ✅ Performance remains smooth with 50+ connections
7. ✅ Routing feels natural and intuitive (matches Simulink UX)

## Non-Goals (Explicitly Out of Scope)

- **Diagonal routing** - Not needed for control diagrams
- **Automatic overlap avoidance** - Users manually route to avoid overlaps
- **Connection bundling** - Multiple connections route independently
- **Bezier curves** - Orthogonal only for professional appearance

## References

- Simulink connection routing behavior
- React Flow custom edge documentation: https://reactflow.dev/examples/edges/custom-edge
- React Flow edge updater example: https://reactflow.dev/examples/edges/edge-with-button

## Next Steps

1. Review this design with stakeholders
2. Prioritize against other post-Phase 8 features
3. Create detailed task breakdown in tasks.md
4. Allocate to future sprint/milestone
