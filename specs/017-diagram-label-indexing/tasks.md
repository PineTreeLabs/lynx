---
# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

description: "Task list for diagram label indexing feature"
---

# Tasks: Diagram Label Indexing

**Input**: Design documents from `/specs/017-diagram-label-indexing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD workflow is mandatory per constitution. Tests MUST be written first and FAIL before implementation begins (RED-GREEN-REFACTOR cycle).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single Python library project:
- **Source**: `src/lynx/` at repository root
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (No Changes Required)

**Purpose**: Project infrastructure already exists

**Status**: ✅ Complete - This is an API enhancement to existing codebase. No setup tasks required.

---

## Phase 2: Foundational (No Changes Required)

**Purpose**: Core infrastructure that blocks all user stories

**Status**: ✅ Complete - All required infrastructure exists:
- Diagram class with update_block_parameter method
- Block base class with label attribute
- Pydantic schemas for serialization
- pytest testing framework
- ValidationError exception hierarchy

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Access Block by Label (Priority: P1) 🎯 MVP

**Goal**: Engineers can access blocks using bracket notation with labels (e.g., `diagram["plant"]`) instead of tracking block IDs

**Independent Test**: Create diagram with labeled blocks, index by label, verify correct block returned. Works independently without US2 or US3.

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL)

> **RED Phase**: Write failing tests BEFORE implementing __getitem__

- [ ] T001 [P] [US1] Test TypeError for integer key in tests/test_diagram.py
- [ ] T002 [P] [US1] Test TypeError for None key in tests/test_diagram.py
- [ ] T003 [P] [US1] Test TypeError for object key in tests/test_diagram.py
- [ ] T004 [P] [US1] Test KeyError for missing label in tests/test_diagram.py
- [ ] T005 [P] [US1] Test KeyError for empty diagram in tests/test_diagram.py
- [ ] T006 [P] [US1] Test KeyError for empty string label in tests/test_diagram.py
- [ ] T007 [P] [US1] Test successful retrieval with unique label in tests/test_diagram.py
- [ ] T008 [P] [US1] Test unlabeled blocks (None) are skipped in tests/test_diagram.py
- [ ] T009 [P] [US1] Test case-sensitive matching ("Plant" vs "plant") in tests/test_diagram.py
- [ ] T010 [P] [US1] Test special characters in labels in tests/test_diagram.py

### Implementation for User Story 1

> **GREEN Phase**: Implement __getitem__ to make tests pass

- [ ] T011 [US1] Implement Diagram.__getitem__ method with type validation in src/lynx/diagram.py
- [ ] T012 [US1] Add label matching logic (case-sensitive, skip unlabeled blocks) in src/lynx/diagram.py
- [ ] T013 [US1] Add error messages with requested label for KeyError in src/lynx/diagram.py
- [ ] T014 [US1] Run tests and verify all US1 tests pass

> **REFACTOR Phase**: Improve implementation if needed (optional)

- [ ] T015 [US1] Refactor __getitem__ for readability if needed in src/lynx/diagram.py

**Checkpoint**: Label indexing works for unique labels. Can retrieve blocks via diagram["label"].

---

## Phase 4: User Story 2 - Prevent Ambiguous Access (Priority: P2)

**Goal**: Detect duplicate labels and raise explicit ValidationError with count and block IDs, preventing silent bugs

**Independent Test**: Create diagram with duplicate labels, attempt indexing, verify ValidationError raised with correct info. Works independently of US1 (US1 must be complete first).

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL)

> **RED Phase**: Write failing tests BEFORE implementing duplicate detection

- [ ] T016 [P] [US2] Test ValidationError for 2 duplicate labels with count and IDs in tests/test_diagram.py
- [ ] T017 [P] [US2] Test ValidationError for 3+ duplicate labels in tests/test_diagram.py
- [ ] T018 [P] [US2] Test unique label succeeds when duplicates exist elsewhere in tests/test_diagram.py

### Implementation for User Story 2

> **GREEN Phase**: Enhance __getitem__ to detect duplicates

- [ ] T019 [US2] Add duplicate label detection to Diagram.__getitem__ in src/lynx/diagram.py
- [ ] T020 [US2] Raise ValidationError with label, count, and block IDs for duplicates in src/lynx/diagram.py
- [ ] T021 [US2] Run tests and verify all US2 tests pass

> **REFACTOR Phase**: Improve implementation if needed (optional)

- [ ] T022 [US2] Refactor duplicate detection logic for clarity if needed in src/lynx/diagram.py

**Checkpoint**: Duplicate label detection works. diagram["label"] raises ValidationError with actionable info for duplicates.

---

## Phase 5: User Story 3 - Update Parameters via Block Objects (Priority: P3)

**Goal**: Engineers can update block parameters naturally using block.set_parameter() or diagram.update_block_parameter(block, ...) without accessing internal IDs

**Independent Test**: Get block via label, call set_parameter(), verify parameter updated and synced. Works independently but builds on US1.

### Tests for User Story 3 (TDD - Write FIRST, ensure FAIL)

> **RED Phase**: Write failing tests BEFORE implementing parent references

- [ ] T023 [P] [US3] Test Block.set_parameter() syncs to diagram in tests/test_diagram.py or tests/test_blocks.py
- [ ] T024 [P] [US3] Test RuntimeError when block not attached to diagram in tests/test_blocks.py
- [ ] T025 [P] [US3] Test RuntimeError when parent diagram deleted in tests/test_blocks.py
- [ ] T026 [P] [US3] Test update_block_parameter accepts Block objects in tests/test_diagram.py
- [ ] T027 [P] [US3] Test update_block_parameter still accepts string IDs (backward compat) in tests/test_diagram.py
- [ ] T028 [P] [US3] Test serialization excludes _diagram attribute in tests/test_blocks.py

### Implementation for User Story 3

> **GREEN Phase**: Implement parent references and parameter update methods

- [ ] T029 [P] [US3] Add _diagram weakref attribute to Block base class in src/lynx/blocks/base.py
- [ ] T030 [P] [US3] Implement Block.set_parameter() method with delegation in src/lynx/blocks/base.py
- [ ] T031 [US3] Update Diagram.add_block() to set block._diagram weakref in src/lynx/diagram.py
- [ ] T032 [US3] Enhance Diagram.update_block_parameter() to accept Union[Block, str] in src/lynx/diagram.py
- [ ] T033 [US3] Verify _diagram excluded from Block.to_dict() serialization in src/lynx/blocks/base.py
- [ ] T034 [US3] Run tests and verify all US3 tests pass

> **REFACTOR Phase**: Improve implementation if needed (optional)

- [ ] T035 [US3] Refactor weakref handling for clarity if needed in src/lynx/blocks/base.py

**Checkpoint**: Parameter updates work naturally. Engineers can use block.set_parameter() or diagram.update_block_parameter(block, ...).

---

## Phase 6: Integration & Validation

**Purpose**: Verify all three user stories work together and validate against quickstart.md

- [ ] T036 [P] Integration test: label indexing → parameter update → widget sync in tests/test_diagram.py
- [ ] T037 [P] Integration test: label indexing with python-control export in tests/test_diagram.py
- [ ] T038 Run all scenarios from quickstart.md and verify results
- [ ] T039 Verify performance: 1000 blocks label lookup <10ms per quickstart.md

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final cleanup

- [ ] T040 [P] Update Diagram class docstring with label indexing examples in src/lynx/diagram.py
- [ ] T041 [P] Update Block class docstring with set_parameter() examples in src/lynx/blocks/base.py
- [ ] T042 Run full test suite (407 Python tests) and verify all pass
- [ ] T043 Run type checker (mypy) and verify no new type errors
- [ ] T044 Run linter (ruff) and verify no new lint errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ Complete (no changes needed)
- **Foundational (Phase 2)**: ✅ Complete (existing infrastructure)
- **User Stories (Phase 3-5)**: Each builds on previous priority
  - **US1 (P1)**: Independent, can start immediately
  - **US2 (P2)**: Enhances US1 (duplicate detection), must complete US1 first
  - **US3 (P3)**: Uses US1 (label indexing for retrieval), must complete US1 first
- **Integration (Phase 6)**: Depends on all user stories
- **Polish (Phase 7)**: Depends on integration validation

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - Core label indexing
- **User Story 2 (P2)**: Depends on US1 complete - Enhances __getitem__ with duplicate detection
- **User Story 3 (P3)**: Depends on US1 complete - Uses label indexing for parameter updates (but US2 not required)

### Within Each User Story (TDD Workflow)

1. **RED**: Write all tests for story, verify they FAIL
2. **GREEN**: Implement feature to make tests pass
3. **REFACTOR**: Improve implementation (optional)
4. **VALIDATE**: Run story's independent test criteria

### Parallel Opportunities

- **Within US1 Tests**: All 10 test tasks (T001-T010) can run in parallel
- **Within US2 Tests**: All 3 test tasks (T016-T018) can run in parallel
- **Within US3 Tests**: All 6 test tasks (T023-T028) can run in parallel
- **Within US3 Implementation**: T029 and T030 (Block class changes) can run in parallel with T032 (Diagram enhancement)
- **Integration Tests**: T036 and T037 can run in parallel
- **Polish Tasks**: T040, T041, T042, T043, T044 can all run in parallel

---

## Parallel Example: User Story 1

```bash
# RED Phase - Launch all US1 tests together:
Task T001: "Test TypeError for integer key in tests/test_diagram.py"
Task T002: "Test TypeError for None key in tests/test_diagram.py"
Task T003: "Test TypeError for object key in tests/test_diagram.py"
Task T004: "Test KeyError for missing label in tests/test_diagram.py"
Task T005: "Test KeyError for empty diagram in tests/test_diagram.py"
Task T006: "Test KeyError for empty string label in tests/test_diagram.py"
Task T007: "Test successful retrieval with unique label in tests/test_diagram.py"
Task T008: "Test unlabeled blocks (None) are skipped in tests/test_diagram.py"
Task T009: "Test case-sensitive matching in tests/test_diagram.py"
Task T010: "Test special characters in labels in tests/test_diagram.py"

# Verify all tests FAIL

# GREEN Phase - Sequential implementation:
Task T011: "Implement Diagram.__getitem__ method"
Task T012: "Add label matching logic"
Task T013: "Add error messages with requested label"
Task T014: "Run tests and verify all pass"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Phase 1: Setup (already complete)
2. ✅ Phase 2: Foundational (already complete)
3. Complete Phase 3: User Story 1 (Label Indexing)
   - Write 10 tests (T001-T010) - verify FAIL
   - Implement __getitem__ (T011-T013)
   - Run tests - verify PASS (T014)
4. **STOP and VALIDATE**: Test label indexing independently
5. Can ship MVP at this point (basic label indexing works)

### Incremental Delivery

1. **MVP** (US1): Label indexing works for unique labels
   - Value: Engineers can use `diagram["plant"]` instead of tracking IDs
   - Test: Create diagram, access by label, verify correct block
2. **+Duplicate Detection** (US1+US2): Add ValidationError for duplicates
   - Value: Prevents silent bugs from ambiguous labels
   - Test: Create duplicates, verify ValidationError with IDs
3. **+Natural Parameter Updates** (US1+US2+US3): Add block.set_parameter()
   - Value: Natural OOP-style parameter updates
   - Test: Get block by label, update parameter, verify sync

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 2-3 developers:

1. **Together**: Validate Phase 1 & 2 (already complete)
2. **Developer A**: User Story 1 (T001-T015)
   - Write tests → Implement __getitem__ → Validate
3. **Developer B** (starts after US1 complete): User Story 2 (T016-T022)
   - Write tests → Add duplicate detection → Validate
4. **Developer C** (starts after US1 complete): User Story 3 (T023-T035)
   - Write tests → Add parent references + set_parameter → Validate
5. **Together**: Integration & Polish (T036-T044)

---

## Notes

- **TDD is mandatory** per Lynx constitution - tests written FIRST, verify FAIL, then implement
- **[P] tasks** = different files or independent test cases, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story is independently testable per spec.md acceptance criteria
- Verify tests fail (RED) before implementing (GREEN)
- Refactor (REFACTOR) only if needed after tests pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total: 44 tasks (10 tests US1, 3 tests US2, 6 tests US3, 5 impl US1, 3 impl US2, 7 impl US3, 4 integration, 5 polish)
