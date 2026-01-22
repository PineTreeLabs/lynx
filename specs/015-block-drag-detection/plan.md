<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Block Drag Detection

**Branch**: `015-block-drag-detection` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-block-drag-detection/spec.md`

## Summary

Implement intelligent drag detection to distinguish between click-to-select (< 5px movement) and drag-to-move (≥ 5px movement) actions for block interactions. When users click and move less than 5 pixels, the block becomes selected with resize handles visible and position unchanged. When users drag more than 5 pixels, the block moves without selection indicators during or after the operation.

**Technical Approach**: Override React Flow's default `onNodeDragStart` behavior to track initial click position and implement a movement threshold check. Use a state machine (PENDING → SELECTING | MOVING) to determine interaction type based on Euclidean distance from initial click point. Preserve all existing behavior (edge updates, canvas boundaries, collinear snapping) while adding the 5-pixel detection layer.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Pydantic (schema validation)
**Storage**: JSON diagram files (existing persistence via Pydantic schemas)
**Testing**: Vitest 2.1.9 + jsdom (frontend unit/integration), pytest (backend unit)
**Target Platform**: Web (Jupyter notebook environment)
**Project Type**: Web application (TypeScript frontend + Python backend)
**Performance Goals**:
- Selection response time < 50ms (SC-001)
- Drag position updates < 16ms / 60 FPS (SC-002)
- 100% drag detection accuracy at 5px threshold (SC-004)
**Constraints**:
- Preserve existing behavior: edge routing, canvas boundaries, collinear snapping, selection model
- No changes to Python backend (drag detection is frontend-only)
- Must work with all 5 block types (Gain, Sum, TransferFunction, StateSpace, IOMarker)
**Scale/Scope**:
- 5 block types affected
- 1 new hook (useDragDetection)
- 3 event handler modifications (onNodeClick, onNodeDragStart, onNodeDragStop)
- ~150 lines of new code (hook + tests)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity Over Features ✅ PASS
- **Compliance**: Feature enhances existing interaction without adding new capabilities. Uses single 5-pixel threshold (no configurability). State machine has 3 states (PENDING, SELECTING, MOVING) - minimal complexity.
- **Justification**: Not adding features, fixing interaction model to prevent accidental moves during selection.

### Principle II: Python Ecosystem First ✅ PASS
- **Compliance**: No vendor lock-in. Drag detection is local UI behavior, doesn't affect diagram persistence format. Python diagram API unchanged.
- **Justification**: Enhancement is purely presentational (how users interact), not structural.

### Principle III: Test-Driven Development (TDD) ✅ PASS (ENFORCED)
- **Compliance**: Will write tests first for:
  1. `useDragDetection` hook (distance calculation, state transitions)
  2. Selection behavior (click < 5px → select, drag ≥ 5px → move)
  3. Edge cases (extended hold, rapid sequences, selected block drag)
- **Test Strategy**: RED-GREEN-REFACTOR cycle strictly enforced per constitution.

### Principle IV: Clean Separation of Concerns ✅ PASS
- **Compliance**: Drag detection logic isolated in `useDragDetection` hook (reusable, testable). No business logic in event handlers - they delegate to hook. No changes to Python backend (frontend-only feature).
- **Justification**: Hook pattern maintains separation: UI events → hook logic → state updates.

### Principle V: User Experience Standards ✅ PASS
- **Compliance**: Performance targets explicit in success criteria (50ms selection, 16ms drag updates). Simplifies interaction by eliminating accidental moves. No learning curve - matches standard diagram tool behavior.
- **Justification**: Addresses user pain point (accidental block movement) with industry-standard threshold.

**Gate Status**: ✅ ALL PRINCIPLES SATISFIED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/015-block-drag-detection/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # N/A (no API contracts for frontend-only feature)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
js/src/
├── DiagramCanvas.tsx                          # MODIFIED: onNodeClick, onNodeDragStart, onNodeDragStop
├── hooks/
│   └── useDragDetection.ts                    # NEW: Drag detection hook
│   └── useDragDetection.test.ts               # NEW: Hook tests
└── blocks/
    ├── gain/GainBlock.tsx                     # NO CHANGE (works via React Flow props)
    ├── sum/SumBlock.tsx                       # NO CHANGE
    ├── transfer_function/TransferFunctionBlock.tsx  # NO CHANGE
    ├── state_space/StateSpaceBlock.tsx        # NO CHANGE
    └── io_marker/IOMarkerBlock.tsx            # NO CHANGE

src/lynx/
├── widget.py                                  # NO CHANGE (no backend modifications)
└── diagram.py                                 # NO CHANGE
```

**Structure Decision**: Single web application structure (TypeScript frontend + Python backend). All changes are frontend-only in the `js/` directory. No new Python files needed - drag detection is purely a React/React Flow integration concern.

## Complexity Tracking

> **No Constitution violations to justify** - all gates passed.

## Phase 0: Research & Technical Decisions

### Research Questions

1. **How does React Flow's drag system work internally?**
   - Need to understand `onNodeDragStart`, `onNodeDrag`, `onNodeDragStop` event timing
   - Research: Can we intercept drag before React Flow moves the node?
   - Research: What position data is available in each event?

2. **What's the best way to track initial click position?**
   - Option A: useRef to store click position in onNodeDragStart
   - Option B: React state (may cause re-renders)
   - Option C: React Flow's internal drag state (if exposed)
   - Research: Performance implications of each approach

3. **How do we prevent position updates when movement < 5px?**
   - Option A: Conditional logic in onNodeDragStop (don't call sendAction)
   - Option B: Reset node position to initial if under threshold
   - Option C: Prevent drag entirely by returning early from onNodeDragStart
   - Research: Which approach preserves React Flow's drag machinery without side effects?

4. **How do we prevent selection during drag ≥ 5px?**
   - Current: onNodeClick fires BEFORE onNodeDragStart
   - Research: Can we delay selection until we know drag distance?
   - Research: Event timing: does onClick fire on mousedown or mouseup?

5. **Canvas deselection interaction**
   - Current: onPaneClick deselects all blocks
   - Research: Does onPaneClick fire for clicks that turn into pans?
   - Research: Movement threshold needed for canvas click-vs-drag?

### Decision Log

**Research findings will be documented in `research.md` with:**
- Decision: [what was chosen]
- Rationale: [why chosen]
- Alternatives considered: [what else evaluated]
- Trade-offs: [what we gain/lose]

## Phase 1: Design Artifacts

### Data Model (`data-model.md`)

**DragState** (frontend state machine):
```typescript
interface DragState {
  status: 'IDLE' | 'PENDING' | 'SELECTING' | 'MOVING';
  initialPosition: { x: number; y: number } | null;
  nodeId: string | null;
  threshold: number; // 5 pixels
}
```

**State Transitions**:
- IDLE → PENDING: onNodeDragStart (capture initial position)
- PENDING → SELECTING: onNodeDragStop AND distance < 5px
- PENDING → MOVING: onNodeDrag AND distance ≥ 5px
- SELECTING → IDLE: selection applied
- MOVING → IDLE: onNodeDragStop (movement applied)

**Distance Calculation**:
```typescript
distance = sqrt((x_current - x_initial)² + (y_current - y_initial)²)
```

### API Contracts (`contracts/`)

**N/A** - No API contracts needed. This is a frontend-only feature using existing Python backend actions (`moveBlock`). No new backend endpoints or data structures.

### Quick Start Guide (`quickstart.md`)

**Test Scenarios**:

1. **Scenario: Click to Select**
   - Setup: Create a Gain block at (100, 100)
   - Action: Click block, move mouse 3 pixels, release
   - Expected: Block selected (highlight + resize handles), position unchanged at (100, 100)
   - Validation: Assert `node.selected === true`, `node.position === {x: 100, y: 100}`

2. **Scenario: Drag to Move**
   - Setup: Create a Sum block at (200, 150)
   - Action: Click block, drag 50 pixels to the right, release
   - Expected: Block moved to (~250, 150), not selected (no highlight/handles)
   - Validation: Assert `node.selected === false`, `node.position.x ≈ 250`

3. **Scenario: Canvas Deselection**
   - Setup: Select a TransferFunction block
   - Action: Click on empty canvas space (not on any block)
   - Expected: Block deselected, no selection indicators visible
   - Validation: Assert all `nodes[].selected === false`

4. **Scenario: Drag Selected Block**
   - Setup: Select a StateSpace block, drag it 100 pixels down
   - Expected: Block moves, selection cleared during drag, remains unselected after release
   - Validation: Assert `node.selected === false` after drag complete

5. **Scenario: Edge Update During Drag**
   - Setup: Create two blocks with a connection, drag source block
   - Expected: Edge follows block in real-time during drag
   - Validation: Visual inspection (no automated check - preserves existing behavior)

## Phase 2: Implementation Strategy

### Core Components

**1. useDragDetection Hook** (`js/src/hooks/useDragDetection.ts`)
```typescript
export function useDragDetection(threshold: number = 5) {
  const [dragState, setDragState] = useState<DragState>({ status: 'IDLE', ... });

  const handleDragStart = (nodeId: string, position: XYPosition) => {
    // Capture initial position, transition to PENDING
  };

  const handleDragMove = (currentPosition: XYPosition) => {
    // Calculate distance, transition to MOVING if threshold exceeded
  };

  const handleDragEnd = (finalPosition: XYPosition) => {
    // Determine final action: SELECT or MOVE
  };

  return { dragState, handleDragStart, handleDragMove, handleDragEnd };
}
```

**2. DiagramCanvas Integration**
- Import `useDragDetection` hook
- Modify `onNodeDragStart`: Call `handleDragStart(node.id, node.position)`
- Add `onNodeDrag`: Call `handleDragMove(node.position)` to track distance
- Modify `onNodeDragStop`: Check `dragState.status` to determine SELECT or MOVE action
- Modify `onNodeClick`: Conditional selection only if not in MOVING state
- Preserve `onPaneClick`: Already deselects all (meets FR-004)

**3. Event Handler Flow**
```
User mousedown on block
  ↓
onNodeDragStart fires
  ↓
useDragDetection.handleDragStart() → PENDING state
  ↓
User moves mouse → onNodeDrag fires repeatedly
  ↓
useDragDetection.handleDragMove() checks distance
  ↓
  IF distance ≥ 5px → MOVING state (allow React Flow drag)
  IF distance < 5px → remain PENDING (no-op)
  ↓
User releases mouse → onNodeDragStop fires
  ↓
useDragDetection.handleDragEnd() checks final state
  ↓
  IF PENDING (distance < 5px):
    - Set node.selected = true
    - Reset position to initial (prevent micro-movements)
  IF MOVING (distance ≥ 5px):
    - Set node.selected = false
    - Apply collinear snapping
    - Send moveBlock action to Python
```

### Testing Strategy

**Unit Tests** (`useDragDetection.test.ts`):
1. Distance calculation accuracy (Euclidean formula)
2. State transitions (IDLE → PENDING → SELECTING/MOVING)
3. Threshold detection (4.9px → SELECTING, 5.1px → MOVING)
4. Edge cases: extended hold (>2s), rapid sequences, drag-and-return

**Integration Tests** (`DiagramCanvas.test.tsx`):
1. Click-to-select workflow (< 5px movement)
2. Drag-to-move workflow (≥ 5px movement)
3. Canvas deselection (click empty space)
4. Selected block drag (clears selection)
5. All 5 block types consistency

**Visual/Manual Tests**:
1. Edge routing during drag (real-time updates)
2. Canvas boundary behavior (no constraints)
3. Collinear snapping (20px threshold preserved)
4. Resize handles visibility (only when selected)

### Performance Considerations

**Optimization 1: useRef for Initial Position**
- Use `useRef` instead of state to avoid re-renders on position capture
- Only update state when transitioning between PENDING/SELECTING/MOVING

**Optimization 2: Distance Calculation Throttling**
- Calculate distance only in `onNodeDrag` (not on every mouse move event)
- React Flow already throttles these events to animation frames

**Optimization 3: Euclidean Distance Optimization**
- Skip `sqrt()` when comparing to threshold: `(dx² + dy²) < threshold²`
- Faster comparison: `(dx² + dy²) < 25` instead of `sqrt(dx² + dy²) < 5`

### Risk Mitigation

**Risk 1: Event Timing Conflicts**
- Problem: onClick might fire before/after onNodeDragStart
- Mitigation: Use drag state machine to gate selection logic in onClick
- Fallback: Research React Flow event order, add explicit timing checks

**Risk 2: React Flow Internal State Corruption**
- Problem: Preventing default drag might break React Flow's internals
- Mitigation: Allow React Flow to manage drag, intercept at onNodeDragStop
- Fallback: Reset position after drag completes if under threshold

**Risk 3: Performance Regression**
- Problem: Distance calculation on every drag event could slow 60 FPS target
- Mitigation: Optimized distance check (no sqrt), useRef for state
- Fallback: Profile with React DevTools, add useMemo/useCallback if needed

## Dependencies & Prerequisites

**Existing Code to Preserve**:
- ✅ Collinear snapping (20px threshold) - keep in onNodeDragStop
- ✅ Edge waypoint clearing on drag start - keep in onNodeDragStart
- ✅ Smart merge logic (>1px position changes) - no changes needed
- ✅ Selection model (single block) - extend, don't replace
- ✅ Canvas deselection (onPaneClick) - already implemented

**New Dependencies**: None (uses existing React Flow, React hooks)

**Breaking Changes**: None (additive feature, preserves all existing behavior)

## Open Questions for Tasks Phase

1. Should extended hold (>2s without movement) have special handling, or treat as normal click?
   - Spec says: "block should be selected when mouse is released"
   - Implementation: No special logic needed (PENDING → SELECTING on release)

2. Do we need undo/redo support for drag operations?
   - Current: moveBlock actions already in undo stack
   - Decision: No changes needed (existing undo/redo handles position changes)

3. Touchscreen support - does React Flow expose touch events with position data?
   - Research: Check React Flow docs for touch event handling
   - Fallback: Test on iPad/tablet, may work automatically via pointer events

4. Should the 5-pixel threshold be configurable (user setting)?
   - Spec: Fixed at 5 pixels (SC-004 requires 100% accuracy at this threshold)
   - Decision: Hardcode for MVP, can make configurable in future feature

## Agent Context Update

After Phase 1 completion, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will add to `.claude/agent-context.md`:
- TypeScript 5.9 (if not already present)
- React Flow 11.11.4 drag detection patterns
- useDragDetection hook API
- Drag state machine (IDLE/PENDING/SELECTING/MOVING)

## Success Metrics (from Spec)

- **SC-001**: Selection indicators appear within 50ms ✅ (React state update is <16ms)
- **SC-002**: Drag updates at 60 FPS ✅ (React Flow handles this, we add <1ms logic)
- **SC-003**: No resize handles during drag ✅ (node.selected stays false in MOVING state)
- **SC-004**: 100% drag detection accuracy ✅ (Euclidean distance, deterministic threshold)
- **SC-005**: 10 consecutive operations without errors ✅ (state machine prevents race conditions)

## Next Steps

1. ✅ Complete this plan (`/speckit.plan` command output)
2. ✅ Generate `research.md` (Phase 0 - resolve unknowns)
3. ✅ Generate `data-model.md` (Phase 1 - DragState entity)
4. ✅ Generate `quickstart.md` (Phase 1 - test scenarios)
5. ✅ Update agent context (Phase 1 - add drag detection patterns)
6. ⏳ Generate `tasks.md` (Phase 2 - `/speckit.tasks` command)
7. ⏳ Implement feature (Phase 3 - `/speckit.implement` command)
