<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Technical Research: Lynx Block Diagram Widget

**Feature**: 001-lynx-jupyter-widget
**Date**: 2025-12-25
**Status**: Complete

## Overview

All technical decisions for Lynx have been made during pre-planning discussions and are documented in `.specify/memory/tech_stack.md` and `.specify/memory/functional_spec.md`. This document consolidates those decisions with rationale.

## Key Technical Decisions

### Decision 1: anywidget Framework for Jupyter Integration

**Decision**: Use anywidget as the foundation for Jupyter widget integration.

**Rationale**:
- Purpose-built for creating Jupyter widgets with modern web technologies
- Handles Python ↔ JavaScript synchronization via traitlets automatically
- Works across JupyterLab, classic Notebook, and VSCode
- Simpler than ipywidgets for React-based UIs
- Active development and good documentation

**Alternatives Considered**:
- **ipywidgets**: More established but more complex for React integration. anywidget is specifically designed for this use case.
- **Voilà + standalone web app**: Would lose Jupyter integration benefits. Users need inline notebook workflow.
- **Pure JavaScript extension**: No Python integration, can't leverage numpy/python-control ecosystem.

### Decision 2: React Flow for Diagram Rendering

**Decision**: Use React Flow library for node-based diagram rendering and interactions.

**Rationale**:
- Battle-tested library specifically for node-graph UIs
- Handles dragging, connecting, zooming, panning out of the box
- Customizable node types (perfect for control system blocks)
- Good performance (50+ nodes confirmed viable)
- TypeScript support
- Active maintenance and large community

**Alternatives Considered**:
- **D3.js**: Too low-level, would require building all interaction patterns from scratch.
- **mxGraph**: Older library, less React-friendly, heavier weight.
- **Custom Canvas/SVG**: Massive development effort for marginal benefit. React Flow solves the problem.

### Decision 3: Explicit JSON Save/Load (No Live Modification)

**Decision**: Diagrams persist via explicit `diagram.save()` and `Diagram.load()` methods. No real-time Python variable modification in MVP.

**Rationale**:
- **Reproducibility**: Notebooks with `Diagram.load()` are fully reproducible ("Restart & Run All" works)
- **Simplicity**: Clear mental model - save to persist, load to restore
- **Git-friendly**: JSON files produce meaningful diffs
- **Foundation**: Can experiment with live modification post-MVP if UX benefits justify complexity

**Alternatives Considered**:
- **Live object modification via traitlets**: Attractive for immediate feedback, but breaks reproducibility unless carefully designed. Deferred to post-MVP exploration.
- **Auto-save**: Adds hidden state, unclear when changes are persisted. Explicit is better.

**Post-MVP Exploration**: Hybrid approach (live modification + explicit save) may provide best of both worlds.

### Decision 4: Hybrid Matrix Parameter Storage (Expression + Value)

**Decision**: Store both Python expression and resolved numpy array value for matrix parameters.

**JSON Format**:
```json
{
  "A": {
    "expression": "np.eye(2)",
    "value": [[1, 0], [0, 1]]
  }
}
```

**Rationale**:
- **Flexibility**: Users can reference variables (`A`), use numpy functions (`np.eye(2)`), or enter literals
- **Reproducibility**: Stored values ensure diagrams load even if variables missing
- **Intent**: Expression shows what user meant, not just numeric result
- **Natural workflow**: Engineers already work with numpy in notebooks

**UI Behavior**: Display both expression and current evaluated value (Simulink-style).

**Alternatives Considered**:
- **Expression only**: Breaks if variable missing on reload.
- **Value only**: Loses user intent, can't see original expression.
- **Value only is clearer and simpler**: Rejected - engineers want to see variable names, not just numbers.

**Post-MVP**: User testing will validate if showing both clarifies or clutters.

### Decision 5: Python 3.11+ Requirement

**Decision**: Require Python 3.11 or newer.

**Rationale**:
- Modern features (better error messages, match statements)
- Significant performance improvements over 3.10
- Enhanced type hints (Self type, TypeVarTuple)
- Still widely supported across platforms (released Oct 2022)

**Alternatives Considered**:
- **Python 3.9+**: Wider compatibility but misses performance gains and modern features.
- **Python 3.12+**: Too new, would limit user base unnecessarily.

### Decision 6: Real-Time Validation for All Checks

**Decision**: Run validation continuously as user edits (not just on-demand).

**Target**: <100ms for all validation operations.

**Rationale**:
- Immediate feedback prevents building invalid states
- Engineers can correct errors while context is fresh
- <100ms feels instantaneous to users

**Implementation**: Debounce if needed, but real-time is the goal.

**Alternatives Considered**:
- **On-demand validation only**: Users might build complex invalid diagrams before discovering errors. Real-time is better UX.

### Decision 7: In-Session Undo/Redo Only

**Decision**: Undo/redo history is session-only (not persisted across restarts).

**Rationale**:
- Simpler implementation
- Matches standard GUI tool behavior
- Undo history not essential for reproducibility (that's what git is for)

**Alternatives Considered**:
- **Persistent undo history**: Complex, marginal benefit. Deferred.

### Decision 8: 20-Pixel Grid Snapping (Optional)

**Decision**: Grid snapping uses 20-pixel grid, toggled on/off by user.

**Rationale**:
- 20px is good balance (not too coarse, not too fine) for control diagrams
- Optional because some users prefer freeform layout
- Simple to implement

### Decision 9: Vite + Tailwind CSS for Frontend Build

**Decision**: Use Vite for bundling, Tailwind CSS for styling.

**Rationale**:
- **Vite**: Fast dev server, modern ESM architecture, good TypeScript support
- **Tailwind**: Rapid UI development, consistent design system (Lynx colors), small bundle size

**Alternatives Considered**:
- **Webpack**: More complex configuration, slower dev server.
- **Custom CSS**: Would require writing and maintaining stylesheets. Tailwind is faster.

### Decision 10: pytest + Vitest for Testing

**Decision**: pytest (Python), Vitest (JavaScript), contract tests for traitlet sync.

**Coverage Target**: 80% minimum on business logic (validation, graph operations).

**Rationale**:
- **pytest**: Standard Python testing framework
- **Vitest**: Fast, Jest-compatible API, Vite integration
- **Contract tests**: Critical for ensuring Python ↔ JavaScript agreement

### Decision 11: Expression Evaluation Security

**Decision**: Evaluate user expressions in notebook namespace using `eval()` with error handling.

**Security Context**: Users already have arbitrary code execution in Jupyter. Evaluating expressions doesn't increase attack surface.

**Mitigations**:
- Proper error handling for malformed expressions
- Clear error messages
- Fall back to stored value if evaluation fails

**Alternatives Considered**:
- **AST parsing + restricted eval**: Over-engineered for Jupyter context where users already have full Python access.

## Research Validation

All decisions align with:
- ✅ Constitution principles (simplicity, Python ecosystem, TDD, separation of concerns, UX)
- ✅ Functional specification requirements
- ✅ Technical stack document
- ✅ User clarifications from planning session

No unresolved technical questions remain. Ready to proceed to Phase 1 (Design & Contracts).
