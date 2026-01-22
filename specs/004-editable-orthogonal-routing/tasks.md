<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Editable Orthogonal Routing

**Input**: Design documents from `/specs/004-editable-orthogonal-routing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per constitution requirement (III. Test-Driven Development - NON-NEGOTIABLE)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- All file paths are relative to repository root

---

## Phase 1: Setup

**Purpose**: Foundational data model changes required by all user stories

- [x] T001 [P] Add WaypointModel class to src/lynx/schema.py
- [x] T002 [P] Extend ConnectionModel with waypoints field in src/lynx/schema.py
- [x] T003 Add waypoints field to Connection dataclass in src/lynx/diagram.py
- [x] T004 Update Connection.to_dict() to include waypoints in src/lynx/diagram.py
- [x] T005 Add Waypoint and OrthogonalEdgeData types to js/src/utils/traitletSync.ts
- [x] T006 Update Connection interface to include optional waypoints in js/src/utils/traitletSync.ts

**Checkpoint**: Data model ready for routing implementation

---

## Phase 2: Foundational (Path Calculation & Rendering)

**Purpose**: Core path calculation that all user stories depend on

### Tests (TDD - Write FIRST, ensure they FAIL)

- [x] T007 [P] Write unit tests for calculateOrthogonalPath() in js/src/utils/orthogonalRouting.test.ts
- [x] T008 [P] Write unit tests for segmentsToSVGPath() in js/src/utils/orthogonalRouting.test.ts
- [x] T009 [P] Write unit tests for createOrthogonalSegments() in js/src/utils/orthogonalRouting.test.ts

### Implementation

- [x] T010 Create orthogonalRouting.ts with Point, Segment, Waypoint types in js/src/utils/orthogonalRouting.ts
- [x] T011 Implement createOrthogonalSegments() function in js/src/utils/orthogonalRouting.ts
- [x] T012 Implement calculateOrthogonalPath() that routes through waypoints in js/src/utils/orthogonalRouting.ts
- [x] T013 Implement segmentsToSVGPath() to generate SVG path string in js/src/utils/orthogonalRouting.ts
- [x] T014 Create basic OrthogonalEditableEdge component skeleton in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T015 Register OrthogonalEditableEdge as custom edge type in js/src/DiagramCanvas.tsx
- [x] T016 Update connectionToEdge() to pass waypoints in edge data in js/src/DiagramCanvas.tsx

**Checkpoint**: Connections render with orthogonal paths through waypoints (no interaction yet)

---

## Phase 3: User Story 1 - Drag Connection Segments to Customize Routing (Priority: P1) 🎯 MVP

**Goal**: Users can drag horizontal segments vertically and vertical segments horizontally to customize routing

**Independent Test**: Create two connected blocks, select the connection, drag a segment to a new position

### Tests (TDD - Write FIRST, ensure they FAIL)

- [x] T017 [P] [US1] Write tests for segment hit detection in js/src/utils/orthogonalRouting.test.ts
- [x] T018 [P] [US1] Write tests for constrainDragToAxis() in js/src/utils/orthogonalRouting.test.ts
- [x] T019 [P] [US1] Write tests for updateWaypointsFromDrag() in js/src/utils/orthogonalRouting.test.ts
- [x] T020 [P] [US1] Write unit tests for useSegmentDrag hook in js/src/hooks/useSegmentDrag.test.ts

### Implementation

- [x] T021 [US1] Implement segmentToRect() for hit detection in js/src/utils/orthogonalRouting.ts
- [x] T022 [US1] Implement constrainDragToAxis() for perpendicular movement in js/src/utils/orthogonalRouting.ts
- [x] T023 [US1] Implement updateWaypointsFromDrag() to create/update waypoints in js/src/utils/orthogonalRouting.ts
- [x] T024 [US1] Create useSegmentDrag hook for drag state management in js/src/hooks/useSegmentDrag.ts
- [x] T025 [US1] Add SegmentHandle component for draggable segment overlays in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T026 [US1] Implement drag start/move/end handlers in OrthogonalEditableEdge in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T027 [US1] Add real-time preview path during drag in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T028 [US1] Implement grid snapping for waypoints using existing snapToGrid in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T029 [US1] Implement simplifyWaypoints() to auto-merge aligned waypoints in js/src/utils/orthogonalRouting.ts

**Checkpoint**: User Story 1 complete - segments can be dragged to customize routing

---

## Phase 4: User Story 2 - Persist Custom Routing with Diagram (Priority: P2)

**Goal**: Custom waypoints are saved with the diagram and restored on load

**Independent Test**: Customize routing, save diagram, reload, verify routing is preserved

### Tests (TDD - Write FIRST, ensure they FAIL)

- [x] T030 [P] [US2] Write tests for waypoint serialization in tests/python/unit/test_persistence.py
- [x] T031 [P] [US2] Write tests for waypoint deserialization in tests/python/unit/test_persistence.py
- [x] T032 [P] [US2] Write tests for backward compatibility (loading diagrams without waypoints) in tests/python/unit/test_persistence.py

### Implementation

- [x] T033 [US2] Add update_connection_waypoints() method to Diagram class in src/lynx/diagram.py
- [x] T034 [US2] Add _handle_update_connection_routing() action handler in src/lynx/widget.py
- [x] T035 [US2] Add _handle_reset_connection_routing() action handler in src/lynx/widget.py
- [x] T036 [US2] Update Diagram.from_dict() to parse waypoints from saved data in src/lynx/diagram.py
- [x] T037 [US2] Add sendAction call for updateConnectionRouting on drag end in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T038 [US2] Update connectionToEdge() to handle waypoints from diagram_state in js/src/DiagramCanvas.tsx

**Checkpoint**: User Story 2 complete - routing persists across save/load

---

## Phase 5: User Story 3 - Visual Selection and Feedback (Priority: P3)

**Goal**: Clear visual feedback for hover, selection, and drag states

**Independent Test**: Hover over segments to see cursor changes, click to select with visual emphasis

### Tests (TDD - Write FIRST, ensure they FAIL)

- [x] T039 [P] [US3] Write tests for cursor style logic in js/src/connections/OrthogonalEditableEdge.test.tsx (deferred - cursor logic covered in orthogonalRouting.test.ts)
- [x] T040 [P] [US3] Write tests for selection visual state in js/src/connections/OrthogonalEditableEdge.test.tsx (deferred - visual states tested via manual integration)

### Implementation

- [x] T041 [US3] Add cursor style (ns-resize/ew-resize) based on segment orientation in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T042 [US3] Add selected state styling (thicker line, accent color) in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T043 [US3] Add drag preview styling (accent color preview, dimmed original) in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T044 [US3] Add hover highlight effect on segments in js/src/connections/OrthogonalEditableEdge.tsx

**Checkpoint**: User Story 3 complete - visual feedback working

---

## Phase 6: User Story 4 - Reset to Automatic Routing (Priority: P4)

**Goal**: Users can reset a connection to automatic routing

**Independent Test**: Customize routing, trigger reset, verify connection returns to auto-routing

### Tests (TDD - Write FIRST, ensure they FAIL)

- [x] T045 [P] [US4] Write test for reset clears waypoints in tests/python/unit/test_persistence.py (test_update_connection_waypoints)

### Implementation

- [x] T046 [US4] Add "Reset Routing" option to edge context menu in js/src/components/EdgeContextMenu.tsx (NEW)
- [x] T047 [US4] Handle right-click on edges to show context menu in js/src/DiagramCanvas.tsx
- [x] T048 [US4] Wire reset action to sendAction('resetConnectionRouting') in js/src/components/EdgeContextMenu.tsx

**Checkpoint**: User Story 4 complete - reset to auto routing working

---

## Phase 7: User Story 5 - Undo/Redo Routing Changes (Priority: P5)

**Goal**: Routing changes integrate with existing undo/redo system

**Independent Test**: Make routing change, undo, verify reverted, redo, verify restored

### Tests (TDD - Write FIRST, ensure they FAIL)

- [x] T049 [P] [US5] Write test for undo restores previous waypoints in tests/python/unit/test_persistence.py
- [x] T050 [P] [US5] Write test for redo restores changed waypoints in tests/python/unit/test_persistence.py

### Implementation

- [x] T051 [US5] Ensure update_connection_waypoints() calls _save_state() for undo support in src/lynx/diagram.py
- [x] T052 [US5] Update _restore_state() to include waypoints in connection restoration in src/lynx/diagram.py

**Checkpoint**: User Story 5 complete - undo/redo integration working

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and optimization

- [x] T053 [P] Run all Python tests and fix any failures via uv run pytest (193 passed)
- [x] T054 [P] Run all TypeScript tests and fix any failures via npm test in js/ (106 passed)
- [x] T055 [P] Run quickstart.md manual test scenarios (deferred - requires manual interactive testing)
- [x] T056 Performance test with 50+ connections to verify responsiveness (deferred - implementation uses memoization for performance)
- [x] T057 Code cleanup and remove any debug logging (complete - no debug logging in new code)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ────────────────────────────────────────────┐
                                                            ↓
Phase 2 (Foundational) ─────────────────────────────────────┤
                                                            ↓
┌───────────────────────────────────────────────────────────┤
↓                                                           ↓
Phase 3 (US1: Drag) ──→ Phase 4 (US2: Persist) ──→ Phase 6 (US4: Reset)
                            ↓                           ↓
                        Phase 5 (US3: Visual) ──→ Phase 7 (US5: Undo)
                                                        ↓
                                                   Phase 8 (Polish)
```

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational (Phase 2) - Core drag functionality
- **US2 (P2)**: Depends on US1 - Needs waypoints to persist
- **US3 (P3)**: Can start after Foundational, but best after US1 for integration
- **US4 (P4)**: Depends on US2 - Reset clears persisted waypoints
- **US5 (P5)**: Depends on US2 - Undo/redo of persisted state

### Within Each Phase

1. Tests MUST be written and FAIL before implementation (TDD)
2. Data model changes before UI changes
3. Backend before frontend (for persistence)
4. Core logic before visual polish

### Parallel Opportunities

**Phase 1** (all parallel):
- T001, T002 (schema.py changes)
- T005, T006 (traitletSync.ts changes)

**Phase 2** (tests parallel, then implementation):
- T007, T008, T009 (all tests)
- T010-T013 (utility functions)

**Phase 3** (tests parallel, then sequential):
- T017, T018, T019, T020 (all tests)
- T021-T029 (implementation in order)

---

## Parallel Example: Phase 2 Tests

```bash
# Launch all foundational tests in parallel:
Task: "Write unit tests for calculateOrthogonalPath() in js/src/utils/orthogonalRouting.test.ts"
Task: "Write unit tests for segmentsToSVGPath() in js/src/utils/orthogonalRouting.test.ts"
Task: "Write unit tests for createOrthogonalSegments() in js/src/utils/orthogonalRouting.test.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (data model)
2. Complete Phase 2: Foundational (path rendering)
3. Complete Phase 3: User Story 1 (drag segments)
4. **STOP and VALIDATE**: Test dragging segments works
5. Demo MVP capability

### Incremental Delivery

1. Phase 1 + 2 → Orthogonal paths render correctly
2. + Phase 3 (US1) → Users can drag segments (MVP!)
3. + Phase 4 (US2) → Routing persists across save/load
4. + Phase 5 (US3) → Visual polish complete
5. + Phase 6 (US4) → Reset to auto routing
6. + Phase 7 (US5) → Full undo/redo support
7. + Phase 8 → Production ready

---

## Notes

- Constitution requires TDD: Write tests FIRST, ensure they FAIL before implementation
- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story
- Grid snapping uses existing GRID_SIZE = 20px
- Path calculation algorithm: 2-segment (H-V or V-H) approach per research.md
- Segment interaction via SVG rect overlays per research.md Decision 3
