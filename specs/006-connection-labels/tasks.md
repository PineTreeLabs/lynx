<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Connection Labels

**Input**: Design documents from `/specs/006-connection-labels/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Tests included for positioning algorithm per Constitution TDD requirements (plan.md:30).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/lynx/` (Python)
- **Frontend**: `js/src/` (TypeScript/React)
- **Tests**: `js/src/test/` (Vitest)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Extend data model with connection label fields (shared by all user stories)

- [x] T001 [P] Add `label` and `label_visible` fields to ConnectionModel in src/lynx/schema.py
- [x] T002 [P] Add `label` and `label_visible` fields to Connection dataclass in src/lynx/diagram.py
- [x] T003 Update Connection.to_dict() to include label fields in src/lynx/diagram.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add toggle_connection_label_visibility() method to Diagram class in src/lynx/diagram.py
- [x] T005 Add update_connection_label() method to Diagram class in src/lynx/diagram.py
- [x] T006 [P] Add _handle_toggle_connection_label_visibility() action handler in src/lynx/widget.py
- [x] T007 [P] Add _handle_update_connection_label() action handler in src/lynx/widget.py
- [x] T008 Register new action types in _on_action() dispatcher in src/lynx/widget.py
- [x] T009 Update connectionToEdge() to include label and label_visible in edge data in js/src/DiagramCanvas.tsx
- [x] T010 Update OrthogonalEdgeData interface to include label and label_visible in js/src/utils/traitletSync.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Show Label via Context Menu (Priority: P1) 🎯 MVP

**Goal**: Users can right-click a connection and select "Show Label" to display the connection's label

**Independent Test**: Right-click any connection → "Show Label" → label appears with connection ID

### Implementation for User Story 1

- [x] T011 [US1] Add labelVisible prop to EdgeContextMenu interface in js/src/components/EdgeContextMenu.tsx
- [x] T012 [US1] Add onToggleLabel callback prop to EdgeContextMenu interface in js/src/components/EdgeContextMenu.tsx
- [x] T013 [US1] Implement "Show Label" menu item in EdgeContextMenu (when label hidden) in js/src/components/EdgeContextMenu.tsx
- [x] T014 [US1] Update edgeContextMenu state to include labelVisible in js/src/DiagramCanvas.tsx
- [x] T015 [US1] Add handleToggleConnectionLabelVisibility callback in js/src/DiagramCanvas.tsx
- [x] T016 [US1] Wire EdgeContextMenu to include labelVisible and onToggleLabel props in js/src/DiagramCanvas.tsx
- [x] T017 [US1] Update onEdgeContextMenu to extract label_visible from edge data in js/src/DiagramCanvas.tsx
- [x] T018 [US1] Render label using EdgeLabelRenderer when label_visible is true in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T019 [US1] Style connection label to match block labels (text-xs font-mono) in js/src/connections/OrthogonalEditableEdge.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - "Show Label" displays label

---

## Phase 4: User Story 2 - Hide Label via Context Menu (Priority: P2)

**Goal**: Users can right-click a connection with visible label and select "Hide Label" to hide it

**Independent Test**: Show a label → right-click → "Hide Label" → label disappears

### Implementation for User Story 2

- [x] T020 [US2] Implement "Hide Label" menu item in EdgeContextMenu (when label visible) in js/src/components/EdgeContextMenu.tsx
- [x] T021 [US2] Ensure context menu text toggles between "Show Label" and "Hide Label" based on state in js/src/components/EdgeContextMenu.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - full show/hide toggle

---

## Phase 5: User Story 3 - Edit Visible Labels (Priority: P3)

**Goal**: Users can double-click a visible label to edit it inline

**Independent Test**: Show label → double-click → type new text → Enter → label updates

### Implementation for User Story 3

- [x] T022 [US3] Create useConnectionLabel hook for label state management in js/src/hooks/useConnectionLabel.ts (SKIPPED: using direct pattern instead)
- [x] T023 [US3] Import EditableLabel component in OrthogonalEditableEdge in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T024 [US3] Replace static label text with EditableLabel component in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T025 [US3] Implement handleLabelSave callback to dispatch updateConnectionLabel action in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T026 [US3] Ensure label defaults to connection ID when label is null/undefined in js/src/connections/OrthogonalEditableEdge.tsx

**Checkpoint**: At this point, User Stories 1-3 work - show/hide/edit labels

---

## Phase 6: User Story 4 - Persist Label Visibility and Text (Priority: P4)

**Goal**: Label text and visibility state persist through save/load cycles

**Independent Test**: Show label → edit text → save diagram → reload → label still visible with custom text

### Implementation for User Story 4

- [x] T027 [US4] Update Diagram.from_dict() to restore connection label fields in src/lynx/diagram.py
- [x] T028 [US4] Update _restore_state() to include connection label fields for undo/redo in src/lynx/diagram.py
- [x] T029 [US4] Verify backward compatibility - old diagrams load with label=None, label_visible=False (handled by defaults)

**Checkpoint**: At this point, User Stories 1-4 work - full persistence

---

## Phase 7: User Story 5 - Smart Label Positioning (Priority: P5)

**Goal**: Labels positioned at horizontal center, shifting to avoid corner waypoints

**Independent Test**: Create connection with waypoints → show label → label avoids corners

### Tests for User Story 5

- [x] T030 [P] [US5] Create test file js/src/test/connectionLabelPosition.test.ts
- [x] T031 [P] [US5] Test: straight connection positions label at horizontal center
- [x] T032 [P] [US5] Test: connection with waypoints avoids corner overlap
- [x] T033 [P] [US5] Test: label shifts minimum distance when overlapping corner

### Implementation for User Story 5

- [x] T034 [US5] Create calculateConnectionLabelPosition() function in js/src/utils/connectionLabelPosition.ts
- [x] T035 [US5] Implement horizontal center calculation (minX + maxX) / 2 in js/src/utils/connectionLabelPosition.ts
- [x] T036 [US5] Implement findSegmentAtX() helper to find segment containing centerX in js/src/utils/connectionLabelPosition.ts
- [x] T037 [US5] Implement corner detection from segments in js/src/utils/connectionLabelPosition.ts
- [x] T038 [US5] Implement overlap detection and minimum shift logic in js/src/utils/connectionLabelPosition.ts
- [x] T039 [US5] Integrate calculateConnectionLabelPosition() into OrthogonalEditableEdge in js/src/connections/OrthogonalEditableEdge.tsx
- [x] T040 [US5] Pass segments array to positioning function in js/src/connections/OrthogonalEditableEdge.tsx

**Checkpoint**: All user stories complete - full feature implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T041 Run quickstart.md validation scenarios manually
- [ ] T042 Verify undo/redo works for label visibility toggle
- [ ] T043 Verify undo/redo works for label text changes
- [x] T044 Run existing test suite to ensure no regressions (npm test in js/)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 → US2 (US2 needs Show Label working first)
  - US1 → US3 (US3 needs label visible to edit)
  - US1-3 → US4 (persistence needs basic functionality)
  - US1 → US5 (positioning needs label rendering)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (needs Show Label to exist to hide)
- **User Story 3 (P3)**: Depends on US1 (needs label visible to edit)
- **User Story 4 (P4)**: Depends on US1-3 (needs label data to persist)
- **User Story 5 (P5)**: Depends on US1 (needs label rendering to position)

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Backend changes before frontend
- Schema before business logic
- Core implementation before integration

### Parallel Opportunities

- T001, T002 can run in parallel (different files)
- T006, T007 can run in parallel (different handlers)
- T030, T031, T032, T033 can run in parallel (different test cases)
- US2-5 can all start immediately after US1 completes (different concerns)

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all setup tasks together:
Task: "Add label fields to ConnectionModel in src/lynx/schema.py"
Task: "Add label fields to Connection dataclass in src/lynx/diagram.py"
```

## Parallel Example: User Story 5 Tests

```bash
# Launch all US5 tests together:
Task: "Test: straight connection positions label at horizontal center"
Task: "Test: connection with waypoints avoids corner overlap"
Task: "Test: label shifts minimum distance when overlapping corner"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Show Label)
4. **STOP and VALIDATE**: Right-click → Show Label → label appears
5. Demo/validate with user if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Show Label works (MVP!)
3. Add User Story 2 → Hide Label works (toggle complete)
4. Add User Story 3 → Edit Label works (editing complete)
5. Add User Story 4 → Persistence works (save/load complete)
6. Add User Story 5 → Smart positioning (polish complete)
7. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 is the MVP - all other stories build on it
- Reuse EditableLabel component from block labels (js/src/components/EditableLabel.tsx)
- Follow existing patterns from 005-hideable-block-labels feature
- Commit after each task or logical group
