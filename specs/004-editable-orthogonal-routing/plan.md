<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Editable Orthogonal Routing

**Branch**: `004-editable-orthogonal-routing` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-editable-orthogonal-routing/spec.md`

## Summary

Add user-editable orthogonal connection routing to the Lynx block diagram editor. Users can click on connections to select them, then drag horizontal segments vertically (or vertical segments horizontally) to customize routing. Waypoints are created automatically when segments are dragged, persisted with the diagram, and support undo/redo. The feature replaces React Flow's default `smoothstep` edge with a custom `OrthogonalEditableEdge` component.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget, Tailwind CSS v4
**Storage**: JSON diagram files (existing persistence layer via Pydantic)
**Testing**: Vitest 2.1.8 (frontend), pytest 9.0 (backend)
**Target Platform**: Jupyter notebooks (browser-based widget)
**Project Type**: Web application (frontend + backend widget)
**Performance Goals**: Responsive routing operations with 50+ connections (no perceptible lag during drag)
**Constraints**: Maintain orthogonal-only routing (no diagonals), grid snapping at 20px
**Scale/Scope**: Typical diagrams have 10-50 blocks and connections

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity Over Features | ✅ PASS | Feature directly addresses core use case (professional diagram layouts) |
| II. Python Ecosystem First | ✅ PASS | Integrates with existing Jupyter widget; data persists in open JSON format |
| III. Test-Driven Development | ✅ PASS | Tests required for path calculation, drag constraints, persistence |
| IV. Clean Separation of Concerns | ✅ PASS | UI logic in React components, business logic in Python diagram model |
| V. User Experience Standards | ✅ PASS | Matches Simulink UX expectations; performance target defined |

**Gate Result**: PASS - No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/004-editable-orthogonal-routing/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (action payloads)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/lynx/                    # Python backend
├── diagram.py               # Connection class (add waypoints field)
├── widget.py                # Action handler (_handle_update_connection_routing)
└── schema.py                # Pydantic models (ConnectionModel waypoints)

js/src/                      # TypeScript frontend
├── connections/
│   └── OrthogonalEditableEdge.tsx  # NEW: Custom edge with segment dragging
├── utils/
│   └── orthogonalRouting.ts        # NEW: Path calculation utilities
├── hooks/
│   └── useSegmentDrag.ts           # NEW: Segment drag interaction hook
├── DiagramCanvas.tsx               # Update edge type registration
└── utils/traitletSync.ts           # Add updateConnectionRouting action

tests/python/
├── unit/
│   └── test_connection_routing.py  # NEW: Waypoint persistence tests
└── contract/
    └── test_routing_sync.py        # NEW: Frontend-backend sync tests

js/src/
├── connections/
│   └── OrthogonalEditableEdge.test.tsx  # NEW: Component tests
└── utils/
    └── orthogonalRouting.test.ts        # NEW: Path calculation tests
```

**Structure Decision**: Web application structure (frontend/backend) matches existing Lynx architecture. New files follow established patterns (connections/, utils/, hooks/).

## Complexity Tracking

> No violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
