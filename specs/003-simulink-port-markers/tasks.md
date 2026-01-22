<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Simulink-Style Port Markers

**Input**: Design documents from `/specs/003-simulink-port-markers/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/PortMarker.yaml, quickstart.md

**Tests**: TDD workflow applies - tests must be written FIRST and FAIL before implementation (Principle III)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

---

## 🎯 Current Status: Core Feature Complete (Phase 1-5)

**Completed Phases**:
- ✅ **Phase 1**: Setup - Development environment verified
- ✅ **Phase 2**: Foundation - Core utilities and hooks implemented
- ✅ **Phase 3**: User Story 1 (P1 - MVP) - Visual port markers on unconnected ports
- ✅ **Phase 4**: User Story 2 (P2) - Connection state visibility (hide when connected)
- ✅ **Phase 5**: User Story 3 (P3) - Horizontal flip orientation support

**Remaining Phases**:
- ❌ **Phase 6**: SKIPPED - Drag-and-drop hover behavior (unnecessary complexity, current behavior is acceptable)
- ✅ **Phase 7**: COMPLETE (automated tasks) - Manual testing remains for user validation

**Test Coverage**: 22 PortMarker tests passing, 10 geometry tests passing

**What Works**:
- Triangular arrowhead markers (two lines, no base) on all block types
- Markers hide when ports are connected, show when disconnected
- Correct orientation for inputs (tip at border) vs outputs (base at border)
- Proper behavior when blocks are flipped horizontally
- Port position swapping when blocks flip
- Sum block port regeneration when signs parameter changes
- Connection cleanup when ports are removed

**Key Files Modified**:
- `js/src/components/PortMarker.tsx` - Core marker component
- `js/src/utils/portMarkerGeometry.ts` - Triangle geometry calculations
- `js/src/hooks/usePortMarkerVisibility.ts` - Connection state detection
- `js/src/blocks/*.tsx` - All 5 block types integrated
- `src/lynx/diagram.py` - Backend port regeneration and cleanup

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend TypeScript/React: `js/src/`
- Frontend tests: `js/src/` (co-located with implementation)
- Backend Python: `src/lynx/` (no changes expected for this feature)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Minimal setup - verify test infrastructure and development environment

- [x] T001 Verify vitest test infrastructure runs successfully with `npm test`
- [x] T002 Verify development server runs with `npm run dev`
- [x] T003 [P] Review existing Handle implementation patterns in js/src/blocks/GainBlock.tsx

**Checkpoint**: Development environment ready, existing patterns understood

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and hooks that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation (TDD - Write FIRST)

- [x] T004 [P] Create test file for triangle geometry utility in js/src/utils/portMarkerGeometry.test.ts
- [x] T005 [P] Create test file for port connection hook in js/src/hooks/usePortMarkerVisibility.test.ts

### Foundation Implementation

- [x] T006 Implement triangle geometry utility in js/src/utils/portMarkerGeometry.ts (satisfies T004 tests)
- [x] T007 Implement usePortConnected hook in js/src/hooks/usePortMarkerVisibility.ts (satisfies T005 tests)
- [x] T008 Run foundation tests and verify all pass: `npm test portMarkerGeometry usePortMarkerVisibility`

**Checkpoint**: Foundation utilities ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Visual Port Identification on Unconnected Blocks (Priority: P1) 🎯 MVP

**Goal**: Display triangular markers on all unconnected ports to indicate port direction (input points left, output points right)

**Independent Test**: Place an unconnected Gain block on canvas - verify input port shows left-pointing triangle, output port shows right-pointing triangle

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Create PortMarker component test file in js/src/components/PortMarker.test.tsx
- [x] T010 [P] [US1] Write visibility tests: renders when isConnected=false, hides when isConnected=true (T009 file)
- [x] T011 [P] [US1] Write geometry tests: left-pointing for input, right-pointing for output (T009 file)
- [x] T012 [P] [US1] Write styling tests: primary-600 stroke, correct size prop handling (T009 file)
- [x] T013 [US1] Run PortMarker tests and verify all FAIL (no implementation yet): `npm test PortMarker`

### Implementation for User Story 1

- [x] T014 [US1] Create PortMarker component in js/src/components/PortMarker.tsx (satisfies T009-T012 tests)
- [x] T015 [US1] Add marker-specific styles to js/src/styles.css (transparent handle background, SVG triangle styles)
- [x] T016 [US1] Run PortMarker tests and verify all PASS: `npm test PortMarker` - **Note: Fixed React 19 async rendering issue in tests by adding waitForRender() helper**
- [x] T017 [P] [US1] Integrate PortMarker into GainBlock in js/src/blocks/GainBlock.tsx (wrap Handles with PortMarker children)
- [x] T018 [P] [US1] Integrate PortMarker into TransferFunctionBlock in js/src/blocks/TransferFunctionBlock.tsx
- [x] T019 [P] [US1] Integrate PortMarker into StateSpaceBlock in js/src/blocks/StateSpaceBlock.tsx
- [x] T020 [P] [US1] Integrate PortMarker into SumBlock in js/src/blocks/SumBlock.tsx (5 ports: 4 inputs + 1 output) - **Note: Created InputHandleWithMarker wrapper component for dynamic ports**
- [x] T021 [P] [US1] Integrate PortMarker into IOMarkerBlock in js/src/blocks/IOMarkerBlock.tsx (single port)
- [x] T022 [US1] Manual test US1 Scenario 1.1: Place Gain block, verify markers on both ports (quickstart.md)
- [x] T023 [US1] Manual test US1 Scenario 1.2: Add all block types, verify correct marker orientation per type (quickstart.md)

**Checkpoint**: ✅ COMPLETE - User Story 1 is fully functional - all unconnected ports show directional markers

**Design Changes Implemented**:
- Changed from filled triangles to two-line arrowheads (no base line) per Simulink style
- Changed from equilateral to isosceles triangles (height = 60% of width)
- Fixed positioning: input tips at border (base extends out), output bases at border (tip extends out)
- Added 3px clearance to prevent port penetration into blocks
- Stroke width matches blocks and edges (2px)

---

## Phase 4: User Story 2 - Port Marker Visibility Based on Connection State (Priority: P2)

**Goal**: Hide markers on connected ports, show markers on unconnected ports, respond to connection add/delete

**Independent Test**: Connect two Gain blocks - markers disappear on connected ports, remain on unconnected ports. Delete connection - markers reappear.

**Dependencies**: User Story 1 complete (PortMarker component exists)

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

- [x] T024 [P] [US2] Add connection state visibility tests to js/src/components/PortMarker.test.tsx (test all 4 visibility states from contract)
- [x] T025 [P] [US2] Add hook tests for edge array updates in js/src/hooks/usePortMarkerVisibility.test.ts (connection add/remove detection)
- [x] T026 [US2] Run US2 tests and verify all FAIL (no connection logic yet): `npm test PortMarker usePortMarkerVisibility`

### Implementation for User Story 2

- [x] T027 [US2] Update PortMarker component to respect isConnected prop visibility logic in js/src/components/PortMarker.tsx
- [x] T028 [US2] Update usePortConnected hook to query edges array in js/src/hooks/usePortMarkerVisibility.ts
- [x] T029 [US2] Update GainBlock to use usePortConnected hook and pass isConnected to PortMarker in js/src/blocks/GainBlock.tsx
- [x] T030 [P] [US2] Update TransferFunctionBlock to use usePortConnected hook in js/src/blocks/TransferFunctionBlock.tsx
- [x] T031 [P] [US2] Update StateSpaceBlock to use usePortConnected hook in js/src/blocks/StateSpaceBlock.tsx
- [x] T032 [P] [US2] Update SumBlock to use usePortConnected hook for all 5 ports in js/src/blocks/SumBlock.tsx
- [x] T033 [P] [US2] Update IOMarkerBlock to use usePortConnected hook in js/src/blocks/IOMarkerBlock.tsx
- [x] T034 [US2] Run US2 tests and verify all PASS: `npm test PortMarker usePortMarkerVisibility`
- [x] T035 [US2] Manual test US2 Scenario 2.1: Connect two blocks, verify markers disappear on connected ports (quickstart.md)
- [x] T036 [US2] Manual test US2 Scenario 2.2: Delete connection, verify markers reappear (quickstart.md)
- [x] T037 [US2] Manual test US2 Scenario 2.3: Sum block with mixed connections - verify selective visibility (quickstart.md)

**Checkpoint**: ✅ COMPLETE - User Stories 1 AND 2 both work - markers appear on unconnected ports only

**Additional Backend Work**:
- Added port regeneration logic in `diagram.py` when Sum block signs parameter changes
- Added connection cleanup when ports are removed (prevents orphaned connections)

---

## Phase 5: User Story 3 - Port Marker Orientation with Horizontal Flip (Priority: P3)

**Goal**: Maintain correct directional semantics when blocks are flipped horizontally (input markers always point in, output markers always point out)

**Independent Test**: Place Gain block, flip it - verify input marker moves to right edge pointing right (into block), output marker moves to left edge pointing left (away from block)

**Dependencies**: User Story 2 complete (connection state visibility working)

### Tests for User Story 3 (TDD - Write FIRST) ⚠️

- [x] T038 [P] [US3] Add flip orientation tests to js/src/components/PortMarker.test.tsx (verify transform inheritance)
- [x] T039 [US3] Run US3 tests and verify FAIL or PASS (flip may already work via CSS transform inheritance): `npm test PortMarker`

### Implementation for User Story 3

- [x] T040 [US3] Update PortMarker component to respect isFlipped prop (if needed - may inherit from block scaleX) in js/src/components/PortMarker.tsx
- [x] T041 [US3] Update GainBlock to pass isFlipped prop to PortMarker in js/src/blocks/GainBlock.tsx
- [x] T042 [P] [US3] Update TransferFunctionBlock to pass isFlipped prop to PortMarker in js/src/blocks/TransferFunctionBlock.tsx
- [x] T043 [P] [US3] Update StateSpaceBlock to pass isFlipped prop to PortMarker in js/src/blocks/StateSpaceBlock.tsx
- [x] T044 [P] [US3] Update SumBlock to pass isFlipped prop to PortMarker in js/src/blocks/SumBlock.tsx
- [x] T045 [P] [US3] Update IOMarkerBlock to pass isFlipped prop to PortMarker in js/src/blocks/IOMarkerBlock.tsx
- [x] T046 [US3] Run US3 tests and verify all PASS: `npm test PortMarker`
- [x] T047 [US3] Manual test US3 Scenario 3.1: Flip unconnected block, verify correct marker orientation (quickstart.md)
- [x] T048 [US3] Manual test US3 Scenario 3.2: Flip connected block, verify markers remain hidden with correct orientation on visible ports (quickstart.md)

**Checkpoint**: ✅ COMPLETE - All user stories independently functional - markers work correctly in all scenarios

**Implementation Notes**:
- Added `portType` prop to PortMarker to determine arrow direction (input vs output)
- Updated `calculateArrowheadLines` to handle flipped horizontal arrows (→ becomes ←)
- Fixed port positioning in all blocks to swap left/right when flipped
- Special handling for Gain block triangle geometry when flipped (accounts for scaleX transform)
- Bottom port on Sum block correctly points up (input orientation)

---

## Phase 6: Drag-and-Drop Hover Behavior (Edge Case Enhancement)

**STATUS**: ❌ **SKIPPED** - Decision made to skip this phase

**Reason**: Current behavior is acceptable. The destination port marker remains visible during drag operations, which provides clear visual feedback about valid connection targets. Adding isDragTarget logic would increase complexity without significant UX benefit.

**Goal**: ~~Hide destination port marker when drag operation hovers over it (per FR-011)~~

**Independent Test**: ~~Drag from Gain1 output, hover over Gain2 input without dropping - Gain2 input marker should disappear, Gain1 output marker should remain visible~~

**Dependencies**: ~~User Story 2 complete (connection visibility working)~~

### Tests for Drag Hover (TDD - Write FIRST) ⚠️

- [ ] ~~T049 [P] Add drag target visibility tests to js/src/components/PortMarker.test.tsx (test isDragTarget prop)~~
- [ ] ~~T050 Run drag hover tests and verify FAIL: `npm test PortMarker`~~

### Implementation for Drag Hover

- [ ] ~~T051 Update PortMarker component to hide when isDragTarget=true in js/src/components/PortMarker.tsx~~
- [ ] ~~T052 Add connection drag state tracking to DiagramCanvas in js/src/DiagramCanvas.tsx (onConnectStart/onConnectEnd handlers)~~
- [ ] ~~T053 Update block components to detect drag target state and pass isDragTarget to PortMarker (implementation TBD - may use React Flow's isConnectableEnd prop)~~
- [ ] ~~T054 Run drag hover tests and verify all PASS: `npm test PortMarker`~~
- [ ] ~~T055 Manual test Edge Case E1: Drag-and-drop hover - verify destination marker disappears on hover (quickstart.md)~~

**Checkpoint**: ~~Drag-and-drop UX polished - destination markers hide on hover~~ **SKIPPED**

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements, performance validation, documentation

- [ ] T056 [P] Manual test Edge Case E2: Rapid connect/disconnect - verify no visual glitches (quickstart.md) - **Requires user testing**
- [ ] T057 [P] Manual test Edge Case E3: Very small block - verify markers render at full size (quickstart.md) - **Requires user testing**
- [ ] T058 [P] Performance test P1: Large diagram (50 blocks) - verify 60fps panning/zooming (quickstart.md) - **Requires user testing**
- [ ] T059 [P] Performance test P2: Connection toggle latency - verify <50ms marker updates (quickstart.md) - **Requires user testing**
- [x] T060 [P] Run full test suite and verify all tests pass: `npm test` - ✅ **70 tests passing**
- [x] T061 [P] Run linter and fix any issues: `npm run lint` - ✅ **Port marker files lint-clean, reduced errors from 40→34**
- [x] T062 [P] Run formatter: `npm run format` - ✅ **All files formatted**
- [x] T063 [P] Build production bundle and verify no errors: `npm run build` - ✅ **Build successful (1.20s)**
- [ ] T064 Review all manual test scenarios from quickstart.md and mark complete - **Requires user review**
- [x] T065 Update CLAUDE.md if any deviations from plan occurred (likely none - architecture as designed) - ✅ **Updated with port markers section**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Depends on US1 (PortMarker component exists)
  - User Story 3 (P3): Depends on US2 (connection visibility working)
- **Drag Hover (Phase 6)**: Depends on US2 (edge case enhancement)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only → PortMarker component + basic rendering
- **User Story 2 (P2)**: US1 complete → Adds connection state visibility logic
- **User Story 3 (P3)**: US2 complete → Adds flip orientation handling

**KEY INSIGHT**: US1 is the MVP - delivers immediate value (directional markers visible)

### Within Each User Story (TDD Workflow)

1. **Tests FIRST** (write all tests for the story)
2. **Run tests** (verify they FAIL - RED state)
3. **Implement** (write code to pass tests - GREEN state)
4. **Refactor** (improve code quality while keeping tests green)
5. **Manual verification** (run quickstart.md scenarios)

### Parallel Opportunities

**Within Foundation (Phase 2)**:
- T004 and T005 (test files for different utilities)

**Within User Story 1 (Phase 3)**:
- T009-T012 (all PortMarker test writing tasks)
- T017-T021 (block integration tasks - different files)

**Within User Story 2 (Phase 4)**:
- T024-T025 (test writing for different modules)
- T030-T033 (block updates - different files)

**Within User Story 3 (Phase 5)**:
- T038 only test task (single component)
- T042-T045 (block updates - different files)

**Within Drag Hover (Phase 6)**:
- T049 only test task

**Within Polish (Phase 7)**:
- T056-T065 (all polish tasks can run in parallel - independent validations)

**Cross-Story Parallelism** (if team capacity):
- After Foundation complete, multiple developers can work on different stories simultaneously
- Developer A: US1 (T009-T023)
- Developer B: Start US2 tests (T024-T026) - wait for A to finish US1 before implementation
- Developer C: Documentation/infrastructure improvements

---

## Parallel Example: User Story 1 (MVP)

```bash
# Step 1: Write all tests in parallel
Task: "[US1] Create PortMarker component test file in js/src/components/PortMarker.test.tsx"
Task: "[US1] Write visibility tests: renders when isConnected=false, hides when isConnected=true"
Task: "[US1] Write geometry tests: left-pointing for input, right-pointing for output"
Task: "[US1] Write styling tests: primary-600 stroke, correct size prop handling"

# Step 2: Run tests (verify FAIL)
Task: "[US1] Run PortMarker tests and verify all FAIL (no implementation yet)"

# Step 3: Implement component
Task: "[US1] Create PortMarker component in js/src/components/PortMarker.tsx"
Task: "[US1] Add marker-specific styles to js/src/styles.css"

# Step 4: Run tests (verify PASS)
Task: "[US1] Run PortMarker tests and verify all PASS"

# Step 5: Integrate into all blocks in parallel
Task: "[US1] Integrate PortMarker into GainBlock in js/src/blocks/GainBlock.tsx"
Task: "[US1] Integrate PortMarker into TransferFunctionBlock in js/src/blocks/TransferFunctionBlock.tsx"
Task: "[US1] Integrate PortMarker into StateSpaceBlock in js/src/blocks/StateSpaceBlock.tsx"
Task: "[US1] Integrate PortMarker into SumBlock in js/src/blocks/SumBlock.tsx"
Task: "[US1] Integrate PortMarker into IOMarkerBlock in js/src/blocks/IOMarkerBlock.tsx"

# Step 6: Manual validation
Task: "[US1] Manual test US1 Scenario 1.1: Place Gain block, verify markers on both ports"
Task: "[US1] Manual test US1 Scenario 1.2: Add all block types, verify correct marker orientation"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - RECOMMENDED 🎯

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T008) - CRITICAL
3. Complete Phase 3: User Story 1 (T009-T023)
4. **STOP and VALIDATE**: Test US1 independently via quickstart.md scenarios
5. Deploy/demo if ready - markers visible on all unconnected ports

**MVP Deliverable**: Triangular port markers show direction on all unconnected blocks

### Incremental Delivery (Full Feature)

1. Foundation ready (Phase 1-2) → Development environment ready
2. Add User Story 1 (Phase 3) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Phase 4) → Test independently → Deploy/Demo (markers hide on connection)
4. Add User Story 3 (Phase 5) → Test independently → Deploy/Demo (flip orientation correct)
5. Add Drag Hover (Phase 6) → Test independently → Deploy/Demo (UX polish)
6. Polish (Phase 7) → Final validation → Production release

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phase 1-2)
2. Once Foundational is done:
   - **Solo developer**: Complete stories sequentially (US1 → US2 → US3)
   - **2 developers**: Dev A on US1, Dev B prepares US2 tests (wait for US1 component)
   - **3+ developers**: Parallel work on different polish tasks after US1-3 complete

---

## Task Count Summary

- **Total Tasks**: 65
- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 5 tasks (BLOCKS all stories)
- **Phase 3 (User Story 1 - MVP)**: 15 tasks (T009-T023)
- **Phase 4 (User Story 2)**: 14 tasks (T024-T037)
- **Phase 5 (User Story 3)**: 11 tasks (T038-T048)
- **Phase 6 (Drag Hover)**: 7 tasks (T049-T055)
- **Phase 7 (Polish)**: 10 tasks (T056-T065)

### Parallel Opportunities

- Foundation: 2 parallel tasks (test file creation)
- US1: 5 parallel block integration tasks + 4 parallel test writing tasks
- US2: 4 parallel block update tasks + 2 parallel test tasks
- US3: 4 parallel block update tasks
- Polish: 10 parallel validation tasks

**Estimated MVP Completion**: 23 tasks (Setup + Foundation + US1)

---

## Notes

- All tasks follow strict format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] = parallelizable (different files, no dependencies)
- [Story] = user story label (US1, US2, US3) for traceability
- TDD workflow enforced: Tests → FAIL → Implement → PASS → Refactor
- Each user story independently testable via quickstart.md scenarios
- Commit after each task or logical group (e.g., all tests for a story)
- Stop at any checkpoint to validate story independently
- Backend unchanged - all work in `js/src/` directory
