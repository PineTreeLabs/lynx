<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Hideable Block Labels

**Branch**: `005-hideable-block-labels` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-hideable-block-labels/spec.md`

## Summary

Add a `label_visible` boolean attribute to blocks (default: false) that controls label visibility. Labels are hidden by default. The block context menu shows dynamic "Show Label" / "Hide Label" option based on current state. The Python Diagram object is the source of truth, with state persisted in saved diagrams.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget, Pydantic
**Storage**: JSON diagram files (existing persistence layer via Pydantic schemas)
**Testing**: Vitest 2.1.8 (frontend), pytest (backend)
**Target Platform**: Jupyter notebooks (JupyterLab, VS Code Jupyter extension)
**Project Type**: Web application (frontend/backend split via anywidget)
**Performance Goals**: Instant label toggle (<50ms response)
**Constraints**: No breaking changes to existing diagram JSON format (backward compatible)
**Scale/Scope**: 5 block types, existing context menu infrastructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Justification |
|-----------|--------|---------------|
| **I. Simplicity Over Features** | PASS | Single boolean attribute, reuses existing context menu pattern |
| **II. Python Ecosystem First** | PASS | Python Diagram is source of truth, no vendor lock-in |
| **III. Test-Driven Development** | DEFER | Tests not explicitly requested in spec; will add if needed |
| **IV. Clean Separation of Concerns** | PASS | Business logic (visibility state) in Diagram, UI in React components |
| **V. User Experience Standards** | PASS | <3s toggle via familiar context menu pattern |

## Project Structure

### Documentation (this feature)

```text
specs/005-hideable-block-labels/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (from /speckit.tasks)
```

### Source Code (repository root)

```text
# Backend (Python)
src/lynx/
├── blocks/
│   └── base.py          # Add label_visible attribute to Block class
├── schema.py            # Add label_visible to BaseBlockModel
├── diagram.py           # Add toggle_label_visibility() method
└── widget.py            # Add _handle_toggle_label action handler

# Frontend (TypeScript)
js/src/
├── components/
│   ├── BlockContextMenu.tsx   # Add "Show Label" / "Hide Label" option
│   └── EditableLabel.tsx      # Conditionally render based on visibility
├── blocks/
│   ├── GainBlock.tsx          # Conditionally render label
│   ├── TransferFunctionBlock.tsx
│   ├── StateSpaceBlock.tsx
│   ├── SumBlock.tsx
│   └── IOMarkerBlock.tsx
├── DiagramCanvas.tsx          # Pass label visibility to context menu
└── utils/
    └── traitletSync.ts        # Already supports sendAction
```

**Structure Decision**: Web application structure (frontend/backend split). This feature adds a single attribute and leverages existing infrastructure patterns.

## Complexity Tracking

> No complexity violations - this feature follows existing patterns for block attributes (like `flipped` and `custom_latex`).

## Architecture Decisions

### Decision 1: Attribute Location

**Choice**: Add `label_visible` as a top-level block attribute (like `flipped` and `custom_latex`), not a parameter.

**Rationale**:
- Parameters are for control system values (K, numerator, etc.)
- Visual display attributes are top-level (flipped, custom_latex, label)
- Follows existing pattern exactly

### Decision 2: Default Value

**Choice**: `label_visible` defaults to `false` (hidden)

**Rationale**:
- Explicit spec requirement: "hidden by default"
- Backward compatibility: existing diagrams without this field default to hidden

### Decision 3: Action Type

**Choice**: Single `toggleLabelVisibility` action that flips the current state

**Rationale**:
- Simpler than separate "show" and "hide" actions
- Context menu only shows one option at a time anyway
- Follows `flipBlock` pattern

### Decision 4: Conditional Rendering

**Choice**: Conditionally render the `<EditableLabel>` component based on `label_visible`

**Rationale**:
- Cleanest approach - no label DOM element when hidden
- Maintains existing double-click editing behavior when visible
- Simple CSS approach (display:none) also viable but adds unnecessary DOM

## Data Flow

```
User right-click → Context Menu shows "Show/Hide Label"
    ↓
User clicks menu item
    ↓
sendAction("toggleLabelVisibility", { blockId })
    ↓
Python: diagram.toggle_label_visibility(block_id)
    ↓
Python: update Block.label_visible, push to undo stack
    ↓
_update_diagram_state() → React receives new state
    ↓
Block component re-renders with/without label
```

## Files to Modify

### Backend (Python)

1. **`src/lynx/blocks/base.py`**
   - Add `label_visible: bool = False` to `Block.__init__`
   - Add to `Block.to_dict()` output

2. **`src/lynx/schema.py`**
   - Add `label_visible: bool = False` to `BaseBlockModel`

3. **`src/lynx/diagram.py`**
   - Add `toggle_label_visibility(block_id: str) -> bool` method
   - Follow pattern from `flip_block()` method

4. **`src/lynx/widget.py`**
   - Add `toggleLabelVisibility` to action dispatcher
   - Add `_handle_toggle_label_visibility()` handler

### Frontend (TypeScript)

5. **`js/src/components/BlockContextMenu.tsx`**
   - Add `labelVisible?: boolean` prop
   - Add `onToggleLabel?: () => void` callback prop
   - Add "Show Label" / "Hide Label" menu item

6. **`js/src/DiagramCanvas.tsx`**
   - Pass `labelVisible` to context menu from block data
   - Add `handleToggleLabelVisibility` callback
   - Connect to `sendAction("toggleLabelVisibility", ...)`

7. **`js/src/blocks/GainBlock.tsx`**
   - Add `label_visible?: boolean` to `GainBlockData` interface
   - Conditionally render `<EditableLabel>` based on `label_visible`

8. **`js/src/blocks/TransferFunctionBlock.tsx`** (same pattern)

9. **`js/src/blocks/StateSpaceBlock.tsx`** (same pattern)

10. **`js/src/blocks/SumBlock.tsx`** (same pattern)

11. **`js/src/blocks/IOMarkerBlock.tsx`** (same pattern)

## Backward Compatibility

- Existing diagrams without `label_visible` field will default to `false` (hidden)
- This matches the spec requirement "hidden by default"
- Pydantic schema's default value handles missing field gracefully
- No migration needed - behavior change is intentional (labels hidden by default)
