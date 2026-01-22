<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Editable Block Labels in Parameter Panel

**Branch**: `013-editable-block-labels` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-editable-block-labels/spec.md`

## Summary

Replace the static "Type: block_type_name" display in the Parameter Panel with an editable label field that allows users to rename blocks directly from the panel interface. Label changes will propagate to the Python Diagram object via existing traitlet sync mechanisms and update the canvas display (when label_visible is true). The implementation leverages the existing registry pattern for parameter editors and follows established patterns for label editing (Enter/blur to commit, Escape to cancel, whitespace trimming).

**Technical Approach**: Add a shared label editor component to the Parameter Panel header that appears for all block types using the panel (Gain, TransferFunction, StateSpace, IOMarker). Use existing `updateBlockLabel` action and `diagram.update_block_label()` backend method for persistence. No new Python API required.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Pydantic (schema validation)
**Storage**: JSON diagram files (existing persistence via Pydantic schemas)
**Testing**: Vitest 2.1.9 + React Testing Library (frontend), pytest (backend)
**Target Platform**: Jupyter Notebook/Lab environment (browser-based UI + Python kernel)
**Project Type**: Web (TypeScript frontend + Python backend with anywidget bridge)
**Performance Goals**: <50ms label persistence to Python backend, <100ms canvas update latency
**Constraints**: No increase in Parameter Panel vertical height, maintain compact layout
**Scale/Scope**: 4 block types with Parameter Panel support (Gain, TransferFunction, StateSpace, IOMarker)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity Over Features ✅ PASS

- **Reuses existing infrastructure**: Uses established `updateBlockLabel` action, `diagram.update_block_label()` method, and traitlet sync mechanism
- **No new abstractions**: Leverages existing Parameter Panel registry pattern and ParameterEditorProps interface
- **Minimal scope**: Label editing only, no changes to visibility toggle or canvas double-click editing
- **Justification**: Feature adds user value (panel-based label editing) while reusing 100% of existing label update infrastructure

### Principle II: Python Ecosystem First ✅ PASS

- **Open format persistence**: Labels stored in JSON diagram files via Pydantic schemas (no lock-in)
- **Jupyter-native**: Works within existing anywidget framework for notebook integration
- **User data ownership**: Labels are plain text attributes in user-controlled diagram files

### Principle III: Test-Driven Development ✅ PASS

- **Frontend tests**: Vitest + React Testing Library for label input component (Enter/blur/Escape, whitespace handling)
- **Backend tests**: pytest for `diagram.update_block_label()` (already exists, verify edge cases)
- **Integration tests**: Verify label sync from Parameter Panel → Python → canvas display
- **TDD commitment**: Tests written first for new LabelEditor component and edge case handling (empty labels, special characters)

### Principle IV: Clean Separation of Concerns ✅ PASS

- **UI-independent logic**: Label validation (trim, normalize whitespace) can be tested without React
- **Backend agnostic to UI**: `diagram.update_block_label()` has no knowledge of Parameter Panel or canvas
- **Clear boundaries**: Parameter Panel (presentation) → sendAction (transport) → widget._handle_update_block_label (dispatch) → diagram.update_block_label (domain logic)

### Principle V: User Experience Standards ✅ PASS

- **Performance targets as requirements**: <50ms persistence, <100ms canvas update (SC-001, SC-002)
- **Immediate usability**: Standard text input controls (select-all, cut/copy/paste), Enter/Escape keyboard shortcuts
- **Compact layout**: No vertical height increase constraint (SC-005) ensures panel remains space-efficient
- **Speed prioritized**: No loading spinners or optimistic updates (labels small enough for instant sync)

**GATE RESULT**: ✅ PASS - All 5 principles satisfied with no violations

## Project Structure

### Documentation (this feature)

```text
specs/013-editable-block-labels/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (Block Label entity)
├── quickstart.md        # Phase 1 output (test scenarios)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Existing Lynx structure (web application: TypeScript frontend + Python backend)

# Frontend (TypeScript/React)
js/
├── src/
│   ├── components/
│   │   └── ParameterPanel.tsx              # [MODIFY] Add label editor section
│   ├── blocks/
│   │   ├── shared/
│   │   │   ├── components/
│   │   │   │   ├── EditableLabel.tsx       # [REUSE] Existing component (canvas)
│   │   │   │   └── LabelEditor.tsx         # [NEW] Parameter panel label editor
│   │   │   └── hooks/
│   │   │       └── useBlockLabel.ts        # [REUSE] Existing hook
│   │   ├── gain/
│   │   │   └── GainParameterEditor.tsx     # [NO CHANGE] Uses new panel header
│   │   ├── transfer_function/
│   │   │   └── TransferFunctionParameterEditor.tsx  # [NO CHANGE]
│   │   ├── state_space/
│   │   │   └── StateSpaceParameterEditor.tsx        # [NO CHANGE]
│   │   └── io_marker/
│   │       └── IOMarkerParameterEditor.tsx          # [NO CHANGE]
│   └── utils/
│       └── traitletSync.ts                 # [REUSE] Existing sendAction()
└── test/
    └── components/
        └── LabelEditor.test.tsx            # [NEW] Vitest tests

# Backend (Python)
src/lynx/
├── blocks/
│   └── base.py                             # [REUSE] Block.label attribute (exists)
├── diagram.py                              # [REUSE] update_block_label() method (exists)
└── widget.py                               # [REUSE] _handle_update_block_label() (exists)

tests/
└── test_diagram.py                         # [EXTEND] Add label edge case tests
```

**Structure Decision**: Reuse existing web application structure (js/ for frontend, src/lynx/ for backend). The feature requires:
1. One new component (`LabelEditor.tsx`) for Parameter Panel label editing
2. Modifications to `ParameterPanel.tsx` to add label editor section above block-specific editors
3. No new Python code (reuses existing `update_block_label()` infrastructure)
4. Tests for new component and edge cases

## Complexity Tracking

> **No violations** - Constitution Check passed all principles without exceptions.

This table intentionally left empty (no unjustified complexity).

---

## Phase 0 Summary: Research Complete ✅

**Output**: [research.md](./research.md)

**Key Decisions**:
1. **Component placement**: Label editor as first section in scrollable content area (maintains visual hierarchy, no height increase)
2. **Component design**: New `LabelEditor` component (different interaction model from canvas `EditableLabel`)
3. **Validation strategy**: Frontend normalization (whitespace) + backend validation (empty → ID)
4. **Action reuse**: Existing `updateBlockLabel` action (zero backend changes)
5. **Focus behavior**: Standard React cleanup (uncommitted edits lost on panel close)
6. **Testing strategy**: Unit tests (LabelEditor) + integration tests (full sync flow) + backend edge cases

**NEEDS CLARIFICATION Resolution**: All technical unknowns resolved through codebase exploration.

---

## Phase 1 Summary: Design & Contracts Complete ✅

**Outputs**:
- [data-model.md](./data-model.md) - Block Label entity lifecycle and validation rules
- [quickstart.md](./quickstart.md) - 21 test scenarios (13 acceptance + 5 edge cases + 3 performance)
- Agent context updated: `CLAUDE.md` includes TypeScript 5.9, React 19.2.3, Pydantic technologies

**Contracts**: N/A (no new API endpoints - UI-only feature using existing backend methods)

**Data Model Highlights**:
- No schema changes (reuses existing `Block.label` attribute)
- Three-state lifecycle: default (label=id) → custom (label≠id) → reverted (label=id)
- Validation rules: trim whitespace, empty→id, normalize newlines/tabs, accept Unicode
- Performance: O(1) operations, <50ms persistence, <100ms canvas update

**Test Scenario Coverage**:
- US1 (Replace Type Display): 3 scenarios
- US2 (Edit Label): 5 scenarios
- US3 (Label Independence): 4 scenarios
- Edge cases: 5 scenarios (duplicates, long labels, special chars, panel closure, concurrent edits)
- Performance: 3 scenarios (SC-001, SC-002, SC-005 validation)

---

## Constitution Re-Check (Post-Design) ✅

**Principle I: Simplicity Over Features** - ✅ PASS (no change)
- Design confirms 100% infrastructure reuse (no new Python code)
- Single new component (`LabelEditor.tsx`, ~80 lines estimated)
- Modification to one existing component (`ParameterPanel.tsx`, +15 lines estimated)

**Principle II: Python Ecosystem First** - ✅ PASS (no change)
- Data model confirms JSON persistence via Pydantic (open format)
- No proprietary formats or vendor dependencies introduced

**Principle III: Test-Driven Development** - ✅ PASS (no change)
- Quickstart provides 21 concrete test scenarios with validation code
- TDD workflow documented in research.md Decision 6
- Test coverage: 8 unit tests (LabelEditor) + 6 integration tests (ParameterPanel) + 3 backend tests (diagram.py)

**Principle IV: Clean Separation of Concerns** - ✅ PASS (no change)
- Data model confirms clean boundaries: UI → action → widget → diagram
- Validation logic split: frontend (UX normalization) vs backend (business rules)
- `LabelEditor` component testable independently of React Flow canvas

**Principle V: User Experience Standards** - ✅ PASS (no change)
- Performance targets validated in quickstart scenarios (50ms persistence, 100ms canvas update)
- Compact layout constraint verified (<280px panel height, no increase from current)
- Standard interaction patterns (Enter/blur/Escape) documented in quickstart

**FINAL GATE RESULT**: ✅ PASS - All 5 principles satisfied, design maintains constitutional compliance

---

## Next Steps

**Phase 2**: Run `/speckit.tasks` to generate dependency-ordered task breakdown from this plan.

**Implementation Order** (derived from design):
1. **Phase 1 (Setup)**: Test infrastructure setup (Vitest config verified)
2. **Phase 2 (Foundation)**: TDD - Write failing tests for LabelEditor component
3. **Phase 3 (US1)**: Implement LabelEditor component (replace Type display)
4. **Phase 4 (US2)**: Add edit functionality (Enter/blur/Escape, whitespace handling)
5. **Phase 5 (US3)**: Verify label independence from visibility toggle (integration tests)
6. **Phase 6 (Polish)**: Edge case handling + performance validation

**Estimated Scope**:
- New code: ~100 lines (LabelEditor component + tests)
- Modified code: ~15 lines (ParameterPanel integration)
- Test code: ~250 lines (unit + integration tests)
- Total: ~365 lines (minimal, focused change)

