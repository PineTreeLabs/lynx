<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Block Resizing

**Input**: Design documents from `/specs/007-block-resizing/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Included as per Constitution Principle III (Test-Driven Development)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/lynx/` (Python)
- **Frontend**: `js/src/` (TypeScript/React)
- **Backend Tests**: `tests/lynx/`
- **Frontend Tests**: `js/src/test/` or co-located `.test.tsx` files

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dimension attributes to Python Block classes and Pydantic schema

- [x] T001 [P] Add width and height attributes to Block base class in src/lynx/blocks/base.py
- [x] T002 [P] Add width and height fields to BaseBlockModel schema in src/lynx/schema.py
- [x] T003 [P] Define BLOCK_DEFAULTS constants (default/min dimensions) in js/src/utils/blockDefaults.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend dimension persistence and widget communication

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add update_block_dimensions() method to Diagram class in src/lynx/diagram.py
- [x] T005 Add dimension update handler to widget in src/lynx/widget.py
- [x] T006 Update to_dict() in Block base class to include width/height in src/lynx/blocks/base.py
- [x] T007 [P] Write test for dimension persistence in tests/python/unit/test_block_dimensions.py

**Checkpoint**: Foundation ready - block dimensions can be stored and synced

---

## Phase 3: User Story 1 - Resize Block via Corner Handles (Priority: P1) 🎯 MVP

**Goal**: Users can select a block and drag corner handles to resize it. Dimensions persist to Python.

**Independent Test**: Select any block, drag a corner handle, verify block resizes and size persists after deselect/reselect.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Write resize geometry tests (anchor corner, aspect ratio lock) in js/src/hooks/useBlockResize.test.ts
- [x] T009 [P] [US1] Write handle visibility tests (selected state) in js/src/components/ResizeHandle.test.tsx

### Implementation for User Story 1

- [x] T010 [P] [US1] Create useBlockResize hook with resize logic in js/src/hooks/useBlockResize.ts
- [x] T011 [P] [US1] Create ResizeHandles component (4 corner handles) in js/src/components/ResizeHandles.tsx
- [x] T012 [US1] Update GainBlock to accept width/height props and add NodeResizer in js/src/blocks/GainBlock.tsx
- [x] T013 [US1] Update SumBlock to accept width/height props and add NodeResizer in js/src/blocks/SumBlock.tsx
- [x] T014 [US1] Update TransferFunctionBlock to accept width/height props and add NodeResizer in js/src/blocks/TransferFunctionBlock.tsx
- [x] T015 [US1] Update StateSpaceBlock to accept width/height props and add NodeResizer in js/src/blocks/StateSpaceBlock.tsx
- [x] T016 [US1] Update IOMarkerBlock to accept width/height props and add NodeResizer in js/src/blocks/IOMarkerBlock.tsx
- [x] T017 [US1] Add resize callback to DiagramCanvas to sync dimensions to Python in js/src/DiagramCanvas.tsx
- [ ] ~~T018 [US1] Implement Shift+drag aspect ratio lock in resize callback in js/src/hooks/useBlockResize.ts~~ (REMOVED - NodeResizer limitations)

**Checkpoint**: Blocks can be resized via corner handles, dimensions persist to Python

---

## Phase 4: User Story 2 - SVG Block Shape Scaling (Priority: P2)

**Goal**: Gain triangle and Sum circle/ellipse scale smoothly to fit new dimensions.

**Independent Test**: Resize Gain block to non-square ratio, verify triangle fills bounding box. Resize Sum block to ellipse.

### Tests for User Story 2 ⚠️

- [ ] T019 [P] [US2] Write SVG scaling tests for GainBlock in js/src/blocks/GainBlock.test.tsx
- [ ] T020 [P] [US2] Write SVG scaling tests for SumBlock (ellipse, X lines) in js/src/blocks/SumBlock.test.tsx

### Implementation for User Story 2

- [x] T021 [US2] Update GainBlock SVG polygon to use dynamic width/height in js/src/blocks/GainBlock.tsx
- [x] T022 [US2] Update SumBlock SVG to render ellipse (rx/ry) instead of fixed circle in js/src/blocks/SumBlock.tsx
- [x] T023 [US2] Update SumBlock X lines to scale proportionally within ellipse in js/src/blocks/SumBlock.tsx

**Checkpoint**: SVG blocks scale correctly with any dimensions

---

## Phase 5: User Story 3 - Block Content Preserves Font Size and Alignment (Priority: P2)

**Goal**: Text and LaTeX content maintains font size and alignment during resize. Sum +/- symbols stay near ports.

**Independent Test**: Resize TransferFunction block with equation, verify LaTeX same font size. Resize Sum, verify +/- near ports.

### Implementation for User Story 3

- [x] T024 [US3] Ensure LaTeX foreignObject uses fixed font size in GainBlock in js/src/blocks/GainBlock.tsx
- [x] T025 [US3] Ensure LaTeX foreignObject centered in resized TransferFunctionBlock in js/src/blocks/TransferFunctionBlock.tsx
- [x] T026 [US3] Ensure LaTeX foreignObject centered in resized StateSpaceBlock in js/src/blocks/StateSpaceBlock.tsx
- [x] T027 [US3] Update SumBlock +/- symbol positions to use relative coordinates based on port angles in js/src/blocks/SumBlock.tsx

**Checkpoint**: Block content remains readable and properly aligned at any size

---

## Phase 6: User Story 4 - Connection Auto-Routing on Resize (Priority: P3)

**Goal**: Connections automatically re-route when block is resized (ports move).

**Independent Test**: Create connected blocks, resize one, verify connections update to new port positions.

### Implementation for User Story 4

- [x] T028 [US4] Call _clear_waypoints_for_block() in update_block_dimensions() in src/lynx/diagram.py
- [x] T029 [US4] Call useUpdateNodeInternals() after resize to update handle positions in js/src/hooks/useBlockResize.ts
- [x] T030 [US4] Verify real-time connection updates during resize drag in js/src/DiagramCanvas.tsx

**Checkpoint**: Connections auto-route correctly during and after resize

---

## Phase 7: User Story 5 - Block Position Stability During Resize (Priority: P3)

**Goal**: Opposite corner stays fixed during resize. No collinearity snapping.

**Independent Test**: Resize block while noting anchor corner coordinates, verify it stays pixel-perfect.

### Implementation for User Story 5

- [x] T031 [US5] Ensure anchor corner calculation is correct in resize logic in js/src/hooks/useBlockResize.ts
- [x] T032 [US5] Disable any snapping behavior during resize operations in js/src/DiagramCanvas.tsx
- [x] T033 [US5] Write test for position stability during resize in js/src/hooks/useBlockResize.test.ts

**Checkpoint**: Block position is stable during resize, no unwanted snapping

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Minimum size enforcement, flipped block handling, edge cases

- [x] T034 [P] Enforce minimum size constraints in NodeResizer props per block type in js/src/blocks/*.tsx
- [x] T035 [P] Ensure resize handles appear at visual corners for flipped blocks in js/src/blocks/*.tsx
- [ ] T036 Run quickstart.md validation scenarios manually
- [x] T037 Update CLAUDE.md with block resizing component documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): Core resize - must complete first
  - US2 (P2): SVG scaling - depends on US1
  - US3 (P2): Content preservation - depends on US1, can parallel with US2
  - US4 (P3): Auto-routing - depends on US1
  - US5 (P3): Position stability - depends on US1
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Core resize functionality - all other stories depend on this
- **User Story 2 (P2)**: SVG scaling - depends on US1 for block dimension props
- **User Story 3 (P2)**: Content preservation - depends on US1, can parallel with US2
- **User Story 4 (P3)**: Auto-routing - depends on US1 for dimension updates
- **User Story 5 (P3)**: Position stability - depends on US1 for resize mechanics

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Hook/utility code before component integration
- Block components in parallel once hook is ready
- DiagramCanvas integration after block components

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks [P] - can run in parallel
```bash
Task: T001 "Add width/height to Block base class"
Task: T002 "Add width/height to BaseBlockModel schema"
Task: T003 "Define BLOCK_DEFAULTS constants"
```

**Phase 3 (US1)**: Tests in parallel, then block updates in parallel
```bash
# Tests first (parallel):
Task: T008 "Write resize geometry tests"
Task: T009 "Write handle visibility tests"

# Then implementation (parallel components):
Task: T012 "Update GainBlock"
Task: T013 "Update SumBlock"
Task: T014 "Update TransferFunctionBlock"
Task: T015 "Update StateSpaceBlock"
Task: T016 "Update IOMarkerBlock"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test resize on all block types
5. Demo if ready - basic resize functionality works

### Incremental Delivery

1. Setup + Foundational → Dimension persistence ready
2. Add User Story 1 → Basic resize works → Demo (MVP!)
3. Add User Story 2 → SVG scaling polished → Demo
4. Add User Story 3 → Content preserved → Demo
5. Add User Stories 4+5 → Full feature complete

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (must complete first for others to build on)
3. After US1 complete:
   - Developer A: User Story 4 (auto-routing)
   - Developer B: User Stories 2+3 (SVG + content)
   - Developer C: User Story 5 (position stability)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- User Story 1 is the core MVP - all other stories build on it
- Test-first per Constitution Principle III
- Commit after each task or logical group
- NodeResizer from React Flow 11.11.4 is used (per research.md decision)
- Python is source of truth for dimensions (per spec requirement)
