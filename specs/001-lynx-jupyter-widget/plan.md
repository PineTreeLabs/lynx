<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Lynx Block Diagram Widget

**Branch**: `001-lynx-jupyter-widget` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-lynx-jupyter-widget/spec.md`

## Summary

Develop Lynx, a Jupyter widget for creating and editing control system block diagrams interactively. Engineers can drag-and-drop blocks (Transfer Function, State Space, Gain, Sum, I/O), connect them, configure parameters using Python expressions, and save diagrams to git-friendly JSON. The widget validates diagrams against control theory rules (algebraic loops, connection constraints) in real-time and provides a reproducible workflow for classical SISO control system design.

**Technical Approach**: anywidget framework provides Jupyter integration with Python ↔ JavaScript sync via traitlets. React Flow handles diagram rendering and interactions. Python backend manages control theory validation, expression evaluation, and JSON persistence. Clean separation: Python owns business logic (validation, graph operations), JavaScript owns presentation (React Flow UI).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
  - Python: anywidget, numpy, traitlets
  - JavaScript: React 18+, TypeScript 5+, React Flow, Vite, Tailwind CSS
**Storage**: File system (JSON diagrams saved via explicit save/load)
**Testing**: pytest (backend), Vitest (frontend), contract tests for traitlet sync
**Target Platform**: Jupyter environments (JupyterLab, classic notebook, VSCode)
**Project Type**: Jupyter widget (frontend + backend with traitlet synchronization)
**Performance Goals**:
  - <100ms validation feedback
  - Smooth rendering/interaction with 50+ blocks
  - <1 second save/load operations
**Constraints**:
  - No localStorage (breaks Jupyter paradigm)
  - No direct file access from frontend
  - All state via Python/traitlets
  - Matrix eval() in Python only (security constraint)
**Scale/Scope**:
  - 50-100 block diagrams (typical control examples)
  - Single user per notebook session
  - 5 block types in MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity Over Features

**Status**: ✅ PASS

- MVP focuses on 5 essential block types (TF, SS, Gain, Sum, I/O)
- Explicitly excludes simulation, visualization, algebra, LaTeX rendering
- JSON persistence approach is simplest (explicit save/load vs. live modification)
- Grid snapping is optional, parameters use simple text inputs

### Principle II: Python Ecosystem First

**Status**: ✅ PASS

- anywidget framework ensures Jupyter compatibility
- JSON format is human-readable, git-friendly
- Matrix expressions leverage existing numpy workflow
- No vendor lock-in - open JSON format
- No localStorage - all state via Python

### Principle III: Test-Driven Development (NON-NEGOTIABLE)

**Status**: ✅ PASS

- Plan includes comprehensive testing strategy:
  - Unit tests: Validation logic, graph operations (80% coverage target)
  - Contract tests: Traitlet synchronization Python ↔ JavaScript
  - Integration tests: End-to-end user workflows
- Tests MUST be written first (Red-Green-Refactor enforced in tasks)

### Principle IV: Clean Separation of Concerns

**Status**: ✅ PASS

- Python: Validation, graph topology, expression evaluation, persistence
- JavaScript: React Flow rendering, UI interactions
- No control theory logic in React components
- Clear boundary via traitlets interface

### Principle V: User Experience Standards

**Status**: ✅ PASS

- Performance targets are requirements: <100ms validation, 50+ blocks smooth
- Keyboard shortcuts for common operations
- Undo/redo for experimentation
- Clear error messages for validation failures
- Grid snapping optional (users choose)

**Gate Result**: ✅ ALL PRINCIPLES SATISFIED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-lynx-jupyter-widget/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (entities, relationships)
├── quickstart.md        # Phase 1 output (development guide)
└── checklists/
    └── requirements.md  # Spec quality validation
```

### Source Code (repository root)

```text
src/
└── lynx/                 # Python package (UV src layout)
    ├── __init__.py
    ├── widget.py         # anywidget integration, traitlet definitions
    ├── diagram.py        # Diagram class, save/load logic
    ├── static/           # Bundled frontend assets (output from Vite)
    ├── blocks/           # Block type definitions
    │   ├── __init__.py
    │   ├── base.py       # Base block class
    │   ├── transfer_function.py
    │   ├── state_space.py
    │   ├── gain.py
    │   ├── sum.py
    │   └── io_marker.py
    ├── validation/       # Control theory validation
    │   ├── __init__.py
    │   ├── graph_validator.py  # Cycle detection, connectivity
    │   ├── algebraic_loop.py   # Detect dynamics-free cycles
    │   └── connection_rules.py # Port constraints
    ├── persistence/      # JSON save/load
    │   ├── __init__.py
    │   ├── schema.py     # JSON schema version management
    │   ├── serializer.py # Diagram → JSON
    │   └── deserializer.py # JSON → Diagram
    └── expression_eval.py # Safe expression evaluation in notebook namespace

js/                       # Frontend (anywidget convention)
├── src/
│   ├── index.tsx         # Widget entry point
│   ├── DiagramCanvas.tsx # Main React Flow component
│   ├── blocks/           # React components for each block type
│   │   ├── TransferFunctionBlock.tsx
│   │   ├── StateSpaceBlock.tsx
│   │   ├── GainBlock.tsx
│   │   ├── SumBlock.tsx
│   │   └── IOMarkerBlock.tsx
│   ├── connections/      # Connection rendering & validation UI
│   │   └── ConnectionLine.tsx
│   ├── palette/          # Block palette UI
│   │   └── BlockPalette.tsx
│   ├── parameters/       # Parameter editing UI
│   │   ├── ParameterPanel.tsx
│   │   └── MatrixDisplay.tsx  # Shows expression + value
│   ├── state/            # State management
│   │   ├── useDiagramState.ts
│   │   ├── useUndo.ts
│   │   └── useValidation.ts
│   └── utils/
│       └── traitletSync.ts  # Sync helpers
├── package.json
├── vite.config.ts
└── tailwind.config.js

tests/
├── python/               # Backend tests
│   ├── unit/
│   │   ├── test_blocks.py
│   │   ├── test_validation.py
│   │   └── test_persistence.py
│   ├── integration/
│   │   └── test_diagram_workflow.py
│   └── contract/
│       └── test_traitlet_sync.py
└── js/                   # Frontend tests
    ├── unit/
    │   ├── blocks.test.tsx
    │   └── validation.test.ts
    └── integration/
        └── diagram.test.tsx

pyproject.toml            # Python package config (UV-managed)
uv.lock                   # UV dependency lock file
README.md
LICENSE
```

**Structure Decision**: Jupyter widget architecture using **UV's modern src layout** for Python (`src/lynx/`) and standard anywidget convention for frontend (`js/`). Python handles business logic and persistence. JavaScript handles rendering via React Flow. Vite bundles frontend to `src/lynx/static/` for anywidget distribution. Tests mirror source structure with unit/integration/contract separation. **Dependency management via UV** (uv.lock ensures reproducible builds).

**anywidget Integration Note**: Implementation uses the **raw anywidget API** (`render({ model, el })`) with a custom React context provider, rather than `@anywidget/react` helper functions. This provides better control over model passing and works reliably with Vite's library bundling mode. The `@anywidget/react` package is kept as a dependency for potential future use, but the core integration is manual to ensure model context is properly provided to all React components.

## Implementation Strategy & Task Sequencing

### Phased Delivery Approach

Implementation follows user story priorities (P1 → P5) with incremental capability delivery. Each phase builds on the previous, with "walking skeleton" approach proving architecture early.

### Phase Breakdown by User Story

#### Walking Skeleton (Minimal Viable Slice)

**Goal**: Prove end-to-end architecture (Python ↔ traitlets ↔ anywidget ↔ React ↔ React Flow)

**Scope**:
- Gain block only (simplest block type - single scalar parameter K)
- Input/Output markers (no parameters - needed for complete diagrams)
- Basic canvas rendering (no connections yet)
- **Result**: Can create minimal diagram (Input → Gain → Output) visually

**Rationale**: Three block types (Gain + I/O) is minimum to prove:
- Block rendering works (Gain)
- Multiple block types coexist (Gain vs I/O)
- Can create a semantically complete diagram (has input and output)

---

#### Phase 1: Interactive Block Diagram Creation (User Story P1)

**Scope Decisions**:

1. **Block Types in P1**:
   - Gain block (scalar K parameter)
   - Input/Output markers (no parameters)
   - Transfer Function (num/den array parameters)
   - Sum block (signs array parameter)
   - State Space (matrix parameters - **basic arrays only, no expression eval**)

2. **Parameter Editing in P1**:
   - **Basic text input only** (user enters `[1, 2, 3]` as string, parsed to array)
   - **No expression evaluation** (no `np.eye(2)` or variable references)
   - **No hybrid storage** (value only, no expression field)
   - Sufficient to create functional diagrams with literal values

3. **Validation in P1**:
   - **Connection constraints ONLY** (one wire per input port, unlimited output fan-out)
   - **No algebraic loop detection** (deferred to P3)
   - **No system completeness check** (deferred to P3)
   - Prevents obviously broken diagrams (double-connected inputs)

4. **Save/Load in P1**:
   - **Basic JSON write/read** (happy path only)
   - Serialize blocks and connections to JSON
   - Deserialize JSON to restore diagram
   - **No edge case handling** (missing files, malformed JSON, schema versioning - deferred to P4)

**P1 Deliverable**: User can create diagrams with all 5 block types, connect them (with connection validation), and save/load (basic).

---

#### Phase 2: Block Parameter Configuration (User Story P2)

**Scope Decisions**:

1. **Expression Evaluation** (matrix parameters only):
   - State Space blocks: Evaluate `np.eye(2)` or variable references (e.g., `A`)
   - **Hybrid storage**: Store both expression and resolved value
   - Error handling for evaluation failures

2. **Simulink-Style UI**:
   - Display both expression (`np.eye(2)`) and current value (`[[1,0],[0,1]]`)
   - MatrixDisplay component

3. **Scalar/Array Parameters**:
   - Keep simple text input from P1 (no expression eval needed for TF numerator/denominator)

**P2 Deliverable**: State Space blocks support numpy expressions and variable references with hybrid storage.

---

#### Phase 3: Control Theory Validation (User Story P3)

**Scope Decisions**:

1. **Algebraic Loop Detection**:
   - Detect cycles in graph
   - Check if cycle contains at least one dynamic block (TF or SS)
   - Error if pure gain/sum cycle

2. **System Completeness**:
   - Check for at least one Input and one Output marker
   - **Warning only** (not blocking - can still save)

3. **Disconnected Blocks**:
   - Detect blocks with no connections
   - **Warning only**

**Note**: Connection constraints already implemented in P1.

**P3 Deliverable**: Full control theory validation (algebraic loops, completeness, disconnected warnings).

---

#### Phase 4: Diagram Persistence & Reproducibility (User Story P4)

**Scope Decisions** (edge cases deferred from P1):

1. **Missing Variable Handling**:
   - On load, try to re-evaluate expressions
   - If variable missing, use stored value + display warning

2. **JSON Schema Versioning**:
   - Include `version: "1.0.0"` in JSON
   - Ignore unknown fields (forward compatibility)
   - Provide defaults for missing fields (backward compatibility)

3. **Error Handling**:
   - File not found errors
   - Malformed JSON errors
   - Schema version mismatch handling

**P4 Deliverable**: Robust save/load with reproducibility guarantees and edge case handling.

---

#### Phase 5: User Experience Essentials (User Story P5)

**Scope Decisions**:

1. **Undo/Redo**:
   - State history tracking (immutable state pattern from P1 enables this)
   - Keyboard shortcuts (Ctrl+Z, Ctrl+Y)
   - In-session only (history not persisted)

2. **Keyboard Shortcuts**:
   - Add block (e.g., "G" for Gain, "T" for Transfer Function)
   - Delete selected block (Delete/Backspace)
   - Save (Ctrl+S triggers Python save dialog)

3. **Grid Snapping**:
   - 20-pixel grid
   - Toggleable on/off
   - Visual grid overlay (optional)

**P5 Deliverable**: Full UX polish (undo/redo, shortcuts, grid snapping).

---

### Block Type Implementation Order

**Rationale**: Simplest → most complex, each adds new capability

1. **Gain** (P1 - walking skeleton): Scalar parameter, proves basic blocks work
2. **Input/Output** (P1 - walking skeleton): No parameters, needed for complete diagrams
3. **Sum** (P1): Array parameter (signs), proves multi-input ports
4. **Transfer Function** (P1): Two array parameters (num/den), proves array handling
5. **State Space** (P1 basic, P2 full): Matrix parameters (P1: arrays only, P2: + expression eval)

---

### Frontend Component Dependencies

**Implementation Order** (bottom-up):

1. **index.tsx** + **traitletSync.ts**: Widget foundation, proves rendering
2. **DiagramCanvas.tsx**: Empty React Flow canvas
3. **GainBlock.tsx**: First block component (proves block rendering)
4. **IOMarkerBlock.tsx**: Second block type (proves multiple types coexist)
5. **ConnectionLine.tsx**: Can connect blocks (proves interactions work)
6. **BlockPalette.tsx**: Can add blocks via UI (not just programmatically)
7. **ParameterPanel.tsx**: Basic text input for parameters (P1)
8. **SumBlock.tsx**, **TransferFunctionBlock.tsx**: Remaining P1 blocks
9. **StateSpaceBlock.tsx**: Arrays only in P1
10. **MatrixDisplay.tsx**: Expression + value display (P2)
11. **ValidationPanel.tsx**: Show errors/warnings (P3)
12. **useUndo.ts** + keyboard shortcuts: Undo/redo (P5)

---

### Testing Strategy (Test-First Order)

**Bottom-Up Approach**:

1. **Python Unit Tests**: Block models, validation logic (fastest feedback)
2. **Python Contract Tests**: Traitlet sync (proves Python ↔ JavaScript agreement)
3. **JavaScript Unit Tests**: React components in isolation
4. **JavaScript Integration Tests**: Component interactions
5. **End-to-End Tests**: Full user workflows in Jupyter notebook

**TDD Workflow** (enforced):
- RED: Write failing test
- GREEN: Minimal code to pass
- REFACTOR: Improve while tests pass

---

### Architectural Decisions

#### State Management Pattern

**Decision**: Immutable state from P1 (enables undo/redo in P5 without refactor)

**Implementation**:
- Python: Each action creates new diagram state (not mutating in place)
- JavaScript: React state updates are immutable
- History tracking: Easy to add later (just keep previous states)

**Rationale**: Designing for undo/redo early prevents refactoring later, but actual undo/redo UI can wait until P5.

---

### Phase Completion Criteria

Each phase complete when:
- ✅ All tests pass (unit + contract + integration)
- ✅ 80% code coverage on business logic
- ✅ User story acceptance scenarios verified
- ✅ No regressions in previous phases
- ✅ Documentation updated (docstrings, README)

---

### Summary Table

| Phase | User Story | Blocks | Parameters | Validation | Save/Load | UX |
|-------|------------|--------|------------|------------|-----------|-----|
| Walking Skeleton | - | Gain, I/O | Basic text | None | None | Canvas only |
| P1 | Interactive Creation | All 5 | Basic text (arrays) | Connection constraints | Basic JSON | - |
| P2 | Parameter Config | (same) | + Expression eval (matrices) | (same) | (same) | - |
| P3 | Validation | (same) | (same) | + Algebraic loops, completeness | (same) | - |
| P4 | Persistence | (same) | (same) | (same) | + Edge cases, schema versioning | - |
| P5 | UX Essentials | (same) | (same) | (same) | (same) | + Undo/redo, shortcuts, grid |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitution principles satisfied.

