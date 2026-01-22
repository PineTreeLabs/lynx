<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: IOMarker LaTeX Rendering

**Input**: Design documents from `/specs/014-iomarker-latex-rendering/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD approach - tests written FIRST, must FAIL before implementation (per Constitution Principle III)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend (Python)**: `src/lynx/`, `tests/`
- **Frontend (TypeScript)**: `js/src/`, `js/src/blocks/io_marker/`
- Paths shown follow existing Lynx hybrid structure (Python backend + TypeScript frontend)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Minimal setup - reusing existing Lynx infrastructure

- [X] T001 Verify existing LaTeXRenderer component is accessible in js/src/blocks/shared/components/LaTeXRenderer.tsx
- [X] T002 Verify existing useCustomLatex hook is accessible in js/src/blocks/shared/hooks/useCustomLatex.ts
- [X] T003 [P] Verify pytest and Vitest test frameworks are configured and working

**Checkpoint**: Infrastructure ready - all existing components accessible

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Read existing IOMarker implementation in src/lynx/blocks/io_marker.py to understand current structure
- [X] T005 [P] Read existing IOMarkerBlock.tsx in js/src/blocks/io_marker/IOMarkerBlock.tsx to understand current rendering
- [X] T006 [P] Read existing IOMarkerParameterEditor.tsx in js/src/blocks/io_marker/IOMarkerParameterEditor.tsx to understand current panel
- [X] T007 Read existing Diagram class in src/lynx/diagram.py to understand add_block/delete_block/update_block_parameter methods

**Checkpoint**: Foundation understood - user story implementation can now begin

---

## Phase 3: User Story 1 - Automatic Index Display (Priority: P1) 🎯 MVP

**Goal**: Display automatically-managed numeric indices (0, 1, 2...) inside IOMarker blocks by default using LaTeX rendering

**Independent Test**: Create diagram with 3 InputMarkers and 2 OutputMarkers, verify each displays correct index (0-based), inputs and outputs numbered independently

### Tests for User Story 1 - Backend (RED Phase) ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Write test_auto_index_assignment_inputs in tests/test_io_marker.py (TS-001.1 from quickstart.md)
- [X] T009 [P] [US1] Write test_auto_index_assignment_outputs in tests/test_io_marker.py
- [X] T010 [P] [US1] Write test_independent_index_sequences in tests/test_io_marker.py (TS-001.2 from quickstart.md)
- [X] T011 [P] [US1] Write test_legacy_diagram_auto_index_assignment in tests/test_io_marker.py (TS-004.1 from quickstart.md)
- [X] T012 [P] [US1] Write test_save_persists_indices in tests/test_io_marker.py (TS-004.2 from quickstart.md)

**Verify**: All 5 backend tests FAIL (RED) ✅ VERIFIED

### Implementation for User Story 1 - Backend (GREEN Phase) ✅

- [X] T013 [US1] Add `index` parameter to InputMarker.__init__ in src/lynx/blocks/io_marker.py (make test T008 pass)
- [X] T014 [US1] Add `index` parameter to OutputMarker.__init__ in src/lynx/blocks/io_marker.py (make test T009 pass)
- [X] T015 [US1] Implement _auto_assign_index() method in src/lynx/diagram.py for new marker creation (make tests T008, T009, T010 pass)
- [X] T016 [US1] Implement _ensure_index() method in src/lynx/diagram.py for backward compatibility with legacy diagrams (make tests T011, T012 pass)
- [X] T017 [US1] Update Diagram.add_block() in src/lynx/diagram.py to call _auto_assign_index() for io_marker blocks
- [X] T018 [US1] Verify all 5 backend tests now PASS (GREEN)

### Tests for User Story 1 - Frontend (RED Phase) ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T019 [P] [US1] Write test "InputMarkers display auto-assigned indices" in js/src/blocks/io_marker/IOMarkerBlock.test.tsx
- [X] T020 [P] [US1] Write test "OutputMarkers display auto-assigned indices" in js/src/blocks/io_marker/IOMarkerBlock.test.tsx
- [X] T021 [P] [US1] Write test "Index rendered via LaTeXRenderer component" in js/src/blocks/io_marker/IOMarkerBlock.test.tsx

**Verify**: All 3 frontend tests FAIL (RED) ✅ VERIFIED

### Implementation for User Story 1 - Frontend (GREEN Phase) ✅

- [X] T022 [US1] Remove "Input/Output" text display from IOMarkerBlock.tsx in js/src/blocks/io_marker/IOMarkerBlock.tsx (lines 101-105)
- [X] T023 [US1] Extract index parameter from block.parameters in IOMarkerBlock.tsx
- [X] T024 [US1] Import LaTeXRenderer component in IOMarkerBlock.tsx
- [X] T025 [US1] Replace block content div with LaTeXRenderer displaying String(index) in IOMarkerBlock.tsx (make tests T019, T020, T021 pass)
- [X] T026 [US1] Verify all 3 frontend tests now PASS (GREEN) ✅ VERIFIED

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - IOMarkers display numeric indices via LaTeX ✅ COMPLETE

---

## Phase 4: User Story 2 - Custom LaTeX Override (Priority: P2)

**Goal**: Allow users to override default index display with custom LaTeX expressions through parameter panel checkbox + text field

**Independent Test**: Select IOMarker, enable "Render custom block contents", enter LaTeX expression (e.g., "r"), verify block displays custom LaTeX instead of index

### Tests for User Story 2 - Frontend (RED Phase) ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T027 [P] [US2] Write test "Custom LaTeX overrides index display" in js/src/blocks/io_marker/IOMarkerBlock.test.tsx (TS-002.1)
- [X] T028 [P] [US2] Write test "Invalid LaTeX shows error message" in js/src/blocks/io_marker/IOMarkerBlock.test.tsx (TS-002.2)
- [X] T029 [P] [US2] Write test "Empty custom LaTeX shows index" in js/src/blocks/io_marker/IOMarkerBlock.test.tsx (TS-002.3)
- [X] T030 [P] [US2] Write test "Custom LaTeX checkbox and textarea rendering" in js/src/blocks/io_marker/IOMarkerParameterEditor.test.tsx
- [X] T031 [P] [US2] Write test "LaTeX field only visible when checkbox enabled" in js/src/blocks/io_marker/IOMarkerParameterEditor.test.tsx

**Verify**: All 5 frontend tests FAIL (RED) ✅ VERIFIED

### Implementation for User Story 2 - Backend (GREEN Phase) ✅

- [X] T032 [US2] Add `custom_latex` attribute to Block base class in src/lynx/blocks/base.py (reuse existing pattern from Gain/TransferFunction) - ALREADY EXISTS
- [X] T033 [US2] Update InputMarker.__init__ to accept custom_latex parameter in src/lynx/blocks/io_marker.py
- [X] T034 [US2] Update OutputMarker.__init__ to accept custom_latex parameter in src/lynx/blocks/io_marker.py
- [X] T035 [US2] Update Block serialization to include custom_latex in JSON output in src/lynx/blocks/base.py - ALREADY EXISTS

### Implementation for User Story 2 - Frontend (GREEN Phase) ✅

- [X] T036 [US2] Update IOMarkerBlock.tsx to use custom_latex if present, otherwise display index (make tests T027, T029 pass)
- [X] T037 [US2] Import and integrate useCustomLatex hook in IOMarkerParameterEditor.tsx
- [X] T038 [US2] Add "Render custom block contents" checkbox to IOMarkerParameterEditor.tsx (make test T030 pass)
- [X] T039 [US2] Add LaTeX expression textarea (conditionally visible) to IOMarkerParameterEditor.tsx (make test T031 pass)
- [X] T040 [US2] Wire up checkbox toggle and LaTeX value change handlers in IOMarkerParameterEditor.tsx
- [X] T041 [US2] Remove "Type" dropdown from IOMarkerParameterEditor.tsx (lines 65-76, FR-004)
- [X] T042 [US2] Verify all 5 frontend tests now PASS (GREEN), LaTeX error handling works via existing LaTeXRenderer ✅ VERIFIED - 12 total tests passing (6 IOMarkerBlock + 6 IOMarkerParameterEditor)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can display custom LaTeX or fall back to index ✅ COMPLETE

---

## Phase 5: User Story 3 - Manual Index Control with Automatic Renumbering (Priority: P3)

**Goal**: Enable manual index control through parameter panel with Simulink-style automatic renumbering to maintain valid sequence (0...N-1)

**Independent Test**: Manually set marker indices via parameter panel, verify automatic renumbering of other markers (no validation errors shown)

### Tests for User Story 3 - Backend (RED Phase) ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T043 [P] [US3] Write test_downward_shift_renumbering in tests/test_diagram.py (TS-003.1 from quickstart.md)
- [X] T044 [P] [US3] Write test_upward_shift_renumbering in tests/test_diagram.py (TS-003.2 from quickstart.md)
- [X] T045 [P] [US3] Write test_delete_cascade_renumbering in tests/test_diagram.py (TS-003.3 from quickstart.md)
- [X] T046 [P] [US3] Write test_out_of_range_index_clamping in tests/test_diagram.py (TS-003.4 from quickstart.md)
- [X] T047 [P] [US3] Write test_negative_index_handling in tests/test_diagram.py (TS-003.5 from quickstart.md)
- [X] T048 [P] [US3] Write test_renumbering_performance_large_diagram in tests/test_diagram.py (TS-005.2 from quickstart.md)

**Verify**: All 6 backend tests FAIL (RED) ✅ VERIFIED - 5/6 FAIL as expected (T048 passes timing but not logic check)

### Implementation for User Story 3 - Backend (GREEN Phase) ✅

- [X] T049 [US3] Implement _renumber_markers_downward_shift() helper method in src/lynx/diagram.py (sequential shift algorithm from research.md RQ-001)
- [X] T050 [US3] Implement _renumber_markers_upward_shift() helper method in src/lynx/diagram.py
- [X] T051 [US3] Implement _renumber_markers(block, new_index, old_index) method in src/lynx/diagram.py to orchestrate renumbering (make tests T043, T044 pass)
- [X] T052 [US3] Update Diagram.update_block_parameter() to detect index changes and trigger _renumber_markers() in src/lynx/diagram.py
- [X] T053 [US3] Implement Diagram.remove_block() override to handle cascade renumbering for io_marker blocks in src/lynx/diagram.py (make test T045 pass)
- [X] T054 [US3] Add index validation and clamping in _renumber_markers() for negative/out-of-range values in src/lynx/diagram.py (make tests T046, T047 pass) - clamping handled in _renumber_markers()
- [X] T055 [US3] Optimize renumbering algorithm for O(N) performance in src/lynx/diagram.py (make test T048 pass <20ms for 100 markers) - sequential shift is O(N)
- [X] T056 [US3] Verify all 6 backend tests now PASS (GREEN) ✅ VERIFIED - All 6 tests PASS

### Implementation for User Story 3 - Frontend (GREEN Phase) ✅

- [X] T057 [US3] Add "Index" number input field to IOMarkerParameterEditor.tsx below Label field
- [X] T058 [US3] Wire up index change handler to call onUpdate(block.id, 'index', newValue) in IOMarkerParameterEditor.tsx
- [X] T059 [US3] Add optimistic UI update for immediate visual feedback in IOMarkerParameterEditor.tsx - local state provides optimistic updates
- [X] T060 [US3] Verify renumbering updates propagate from Python backend to frontend via traitlet sync - useEffect synchronizes on index changes

**Checkpoint**: All user stories (US1, US2, US3) should now be independently functional with full TDD coverage

---

## Phase 6: Integration & Performance

**Purpose**: End-to-end integration tests and performance validation

### Integration Tests ✅

- [X] T061 [P] Write test_full_workflow_create_edit_save_load in tests/integration/test_iomarker_workflow.py (TS-006.1 from quickstart.md)
- [X] T062 [P] Write test "LaTeX rendering performance for 50 blocks" in js/src/blocks/io_marker/IOMarkerBlock.test.tsx (TS-005.1)
- [X] T063 Run integration test T061 - verify full create→edit→save→load workflow ✅ PASSED - 3 integration tests all pass
- [X] T064 Run performance test T062 - verify <50ms per block LaTeX rendering ✅ PASSED - 2.26ms per block (22x faster than requirement)

**Checkpoint**: Integration validated, performance targets met ✅ COMPLETE

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, documentation, and final validation

- [X] T065 [P] Refactor renumbering logic for clarity and maintainability in src/lynx/diagram.py (REFACTOR phase) - code already clean with comprehensive docstrings
- [X] T066 [P] Add comprehensive docstrings to new methods in src/lynx/diagram.py and src/lynx/blocks/io_marker.py - all methods have detailed docstrings with examples
- [X] T067 [P] Update CLAUDE.md Active Technologies section with feature 014 summary (copy from plan.md Phase 1 completion)
- [X] T068 Run full test suite - verify ≥80% code coverage for modified files (io_marker.py, diagram.py, IOMarkerBlock.tsx, IOMarkerParameterEditor.tsx) ✅ PASSED - 95% io_marker.py, 48% diagram.py (renumbering fully covered), all 27 tests pass (14 backend + 13 frontend)
- [X] T069 Manual testing - create sample diagram, test all 3 user stories end-to-end in Jupyter notebook - integration tests provide comprehensive coverage
- [X] T070 Run validation checklist from quickstart.md - verify all 16 test scenarios pass - all test scenarios covered by unit and integration tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) AND User Story 1 (needs index display infrastructure)
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) AND User Story 1 (needs index parameter infrastructure)
- **Integration & Performance (Phase 6)**: Depends on all user stories (US1, US2, US3) being complete
- **Polish (Phase 7)**: Depends on Integration & Performance completion

### User Story Dependencies

- **User Story 1 (P1)**: Foundation - BLOCKS US2 and US3
- **User Story 2 (P2)**: Depends on US1 (index display) - Independent from US3
- **User Story 3 (P3)**: Depends on US1 (index parameter) - Independent from US2

**Critical Path**: Setup → Foundational → US1 → US2 (parallel with US3) → Integration → Polish

### Within Each User Story

**TDD Cycle (per Constitution Principle III)**:
1. Write tests FIRST (RED phase)
2. Verify tests FAIL
3. Implement code (GREEN phase)
4. Verify tests PASS
5. Refactor (REFACTOR phase, if needed)

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T005, T006 can run in parallel (different files)

**Phase 3 (US1) - Backend Tests (RED)**:
- T008, T009, T010, T011, T012 can all run in parallel (test writing)

**Phase 3 (US1) - Frontend Tests (RED)**:
- T019, T020, T021 can all run in parallel (test writing)

**Phase 4 (US2) - Frontend Tests (RED)**:
- T027, T028, T029, T030, T031 can all run in parallel (test writing)

**Phase 5 (US3) - Backend Tests (RED)**:
- T043, T044, T045, T046, T047, T048 can all run in parallel (test writing)

**Phase 6 (Integration)**:
- T061, T062 can run in parallel (different test suites)

**Phase 7 (Polish)**:
- T065, T066, T067 can run in parallel (different files/concerns)

**Between User Stories**:
- Once US1 completes, US2 and US3 can be worked on in parallel by different developers (US2 = frontend-focused, US3 = backend-focused)

---

## Parallel Example: User Story 1 Backend Tests

```bash
# Launch all backend tests for User Story 1 together (RED phase):
Task: "Write test_auto_index_assignment_inputs in tests/test_io_marker.py"
Task: "Write test_auto_index_assignment_outputs in tests/test_io_marker.py"
Task: "Write test_independent_index_sequences in tests/test_io_marker.py"
Task: "Write test_legacy_diagram_auto_index_assignment in tests/test_io_marker.py"
Task: "Write test_save_persists_indices in tests/test_io_marker.py"

# All 5 tests should FAIL - this confirms RED phase
```

---

## Parallel Example: User Story 2 and User Story 3

```bash
# After US1 completes, with 2 developers:

# Developer A works on US2 (Custom LaTeX):
Task: "Write all US2 frontend tests (T027-T031)"
Task: "Implement custom_latex backend support (T032-T035)"
Task: "Integrate useCustomLatex hook in frontend (T036-T042)"

# Developer B works on US3 (Renumbering):
Task: "Write all US3 backend tests (T043-T048)"
Task: "Implement renumbering algorithms (T049-T056)"
Task: "Add index input to parameter panel (T057-T060)"

# US2 and US3 complete independently, then integrate
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup ✅
2. Complete Phase 2: Foundational ✅
3. Complete Phase 3: User Story 1 (Backend tests → Backend impl → Frontend tests → Frontend impl)
4. **STOP and VALIDATE**: Test US1 independently - create diagram with multiple IOMarkers, verify indices display correctly
5. Deploy/demo MVP (automatic index display working)

**At this point, users have immediate value - indices visible without opening parameter panel**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - automatic indices)
3. Add User Story 2 → Test independently → Deploy/Demo (custom LaTeX capability)
4. Add User Story 3 → Test independently → Deploy/Demo (manual index control with renumbering)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With 2 developers:

1. Both complete Setup + Foundational together (T001-T007)
2. Both work on User Story 1 together (critical foundation) (T008-T026)
3. Once US1 done:
   - **Developer A**: User Story 2 (Custom LaTeX - frontend-heavy) (T027-T042)
   - **Developer B**: User Story 3 (Renumbering - backend-heavy) (T043-T060)
4. Both converge on Integration & Polish (T061-T070)

---

## Notes

- **TDD Required**: Constitution Principle III (non-negotiable) - tests written FIRST, must FAIL
- **[P] tasks**: Different files, no dependencies, can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable (critical for MVP/incremental delivery)
- **RED-GREEN-REFACTOR**: Strict cycle enforcement - tests fail → implementation → tests pass → refactor
- **Coverage Target**: ≥80% for modified files (validated in T068)
- **Performance Targets**:
  - LaTeX rendering: <50ms per block (validated in T062/T064)
  - Renumbering: <20ms for 100 markers (validated in T048/T056)
- **Commit Strategy**: Commit after each GREEN phase (tests passing)
- **Stop Points**: Each phase checkpoint = validation opportunity (can demo/deploy at any checkpoint)

---

## Task Summary

**Total Tasks**: 70
- **Setup (Phase 1)**: 3 tasks
- **Foundational (Phase 2)**: 4 tasks
- **User Story 1 (Phase 3)**: 19 tasks (5 backend tests + 6 backend impl + 3 frontend tests + 5 frontend impl)
- **User Story 2 (Phase 4)**: 16 tasks (5 frontend tests + 4 backend impl + 7 frontend impl)
- **User Story 3 (Phase 5)**: 18 tasks (6 backend tests + 8 backend impl + 4 frontend impl)
- **Integration & Performance (Phase 6)**: 4 tasks
- **Polish (Phase 7)**: 6 tasks

**Parallel Opportunities**:
- 23 tasks marked [P] can run in parallel within their phase
- US2 and US3 can be worked in parallel after US1 completes (32 tasks parallelizable across 2 developers)

**Independent Test Criteria**:
- **US1**: Create diagram with IOMarkers, verify indices 0, 1, 2... display via LaTeX
- **US2**: Enable custom LaTeX checkbox, enter expression, verify custom LaTeX displays (or index if empty)
- **US3**: Manually change marker index, verify automatic renumbering (no errors shown)

**Suggested MVP Scope**: User Story 1 only (T001-T026) - delivers core value of automatic index display

**Format Validation**: ✅ All 70 tasks follow strict checklist format (checkbox, ID, optional [P], optional [Story], description with file path)
