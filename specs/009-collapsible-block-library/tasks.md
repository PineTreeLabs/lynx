<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Collapsible Block Library

**Input**: Design documents from `/specs/009-collapsible-block-library/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓

**Tests**: Included per constitution (Test-Driven Development - NON-NEGOTIABLE)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `js/src/` (TypeScript/React)
- **Tests**: `js/src/palette/` (colocated with component)

---

## Phase 1: Setup

**Purpose**: No setup required - modifying existing component with existing test infrastructure

*This phase is empty - all infrastructure already exists.*

---

## Phase 2: Foundational (Core State Management)

**Purpose**: Add the core expand/collapse state and timing logic that ALL user stories depend on

**⚠️ CRITICAL**: This state management must be complete before any user story behavior can work

- [x] T001 Add `isExpanded` state (default false) and `collapseTimeoutRef` to js/src/palette/BlockPalette.tsx
- [x] T002 Add `COLLAPSE_DELAY_MS` constant (200ms) to js/src/palette/BlockPalette.tsx
- [x] T003 Implement `handleMouseEnter` callback that clears timeout and sets expanded=true in js/src/palette/BlockPalette.tsx
- [x] T004 Implement `handleMouseLeave` callback with delayed collapse in js/src/palette/BlockPalette.tsx
- [x] T005 Add cleanup effect to clear timeout on unmount in js/src/palette/BlockPalette.tsx

**Checkpoint**: State management ready - user story implementation can begin ✅

---

## Phase 3: User Story 1 - View Collapsed Library Icon (Priority: P1) 🎯 MVP

**Goal**: Display compact "Blocks" label by default, hiding block buttons until hover

**Independent Test**: Open any diagram and verify collapsed icon appears with consistent styling

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Test: panel renders collapsed by default (buttons hidden) in js/src/palette/BlockPalette.test.tsx
- [x] T007 [P] [US1] Test: collapsed header shows "Blocks" text in js/src/palette/BlockPalette.test.tsx
- [x] T008 [P] [US1] Test: collapsed header has consistent styling (border, shadow) in js/src/palette/BlockPalette.test.tsx

### Implementation for User Story 1

- [x] T009 [US1] Add collapsed header div with "Blocks" text and styling in js/src/palette/BlockPalette.tsx
- [x] T010 [US1] Wrap button panel in collapsible container with conditional visibility in js/src/palette/BlockPalette.tsx
- [x] T011 [US1] Apply matching styling to collapsed header (bg-white, border-2, border-slate-300, rounded-lg, shadow-lg) in js/src/palette/BlockPalette.tsx
- [x] T012 [US1] Add Tailwind transition classes for smooth animation (transition-all, duration-150) in js/src/palette/BlockPalette.tsx

**Checkpoint**: Collapsed state visible by default with styled header ✅

---

## Phase 4: User Story 2 - Expand Library on Hover (Priority: P1)

**Goal**: Panel expands smoothly when user hovers over the "Blocks" label

**Independent Test**: Hover over collapsed icon and verify full panel appears with all buttons

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US2] Test: panel expands on mouseEnter event in js/src/palette/BlockPalette.test.tsx
- [x] T014 [P] [US2] Test: all 6 buttons visible when expanded (Gain, Input, Output, Sum, TF, SS) in js/src/palette/BlockPalette.test.tsx
- [x] T015 [P] [US2] Test: expansion animation is smooth (uses CSS transitions) in js/src/palette/BlockPalette.test.tsx

### Implementation for User Story 2

- [x] T016 [US2] Add onMouseEnter handler to outer container in js/src/palette/BlockPalette.tsx
- [x] T017 [US2] Apply expanded state CSS classes when isExpanded=true (opacity-100, max-h-96) in js/src/palette/BlockPalette.tsx
- [x] T018 [US2] Ensure collapsed header remains fixed while panel grows downward in js/src/palette/BlockPalette.tsx

**Checkpoint**: Hover expansion working with smooth animation ✅

---

## Phase 5: User Story 3 - Collapse Library on Mouse Leave (Priority: P1)

**Goal**: Panel collapses back to icon when cursor leaves, with delay to prevent flickering

**Independent Test**: Hover to expand, move cursor away, verify collapse after brief delay

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T019 [P] [US3] Test: panel collapses on mouseLeave after delay in js/src/palette/BlockPalette.test.tsx
- [x] T020 [P] [US3] Test: rapid enter/leave does not cause flickering in js/src/palette/BlockPalette.test.tsx
- [x] T021 [P] [US3] Test: re-entering panel cancels collapse timeout in js/src/palette/BlockPalette.test.tsx

### Implementation for User Story 3

- [x] T022 [US3] Add onMouseLeave handler to outer container in js/src/palette/BlockPalette.tsx
- [x] T023 [US3] Apply collapsed state CSS classes when isExpanded=false (opacity-0, max-h-0, overflow-hidden) in js/src/palette/BlockPalette.tsx
- [x] T024 [US3] Verify collapse delay prevents accidental closures in js/src/palette/BlockPalette.tsx

**Checkpoint**: Full expand/collapse cycle working with anti-flicker delay ✅

---

## Phase 6: User Story 4 - Add Block While Panel is Expanded (Priority: P2)

**Goal**: Block buttons remain functional and panel stays open during interaction

**Independent Test**: Expand panel, click button, verify block added and panel stays open

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T025 [P] [US4] Test: clicking button does not collapse panel in js/src/palette/BlockPalette.test.tsx
- [x] T026 [P] [US4] Test: moving between buttons keeps panel expanded in js/src/palette/BlockPalette.test.tsx

### Implementation for User Story 4

- [x] T027 [US4] Ensure button clicks do not trigger mouseLeave behavior in js/src/palette/BlockPalette.tsx
- [x] T028 [US4] Verify existing addBlock functionality works when expanded in js/src/palette/BlockPalette.tsx

**Checkpoint**: All user stories complete - full feature functional ✅

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and edge case handling

- [x] T029 Run all tests and verify passing: `cd js && npm test`
- [x] T030 Build and verify no errors: `cd js && npm run build`
- [ ] T031 Run quickstart.md manual verification scenarios
- [ ] T032 [P] Optional: Add touch device click-to-toggle support in js/src/palette/BlockPalette.tsx

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Empty - infrastructure exists
- **Foundational (Phase 2)**: No dependencies - state management first
- **User Stories (Phase 3-6)**: All depend on Foundational (Phase 2)
  - US1, US2, US3 are all P1 and tightly coupled (same component)
  - US4 depends on US1-3 being complete (needs expand to work)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 foundational state - Can be MVP
- **US2 (P1)**: Depends on US1 (needs collapsed state to expand from)
- **US3 (P1)**: Depends on US2 (needs expanded state to collapse from)
- **US4 (P2)**: Depends on US1-3 (needs full expand/collapse working)

### Within Each User Story

1. Tests MUST be written FIRST and FAIL
2. Implementation tasks in order
3. Verify tests pass after implementation

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
- T001-T005 are sequential (state depends on previous)

**Within Each User Story**:
- Test tasks (T006-T008, T013-T015, T019-T021, T025-T026) can run in parallel
- Implementation tasks are sequential within a story

**Across Stories**:
- Stories are sequential due to tight coupling in single component
- Cannot parallelize across US1/US2/US3/US4

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together:
Task: "Test: panel renders collapsed by default (buttons hidden) in js/src/palette/BlockPalette.test.tsx"
Task: "Test: collapsed header shows 'Blocks' text in js/src/palette/BlockPalette.test.tsx"
Task: "Test: collapsed header has consistent styling (border, shadow) in js/src/palette/BlockPalette.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational state management
2. Complete Phase 3: User Story 1 (collapsed default state)
3. **STOP and VALIDATE**: Verify collapsed icon appears correctly
4. Continue to US2/US3 for functional expand/collapse

### Incremental Delivery

1. Phase 2 → Core state ready
2. Phase 3 (US1) → Collapsed state visible (partial feature)
3. Phase 4 (US2) → Expansion works (half feature)
4. Phase 5 (US3) → Collapse works (core feature complete!)
5. Phase 6 (US4) → Interaction polished (full feature)
6. Phase 7 → Final verification

### TDD Workflow

For each user story:
1. Write test file with test cases
2. Run `npm test` - verify tests FAIL
3. Implement functionality
4. Run `npm test` - verify tests PASS
5. Move to next story

---

## Notes

- All tasks modify single file: `js/src/palette/BlockPalette.tsx`
- Test file to create: `js/src/palette/BlockPalette.test.tsx`
- Stories are tightly coupled - implement sequentially
- Existing test infrastructure: Vitest 2.1.8 + React Testing Library
- Use `@testing-library/react` for component testing
- Use `vi.useFakeTimers()` for testing collapse delay behavior
