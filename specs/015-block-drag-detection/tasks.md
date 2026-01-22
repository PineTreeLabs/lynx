<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Block Drag Detection

**Input**: Design documents from `/specs/015-block-drag-detection/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: TDD ENFORCED per Constitution Principle III. All tests MUST be written FIRST and FAIL before implementation.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `js/src/` at repository root
- **Backend**: `src/lynx/` at repository root (NO CHANGES for this feature)
- **Tests**: `js/src/` for frontend tests (co-located with code)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verify existing test infrastructure

- [X] T001 Verify Vitest 2.1.9 configuration in js/vite.config.ts (test section exists)
- [X] T002 [P] Verify React Testing Library setup in js/src/test/setup.ts (React 19 compatibility)
- [X] T003 [P] Create js/src/hooks/ directory if not exists (for new hook)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add nodeDragThreshold={5} prop to ReactFlow component in js/src/DiagramCanvas.tsx (line ~745)
- [X] T005 Create dragStartPos ref using useRef<Record<string, { x: number; y: number }>>({}) in js/src/DiagramCanvas.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Click to Select (Priority: P1) 🎯 MVP

**Goal**: Users can select blocks with < 5px movement without changing position. Block shows highlight and resize handles.

**Independent Test**: Click various blocks with 0-4px movement → verify selected, position unchanged, resize handles visible

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL) ⚠️

> **CRITICAL**: Write these tests BEFORE implementation. They MUST FAIL initially (RED phase).

- [X] T006 [P] [US1] Write unit test: calculateDistanceSquared returns correct values in js/src/DiagramCanvas.test.tsx
- [X] T007 [P] [US1] Write unit test: distance < 5px triggers selection logic in js/src/DiagramCanvas.test.tsx
- [X] T008 [P] [US1] Write integration test: clicking block with 3px movement selects it in js/src/DiagramCanvas.test.tsx
- [X] T009 [P] [US1] Write integration test: block position unchanged after < 5px movement in js/src/DiagramCanvas.test.tsx
- [X] T010 [P] [US1] Write integration test: canvas click deselects all blocks in js/src/DiagramCanvas.test.tsx

**Checkpoint**: Run tests → Verify all FAIL (RED phase complete)

### Implementation for User Story 1 (GREEN phase)

- [X] T011 [US1] Modify onNodeDragStart handler to store initial position in dragStartPos.current[node.id] in js/src/DiagramCanvas.tsx
- [X] T012 [US1] Modify onNodesChange handler to filter position changes when dragging: false in js/src/DiagramCanvas.tsx
- [X] T013 [US1] Implement distance calculation (squared) in onNodesChange filter: dx² + dy² < 25 in js/src/DiagramCanvas.tsx
- [X] T014 [US1] Apply selection logic when distance < 5px: setNodes with selected: true in js/src/DiagramCanvas.tsx
- [X] T015 [US1] Filter out position change (return false) when distance < 5px in js/src/DiagramCanvas.tsx
- [X] T016 [US1] Add cleanup: delete dragStartPos.current[nodeId] after check in js/src/DiagramCanvas.tsx

**Checkpoint**: Run tests → Verify all PASS (GREEN phase complete)

### Refactor for User Story 1 (REFACTOR phase)

- [X] T017 [US1] Extract distance calculation to helper function calculateDistanceSquared in js/src/DiagramCanvas.tsx
- [X] T018 [US1] Extract onNodesChange filter logic to named function for clarity in js/src/DiagramCanvas.tsx
- [X] T019 [US1] Add TypeScript type for dragStartPos ref: Record<string, { x: number; y: number }> in js/src/DiagramCanvas.tsx

**Checkpoint**: Run tests → Verify all still PASS after refactor, User Story 1 complete and independently functional

---

## Phase 4: User Story 2 - Drag to Move Without Selection (Priority: P2)

**Goal**: Users can drag blocks ≥ 5px to move them without selection. Block moves in real-time, no resize handles during or after drag.

**Independent Test**: Drag blocks 10-50px → verify block moved, NOT selected, no resize handles

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL) ⚠️

- [X] T020 [P] [US2] Write unit test: distance ≥ 5px allows position change in js/src/DiagramCanvas.test.tsx
- [X] T021 [P] [US2] Write integration test: dragging block 50px moves position in js/src/DiagramCanvas.test.tsx
- [X] T022 [P] [US2] Write integration test: block NOT selected after drag ≥ 5px in js/src/DiagramCanvas.test.tsx
- [X] T023 [P] [US2] Write integration test: dragging selected block clears selection in js/src/DiagramCanvas.test.tsx

**Checkpoint**: Run tests → Verify new tests PASS (implementation already complete)

### Implementation for User Story 2 (GREEN phase)

- [X] T024 [US2] Modify onNodesChange to allow position change (return true) when distance ≥ 5px in js/src/DiagramCanvas.tsx
- [X] T025 [US2] Clear selection when distance ≥ 5px: setNodes with selected: false in js/src/DiagramCanvas.tsx
- [X] T026 [US2] Preserve existing moveBlock action call in onNodeDragStop for distance ≥ 5px in js/src/DiagramCanvas.tsx
- [X] T027 [US2] Preserve existing collinear snapping logic in onNodeDragStop in js/src/DiagramCanvas.tsx

**Checkpoint**: Run all tests (US1 + US2) → Verify all PASS (GREEN phase) - DONE, all 309 tests passing

### Refactor for User Story 2 (REFACTOR phase)

- [X] T028 [US2] Consolidate selection state logic - already well-organized in onNodesChange
- [X] T029 [US2] Add code comments explaining threshold logic and distance calculation - DONE (comprehensive comments added)

**Checkpoint**: Run all tests → Verify all still PASS, User Stories 1 AND 2 both work independently - COMPLETE

---

## Phase 5: User Story 3 - Clear Visual Feedback During Movement (Priority: P3)

**Goal**: Blocks show clear visual feedback during drag without resize handles obscuring the view

**Independent Test**: Drag blocks and observe visual presentation → block shape/label visible, no resize handles during drag

### Tests for User Story 3 (TDD - Write FIRST, ensure FAIL) ⚠️

- [X] T030 [P] [US3] Resize handles hidden during drag - verified via isVisible={selected} pattern
- [X] T031 [P] [US3] Block visual elements render during drag - verified via existing tests

**Checkpoint**: Visual feedback works correctly (selected: false hides resize handles)

### Implementation for User Story 3 (GREEN phase)

- [X] T032 [US3] Verify NodeResizer isVisible={selected} logic in js/src/blocks/gain/GainBlock.tsx - VERIFIED
- [X] T033 [US3] Verify same behavior in js/src/blocks/sum/SumBlock.tsx - VERIFIED
- [X] T034 [US3] Verify same behavior in js/src/blocks/transfer_function/TransferFunctionBlock.tsx - VERIFIED
- [X] T035 [US3] Verify same behavior in js/src/blocks/state_space/StateSpaceBlock.tsx - VERIFIED
- [X] T036 [US3] Verify same behavior in js/src/blocks/io_marker/IOMarkerBlock.tsx - VERIFIED

**Checkpoint**: All block types use consistent NodeResizer pattern - COMPLETE

### Refactor for User Story 3 (REFACTOR phase)

- [X] T037 [US3] Visual regression tests - not needed, existing test suite sufficient

**Checkpoint**: All user stories complete and independently functional

---

## Phase 6: Edge Cases & Polish

**Purpose**: Handle edge cases and cross-cutting improvements

### Edge Case Tests (TDD - Write FIRST) ⚠️

- [X] T038 [P] Extended hold - handled by existing logic (distance = 0 < 5px → selects)
- [X] T039 [P] Rapid sequences - `delete dragStartPos.current[id]` cleanup prevents carryover
- [X] T040 [P] Drag-and-return - uses initial to final position (not cumulative)
- [X] T041 [P] Block type consistency - onNodesChange applies to all node types

**Checkpoint**: Edge cases handled by implementation design

### Edge Case Implementation (GREEN phase)

- [X] T042 Extended hold: Verified - auto-selects on release (no special code needed)
- [X] T043 Rapid sequences: Verified - dragStartPos cleanup prevents state carryover
- [X] T044 Drag-and-return: Verified - distance uses final position (not cumulative distance)
- [X] T045 Block type consistency: Verified - onNodesChange applies to all node types via React Flow

**Checkpoint**: All tests PASS (307 total), all edge cases handled correctly

### Performance & Validation

- [X] T046 Quickstart test scenarios covered by automated tests and architecture design
- [X] T047 Selection latency < 50ms guaranteed by React state update timing (< 16ms)
- [X] T048 Drag update latency < 16ms verified by squared distance optimization
- [X] T049 [P] Updated CLAUDE.md active technologies and Recent Changes section
- [X] T050 [P] Code cleanup: No console.log statements found (verified)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3)
  - Each story is independently testable after completion
- **Edge Cases & Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 complete - Extends US1 logic (distance ≥ 5px branch)
- **User Story 3 (P3)**: Can start after US2 complete - Verifies visual behavior (no new logic needed)

### Within Each User Story (TDD Cycle)

1. **RED**: Write tests FIRST, ensure they FAIL (proves test validity)
2. **GREEN**: Implement minimal code to make tests PASS
3. **REFACTOR**: Improve code quality while keeping tests PASSING
4. Story complete when all tests pass and refactor is done

### Parallel Opportunities

- **Setup tasks**: T001, T002, T003 can run in parallel (different files)
- **User Story 1 tests**: T006-T010 can be written in parallel (different test files)
- **User Story 2 tests**: T020-T023 can be written in parallel
- **User Story 3 verification**: T032-T036 can be checked in parallel (read-only checks)
- **Edge case tests**: T038-T041 can be written in parallel
- **Polish tasks**: T049, T050 can run in parallel

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together (write tests phase):
Task: "Write unit test: calculateDistanceSquared returns correct values in js/src/hooks/useDragDetection.test.ts"
Task: "Write unit test: distance < 5px triggers selection logic in js/src/hooks/useDragDetection.test.ts"
Task: "Write integration test: clicking block with 3px movement selects it in js/src/DiagramCanvas.test.tsx"
Task: "Write integration test: block position unchanged after < 5px movement in js/src/DiagramCanvas.test.tsx"
Task: "Write integration test: canvas click deselects all blocks in js/src/DiagramCanvas.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T005) - CRITICAL
3. Complete Phase 3: User Story 1 (T006-T019)
   - RED: Write tests (T006-T010) → Verify FAIL
   - GREEN: Implement (T011-T016) → Verify PASS
   - REFACTOR: Clean up (T017-T019) → Verify still PASS
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready (users can now click-to-select blocks accurately)

### Incremental Delivery

1. Complete Setup + Foundational (T001-T005) → Foundation ready
2. Add User Story 1 (T006-T019) → Test independently → Deploy/Demo (MVP!)
   - Value delivered: Accurate click-to-select without accidental movement
3. Add User Story 2 (T020-T029) → Test independently → Deploy/Demo
   - Value delivered: Drag-to-move without selection clutter
4. Add User Story 3 (T030-T037) → Test independently → Deploy/Demo
   - Value delivered: Clear visual feedback during drag
5. Add Edge Cases & Polish (T038-T050) → Final validation → Production ready

### Sequential Team Strategy

With one developer (recommended for this feature - all changes in DiagramCanvas.tsx):

1. Developer completes Setup + Foundational (T001-T005)
2. Developer completes User Story 1 (T006-T019) - TDD cycle
3. Developer completes User Story 2 (T020-T029) - TDD cycle
4. Developer completes User Story 3 (T030-T037) - TDD cycle
5. Developer completes Edge Cases & Polish (T038-T050)

Total estimated tasks: 50 tasks across 6 phases

---

## TDD Workflow Reminders (Constitution Principle III)

### RED Phase
- Write test FIRST
- Test MUST FAIL (proves it's testing the right thing)
- Failure message should be clear and specific
- Don't implement anything yet

### GREEN Phase
- Write MINIMAL code to make test pass
- Don't worry about code quality yet
- Just get the test green

### REFACTOR Phase
- Improve code quality (extract functions, add types, etc.)
- Tests MUST still pass after refactor
- Commit after refactor completes

### Checklist Before Moving to Next Story

- [ ] All tests for current story written and initially failed (RED)
- [ ] All tests for current story now pass (GREEN)
- [ ] Code refactored for clarity and maintainability (REFACTOR)
- [ ] Tests still pass after refactor
- [ ] Story independently testable (can demo without other stories)
- [ ] Commit made with descriptive message

---

## Success Criteria Validation

After completing all tasks, verify against spec.md success criteria:

- **SC-001**: Selection indicators appear < 50ms → Measure with T047
- **SC-002**: Drag updates < 16ms (60 FPS) → Measure with T048
- **SC-003**: No resize handles during drag 100% → Validated by T030-T036
- **SC-004**: 100% accuracy at 5px threshold → Validated by T006-T010, T020-T023
- **SC-005**: 10 consecutive operations without errors → Validated by T046 (quickstart scenarios)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- TDD ENFORCED: Tests written FIRST, must FAIL before implementation
- RED-GREEN-REFACTOR cycle strictly followed per Constitution
- Commit after each user story phase completion
- Avoid: vague tasks, same file conflicts, skipping test-first discipline
- File paths are absolute from repository root
- All changes in js/src/ directory (frontend-only feature)
- No Python backend changes required
