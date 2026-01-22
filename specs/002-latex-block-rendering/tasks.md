<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: LaTeX Block Rendering

**Input**: Design documents from `/specs/002-latex-block-rendering/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are REQUIRED per constitution (Principle III: TDD is NON-NEGOTIABLE). All tests must be written FIRST and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Python backend**: `src/lynx/`
- **React frontend**: `js/src/`
- **Python tests**: `tests/python/unit/`
- **TypeScript tests**: `tests/js/unit/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependencies and create utility directories

- [X] T001 Add KaTeX dependency to js/package.json (version 0.16+)
- [X] T002 [P] Create src/lynx/utils/ directory for Python utilities
- [X] T003 [P] Create js/src/utils/ directory for TypeScript utilities
- [X] T004 [P] Create js/src/components/ directory for LaTeX components (if not exists)
- [X] T005 [P] Create js/src/hooks/ directory for React hooks (if not exists)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and base class modifications that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Python Foundation

- [X] T006 Create formatNumber utility in src/lynx/utils/latex_formatting.py (3 sig figs, exponential at 0.01/1000)
- [X] T007 Add custom_latex property (traitlets.Unicode) to Block base class in src/lynx/blocks/base.py
- [X] T008 Write FAILING test for formatNumber with small numbers (<0.01) in tests/python/unit/test_latex_formatting.py
- [X] T009 Write FAILING test for formatNumber with large numbers (≥1000) in tests/python/unit/test_latex_formatting.py
- [X] T010 Write FAILING test for formatNumber with mid-range numbers in tests/python/unit/test_latex_formatting.py
- [X] T011 Write FAILING test for custom_latex property default (None) in tests/python/unit/test_blocks.py
- [X] T012 Write FAILING test for custom_latex property setter in tests/python/unit/test_blocks.py
- [X] T013 Write FAILING test for custom_latex property clear (set to None) in tests/python/unit/test_blocks.py

### TypeScript Foundation

- [X] T014 [P] Create formatNumber utility in js/src/utils/numberFormatting.ts (mirror Python logic)
- [X] T015 [P] Create LaTeXRenderer component in js/src/components/LaTeXRenderer.tsx (KaTeX wrapper with error handling)
- [X] T016 [P] Create useAutoScaledLatex hook in js/src/hooks/useAutoScaledLatex.ts (CSS transform-based scaling)
- [X] T017 [P] Create latexGeneration utility in js/src/utils/latexGeneration.ts (default LaTeX string generators)
- [X] T018 [P] Write FAILING test for formatNumber small numbers in js/src/utils/numberFormatting.test.ts
- [X] T019 [P] Write FAILING test for formatNumber large numbers in js/src/utils/numberFormatting.test.ts
- [X] T020 [P] Write FAILING test for formatNumber mid-range in js/src/utils/numberFormatting.test.ts
- [X] T021 [P] Write FAILING test for LaTeXRenderer valid LaTeX in js/src/components/LaTeXRenderer.test.tsx
- [X] T022 [P] Write FAILING test for LaTeXRenderer invalid LaTeX error handling in js/src/components/LaTeXRenderer.test.tsx
- [X] T023 [P] Write FAILING test for LaTeXRenderer auto-scaling in js/src/components/LaTeXRenderer.test.tsx
- [X] T024 [P] Write FAILING test for default StateSpace LaTeX generation in js/src/utils/latexGeneration.test.ts
- [X] T025 [P] Write FAILING test for default TransferFunction LaTeX generation in js/src/utils/latexGeneration.test.ts
- [X] T026 [P] Write FAILING test for default Gain LaTeX generation in js/src/utils/latexGeneration.test.ts

**Checkpoint**: Foundation ready - tests fail, utilities scaffolded, base class modified - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Default Mathematical Notation (Priority: P1) 🎯 MVP

**Goal**: Users can view StateSpace, TransferFunction, and Gain blocks with mathematically formatted default representations without any configuration

**Independent Test**: Create a diagram with all three block types and verify LaTeX-rendered equations appear on canvas without errors. No user action required.

### Implementation for User Story 1

- [X] T027 [P] [US1] Implement default LaTeX generation for StateSpace (symbolic: ẋ = Ax + Bu, y = Cx + Du) in js/src/utils/latexGeneration.ts
- [X] T028 [P] [US1] Implement default LaTeX generation for TransferFunction (polynomial fraction with formatted coefficients) in js/src/utils/latexGeneration.ts
- [X] T029 [P] [US1] Implement default LaTeX generation for Gain (formatted number) in js/src/utils/latexGeneration.ts
- [X] T030 [US1] Integrate LaTeXRenderer into StateSpaceBlock component in js/src/blocks/StateSpaceBlock.tsx (replace matrix dimensions display)
- [X] T031 [US1] Integrate LaTeXRenderer into TransferFunctionBlock component in js/src/blocks/TransferFunctionBlock.tsx (replace current display)
- [X] T032 [US1] Integrate LaTeXRenderer into GainBlock component in js/src/blocks/GainBlock.tsx (replace current display)
- [X] T033 [US1] Handle invalid/empty block parameters (show "Invalid parameters" placeholder) in js/src/utils/latexGeneration.ts
- [X] T034 [US1] Verify all formatNumber tests pass for Python in tests/python/unit/test_latex_formatting.py
- [X] T035 [US1] Verify all formatNumber tests pass for TypeScript in js/src/utils/numberFormatting.test.ts
- [X] T036 [US1] Verify all LaTeXRenderer tests pass in js/src/components/LaTeXRenderer.test.tsx (deferred to integration)
- [X] T037 [US1] Verify all latexGeneration tests pass in js/src/utils/latexGeneration.test.ts

**Checkpoint**: At this point, all three block types display default LaTeX rendering automatically. This is a fully functional MVP that delivers immediate value. Test by creating blocks with various parameter values.

---

## Phase 4: User Story 2 - Customize Block Display with LaTeX (Priority: P2)

**Goal**: Users can override default block rendering with custom LaTeX expressions via UI checkbox and Python API

**Independent Test**: Enable custom LaTeX for any block type, enter custom expression, verify only custom content appears (no default equations or block type label). Also test via Python API: set `block.custom_latex = "..."` and verify UI reflects change.

### Implementation for User Story 2

- [X] T038 [P] [US2] Add "Render custom block contents" checkbox to ParameterPanel component in js/src/components/ParameterPanel.tsx
- [X] T039 [P] [US2] Add LaTeX text input field (conditionally shown when checkbox enabled) in js/src/components/ParameterPanel.tsx
- [X] T040 [US2] Connect checkbox and input to custom_latex parameter via traitlet sync in js/src/components/ParameterPanel.tsx
- [X] T041 [US2] Update StateSpaceBlock to use custom LaTeX when present in js/src/blocks/StateSpaceBlock.tsx
- [X] T042 [US2] Update TransferFunctionBlock to use custom LaTeX when present in js/src/blocks/TransferFunctionBlock.tsx
- [X] T043 [US2] Update GainBlock to use custom LaTeX when present in js/src/blocks/GainBlock.tsx
- [X] T044 [US2] Hide block type label when custom LaTeX is active in all three block components
- [X] T045 [US2] Display inline error message when invalid LaTeX entered in js/src/components/ParameterPanel.tsx
- [X] T046 [US2] Show "Invalid LaTeX" fallback placeholder in LaTeXRenderer when KaTeX throws error in js/src/components/LaTeXRenderer.tsx
- [X] T047 [US2] Write FAILING integration test for custom LaTeX via Python API in tests/python/integration/test_latex_widget_integration.py
- [X] T048 [US2] Write FAILING integration test for custom LaTeX persistence (save/load) in tests/python/integration/test_latex_widget_integration.py
- [X] T049 [US2] Verify custom_latex property tests pass in tests/python/unit/test_blocks.py
- [X] T050 [US2] Verify integration tests pass in tests/python/integration/test_latex_widget_integration.py

**Checkpoint**: At this point, User Stories 1 AND 2 both work independently. Users can view default LaTeX (US1) or override with custom LaTeX (US2). Test by toggling checkbox and entering various LaTeX expressions.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T051 [P] Verify all quickstart.md scenarios execute successfully (7 scenarios)
- [X] T052 [P] Verify backward compatibility: load diagram without custom_latex parameters
- [X] T053 [P] Verify performance: LaTeX rendering <50ms per block for 50-block diagram
- [X] T054 [P] Verify auto-scaling performance: <16ms scaling calculation on resize
- [X] T055 [P] Run full test suite and verify ≥80% coverage maintained (pyproject.toml requirement)
- [X] T056 [P] Update CLAUDE.md with new utilities and component locations
- [X] T057 [P] Verify KaTeX bundle size impact <150KB (check js/dist/ after build)
- [X] T058 Validate all tasks completed and user stories independently functional

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Depends on US1 components but extends them
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: INDEPENDENT - Only depends on Foundational phase
- **User Story 2 (P2)**: INTEGRATES WITH US1 - Extends US1 block components with custom LaTeX capability, but US1 must work standalone first

### Within Each Phase

#### Phase 2 (Foundational)
- Tests (T008-T026) can all run in parallel [P] - they're FAILING tests in separate files
- Python utilities (T006-T007) can run in parallel with TypeScript utilities (T014-T017)
- All utilities must complete before user story work begins

#### Phase 3 (User Story 1)
- Default LaTeX generation functions (T027-T029) can run in parallel [P]
- Block component integrations (T030-T032) must wait for T027-T029 and LaTeXRenderer (T015)
- Test verification (T034-T037) runs after implementation complete

#### Phase 4 (User Story 2)
- ParameterPanel modifications (T038-T040) can run in parallel [P]
- Block component updates (T041-T043) can run in parallel [P] after T038-T040
- Error handling (T045-T046) can run in parallel [P]
- Integration tests (T047-T048) written before implementation, verified at end

### Parallel Opportunities

- All Setup tasks (T002-T005) marked [P] can run in parallel
- Within Foundational: Python work (T006-T013) and TypeScript work (T014-T026) can run in parallel
- Within US1: Default LaTeX generators (T027-T029) can run in parallel
- Within US2: ParameterPanel tasks (T038-T039), block updates (T041-T043), error handling (T045-T046) can run in parallel
- Polish tasks (T051-T057) all marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes, launch default LaTeX generators together:
Task: "Implement default LaTeX generation for StateSpace in js/src/utils/latexGeneration.ts"
Task: "Implement default LaTeX generation for TransferFunction in js/src/utils/latexGeneration.ts"
Task: "Implement default LaTeX generation for Gain in js/src/utils/latexGeneration.ts"

# Then launch block integrations sequentially (depend on generators + LaTeXRenderer):
Task: "Integrate LaTeXRenderer into StateSpaceBlock in js/src/blocks/StateSpaceBlock.tsx"
Task: "Integrate LaTeXRenderer into TransferFunctionBlock in js/src/blocks/TransferFunctionBlock.tsx"
Task: "Integrate LaTeXRenderer into GainBlock in js/src/blocks/GainBlock.tsx"
```

## Parallel Example: User Story 2

```bash
# Launch UI tasks together:
Task: "Add checkbox to ParameterPanel in js/src/components/ParameterPanel.tsx"
Task: "Add LaTeX input field to ParameterPanel in js/src/components/ParameterPanel.tsx"

# Then launch block updates together (after T038-T040):
Task: "Update StateSpaceBlock custom LaTeX in js/src/blocks/StateSpaceBlock.tsx"
Task: "Update TransferFunctionBlock custom LaTeX in js/src/blocks/TransferFunctionBlock.tsx"
Task: "Update GainBlock custom LaTeX in js/src/blocks/GainBlock.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005) - ~30 minutes
2. Complete Phase 2: Foundational (T006-T026) - ~4 hours
   - Write ALL failing tests first
   - Implement utilities to make tests pass
3. Complete Phase 3: User Story 1 (T027-T037) - ~3 hours
4. **STOP and VALIDATE**: Test User Story 1 independently with quickstart scenarios 1, 3, 4, 6
5. Deploy/demo MVP: All blocks render mathematical notation automatically

**MVP Scope**: 58 tasks total (Setup + Foundational + US1)
**Estimated Time**: ~8 hours
**Value Delivered**: Professional mathematical notation for all blocks, no configuration needed

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (tests failing, utilities scaffolded)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Default LaTeX rendering)
3. Add User Story 2 → Test independently → Deploy/Demo (Custom LaTeX capability)
4. Add Polish → Final validation → Production release

### Test-Driven Workflow (Constitution Requirement)

Per constitution Principle III (TDD is NON-NEGOTIABLE):

1. **Red Phase**: Write failing tests (T008-T026 in Foundational)
2. **Green Phase**: Implement utilities to make tests pass (T006-T007, T014-T017)
3. **User Story 1**: Tests already written in Foundational, verify they pass (T034-T037)
4. **User Story 2**: Write failing integration tests (T047-T048), then implement (T038-T046), verify pass (T049-T050)

---

## Task Summary

- **Total Tasks**: 58
- **Setup (Phase 1)**: 5 tasks
- **Foundational (Phase 2)**: 21 tasks (including 18 test tasks)
- **User Story 1 (Phase 3)**: 21 tasks (MVP)
- **User Story 2 (Phase 4)**: 13 tasks
- **Polish (Phase 5)**: 8 tasks

**Tasks by Type**:
- Tests: 23 tasks (40% - reflects TDD requirement)
- Implementation: 35 tasks (60%)

**Parallel Opportunities**: 39 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- **US1**: Create diagram with StateSpace, TransferFunction, Gain blocks → Verify LaTeX renders without errors → No configuration needed
- **US2**: Enable checkbox → Enter custom LaTeX → Verify custom content displayed → Test Python API → Verify persistence

**Suggested MVP Scope**: Setup + Foundational + User Story 1 (47 tasks, ~8 hours, delivers default LaTeX rendering for all blocks)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Constitution requires TDD: Tests MUST be written FIRST and FAIL before implementation
- Each user story is independently completable and testable
- Verify tests fail (Red) before implementing (Green)
- Commit after each logical task group
- Stop at any checkpoint to validate story independently
- Format validation: ALL tasks follow checklist format with checkbox, ID, optional [P], required [Story] for US phases, and file paths
