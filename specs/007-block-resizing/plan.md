<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Block Resizing

**Branch**: `007-block-resizing` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-block-resizing/spec.md`

## Summary

Add manual block resizing capability with corner drag handles. Users single-click to select a block, revealing 8x8 pixel handles at all four corners. Dragging any handle resizes the block (free-form by default, Shift+drag for aspect-ratio lock) while the opposite corner stays fixed. Block dimensions are stored in Python (source of truth), serialized to JSON, and propagated to React Flow. SVG-based blocks (Gain, Sum) scale their shapes; text/LaTeX content preserves font size and alignment. Connections auto-route on resize.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget, Pydantic, KaTeX
**Storage**: JSON diagram files (existing persistence layer via Pydantic schemas)
**Testing**: Vitest 2.1.8 (frontend), pytest (backend)
**Target Platform**: Jupyter Notebook widget (browser-based)
**Project Type**: Web application (frontend + backend widget)
**Performance Goals**: Smooth resize at 60fps, no perceptible lag for 50-block diagrams
**Constraints**: Real-time synchronization between React Flow and Python state
**Scale/Scope**: 5 block types, ~50 blocks per diagram typical

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Simplicity Over Features | PASS | Resize is a core diagramming capability; no feature creep |
| II. Python Ecosystem First | PASS | Dimensions stored in Python Block objects as source of truth |
| III. Test-Driven Development | PASS | Will write tests first for resize geometry, persistence, and UI |
| IV. Clean Separation of Concerns | PASS | Python handles data/persistence; React handles interaction/rendering |
| V. User Experience Standards | PASS | Standard corner-handle resize matches user expectations (Figma, Simulink) |

**Gate Result**: PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/007-block-resizing/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - no new APIs)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Existing web application structure (frontend + backend)
src/lynx/
├── blocks/
│   ├── base.py          # Add width/height attributes
│   ├── gain.py          # Default dimensions constant
│   ├── sum.py           # Default dimensions constant
│   ├── transfer_function.py
│   ├── state_space.py
│   └── io_marker.py
├── schema.py            # Add width/height to BaseBlockModel
├── diagram.py           # Add update_block_dimensions()
└── widget.py            # Handle dimension update events

js/src/
├── blocks/
│   ├── GainBlock.tsx    # Accept dynamic width/height props
│   ├── SumBlock.tsx     # Accept dynamic width/height, scale ellipse
│   ├── TransferFunctionBlock.tsx
│   ├── StateSpaceBlock.tsx
│   └── IOMarkerBlock.tsx
├── components/
│   └── ResizeHandle.tsx # New: corner handle component
├── hooks/
│   └── useBlockResize.ts # New: resize interaction logic
└── DiagramCanvas.tsx    # Integrate resize callbacks

tests/
└── lynx/
    └── test_block_dimensions.py # New: persistence tests

js/src/test/
├── ResizeHandle.test.tsx # New: handle rendering tests
└── useBlockResize.test.ts # New: resize logic tests
```

**Structure Decision**: Extends existing web application structure. New components (ResizeHandle, useBlockResize hook) follow established patterns. Backend changes minimal (add 2 attributes to Block, 1 method to Diagram).

## Complexity Tracking

> No Constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Design Decisions

### D1: React Flow NodeResizer vs Custom Implementation

**Decision**: Use custom ResizeHandle component (not React Flow's built-in NodeResizer)

**Rationale**:
- React Flow 11.x NodeResizer is designed for @reactflow/node-resizer package with specific styling
- Custom handles give full control over appearance (8x8 squares matching block stroke color)
- Easier to implement Shift+drag aspect ratio lock behavior
- Better integration with existing selection state (`selectedBlockId`)

### D2: Dimension Storage Location

**Decision**: Add `width` and `height` as top-level Block attributes (not parameters)

**Rationale**:
- Dimensions are structural (like `position`, `flipped`) not behavioral (like `K`, `numerator`)
- Consistent with Python-as-source-of-truth principle
- Matches how `position` is handled: stored in Block, synced via widget traitlets

### D3: Minimum Block Sizes

**Decision**: Per-block-type minimums based on content requirements

| Block Type | Min Width | Min Height | Rationale |
|------------|-----------|------------|-----------|
| Gain | 60 | 40 | Triangle must be recognizable |
| Sum | 40 | 40 | Circle/ellipse must fit X and +/- |
| TransferFunction | 80 | 40 | Fraction must be readable |
| StateSpace | 80 | 40 | Matrix notation space |
| IOMarker | 60 | 40 | Label must fit |

### D4: Resize Handle Visibility

**Decision**: Show handles only when block is selected AND not being dragged

**Rationale**:
- Matches Figma/Sketch/Illustrator behavior
- Avoids cluttering canvas during pan/zoom
- Integrates with existing `node.selected` React Flow state

### D5: Connection Re-routing Strategy

**Decision**: Reuse existing `_clear_waypoints_for_block()` mechanism

**Rationale**:
- Block resize changes port positions just like block move
- Existing auto-routing handles cleared waypoints
- No new routing logic needed; just trigger same path as move

## Implementation Approach

### Phase 1: Backend (Python)
1. Add `width: Optional[float]` and `height: Optional[float]` to Block base class
2. Add to BaseBlockModel schema with default None (backward compatible)
3. Add `update_block_dimensions()` method to Diagram class
4. Add widget handler for dimension updates (similar to position updates)
5. Define default dimensions constants per block type

### Phase 2: Frontend Foundation
1. Create ResizeHandle component (styled 8x8 square, corner positioning)
2. Create useBlockResize hook (drag logic, Shift detection, anchor corner math)
3. Modify block components to accept width/height from data props
4. Add dimension fallbacks to default values when undefined

### Phase 3: Block Component Updates
1. Update GainBlock SVG to use dynamic width/height in viewBox and polygon
2. Update SumBlock to render ellipse (cx/cy/rx/ry) instead of circle
3. Ensure LaTeX content stays centered, font size unchanged
4. Ensure +/- symbols position relative to port angles

### Phase 4: Integration
1. Add resize handles to selected blocks in each block component
2. Wire resize callbacks to update widget model
3. Disable collinearity snapping during resize
4. Trigger connection auto-route on resize complete
