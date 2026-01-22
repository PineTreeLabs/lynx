<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Python-Control Export

**Branch**: `012-python-control-export` | **Date**: 2026-01-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-python-control-export/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable conversion from Lynx block diagrams to python-control's `InterconnectedSystem` objects for simulation and analysis. Implements a `Diagram.to_interconnect()` method that maps Lynx block types (Gain, TransferFunction, StateSpace, Sum) to python-control subsystems, converts connections to signal routing format, handles sum block sign negation, extracts I/O markers to system boundaries, and validates diagram completeness before export.

## Technical Context

**Language/Version**: Python 3.11+ (existing Lynx requirement)
**Primary Dependencies**:
- python-control ≥0.10.2 (already in pyproject.toml)
- NumPy ≥2.4.0 (already in pyproject.toml)
- Pydantic ≥2.12.5 (for schema validation, already in pyproject.toml)

**Storage**: N/A (operates on in-memory Diagram objects)
**Testing**: pytest (existing test infrastructure in `tests/`)
**Target Platform**: Cross-platform Python (Linux, macOS, Windows) via Jupyter notebooks
**Project Type**: Single Python package (backend-only feature, no UI changes)
**Performance Goals**: <100ms export time for 50-block diagrams (from SC-003)
**Constraints**: SISO blocks only (MIMO deferred), flat diagrams only (no hierarchical subsystems)
**Scale/Scope**: 50-block diagrams typical, up to 100 blocks acceptable (from risk analysis)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Simplicity Over Features ✅
- **Alignment**: Export functionality is essential - Lynx's core value proposition is visual design + computational analysis with python-control
- **Justification**: Without export, Lynx is only a drawing tool. This feature enables the primary use case.
- **Simplicity check**: Single method `to_interconnect()` with no parameters, fail-fast validation, no optional behaviors

### II. Python Ecosystem First ✅
- **Alignment**: Directly integrates with python-control (the standard library for control systems in Python)
- **No vendor lock-in**: Exports to open python-control API, users can modify/analyze systems in any python-control workflow
- **Data ownership**: Users get python-control objects they fully control, can serialize/share via standard python-control mechanisms

### III. Test-Driven Development (NON-NEGOTIABLE) ✅
- **Commitment**: All tests will be written BEFORE implementation
- **Test categories**:
  1. Block conversion tests (Gain, TF, SS, Sum → python-control subsystems)
  2. Connection mapping tests (Lynx connections → python-control signal format)
  3. Sum block sign handling tests (all combinations of +/-/| signs)
  4. Validation tests (unconnected inputs, missing I/O markers, disconnected graphs)
  5. Integration tests (export → simulate → verify behavior)
- **Red-Green-Refactor**: Each test fails first, then implementation makes it pass

### IV. Clean Separation of Concerns ✅
- **Business logic**: Export/conversion logic in `src/lynx/diagram.py` (domain model)
- **No presentation coupling**: Export operates on pure Diagram objects, no widget/UI dependencies
- **Testability**: All conversion logic testable without Jupyter widget or frontend

### V. User Experience Standards ✅
- **Immediate usability**: Single method call `diagram.to_interconnect()` - no configuration needed
- **Performance target**: <100ms for 50-block diagrams (specified in SC-003)
- **Error clarity**: Descriptive exceptions identify exact problem (block ID, port ID, issue) per FR-013

**GATE STATUS**: ✅ **PASSED** - All principles satisfied, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/lynx/
├── diagram.py           # ADD: to_interconnect() method (main implementation)
├── blocks/
│   ├── base.py          # UNCHANGED: Block base class
│   ├── gain.py          # UNCHANGED: GainBlock
│   ├── transfer_function.py  # UNCHANGED: TransferFunctionBlock
│   ├── state_space.py   # UNCHANGED: StateSpaceBlock
│   ├── sum.py           # UNCHANGED: SumBlock
│   └── io_marker.py     # UNCHANGED: InputMarker, OutputMarker
└── export/              # NEW: Export module (if needed for organization)
    └── python_control.py # NEW: Helper functions for conversion logic

tests/
├── unit/
│   └── test_export_python_control.py  # NEW: Unit tests for conversion logic
└── integration/
    └── test_python_control_integration.py  # NEW: End-to-end export + simulation tests
```

**Structure Decision**: Single Python package structure (Option 1). All export logic lives in `src/lynx/diagram.py` as a new method on the `Diagram` class. Helper functions may be extracted to `src/lynx/export/python_control.py` if conversion logic becomes complex, but starting with a single method keeps it simple per Constitution Principle I.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitution violations. All principles satisfied.

## Design Summary

### Phase 0: Research Outcomes ✅

All technical decisions documented in [research.md](research.md):

1. **python-control API Contract**: Use `interconnect()` with named signals, summing_junction for Sum blocks
2. **Sum Block Sign Mapping**: Quadrant-to-port algorithm handles skipped "|" signs correctly
3. **Validation Strategy**: Layered fail-fast (boundaries → connections → optional graph analysis)
4. **Performance**: Linear O(n+m) algorithm sufficient, no optimization needed for 50-block target
5. **Exception Design**: Custom `ValidationError` with structured messages (block_id, port_id fields)

### Phase 1: Design Artifacts ✅

**Data Model** ([data-model.md](data-model.md)):
- Block conversion mappings (Gain, TF, SS, Sum, I/O markers → python-control types)
- Connection transformation rules (signal naming, negation handling)
- Validation rules (system boundaries, port connections, sum signs)
- Performance characteristics (O(n+m) space/time, ~70ms for 50 blocks)

**Quickstart Scenarios** ([quickstart.md](quickstart.md)):
- 6 end-to-end test scenarios covering all user stories (P1-P3)
- Simple feedback loop, sum block signs, validation errors, state-space, performance, complex PID
- Ready for copy-paste into integration tests

**Agent Context** (CLAUDE.md):
- Updated with Python 3.11+ requirement (no new dependencies needed)
- Noted in-memory operation (no persistence layer)

### Implementation Approach

**File Changes**:
- `src/lynx/diagram.py`: Add `to_interconnect()` method (primary implementation)
- `tests/unit/test_export_python_control.py`: Unit tests for block conversion, connection mapping, validation
- `tests/integration/test_python_control_integration.py`: End-to-end scenarios from quickstart.md

**Method Signature**:
```python
def to_interconnect(self) -> control.InterconnectedSystem:
    """Export diagram to python-control InterconnectedSystem.

    Returns:
        InterconnectedSystem: Ready for simulation with ct.step_response(), etc.

    Raises:
        ValidationError: If diagram is incomplete (unconnected ports, missing I/O markers)
        DiagramExportError: If python-control conversion fails
    """
```

**Algorithm Flow**:
1. Validate system boundaries (at least one InputMarker, one OutputMarker)
2. Validate port connections (all non-InputMarker inputs connected)
3. Convert blocks to python-control subsystems (iterate blocks, dispatch by type)
4. Map connections to signal pairs (apply negation for Sum block subtraction)
5. Extract I/O markers to inplist/outlist
6. Call `ct.interconnect(systems, connections, inplist, outlist)`
7. Wrap any python-control errors with context and re-raise

**Key Implementation Details**:
- Sum block sign mapping: Count non-"|" signs to map port ID to quadrant
- Signal names: `f"{block.id}.{port.id}"` with optional `-` prefix
- Validation first: Fail fast before any conversion work
- No state changes: Export is read-only operation on diagram

### Post-Design Constitution Re-Check ✅

**All principles remain satisfied:**

- **I. Simplicity**: Single method, no parameters, linear algorithm
- **II. Python Ecosystem**: Direct python-control integration, no lock-in
- **III. TDD**: Test scenarios defined, ready for red-green-refactor
- **IV. Separation of Concerns**: Pure domain logic in diagram.py
- **V. UX Standards**: <100ms target achievable, clear error messages

**No violations introduced during design.**

### Ready for Phase 2

All planning complete. Next step: `/speckit.tasks` to generate task breakdown.

**Artifacts Generated**:
- ✅ plan.md (this file)
- ✅ research.md (5 research questions resolved)
- ✅ data-model.md (mappings, validation rules, performance)
- ✅ quickstart.md (6 test scenarios)
- ✅ CLAUDE.md (agent context updated)

**No contracts/** directory (not applicable - Python library method, not REST API)
