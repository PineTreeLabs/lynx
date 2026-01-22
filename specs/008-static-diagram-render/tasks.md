<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Static Diagram Render

**Input**: Design documents from `/specs/008-static-diagram-render/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in spec - test tasks omitted per constitution.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/lynx/` (Python)
- **Frontend**: `js/src/` (TypeScript/React)
- **Tests**: `tests/python/`, `js/src/` (Vitest)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add html-to-image dependency and create capture module structure

- [x] T001 Add html-to-image dependency to js/package.json
- [x] T002 [P] Create capture module directory structure at js/src/capture/
- [x] T003 [P] Add CaptureRequest and CaptureResult TypeScript interfaces to js/src/capture/types.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core traitlet infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add `_capture_request` Dict traitlet to LynxWidget in src/lynx/widget.py
- [x] T005 Add `_capture_result` Dict traitlet to LynxWidget in src/lynx/widget.py
- [x] T006 Add `_capture_mode` Bool traitlet to LynxWidget in src/lynx/widget.py
- [x] T007 Add capture request observer `_on_capture_request()` to LynxWidget in src/lynx/widget.py
- [x] T008 Create CaptureCanvas component skeleton in js/src/capture/CaptureCanvas.tsx
- [x] T009 Add capture mode CSS styles to js/src/styles.css (off-screen hidden positioning)
- [x] T010 Update widget render function in js/src/index.tsx to conditionally render CaptureCanvas in capture mode
- [x] T011 Add capture request handler in js/src/capture/CaptureCanvas.tsx that listens to `_capture_request` traitlet changes

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 & 2 - Export as PNG/SVG (Priority: P1) 🎯 MVP

**Goal**: Enable basic diagram export to PNG and SVG formats with white background

**Independent Test**: Create diagram with 2-3 blocks, call `lynx.render(diagram, "test.png")` and `lynx.render(diagram, "test.svg")`, verify files are created with correct content

**Note**: US1 (PNG) and US2 (SVG) are combined because they share 90% of the implementation and are both P1 priority.

### Implementation for User Story 1 & 2

- [x] T012 [P] [US1] Implement content bounds calculation utility in js/src/capture/captureUtils.ts using React Flow getNodesBounds()
- [x] T013 [P] [US1] Implement viewport fitting logic in js/src/capture/captureUtils.ts using fitBounds()
- [x] T014 [US1] Build CaptureCanvas React component in js/src/capture/CaptureCanvas.tsx with diagram-only rendering (no UI chrome)
- [x] T015 [US1] Integrate all block types (Gain, Sum, TransferFunction, StateSpace, IOMarker) in CaptureCanvas
- [x] T016 [US1] Integrate orthogonal edge rendering with arrowheads in CaptureCanvas
- [x] T017 [US1] Integrate port markers rendering for unconnected ports in CaptureCanvas
- [x] T018 [US1] Integrate block labels and connection labels rendering in CaptureCanvas
- [x] T019 [US1] Implement PNG capture using html-to-image toPng() in js/src/capture/captureUtils.ts
- [x] T020 [US2] Implement SVG capture using html-to-image toSvg() in js/src/capture/captureUtils.ts
- [x] T021 [US1] Implement capture orchestration in CaptureCanvas that calls capture utility and sets `_capture_result` traitlet
- [x] T022 [US1] Create render.py module skeleton in src/lynx/render.py with function signature
- [x] T023 [US1] Implement format detection from file extension in src/lynx/render.py
- [x] T024 [US1] Implement empty diagram validation in src/lynx/render.py (raise ValueError)
- [x] T025 [US1] Implement invalid extension validation in src/lynx/render.py (raise ValueError)
- [x] T026 [US1] Implement hidden widget creation and display in src/lynx/render.py
- [x] T027 [US1] Implement capture request sending and result waiting in src/lynx/render.py
- [x] T028 [US1] Implement base64 decoding and file writing in src/lynx/render.py
- [x] T029 [US1] Implement widget cleanup after capture in src/lynx/render.py
- [x] T030 [US1] Export render function from src/lynx/__init__.py

**Checkpoint**: Basic PNG and SVG export working with default dimensions and white background

---

## Phase 4: User Story 3 - Specify Output Dimensions (Priority: P2)

**Goal**: Allow users to specify exact output dimensions (width, height, or both)

**Independent Test**: Export same diagram with `width=1200, height=800`, verify output dimensions match

### Implementation for User Story 3

- [x] T031 [US3] Add width and height parameter handling to capture request in src/lynx/render.py
- [x] T032 [US3] Implement dimension calculation logic in js/src/capture/captureUtils.ts (auto-calculate missing dimension from aspect ratio)
- [x] T033 [US3] Update toPng/toSvg calls with width/height options in js/src/capture/captureUtils.ts
- [x] T034 [US3] Implement viewport scaling for fixed dimensions in js/src/capture/CaptureCanvas.tsx
- [x] T035 [US3] Add actual dimensions to CaptureResult in js/src/capture/CaptureCanvas.tsx

**Checkpoint**: Custom dimensions working - users can specify width, height, or both

---

## Phase 5: User Story 4 - Transparent Background (Priority: P2)

**Goal**: Support transparent backgrounds for PNG and SVG export

**Independent Test**: Export with `transparent=True`, place over colored background, verify transparency works

### Implementation for User Story 4

- [x] T036 [US4] Add transparent parameter handling to capture request in src/lynx/render.py
- [x] T037 [US4] Update toPng() call with backgroundColor option in js/src/capture/captureUtils.ts
- [x] T038 [US4] Update toSvg() call with backgroundColor option in js/src/capture/captureUtils.ts
- [x] T039 [US4] Ensure CaptureCanvas has no background element when transparent=true in js/src/capture/CaptureCanvas.tsx

**Checkpoint**: Transparent background working for both PNG and SVG

---

## Phase 6: User Story 5 - Auto-fit Diagram to Canvas (Priority: P3)

**Goal**: Automatically crop output to content bounds with consistent padding

**Independent Test**: Create diagram with blocks at extreme positions, verify output has consistent margins without excess whitespace

### Implementation for User Story 5

- [x] T040 [US5] Refine content bounds calculation to include block labels in js/src/capture/captureUtils.ts
- [x] T041 [US5] Add configurable padding constant (40px default) in js/src/capture/captureUtils.ts
- [x] T042 [US5] Ensure viewport is set to content bounds before capture in js/src/capture/CaptureCanvas.tsx

**Checkpoint**: Auto-fit working - output cropped to content with consistent padding

---

## Phase 7: Polish & Error Handling

**Purpose**: Robust error handling and edge cases

- [x] T043 Implement path writability validation in src/lynx/render.py (raise IOError)
- [x] T044 Implement capture timeout handling in src/lynx/render.py (raise RuntimeError after 10s)
- [x] T045 Add error propagation from JS capture failures to Python in src/lynx/render.py
- [x] T046 [P] Verify all block types render correctly with complex parameters (manual testing)
- [x] T047 [P] Verify LaTeX content renders correctly in exports (manual testing)
- [x] T048 Run quickstart.md test scenarios and document results

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 & US2 (Phase 3): Can start after Foundational
  - US3 (Phase 4): Can start after Phase 3 (builds on basic export)
  - US4 (Phase 5): Can start after Phase 3 (builds on basic export)
  - US5 (Phase 6): Can start after Phase 3 (builds on basic export)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 & 2 (P1)**: Core functionality - no dependencies on other stories
- **User Story 3 (P2)**: Depends on US1/US2 - extends capture with dimension options
- **User Story 4 (P2)**: Depends on US1/US2 - extends capture with transparency option
- **User Story 5 (P3)**: Depends on US1/US2 - refines viewport calculation

### Within Each User Story

- TypeScript utilities before React components
- React components before Python integration
- Python module skeleton before implementation details
- Core implementation before error handling

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T012 and T013 can run in parallel (different utilities in same file)
- T046 and T047 can run in parallel (independent manual tests)
- US3, US4, and US5 can be worked in parallel after US1/US2 complete

---

## Parallel Example: Phase 3 (US1 & US2)

```bash
# Launch utility implementations together:
Task: "Implement content bounds calculation utility in js/src/capture/captureUtils.ts"
Task: "Implement viewport fitting logic in js/src/capture/captureUtils.ts"

# Then build CaptureCanvas sequentially (depends on utilities)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Stories 1 & 2 (PNG/SVG export)
4. **STOP and VALIDATE**: Test basic export with simple diagrams
5. Deploy/demo if ready - users can now export diagrams!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 & US2 → Test exports → Deploy (MVP!)
3. Add US3 → Custom dimensions → Deploy
4. Add US4 → Transparent backgrounds → Deploy
5. Add US5 → Auto-fit refinement → Deploy
6. Each story adds value without breaking previous functionality

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 and US2 combined because they share implementation (format difference only)
- CaptureCanvas is the key component - it renders diagram without UI chrome
- html-to-image handles the heavy lifting for DOM-to-image conversion
- Python render() function orchestrates: create hidden widget → send request → wait for result → write file
- Timeout handling (T044) is critical for robustness - don't let render() hang forever
