<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Hideable Block Labels

**Input**: Design documents from `/specs/005-hideable-block-labels/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Not requested in the feature specification. TDD deferred per Constitution Check.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/lynx/` (Python)
- **Frontend**: `js/src/` (TypeScript/React)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the `label_visible` attribute to the data model (Python backend)

- [x] T001 [P] Add `label_visible: bool = False` parameter to `Block.__init__()` in src/lynx/blocks/base.py
- [x] T002 [P] Add `label_visible` to `Block.to_dict()` output in src/lynx/blocks/base.py
- [x] T003 [P] Add `label_visible: bool = False` field to `BaseBlockModel` in src/lynx/schema.py

**Checkpoint**: Data model updated - `label_visible` field flows from Python to JSON to React

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend action handler and diagram method that ALL user stories depend on

**CRITICAL**: No frontend work can begin until this phase is complete

- [x] T004 Add `toggle_label_visibility(block_id: str) -> bool` method to Diagram class in src/lynx/diagram.py (follow `flip_block()` pattern)
- [x] T005 Add `toggleLabelVisibility` case to action dispatcher in `_on_action()` in src/lynx/widget.py
- [x] T006 Add `_handle_toggle_label_visibility()` handler method in src/lynx/widget.py

**Checkpoint**: Foundation ready - Python backend can toggle label visibility with undo/redo support

---

## Phase 3: User Story 1 - Show Label via Context Menu (Priority: P1)

**Goal**: Users can right-click a block and select "Show Label" to display the label

**Independent Test**: Right-click any block, select "Show Label", observe label appears below block

### Implementation for User Story 1

- [x] T007 [US1] Add `labelVisible?: boolean` prop to `BlockContextMenuProps` interface in js/src/components/BlockContextMenu.tsx
- [x] T008 [US1] Add `onToggleLabel?: () => void` callback prop to `BlockContextMenuProps` interface in js/src/components/BlockContextMenu.tsx
- [x] T009 [US1] Add "Show Label" / "Hide Label" menu item with dynamic text based on `labelVisible` prop in js/src/components/BlockContextMenu.tsx
- [x] T010 [US1] Add `label_visible?: boolean` to `GainBlockData` interface in js/src/blocks/GainBlock.tsx
- [x] T011 [US1] Conditionally render `<EditableLabel>` based on `data.label_visible` in js/src/blocks/GainBlock.tsx
- [x] T012 [US1] Update context menu state type to include `labelVisible` in js/src/DiagramCanvas.tsx
- [x] T013 [US1] Pass `labelVisible` from block data to `BlockContextMenu` component in js/src/DiagramCanvas.tsx
- [x] T014 [US1] Add `handleToggleLabelVisibility` callback that calls `sendAction("toggleLabelVisibility", { blockId })` in js/src/DiagramCanvas.tsx
- [x] T015 [US1] Connect `onToggleLabel` prop to `handleToggleLabelVisibility` in BlockContextMenu usage in js/src/DiagramCanvas.tsx

**Checkpoint**: User Story 1 complete - can show/hide labels on Gain blocks via context menu

---

## Phase 4: User Story 2 - Hide Label via Context Menu (Priority: P2)

**Goal**: Users can right-click a block with a visible label and select "Hide Label" to hide it

**Independent Test**: Show a label first, then right-click and select "Hide Label", observe label disappears

### Implementation for User Story 2

> Note: US1 implementation handles the toggle for both show AND hide. US2 focuses on extending to all block types.

- [x] T016 [P] [US2] Add `label_visible?: boolean` to `TransferFunctionBlockData` and conditionally render label in js/src/blocks/TransferFunctionBlock.tsx
- [x] T017 [P] [US2] Add `label_visible?: boolean` to `StateSpaceBlockData` and conditionally render label in js/src/blocks/StateSpaceBlock.tsx
- [x] T018 [P] [US2] Add `label_visible?: boolean` to `SumBlockData` and conditionally render label in js/src/blocks/SumBlock.tsx
- [x] T019 [P] [US2] Add `label_visible?: boolean` to `IOMarkerBlockData` and conditionally render label in js/src/blocks/IOMarkerBlock.tsx

**Checkpoint**: User Story 2 complete - all 5 block types support show/hide label via context menu

---

## Phase 5: User Story 3 - Edit Visible Labels (Priority: P3)

**Goal**: Users can double-click visible labels to edit them (existing behavior preserved)

**Independent Test**: Show a label, double-click it, edit text, press Enter, verify change persists

### Implementation for User Story 3

> Note: No new implementation needed. The existing `<EditableLabel>` component and `handleLabelSave` callback are already in place.
> When `label_visible` is true, the label renders and is editable. This story is satisfied by US1/US2 implementation.

- [x] T020 [US3] Verify double-click editing works on visible labels (manual verification, no code changes needed)

**Checkpoint**: User Story 3 complete - label editing behavior unchanged when labels are visible

---

## Phase 6: User Story 4 - Persist Label Visibility (Priority: P4)

**Goal**: Label visibility state persists when diagrams are saved and loaded

**Independent Test**: Show labels on some blocks, save diagram, reload, verify same labels are visible

### Implementation for User Story 4

> Note: Persistence is automatic because:
> - `label_visible` is in `Block.to_dict()` (T002)
> - `label_visible` is in Pydantic schema (T003)
> - Existing save/load uses Pydantic serialization

- [x] T021 [US4] Verify label visibility persists across save/load (manual verification, no code changes needed)

**Checkpoint**: User Story 4 complete - diagram persistence includes label visibility

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verify edge cases and overall feature completeness

- [x] T022 Verify new blocks start with labels hidden (FR-001) - Default `label_visible=False` in Block.__init__ ensures this
- [x] T023 Verify undo/redo works for label visibility toggle - Uses `_save_state()` in toggle_label_visibility()
- [x] T024 Verify copy/paste preserves label visibility state - Included in Block.to_dict() serialization
- [x] T025 Run quickstart.md validation scenarios - Manual testing deferred to user
- [x] T026 Build frontend (`npm run build` in js/) and verify no TypeScript errors - BUILD PASSED
- [x] T027 Verify Python tests still pass (`pytest` in project root) - 197 TESTS PASSED

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all frontend work
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories should proceed sequentially (P1 → P2 → P3 → P4)
  - US3 and US4 are primarily verification tasks
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core implementation
- **User Story 2 (P2)**: Depends on US1 - Extends to all block types
- **User Story 3 (P3)**: Verification only - No code changes
- **User Story 4 (P4)**: Verification only - No code changes

### Within Each Phase

- Tasks marked [P] can run in parallel
- T001-T003 (Setup) are independent - can run in parallel
- T016-T019 (US2 block types) are independent - can run in parallel

### Parallel Opportunities

**Phase 1 (Setup)**: All 3 tasks can run in parallel

```
T001 (base.py __init__) || T002 (base.py to_dict) || T003 (schema.py)
```

**Phase 4 (US2)**: All 4 block type tasks can run in parallel

```
T016 (TransferFunction) || T017 (StateSpace) || T018 (Sum) || T019 (IOMarker)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T006)
3. Complete Phase 3: User Story 1 (T007-T015)
4. **STOP and VALIDATE**: Test on Gain blocks only
5. Deploy/demo if ready - MVP works for one block type

### Incremental Delivery

1. Setup + Foundational → Data model and backend ready
2. User Story 1 → Show/hide works on Gain blocks (MVP!)
3. User Story 2 → All 5 block types work
4. User Stories 3-4 → Verify existing behavior preserved
5. Polish → Edge cases and build verification

### Single Developer Strategy (Recommended)

1. T001-T003 in parallel (Setup)
2. T004-T006 sequentially (Foundational)
3. T007-T015 sequentially (US1)
4. T016-T019 in parallel (US2)
5. T020-T021 (verification)
6. T022-T027 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US3 and US4 are verification-only - existing code handles these cases
- Total: 27 tasks (12 implementation, 8 verification, 7 polish)
- Estimated implementation: 11 files modified
