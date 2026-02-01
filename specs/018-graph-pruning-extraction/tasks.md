<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Graph-Based Subsystem Extraction

**Input**: Design documents from `/specs/018-graph-pruning-extraction/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Following Constitution Principle III (TDD Non-Negotiable), ALL implementation tasks include tests that MUST be written first and FAIL before implementation begins.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure (Python package):
- Source: `src/lynx/conversion/`
- Tests: `tests/python/unit/` and `tests/python/integration/`

---

## Phase 1: Setup

**Purpose**: Project initialization and test infrastructure

- [X] T001 [P] Create new module `src/lynx/conversion/graph_pruning.py` with module docstring and license header
- [X] T002 [P] Create unit test file `tests/python/unit/test_graph_pruning.py` with test class structure
- [X] T003 [P] Create integration test file `tests/python/integration/test_pruned_extraction.py` with test class structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core graph analysis algorithms that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests (Write FIRST, ensure they FAIL)

- [X] T004 [P] Write failing test for `_build_connection_graph()` with simple 3-block diagram in `tests/python/unit/test_graph_pruning.py`
- [X] T005 [P] Write failing test for `_dfs_forward()` exploring downstream blocks in `tests/python/unit/test_graph_pruning.py`
- [X] T006 [P] Write failing test for `_dfs_backward()` exploring upstream blocks in `tests/python/unit/test_graph_pruning.py`
- [X] T007 [P] Write failing test for cycle handling in DFS (visited set protection) in `tests/python/unit/test_graph_pruning.py`
- [X] T008 [P] Write failing test for `_find_reachable_blocks()` computing intersection in `tests/python/unit/test_graph_pruning.py`

### Implementation (After tests FAIL)

- [X] T009 [P] Implement `_build_connection_graph()` to create forward/backward adjacency lists in `src/lynx/conversion/graph_pruning.py`
- [X] T010 [P] Implement `_dfs_forward()` with visited set tracking in `src/lynx/conversion/graph_pruning.py`
- [X] T011 [P] Implement `_dfs_backward()` with reverse edge traversal in `src/lynx/conversion/graph_pruning.py`
- [X] T012 Implement `_find_reachable_blocks()` using bidirectional DFS and intersection logic in `src/lynx/conversion/graph_pruning.py`

### Tests (Verify GREEN after implementation)

- [X] T013 Run foundational unit tests - verify all tests PASS after implementation

**Checkpoint**: Foundation ready - graph analysis algorithms tested and working. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Extract Single Block Transfer Function (Priority: P1) 🎯 MVP

**Goal**: Extract TF of a single controller block from complex diagram without downstream coupling

**Independent Test**: Create minimal diagram with feedforward path plus unrelated downstream feedback, extract single block TF, verify it matches isolated block's order/dynamics (SC-001, SC-003)

### Tests for US1 (Write FIRST, ensure they FAIL) ⚠️

- [X] T014 [P] [US1] Write failing integration test for Scenario 1 (quickstart.md) - single block extraction with downstream feedback in `tests/python/integration/test_pruned_extraction.py`
- [X] T015 [P] [US1] Write failing unit test for `prune_diagram()` removing unrelated blocks in `tests/python/unit/test_graph_pruning.py`
- [X] T016 [P] [US1] Write failing integration test for acceptance scenario 1a (A→B→C with B extraction) in `tests/python/integration/test_pruned_extraction.py`
- [X] T017 [P] [US1] Write failing integration test for acceptance scenario 1c (sum→controller extraction excluding downstream plant) in `tests/python/integration/test_pruned_extraction.py`

### Implementation for US1 (After tests FAIL)

- [X] T018 [US1] Implement `prune_diagram()` to clone and remove non-path blocks in `src/lynx/conversion/graph_pruning.py`
- [X] T019 [US1] Integrate pruning into `_prepare_for_extraction()` after signal resolution in `src/lynx/conversion/signal_extraction.py`
- [X] T020 [US1] Add validation for no-path-exists case (FR-007) with clear error message in `src/lynx/conversion/graph_pruning.py`
- [X] T021 [US1] Handle same-block extraction edge case (FR-008) in `src/lynx/conversion/graph_pruning.py`

### Validation for US1

- [X] T022 [US1] Run all US1 integration tests - verify extracted TF order matches isolated block (SC-001)
- [X] T023 [US1] Verify state count equals sum of path blocks only (SC-003) using quickstart.md Scenario 1
- [ ] T024 [US1] Test extraction completes in <500ms for 50-block diagram (SC-002) - create performance test in `tests/python/integration/test_pruned_extraction.py`

**Checkpoint**: User Story 1 should be fully functional - single block extraction works correctly without downstream coupling

---

## Phase 4: User Story 2 - Preserve Internal Feedback Loops (Priority: P2)

**Goal**: Extract multi-block subsystems with internal feedback while excluding external loops

**Independent Test**: Create diagram with inner loop (controller+plant+feedback) and outer cascade controller. Extract inner loop subsystem - should include both blocks and their feedback, exclude outer controller (quickstart.md Scenario 2)

### Tests for US2 (Write FIRST, ensure they FAIL) ⚠️

- [X] T025 [P] [US2] Write failing integration test for Scenario 2 (quickstart.md) - inner loop with external cascade in `tests/python/integration/test_pruned_extraction.py`
- [X] T026 [P] [US2] Write failing integration test for acceptance scenario 2a (inner+outer loop extraction) in `tests/python/integration/test_pruned_extraction.py`
- [X] T027 [P] [US2] Write failing unit test verifying internal feedback blocks are in both forward AND backward reachable sets in `tests/python/unit/test_graph_pruning.py`
- [X] T028 [P] [US2] Write failing integration test for acceptance scenario 2b (multi-rate fast/slow loop boundary) in `tests/python/integration/test_pruned_extraction.py`

### Implementation for US2 (After tests FAIL)

- [X] T029 [US2] Verify bidirectional reachability correctly identifies internal feedback (blocks reachable both ways stay in intersection) - no code changes needed if foundational phase correct
- [X] T030 [US2] Add validation that feedback connections between pruned blocks are preserved in `src/lynx/conversion/graph_pruning.py`
- [X] T031 [US2] Test and verify removal of feedback connections involving blocks outside path in `src/lynx/conversion/graph_pruning.py`

### Validation for US2

- [X] T032 [US2] Run all US2 integration tests - verify inner loop TF includes internal feedback (DC gain calculation)
- [X] T033 [US2] Verify external feedback blocks excluded (state count validation) using quickstart.md Scenario 2
- [X] T034 [US2] Validate that US1 tests still pass (backward compatibility check - SC-004)

**Checkpoint**: User Stories 1 AND 2 should both work independently - can extract single blocks AND multi-block subsystems with internal feedback

---

## Phase 5: User Story 3 - Handle Complex Path Topologies (Priority: P3)

**Goal**: Extract subsystems with parallel paths (feedforward + feedback) while excluding unrelated branches

**Independent Test**: Create diagram with parallel feedforward and feedback paths between two points, plus unrelated side branch. Extraction should include both paths, exclude side branch (quickstart.md Scenario 3)

### Tests for US3 (Write FIRST, ensure they FAIL) ⚠️

- [X] T035 [P] [US3] Write failing integration test for Scenario 3 (quickstart.md) - parallel paths with side branch in `tests/python/integration/test_pruned_extraction.py`
- [X] T036 [P] [US3] Write failing integration test for acceptance scenario 3a (feedforward + feedback loop, exclude unrelated branch D) in `tests/python/integration/test_pruned_extraction.py`
- [X] T037 [P] [US3] Write failing unit test verifying parallel paths both appear in intersection (blocks on either path included) in `tests/python/unit/test_graph_pruning.py`
- [X] T038 [P] [US3] Write failing integration test for acceptance scenario 3b (MIMO cross-coupling) in `tests/python/integration/test_pruned_extraction.py`

### Implementation for US3 (After tests FAIL)

- [X] T039 [US3] Verify bidirectional reachability captures all parallel paths (union of forward paths in intersection) - no code changes needed if foundational phase correct
- [X] T040 [US3] Test edge case: blocks with multiple outputs where only one output is on path (FR-009) in `src/lynx/conversion/graph_pruning.py`
- [X] T041 [US3] Add validation for disconnected paths edge case (FR-007) in `src/lynx/conversion/graph_pruning.py`

### Validation for US3

- [X] T042 [US3] Run all US3 integration tests - verify DC gain includes all parallel paths (SC-006)
- [X] T043 [US3] Verify side branches excluded from extraction (state count check) using quickstart.md Scenario 3
- [X] T044 [US3] Validate that US1 and US2 tests still pass (backward compatibility - SC-004)

**Checkpoint**: All user stories should now be independently functional - handles single blocks, internal feedback, AND parallel paths

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, performance optimization, and documentation

### Edge Case Handling

- [ ] T045 [P] Write failing test for edge case: source and destination in same block (extract block input→output) in `tests/python/unit/test_graph_pruning.py`
- [ ] T046 [P] Write failing test for edge case: no path exists between source and destination (should raise SignalNotFoundError) in `tests/python/integration/test_pruned_extraction.py`
- [ ] T047 [P] Write failing test for edge case: algebraic loop within pruned subsystem (should propagate validation error) in `tests/python/integration/test_pruned_extraction.py`
- [ ] T048 Implement same-block edge case handling if not already covered by T021 in `src/lynx/conversion/graph_pruning.py`
- [ ] T049 Implement no-path-exists validation if not already covered by T020 in `src/lynx/conversion/graph_pruning.py`

### Performance & Optimization

- [ ] T050 [P] Add performance benchmark test for 100-block diagram (<1s per SC-002) in `tests/python/integration/test_pruned_extraction.py`
- [ ] T051 Profile graph analysis for 500-block diagram edge case (graceful degradation check) in `tests/python/integration/test_pruned_extraction.py`
- [ ] T052 Optimize DFS if needed based on profiling results (visited set implementation, early termination) in `src/lynx/conversion/graph_pruning.py`

### Documentation & Validation

- [ ] T053 [P] Add module-level docstring with algorithm explanation and complexity analysis to `src/lynx/conversion/graph_pruning.py`
- [ ] T054 [P] Add function docstrings with type hints to all public functions in `src/lynx/conversion/graph_pruning.py`
- [ ] T055 [P] Update `src/lynx/conversion/__init__.py` to export new pruning functions if needed
- [ ] T056 Run full test suite - verify SC-004 (all existing extraction tests still pass)
- [ ] T057 Run quickstart.md validation for all three scenarios (manual verification of expected behavior)
- [ ] T058 Commit the cascaded.json fix validation - verify `diagram.get_tf("rate_err", "tau_cmd")` now returns 2nd-order PID

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) OR sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - No dependencies on US1 (independently testable)
- **User Story 3 (P3)**: Can start after Foundational - No dependencies on US1/US2 (independently testable)

### Within Each User Story (TDD Workflow)

1. **RED**: Write ALL tests for the story - verify they FAIL
2. **GREEN**: Implement minimal code to make tests PASS
3. **REFACTOR**: Clean up implementation while keeping tests GREEN
4. Story complete - validate independently before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: All 3 tasks [P] can run in parallel
- **Foundational Tests (Phase 2)**: T004-T008 can run in parallel (5 test files)
- **Foundational Implementation (Phase 2)**: T009-T011 can run in parallel (3 functions)
- **Once Foundational completes**: US1, US2, US3 can start in parallel (different team members)
- **US1 Tests**: T014-T017 can run in parallel (4 test scenarios)
- **US2 Tests**: T025-T028 can run in parallel (4 test scenarios)
- **US3 Tests**: T035-T038 can run in parallel (4 test scenarios)
- **Polish**: T045-T047 (edge case tests), T050-T051 (performance tests), T053-T055 (docs) can run in parallel

---

## Parallel Example: User Story 1 (TDD Cycle)

**RED Phase** (write tests first, verify FAIL):
```bash
# Launch all US1 tests in parallel:
Task T014: "Write failing integration test for Scenario 1..."
Task T015: "Write failing unit test for prune_diagram..."
Task T016: "Write failing integration test for acceptance 1a..."
Task T017: "Write failing integration test for acceptance 1c..."

# Run tests - should all FAIL (no implementation yet)
uv run pytest tests/python/integration/test_pruned_extraction.py::TestUS1 -v
# Expected: FAIL FAIL FAIL FAIL
```

**GREEN Phase** (implement to make tests PASS):
```bash
# Implement in sequence (dependencies matter here):
Task T018: prune_diagram()
Task T019: integrate into _prepare_for_extraction()
Task T020: validation for no-path case
Task T021: same-block edge case

# Run tests - should all PASS
uv run pytest tests/python/integration/test_pruned_extraction.py::TestUS1 -v
# Expected: PASS PASS PASS PASS
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Recommended Initial Deployment

1. ✅ Complete Phase 1: Setup (T001-T003)
2. ✅ Complete Phase 2: Foundational (T004-T013) - CRITICAL: blocks all stories
3. ✅ Complete Phase 3: User Story 1 (T014-T024)
4. **STOP and VALIDATE**: Test US1 independently using quickstart.md Scenario 1
5. **Commit and Deploy** if ready - fixes the core bug for single-block extraction

### Incremental Delivery (Full Feature)

1. Complete Setup + Foundational → Foundation ready (T001-T013)
2. Add User Story 1 → Test independently → Commit (T014-T024) **← MVP!**
3. Add User Story 2 → Test independently → Commit (T025-T034)
4. Add User Story 3 → Test independently → Commit (T035-T044)
5. Add Polish → Final validation → Commit (T045-T058)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T014-T024) - Core value, highest priority
   - **Developer B**: User Story 2 (T025-T034) - Feedback preservation
   - **Developer C**: User Story 3 (T035-T044) - Parallel paths
3. Stories integrate independently, tested separately

---

## Task Statistics

**Total Tasks**: 58
- **Phase 1 (Setup)**: 3 tasks (5%)
- **Phase 2 (Foundational)**: 10 tasks (17%) - BLOCKING
- **Phase 3 (US1 - MVP)**: 11 tasks (19%)
- **Phase 4 (US2)**: 10 tasks (17%)
- **Phase 5 (US3)**: 10 tasks (17%)
- **Phase 6 (Polish)**: 14 tasks (24%)

**Tasks by Story**:
- US1 (P1): 11 tasks - single block extraction
- US2 (P2): 10 tasks - internal feedback preservation
- US3 (P3): 10 tasks - parallel paths handling
- Infrastructure: 27 tasks (setup + foundational + polish)

**Parallel Opportunities**: 26 tasks marked [P] (45% can run in parallel within phases)

**Independent Testing**: Each user story has 4-5 dedicated integration tests covering acceptance scenarios from spec.md

**Suggested MVP**: Phase 1-3 only (24 tasks, ~40% of total) - delivers core value of fixing single-block extraction bug

---

## Notes

- All tasks follow TDD: Write test → Verify FAIL → Implement → Verify PASS → Refactor
- [P] tasks = different files OR no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable per quickstart.md scenarios
- Commit after GREEN phase of each TDD cycle
- Stop at any checkpoint to validate story independently
- SC-001 to SC-006 map to Success Criteria from spec.md
- FR-001 to FR-012 map to Functional Requirements from spec.md
