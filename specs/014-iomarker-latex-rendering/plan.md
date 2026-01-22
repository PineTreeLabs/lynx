<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: IOMarker LaTeX Rendering

**Branch**: `014-iomarker-latex-rendering` | **Date**: 2026-01-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/014-iomarker-latex-rendering/spec.md`

## Summary

Redesign IOMarker blocks to follow the LaTeX-rendering pattern used by Gain, TransferFunction, and StateSpace blocks. Replace "Input/Output" text with automatically-managed numeric indices (0, 1, 2...) displayed via LaTeX rendering. Support custom LaTeX override through parameter panel checkbox + text field. Implement Simulink-style automatic renumbering when markers are added, deleted, or manually reordered. Remove Type dropdown from parameter panel (visually obvious from port orientation).

**Technical Approach**: Extend existing LaTeXRenderer component and useCustomLatex hook to IOMarker blocks. Add `index` parameter to Python IOMarker class with automatic assignment logic. Implement automatic renumbering in Diagram class triggered by add_block, delete_block, and update_block_parameter operations.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.9 (frontend)
**Primary Dependencies**:
- Backend: Pydantic (schema validation)
- Frontend: React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), KaTeX 0.16.27 (LaTeX rendering), Tailwind CSS v4
**Storage**: JSON diagram files (existing persistence via Pydantic schemas)
**Testing**: pytest (backend), Vitest 2.1.9 + React Testing Library (frontend)
**Target Platform**: Jupyter notebooks (cross-platform via anywidget)
**Project Type**: Web (TypeScript frontend + Python backend widget)
**Performance Goals**:
- LaTeX rendering <50ms per block for 50-block diagrams
- Index renumbering <20ms for diagrams with <100 markers
**Constraints**:
- Must maintain backward compatibility with existing diagrams (no `index` parameter)
- Must match visual consistency of existing LaTeX-rendered blocks
- Automatic renumbering must be deterministic and reproducible
**Scale/Scope**:
- Typical diagrams: 5-20 IOMarker blocks
- Large diagrams: up to 100 IOMarker blocks
- Frontend: 2 files modified (IOMarkerBlock.tsx, IOMarkerParameterEditor.tsx)
- Backend: 2 files modified (io_marker.py, diagram.py)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Simplicity Over Features ✅
- **Compliance**: Feature simplifies UX by removing Type dropdown and using automatic indexing
- **Rationale**: Reduces user cognitive load - indices are automatic, type is visually obvious from ports
- **Simplicity Win**: Automatic renumbering eliminates validation errors (simpler than error handling + manual fixes)

### II. Python Ecosystem First ✅
- **Compliance**: Maintains JSON diagram persistence (open format), no vendor lock-in
- **Rationale**: Index parameter is backward compatible (auto-assigned if missing)
- **User Data Ownership**: Diagrams remain portable, human-readable JSON

### III. Test-Driven Development (NON-NEGOTIABLE) ✅
- **Compliance**: TDD required for all implementation tasks
- **Test Strategy**:
  - Backend: pytest unit tests for index assignment, renumbering logic, validation
  - Frontend: Vitest component tests for LaTeX rendering, parameter panel, user interactions
  - Integration: End-to-end tests for diagram load/save with indices
- **RED-GREEN-REFACTOR**: Tests written first, fail before implementation, then implementation, then refactor

### IV. Clean Separation of Concerns ✅
- **Compliance**: Business logic (index assignment, renumbering) in Python Diagram class (UI-independent)
- **Presentation**: React components handle only rendering and user events
- **No Leakage**: Renumbering algorithm testable without UI, LaTeX rendering testable in isolation

### V. User Experience Standards ✅
- **Compliance**: Performance targets specified (<50ms LaTeX, <20ms renumbering)
- **Usability**: Immediate visual feedback (real-time index updates), no validation errors to frustrate users
- **Speed**: Automatic indexing faster than manual assignment, graceful degradation (empty LaTeX → show index)

**GATE STATUS**: ✅ **PASS** - All constitution principles satisfied, no violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/014-iomarker-latex-rendering/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (IOMarker entity schema)
├── quickstart.md        # Phase 1 output (test scenarios)
└── checklists/
    └── requirements.md  # Spec quality validation (completed)
```

### Source Code (repository root)

```text
# Backend (Python)
src/lynx/
├── blocks/
│   ├── base.py                  # Block base class (existing, modified for custom_latex)
│   └── io_marker.py             # IOMarker classes (MODIFIED - add index parameter)
├── diagram.py                   # Diagram class (MODIFIED - add renumbering logic)
└── widget.py                    # anywidget traitlet sync (existing, may need index action)

# Frontend (TypeScript)
js/src/
├── blocks/
│   ├── io_marker/
│   │   ├── IOMarkerBlock.tsx              # Block visualization (MODIFIED - LaTeX rendering)
│   │   ├── IOMarkerParameterEditor.tsx    # Parameter panel (MODIFIED - remove Type, add LaTeX)
│   │   └── index.ts
│   └── shared/
│       ├── components/
│       │   └── LaTeXRenderer.tsx          # Existing LaTeX component (REUSED)
│       └── hooks/
│           └── useCustomLatex.ts          # Existing LaTeX hook (REUSED)
└── utils/
    └── traitletSync.ts                    # Python-JS sync (existing, may need index action)

# Tests
tests/                                     # Backend pytest tests (NEW - index tests)
js/src/blocks/io_marker/                  # Frontend Vitest tests (MODIFIED - add LaTeX tests)
```

**Structure Decision**: Hybrid web structure (Python backend + TypeScript frontend) using existing Lynx architecture. Changes are localized to IOMarker-specific files plus Diagram class renumbering logic. Reuses existing LaTeX infrastructure from other blocks (Gain, TransferFunction, StateSpace).

## Complexity Tracking

> **No violations - table not needed**

All constitution principles satisfied without requiring additional complexity or exceptions.

---

## Phase 0: Research ✅

**Completed**: 2026-01-17

**Research Document**: [research.md](research.md)

**Key Decisions**:
1. **RQ-001**: Sequential shift algorithm for Simulink-style renumbering
2. **RQ-002**: Block ID alphabetical order for backward compatibility
3. **RQ-003**: Plain numeric strings for LaTeX index rendering
4. **RQ-004**: Three-section vertical parameter panel layout
5. **RQ-005**: Optimistic UI updates with immediate backend sync

**Best Practices Identified**:
- LaTeX error handling: "Invalid LaTeX" placeholder (existing pattern)
- Empty LaTeX graceful degradation: Display index (clarification answer)
- Comprehensive renumbering test coverage (10 critical test cases)

**All NEEDS CLARIFICATION resolved** ✅

---

## Phase 1: Design & Contracts ✅

**Completed**: 2026-01-17

### Generated Artifacts

1. **[data-model.md](data-model.md)** ✅
   - IOMarker entity schema with attributes, relationships, invariants
   - Index assignment rules (5 rules documented)
   - JSON serialization format
   - Python and TypeScript type definitions
   - Validation rules and migration strategy
   - Performance analysis (O(N) operations, ~270 bytes per block)

2. **[quickstart.md](quickstart.md)** ✅
   - 16 test scenarios across 6 categories
   - TDD execution order (RED-GREEN-REFACTOR)
   - Backend: 10 pytest tests
   - Frontend: 6 Vitest tests
   - Performance benchmarks (TS-005)
   - Integration test (TS-006)
   - Validation checklist

3. **Agent Context Updated** ✅
   - Added to CLAUDE.md Active Technologies section:
     - Language: Python 3.11+ (backend), TypeScript 5.9 (frontend)
     - Database: JSON diagram files (existing persistence via Pydantic schemas)

### No API Contracts Generated

**Rationale**: This is a UI/widget feature, not a web API feature. Data flows through:
- **Frontend → Backend**: anywidget traitlet sync (existing mechanism)
- **Backend → Frontend**: State updates via widget model (existing mechanism)

No REST/GraphQL endpoints needed - all communication via anywidget's existing bidirectional sync.

---

## Constitution Check (Post-Design) ✅

**Re-evaluation after Phase 1 design artifacts**

### I. Simplicity Over Features ✅
- **Design Verification**: Renumbering algorithm is O(N) sequential shift, no complex data structures
- **Code Reuse**: LaTeXRenderer and useCustomLatex reused verbatim from existing blocks
- **No New Patterns**: Follows existing parameter panel registry pattern from features 002/013

### II. Python Ecosystem First ✅
- **Open Format**: JSON diagram persistence unchanged, human-readable
- **No Lock-in**: Diagrams portable, backward compatible with older Lynx versions
- **Data Ownership**: Users control diagram files, indices optional (graceful degradation)

### III. Test-Driven Development ✅
- **RED Phase**: 16 test scenarios documented in quickstart.md (must fail first)
- **Coverage Target**: ≥80% for io_marker.py, diagram.py, IOMarkerBlock.tsx, IOMarkerParameterEditor.tsx
- **Test Categories**: Unit (backend/frontend), integration, performance
- **Execution Order**: Backend tests → Frontend tests → Integration (documented)

### IV. Clean Separation of Concerns ✅
- **Business Logic**: Renumbering in diagram.py (UI-independent, testable)
- **Presentation**: React components render state, emit events
- **No Leakage**: TypeScript has no renumbering logic (defers to Python)
- **Data Flow**: Unidirectional (Python source of truth → Frontend reflects state)

### V. User Experience Standards ✅
- **Performance Targets Met**:
  - LaTeX rendering: <50ms/block (TS-005.1)
  - Renumbering: <20ms for 100 markers (TS-005.2)
- **Usability**: Immediate visual feedback (optimistic UI), graceful degradation (empty LaTeX)
- **No Friction**: Automatic renumbering eliminates validation errors

**GATE STATUS**: ✅ **PASS** - All principles satisfied post-design. No rework needed.

---

## Ready for Implementation

**Next Command**: `/speckit.tasks` - Generate actionable task list from plan + test scenarios

**Implementation Strategy**:
1. Backend TDD (RED → GREEN): io_marker.py + diagram.py
2. Frontend TDD (RED → GREEN): IOMarkerBlock.tsx + IOMarkerParameterEditor.tsx
3. Integration tests (REFACTOR phase)
4. Performance validation
5. Documentation updates

**Estimated Scope**:
- Backend: ~150 LOC (renumbering logic + tests)
- Frontend: ~100 LOC (LaTeX integration + parameter panel)
- Tests: ~300 LOC total (16 test scenarios)
- Total: ~550 LOC added/modified
