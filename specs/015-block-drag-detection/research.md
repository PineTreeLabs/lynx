<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Block Drag Detection

**Date**: 2026-01-18
**Feature**: Block Drag Detection (015)
**Purpose**: Resolve technical unknowns for implementing 5-pixel drag threshold

## Research Questions & Decisions

### 1. React Flow Drag Event System

**Question**: How does React Flow's drag system work internally? Can we intercept drag before position changes?

**Decision**: Use `nodeDragThreshold={5}` prop + `onNodesChange` filtering

**Rationale**:
- React Flow 11.9+ includes `nodeDragThreshold` prop (default: 1px)
- Setting to 5px automatically separates click from drag at the React Flow level
- `NodePositionChange` includes `dragging` boolean: `true` during drag, `false` at completion
- Filtering `onNodesChange` when `dragging === false` intercepts final position before Python sync

**Event Firing Sequence**:
```
User mousedown → React Flow measures movement
  ↓
Movement < 5px → onNodeClick fires (no drag events)
Movement ≥ 5px → onNodeDragStart → onNodeDrag (continuous) → onNodeDragStop
```

**Position Data Available**:
- `onNodeDragStart(event, node)` → `node.position` (initial)
- `onNodeDrag(event, node)` → `node.position` (current during drag)
- `onNodeDragStop(event, node)` → `node.position` (final)

**Alternatives Considered**:
- Manual distance tracking in onNodeDragStop: More complex, duplicates React Flow logic
- Custom mouse event handlers: Bypasses React Flow, risks breaking existing drag machinery

**Trade-offs**:
- ✅ Gain: Simple, uses native React Flow feature, zero performance overhead
- ✅ Gain: Automatic click/drag separation - no manual state machine needed
- ⚠️ Lose: Less control over threshold calculation (fixed 5px, can't use Euclidean distance)

**Sources**:
- [React Flow API Reference](https://reactflow.dev/api-reference/react-flow)
- [nodeDragThreshold feature](https://github.com/wbkd/react-flow/issues/3428)
- [React Flow 11.9.0 release notes](https://xyflow.com/blog/svelte-flow-alpha-xyflow)

---

### 2. Tracking Initial Click Position

**Question**: What's the best way to store initial position for distance calculation?

**Decision**: Use `useRef` to store drag start positions by node ID

**Rationale**:
- No re-renders when updating ref value (better performance than useState)
- Persists across render cycles
- Existing Lynx patterns already use useRef (see `useBlockResize.ts` line 133)
- Can store multiple positions: `dragStartPos.current[nodeId] = { x, y }`

**Implementation Pattern**:
```typescript
const dragStartPos = useRef<Record<string, { x: number; y: number }>>({});

const onNodeDragStart = useCallback((_, node: Node) => {
  dragStartPos.current[node.id] = { x: node.position.x, y: node.position.y };
}, []);

const onNodeDragStop = useCallback((_, node: Node) => {
  const startPos = dragStartPos.current[node.id];
  if (!startPos) return;

  const dx = node.position.x - startPos.x;
  const dy = node.position.y - startPos.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // ... distance check logic

  delete dragStartPos.current[node.id]; // Cleanup
}, []);
```

**Alternatives Considered**:
- useState: Causes unnecessary re-renders, no performance benefit
- React Flow internal state: Not exposed, would require reverse-engineering

**Trade-offs**:
- ✅ Gain: Zero re-render overhead
- ✅ Gain: Supports concurrent drags (multi-touch, if needed in future)
- ⚠️ Lose: Manual cleanup required (delete after use)

**Sources**:
- [React Flow drag handle example](https://reactflow.dev/examples/nodes/drag-handle)
- [Custom node drag behavior](https://github.com/xyflow/xyflow/discussions/3351)

---

### 3. Preventing Position Updates for Small Movements

**Question**: How do we prevent block position from changing when movement < 5px?

**Decision**: Filter `NodePositionChange` events in `onNodesChange` handler

**Rationale**:
- `onNodesChange` receives all node updates before they're applied
- `NodePositionChange` includes `dragging` boolean to distinguish active drag from completion
- Filter when `dragging === false` (drag just ended) to check final distance
- Return `false` from filter to prevent position update

**Implementation Pattern**:
```typescript
const onNodesChange: OnNodesChange = useCallback((changes) => {
  const filteredChanges = changes.filter(change => {
    if (change.type === 'position' && !change.dragging) {
      // Drag ended - check distance from start
      const startPos = dragStartPos.current[change.id];
      if (startPos) {
        const dx = change.position.x - startPos.x;
        const dy = change.position.y - startPos.y;
        const distanceSquared = dx * dx + dy * dy;

        if (distanceSquared < 25) {  // 5px threshold (5² = 25)
          // Movement too small - don't apply this change
          // Also trigger selection here
          setNodes(nds => nds.map(n => ({ ...n, selected: n.id === change.id })));
          delete dragStartPos.current[change.id];
          return false; // Filter out this position change
        }

        delete dragStartPos.current[change.id];
      }
    }
    return true; // Apply all other changes
  });

  setNodes(nds => applyNodeChanges(filteredChanges, nds));
}, []);
```

**Key Insight**: The `dragging` boolean is critical
- `dragging: true` → Position updates during active drag (continuous)
- `dragging: false` → Final position when drag completes (one-time)
- Only check distance when `dragging: false`

**Alternatives Considered**:
- Reset position in onNodeDragStop: Race condition with React Flow's internal update
- Prevent drag in onNodeDragStart: Breaks React Flow's drag machinery

**Trade-offs**:
- ✅ Gain: Clean interception point before position persists
- ✅ Gain: No risk of React Flow state corruption
- ✅ Gain: Can trigger selection in same handler (single responsibility)
- ⚠️ Lose: Slightly more complex than simple conditional in onNodeDragStop

**Sources**:
- [NodeChange type reference](https://reactflow.dev/api-reference/types/node-change)
- [OnNodesChange handler](https://reactflow.dev/api-reference/types/on-nodes-change)
- [Preventing drag beyond container](https://github.com/wbkd/react-flow/issues/2459)

---

### 4. Selection Timing Strategy

**Question**: How do we delay selection until we know drag distance?

**Decision**: Remove onClick selection, apply selection in onNodesChange filter for small movements

**Rationale**:
- With `nodeDragThreshold={5}`, React Flow prevents onClick from firing if movement ≥ 5px
- For movements < 5px: `nodeDragThreshold` allows onClick to fire normally
- **Problem**: onClick fires BEFORE onNodeDragStop, so we can't check distance yet
- **Solution**: Disable selection in onClick, apply it in onNodesChange when `dragging: false` and distance < 5px

**Implementation Pattern**:
```typescript
// Remove existing onClick selection logic
const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
  // NO-OP - selection handled by drag detection in onNodesChange
  // Keep this handler for future extensions (double-click, etc.)
}, []);

// Apply selection in onNodesChange for small movements
const onNodesChange: OnNodesChange = useCallback((changes) => {
  const filteredChanges = changes.filter(change => {
    if (change.type === 'position' && !change.dragging) {
      const startPos = dragStartPos.current[change.id];
      if (startPos) {
        const distance = calculateDistance(startPos, change.position);

        if (distance < 5) {
          // Small movement - SELECT the block
          setNodes(nds => nds.map(n => ({
            ...n,
            selected: n.id === change.id  // Exclusive selection
          })));
          return false; // Don't apply position change
        }
      }
    }
    return true;
  });

  setNodes(nds => applyNodeChanges(filteredChanges, nds));
}, []);
```

**Simplified Approach (Alternative)**:
If `nodeDragThreshold={5}` perfectly separates click/drag:
- Keep onClick for selection (< 5px movement → no drag events → onClick fires)
- In onNodeDragStop, clear selection if movement ≥ 5px
- Simpler, but relies on `nodeDragThreshold` accuracy

**Alternatives Considered**:
- pendingSelection ref + coordination: More complex state management
- Delay onClick with setTimeout: Unreliable timing, poor UX

**Trade-offs**:
- ✅ Gain: Single source of truth for selection logic (onNodesChange)
- ✅ Gain: Guaranteed coordination between movement and selection
- ⚠️ Lose: onClick no longer triggers selection (behavior change)

**Sources**:
- [nodeDragThreshold feature](https://github.com/wbkd/react-flow/issues/3428)
- [Drag and click nodes issue](https://github.com/wbkd/react-flow/issues/1457)

---

### 5. Canvas Deselection (Click Empty Space)

**Question**: Does onPaneClick fire for panning? Do we need a movement threshold?

**Decision**: Keep existing onPaneClick behavior (deselect all blocks) - acceptable as-is

**Rationale**:
- Current Lynx implementation: onPaneClick deselects all blocks (line 559-580)
- Known issue: onPaneClick can fire after connection drag or short pan
- **In practice**: Panning typically involves >5px movement, users expect deselection
- **Risk**: False positives if user pans <5px, but rare in real usage
- **Cost-benefit**: Adding pan detection (mousedown/mousemove/mouseup tracking) adds complexity for edge case

**Current Behavior** (Acceptable):
```typescript
const onPaneClick = useCallback(() => {
  setNodes((nodes) => nodes.map((n) => ({ ...n, selected: false })));
  setSelectedBlockId(null);
  setShowSettings(false);
  setContextMenu(null);
}, [setNodes]);
```

**If Issues Arise (Future Enhancement)**:
```typescript
const paneClickStart = useRef<{ x: number; y: number } | null>(null);

const handlePaneMouseDown = (event: React.MouseEvent) => {
  paneClickStart.current = { x: event.clientX, y: event.clientY };
};

const handlePaneMouseUp = (event: React.MouseEvent) => {
  if (!paneClickStart.current) return;

  const dx = event.clientX - paneClickStart.current.x;
  const dy = event.clientY - paneClickStart.current.y;
  const distanceSquared = dx * dx + dy * dy;

  if (distanceSquared < 25) {  // 5px threshold
    // True click - deselect
    onPaneClick();
  }

  paneClickStart.current = null;
};
```

**Alternatives Considered**:
- Add explicit "Deselect All" button: Extra UI clutter
- ESC key for deselection: Good addition, but doesn't replace pane click
- Remove pane click deselection: Users lose intuitive deselect gesture

**Trade-offs**:
- ✅ Gain: Keep simple, intuitive behavior
- ✅ Gain: Avoid adding complexity for edge case
- ⚠️ Lose: Possible false deselection on very short pans (< 5px)

**Sources**:
- [onPaneClick triggers after connection drag](https://github.com/xyflow/xyflow/issues/5057)
- [Panning and Zooming concepts](https://reactflow.dev/learn/concepts/the-viewport)

---

## Performance Optimization Decisions

### Euclidean Distance Calculation

**Decision**: Use squared distance comparison (avoid sqrt)

**Rationale**:
- `sqrt(dx² + dy²)` is computationally expensive
- Comparing `dx² + dy²` to `threshold²` gives same result
- Example: Instead of `distance < 5`, use `distanceSquared < 25`

**Implementation**:
```typescript
// Slow (sqrt overhead)
const distance = Math.sqrt(dx * dx + dy * dy);
if (distance < 5) { /* ... */ }

// Fast (no sqrt)
const distanceSquared = dx * dx + dy * dy;
if (distanceSquared < 25) { /* ... */ }  // 5² = 25
```

**Performance Impact**:
- `Math.sqrt` takes ~5-10ns per call
- With 60 FPS drag updates: ~600ns saved per second
- Negligible individually, good practice for high-frequency calculations

---

## Final Architecture Decision

**Chosen Approach**: Hybrid Strategy

1. **Use `nodeDragThreshold={5}`** on ReactFlow component
   - Automatic click/drag separation at React Flow level
   - Prevents unnecessary drag events for small movements
   - Zero implementation overhead

2. **Filter `onNodesChange` for position updates**
   - Check `change.type === 'position' && change.dragging === false`
   - Calculate distance from dragStartPos ref
   - If distance < 5px:
     - Apply selection (`node.selected = true`)
     - Filter out position change (return false)
   - If distance ≥ 5px:
     - Clear selection (`node.selected = false`)
     - Apply position change (return true)
     - Send `moveBlock` action to Python

3. **Keep onClick as NO-OP**
   - Let onNodesChange handle all selection logic
   - Preserves handler for future extensions (double-click, etc.)

4. **Preserve onPaneClick**
   - Deselect all blocks when clicking empty canvas
   - Accept rare false positives on very short pans

**Why This Architecture**:
- Leverages React Flow's built-in threshold feature
- Single source of truth for selection (onNodesChange)
- Minimal code changes to existing Lynx implementation
- Preserves all existing behavior (edge updates, snapping, canvas boundaries)
- Meets all performance targets (< 16ms drag updates, < 50ms selection)

---

## Risks & Mitigations

### Risk 1: nodeDragThreshold Not Exact 5px
- **Probability**: Low (feature designed for this use case)
- **Impact**: onClick might fire for 5.1px movement (minor UX issue)
- **Mitigation**: onNodesChange filter acts as second layer of defense

### Risk 2: Race Condition in onNodesChange
- **Probability**: Low (React Flow controls change timing)
- **Impact**: Position update applied before distance check
- **Mitigation**: `dragging: false` guarantees final position is checked

### Risk 3: Performance Regression
- **Probability**: Very Low (optimized distance check, ref-based tracking)
- **Impact**: Drag updates slower than 60 FPS
- **Mitigation**: Profile with React DevTools, add useMemo if needed

---

## Technology Stack Additions

**No new dependencies required**. All features use existing React Flow 11.11.4 capabilities:
- `nodeDragThreshold` prop (React Flow 11.9+)
- `NodePositionChange` type (React Flow 11.0+)
- `onNodesChange` handler (existing)
- `useRef` hook (React 19.2.3)

---

## Next Phase

All research questions resolved. Ready to proceed to:
- Phase 1: Generate `data-model.md` (DragState entity)
- Phase 1: Generate `quickstart.md` (test scenarios)
- Phase 1: Update agent context (drag detection patterns)
