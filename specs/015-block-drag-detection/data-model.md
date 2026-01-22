<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Block Drag Detection

**Feature**: Block Drag Detection (015)
**Date**: 2026-01-18
**Purpose**: Define entities and state machines for drag detection implementation

## Overview

This feature operates entirely in the frontend (TypeScript/React) and does not introduce new persistent data structures. The data model describes transient state used during user interactions.

## Entities

### 1. DragStartPosition (Transient State)

**Description**: Tracks initial position when a drag operation begins, used to calculate movement distance when drag completes.

**Storage**: React `useRef` (non-rendering state)

**Structure**:
```typescript
type DragStartPosition = Record<string, { x: number; y: number }>;

// Example:
{
  "block_1": { x: 100, y: 150 },
  "block_2": { x: 250, y: 300 }
}
```

**Lifecycle**:
- **Created**: When `onNodeDragStart` fires for a block
- **Updated**: Never (immutable after creation)
- **Deleted**: When `onNodesChange` processes final position (dragging: false)

**Validation Rules**:
- Position values must be finite numbers
- Node ID must match existing block in diagram
- Only one position stored per node at a time

**Relationships**:
- **References**: Block ID (from React Flow node)
- **Used by**: Distance calculation in `onNodesChange` filter

---

### 2. NodePositionChange (React Flow Type)

**Description**: React Flow's built-in change event for node position updates. Used to intercept and filter position changes based on drag distance.

**Source**: `@xyflow/react` library (not defined by Lynx)

**Structure**:
```typescript
type NodePositionChange = {
  id: string;                    // Block ID
  type: "position";              // Change type discriminator
  position: XYPosition;          // New position { x, y }
  positionAbsolute: XYPosition;  // Absolute position (accounts for parent)
  dragging: boolean;             // true during drag, false when drag ends
};
```

**Key Field: `dragging`**:
- `true`: Position update during active drag (continuous updates while mouse moves)
- `false`: Final position update when drag completes (mouse released)

**Usage in Drag Detection**:
```typescript
onNodesChange((changes) => {
  changes.filter(change => {
    if (change.type === 'position' && !change.dragging) {
      // Drag just ended - check distance threshold
      const startPos = dragStartPos.current[change.id];
      const distance = calculateDistance(startPos, change.position);
      return distance >= 5; // true = apply change, false = filter out
    }
    return true; // Apply all other changes
  });
});
```

---

### 3. Node Selection State (React Flow Type)

**Description**: React Flow's built-in node property for selection state. Controls visibility of resize handles and selection highlight.

**Storage**: Part of React Flow's `nodes` array state

**Structure**:
```typescript
type Node = {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: any;
  selected: boolean;  // Selection state
  // ... other React Flow properties
};
```

**Selection Behavior**:
- **Exclusive Selection**: Only one block can be `selected: true` at a time
- **Selection Triggers**:
  - Drag ends with distance < 5px → `selected: true`
  - Drag ends with distance ≥ 5px → `selected: false`
  - Click empty canvas → all blocks `selected: false`

**Visual Effects of `selected: true`**:
- Resize handles visible (NodeResizer `isVisible={selected}`)
- Selection highlight border (React Flow styling)
- Parameter panel opens (if double-clicked while selected)

---

## State Machines

### Drag Detection State Machine

**Purpose**: Track drag interaction state from start to completion

**States**: (Implicit - derived from React Flow events)

```
IDLE (no drag in progress)
  ↓ onNodeDragStart fires
DRAGGING (mouse button down, node moving)
  ↓ onNodeDragStop fires
  ↓ onNodesChange fires with dragging: false
EVALUATING (checking distance threshold)
  ↓
  IF distance < 5px
    → SELECT (apply selection, filter position change)
  IF distance ≥ 5px
    → MOVE (apply position change, clear selection)
  ↓
IDLE (drag complete, state reset)
```

**State Transitions**:

| From State | Event | Condition | To State | Actions |
|-----------|-------|-----------|----------|---------|
| IDLE | onNodeDragStart | Always | DRAGGING | Store initial position in dragStartPos ref |
| DRAGGING | onNodesChange | dragging: true | DRAGGING | Allow position updates (live preview) |
| DRAGGING | onNodesChange | dragging: false | EVALUATING | Calculate distance from dragStartPos |
| EVALUATING | Distance check | distance < 5px | SELECT | Set node.selected = true, filter position change |
| EVALUATING | Distance check | distance ≥ 5px | MOVE | Set node.selected = false, apply position change |
| SELECT | Immediate | Always | IDLE | Delete dragStartPos[nodeId] |
| MOVE | Immediate | Always | IDLE | Delete dragStartPos[nodeId], send moveBlock to Python |

**Implementation Note**: This is a conceptual state machine. The actual implementation uses React Flow events and `dragging` boolean rather than explicit state enum.

---

## Data Flow Diagrams

### Click-to-Select Flow (distance < 5px)

```
User clicks block
  ↓
onNodeDragStart fires
  ↓
dragStartPos.current[nodeId] = { x: initialX, y: initialY }
  ↓
User moves mouse slightly (< 5px)
  ↓
onNodesChange fires (dragging: true) multiple times
  ↓
React Flow updates node position in UI (live preview)
  ↓
User releases mouse
  ↓
onNodesChange fires (dragging: false)
  ↓
Calculate: distance = sqrt((finalX - initialX)² + (finalY - initialY)²)
  ↓
distance < 5px → TRUE
  ↓
setNodes(nodes => nodes.map(n => ({ ...n, selected: n.id === nodeId })))
  ↓
Filter out position change (return false from filter)
  ↓
delete dragStartPos.current[nodeId]
  ↓
RESULT: Block selected, position unchanged
```

### Drag-to-Move Flow (distance ≥ 5px)

```
User clicks block
  ↓
onNodeDragStart fires
  ↓
dragStartPos.current[nodeId] = { x: initialX, y: initialY }
  ↓
User drags mouse (≥ 5px)
  ↓
onNodesChange fires (dragging: true) continuously
  ↓
React Flow updates node position in UI (live tracking)
  ↓
User releases mouse at final position
  ↓
onNodesChange fires (dragging: false)
  ↓
Calculate: distance = sqrt((finalX - initialX)² + (finalY - initialY)²)
  ↓
distance ≥ 5px → TRUE
  ↓
setNodes(nodes => nodes.map(n => n.id === nodeId ? { ...n, selected: false } : n))
  ↓
Allow position change (return true from filter)
  ↓
Apply collinear snapping (existing logic in onNodeDragStop)
  ↓
sendAction(model, "moveBlock", { blockId: nodeId, position: snappedPosition })
  ↓
delete dragStartPos.current[nodeId]
  ↓
RESULT: Block moved, not selected, position synced to Python
```

### Canvas Deselection Flow

```
User clicks empty canvas space
  ↓
onPaneClick fires
  ↓
setNodes(nodes => nodes.map(n => ({ ...n, selected: false })))
  ↓
setSelectedBlockId(null)
  ↓
setShowSettings(false)
  ↓
setContextMenu(null)
  ↓
RESULT: All blocks deselected, UI state cleared
```

---

## Distance Calculation

**Formula**: Euclidean distance between two points

```typescript
function calculateDistance(
  start: { x: number; y: number },
  end: { x: number; y: number }
): number {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  return Math.sqrt(dx * dx + dy * dy);
}
```

**Optimization**: Use squared distance to avoid `sqrt()` overhead

```typescript
function calculateDistanceSquared(
  start: { x: number; y: number },
  end: { x: number; y: number }
): number {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  return dx * dx + dy * dy;
}

// Usage: Compare to threshold²
const THRESHOLD_SQUARED = 25; // 5px * 5px
if (calculateDistanceSquared(start, end) < THRESHOLD_SQUARED) {
  // Movement < 5px
}
```

**Threshold**: 5 pixels (screen pixels, not canvas coordinates)

**Edge Cases**:
- Start position not found: Treat as normal click (no distance check)
- Distance exactly 5.0px: Treat as drag-to-move (≥ threshold)
- Negative distance: Impossible (sqrt of squared values is always ≥ 0)

---

## Integration with Existing Lynx Data Model

### No Changes to Python Backend

**Diagram State** (`src/lynx/diagram.py`):
- No changes required
- `moveBlock` action already exists
- Drag detection is frontend-only

**Block Model** (`src/lynx/blocks/base.py`):
- No new attributes needed
- Position already stored as (x, y) coordinates
- Selection state not persisted (UI-only)

### Frontend State Compatibility

**Existing State**:
- `selectedBlockId`: UI state for parameter panel (unchanged)
- `nodes`: React Flow nodes array (add/modify `selected` property)
- `edges`: React Flow edges array (unchanged - edge routing preserved)

**New State**:
- `dragStartPos`: useRef for initial positions (transient, non-rendering)

**No Conflicts**: Drag detection uses separate state (ref) and modifies existing `node.selected` property (already used by resize handles).

---

## Validation Rules

### DragStartPosition Validation

1. **Position Validity**:
   - x and y must be finite numbers
   - No NaN or Infinity values
   - Negative values allowed (blocks can be positioned at negative coordinates)

2. **Node ID Validity**:
   - Must match existing node in React Flow's nodes array
   - Must not be empty string or null

3. **Cleanup**:
   - Entry must be deleted after distance check completes
   - No stale entries (memory leak prevention)

### Distance Threshold Validation

1. **Threshold Value**:
   - Fixed at 5 pixels (not configurable in MVP)
   - Applied consistently across all block types
   - Measured in screen pixels (not canvas coordinates accounting for zoom)

2. **Distance Calculation**:
   - Must use Euclidean distance formula
   - Must handle zero movement (distance = 0)
   - Must handle very large movements (e.g., drag across entire canvas)

---

## Performance Characteristics

### Memory Usage

- **DragStartPosition**: O(n) where n = number of blocks being dragged simultaneously
- **Typical case**: 1 block dragged at a time → ~16 bytes per entry (2 floats × 8 bytes)
- **Worst case**: All blocks dragged simultaneously → 16 bytes × block count
- **Example**: 50 blocks → 800 bytes (negligible)

### Computational Complexity

- **Distance calculation**: O(1) per drag operation
- **onNodesChange filtering**: O(m) where m = number of position changes per event
- **Typical case**: 1 position change per event → O(1)
- **Worst case**: All blocks moved simultaneously → O(n) linear scan

### Time Complexity

- **Distance check**: ~5-10ns (arithmetic + comparison)
- **Selection update**: ~1-2ms (React state update + re-render)
- **Total overhead per drag**: < 5ms (well within 16ms / 60 FPS budget)

---

## Testing Considerations

### Unit Test Cases

1. **Distance Calculation**:
   - Zero distance (start = end)
   - Small distance (4.9px → SELECT)
   - Threshold distance (5.0px → MOVE)
   - Large distance (100px → MOVE)
   - Diagonal movement (Euclidean vs Manhattan distance)

2. **State Transitions**:
   - IDLE → DRAGGING → SELECT
   - IDLE → DRAGGING → MOVE
   - Cleanup (dragStartPos entry deleted)

3. **Edge Cases**:
   - Drag without onNodeDragStart (missing start position)
   - Multiple concurrent drags (different blocks)
   - Rapid click-drag-click sequences

### Integration Test Cases

1. **User Scenarios** (from spec):
   - Click to select (< 5px)
   - Drag to move (≥ 5px)
   - Canvas deselection
   - Drag selected block (clears selection)

2. **Cross-Feature Integration**:
   - Edge routing during drag (preserves existing behavior)
   - Collinear snapping (preserves 20px threshold)
   - Resize handles visibility (controlled by `selected` property)

---

## Future Extensions (Out of Scope for MVP)

### Potential Enhancements

1. **Configurable Threshold**:
   - Add user setting for drag threshold (default: 5px, range: 1-10px)
   - Store in diagram metadata or user preferences

2. **Multi-Select Support**:
   - Shift+click to add blocks to selection
   - Drag multiple selected blocks together
   - Distance threshold applies to first block in selection

3. **Touch Gesture Support**:
   - Long-press to select (instead of click)
   - Separate threshold for touch events (8-10px)

4. **Drag Cancellation**:
   - ESC key to cancel in-progress drag
   - Reset block to initial position

5. **Visual Feedback**:
   - Show threshold circle when hovering block
   - Highlight block when about to select (distance < 5px)

---

## Appendix: TypeScript Type Definitions

```typescript
// Drag start position tracking
type DragStartPosition = Record<string, { x: number; y: number }>;

// React Flow position type (existing)
type XYPosition = {
  x: number;
  y: number;
};

// React Flow node change type (existing)
type NodePositionChange = {
  id: string;
  type: "position";
  position: XYPosition;
  positionAbsolute: XYPosition;
  dragging: boolean;
};

// Distance calculation
type DistanceCalculator = (
  start: XYPosition,
  end: XYPosition
) => number;

// Drag detection hook interface (conceptual)
interface DragDetectionHook {
  dragStartPos: React.MutableRefObject<DragStartPosition>;
  handleNodeDragStart: (nodeId: string, position: XYPosition) => void;
  handlePositionChange: (change: NodePositionChange) => boolean; // true = apply, false = filter
}
```
