<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Simulink-Style Port Markers

**Branch**: `003-simulink-port-markers` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-simulink-port-markers/spec.md`

## Summary

Replace current circular dot port markers (8px diameter circles in primary-600) with Simulink-style triangular markers on block ports. Input ports will display inward-pointing triangles, output ports will display outward-pointing triangles. Markers will be visible only on unconnected ports, disappear during drag-and-drop hover interactions, and maintain correct directional semantics when blocks are flipped horizontally.

Technical approach: Extend React Flow's Handle component styling to render SVG triangular markers positioned on block edges, with visibility controlled by connection state from the Python backend's diagram model.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Tailwind CSS v4
**Storage**: JSON diagram files (existing persistence layer)
**Testing**: pytest (Python backend), vitest (TypeScript frontend - to be confirmed in research phase)
**Target Platform**: Jupyter Notebook / JupyterLab (via anywidget), modern browsers (Chrome, Firefox, Safari)
**Project Type**: Web-based Jupyter widget (frontend TypeScript/React + Python backend)
**Performance Goals**: <100ms marker rendering/update latency, <50ms port visibility toggle on connection state change, 60fps smooth interactions during drag operations
**Constraints**: Must integrate with existing React Flow Handle system, must not interfere with connection drag-and-drop UX, must respect existing theming (primary-600 color), must work with existing block flip transformation logic (scaleX)
**Scale/Scope**: 5 block types (Gain, TransferFunction, StateSpace, Sum, IOMarker), ~10-50 blocks per typical diagram

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity Over Features ✅

- **Status**: PASS
- **Justification**: Feature focuses exclusively on visual marker replacement - no new functionality beyond port visualization. Extends existing Handle rendering without adding architectural complexity.

### Principle II: Python Ecosystem First ✅

- **Status**: PASS
- **Justification**: Changes are frontend-only visual enhancements. Diagram data remains in JSON format (no format changes). No vendor lock-in introduced.

### Principle III: Test-Driven Development (NON-NEGOTIABLE) ✅

- **Status**: PASS
- **Resolution**: Frontend test infrastructure exists (Vitest 2.1.8 + React Testing Library 16.1.0). TDD workflow APPLIES - component tests must be written before implementation.
- **Test Framework**: vitest with jsdom environment, @testing-library/react for component testing
- **Existing Tests**: 56 tests in utils layer (latexGeneration, numberFormatting)

### Principle IV: Clean Separation of Concerns ✅

- **Status**: PASS
- **Justification**: Port marker rendering is presentation logic (frontend). Connection state remains in Python backend domain model. No business logic mixing.

### Principle V: User Experience Standards ✅

- **Status**: PASS
- **Justification**: Performance targets specified (<100ms rendering, <50ms visibility toggle). Feature directly improves usability by providing clearer port direction feedback. No breaking changes to existing UX.

## Project Structure

### Documentation (this feature)

```text
specs/003-simulink-port-markers/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (marker state model)
├── quickstart.md        # Phase 1 output (test scenarios)
└── contracts/           # Phase 1 output (component interfaces)
    └── PortMarker.yaml  # PortMarker component contract
```

### Source Code (repository root)

```text
js/                                    # Frontend (TypeScript/React)
├── src/
│   ├── components/
│   │   └── PortMarker.tsx             # NEW: Triangular marker component
│   ├── blocks/
│   │   ├── GainBlock.tsx              # MODIFIED: Use PortMarker on handles
│   │   ├── TransferFunctionBlock.tsx  # MODIFIED: Use PortMarker on handles
│   │   ├── StateSpaceBlock.tsx        # MODIFIED: Use PortMarker on handles
│   │   ├── SumBlock.tsx               # MODIFIED: Use PortMarker on handles
│   │   └── IOMarkerBlock.tsx          # MODIFIED: Use PortMarker on handles
│   ├── hooks/
│   │   ├── useFlippableBlock.ts       # MODIFIED: Export marker orientation logic
│   │   └── usePortMarkerVisibility.ts # NEW: Visibility logic hook
│   ├── utils/
│   │   └── portMarkerGeometry.ts      # NEW: Triangle positioning calculations
│   ├── styles.css                     # MODIFIED: Add marker-specific classes
│   └── DiagramCanvas.tsx              # MODIFIED: Handle drag hover state
└── tests/                             # Frontend tests (if infrastructure exists)
    └── components/
        └── PortMarker.test.tsx        # NEW: Marker rendering tests

src/lynx/                              # Backend (Python) - NO CHANGES EXPECTED
└── (no modifications required - connection state already tracked)
```

**Structure Decision**: Frontend-only changes. All modifications in `js/src/` directory. New `PortMarker` component encapsulates triangular marker rendering logic. Existing block components modified to use PortMarker instead of default React Flow Handle styling. Backend diagram state remains unchanged (connection tracking already exists).

## Complexity Tracking

> **No violations** - All constitution principles pass after research phase resolution.

---

## Phase 0: Research - ✅ COMPLETE

**Output**: [research.md](./research.md)

**Key Findings**:
- Frontend test infrastructure EXISTS (Vitest 2.1.8 + React Testing Library) → TDD applies
- React Flow Handle supports children → Wrap SVG triangles in Handle components
- Connection state derivable from edges array → No backend changes needed
- Drag hover detection via React Flow's `isConnectableEnd` prop
- SVG `<polygon>` with calculated points → Simple, performant triangle rendering

**Technical Decisions Documented**: 6 research questions resolved, all unknowns from Technical Context addressed.

---

## Phase 1: Design & Contracts - ✅ COMPLETE

**Outputs**:
- [data-model.md](./data-model.md) - PortMarker component props, connection state derivation, geometry calculations
- [contracts/PortMarker.yaml](./contracts/PortMarker.yaml) - Component interface contract with behavior spec
- [quickstart.md](./quickstart.md) - Comprehensive test scenarios (automated + manual)
- [CLAUDE.md](../../CLAUDE.md) - Updated with TypeScript 5.9, React 19.2.3, React Flow 11.11.4 (via agent context script)

**Data Model Summary**:
- **PortMarker**: Pure presentational component (no internal state)
- **PortConnectionState**: Derived from React Flow edges array at runtime
- **TriangleGeometry**: Utility for SVG polygon point calculation
- **No Backend Changes**: All state derived from existing diagram model

**Contract Highlights**:
- 6 props (direction, isConnected, isFlipped, isDragTarget, size, className)
- 4 visibility states (VISIBLE, HIDDEN_CONNECTED, HIDDEN_DRAG, HIDDEN_BOTH)
- 2 orientations (input left-pointing, output right-pointing)
- Type-safe TypeScript interface

---

## Constitution Check - RE-EVALUATION (Post-Design)

All principles remain **PASS** after design phase:

- **Principle I** ✅: Simplicity maintained - no architectural complexity added
- **Principle II** ✅: Python ecosystem unchanged - frontend-only visual enhancement
- **Principle III** ✅: TDD workflow confirmed - vitest infrastructure ready
- **Principle IV** ✅: Separation preserved - presentation logic in frontend, domain logic in backend
- **Principle V** ✅: UX standards met - performance targets achievable with standard React rendering

---

## Next Phase

**Phase 2**: Task Generation (NOT part of `/speckit.plan` command)

Run `/speckit.tasks` to generate `tasks.md` with:
- TDD workflow (test files first, implementation second)
- Dependency-ordered tasks across 3 user stories
- Parallelizable tasks marked with [P]
- File-level implementation breakdown
