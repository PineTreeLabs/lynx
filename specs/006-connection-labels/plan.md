<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Connection Labels

**Branch**: `006-connection-labels` | **Date**: 2026-01-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-connection-labels/spec.md`

## Summary

Add editable labels to connections with behavior matching block labels: hidden by default, toggleable via context menu, with text and visibility persisted in the Python diagram object. Labels positioned at horizontal center of connection path with smart adjustment to avoid corner waypoints.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget, Pydantic
**Storage**: JSON diagram files (existing persistence layer via Pydantic schemas)
**Testing**: Vitest 2.1.8 (frontend), pytest (backend)
**Target Platform**: Jupyter notebooks via anywidget
**Project Type**: Web application (frontend/backend)
**Performance Goals**: Label rendering <50ms per connection for 50-connection diagrams
**Constraints**: Labels must not overlap corner waypoints on standard segments
**Scale/Scope**: Typical diagrams have 5-20 connections

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity Over Features | PASS | Extends existing block label pattern; no new abstractions |
| II. Python Ecosystem First | PASS | Data persisted in Python Diagram object; JSON serialization |
| III. Test-Driven Development | PASS | Tests for positioning algorithm and schema validation |
| IV. Clean Separation of Concerns | PASS | Business logic (Connection model) separate from UI (EdgeContextMenu, OrthogonalEditableEdge) |
| V. User Experience Standards | PASS | Matches established block label UX; <3s to toggle visibility |

## Project Structure

### Documentation (this feature)

```text
specs/006-connection-labels/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/lynx/
├── schema.py            # ConnectionModel gains label, label_visible fields
├── diagram.py           # Connection dataclass + toggle/update methods
└── widget.py            # Action handlers for connection label operations

js/src/
├── DiagramCanvas.tsx    # Edge context menu state + handlers
├── connections/
│   └── OrthogonalEditableEdge.tsx  # Label rendering via EdgeLabelRenderer
├── components/
│   ├── EdgeContextMenu.tsx         # Show/Hide Label menu items
│   └── EditableLabel.tsx           # Reuse for connection labels
└── utils/
    └── connectionLabelPosition.ts  # NEW: Smart label positioning algorithm

js/src/test/
├── connectionLabelPosition.test.ts # NEW: Positioning algorithm tests
└── ...
```

**Structure Decision**: Web application structure - existing frontend/backend split. Connection labels follow same pattern as block labels with UI in React (js/src/) and data model in Python (src/lynx/).

## Design Decisions

### D1: Data Model Extension

Extend `ConnectionModel` in schema.py with two new optional fields:
- `label: Optional[str] = None` - defaults to connection ID if not set
- `label_visible: bool = False` - hidden by default (matches blocks)

The Python `Connection` dataclass in diagram.py gains matching fields.

### D2: Label Positioning Algorithm

The label position is computed on the frontend based on connection geometry:

1. Calculate horizontal center: `centerX = (minX + maxX) / 2` where minX/maxX are extrema of connection path
2. Find the segment containing centerX (or closest segment if between waypoints)
3. Calculate text width (font: `text-xs font-mono` = ~7px per character)
4. Check if label would extend past nearest corner waypoints
5. If overlap detected, shift label left or right by minimum distance to avoid corner

Position is NOT persisted - only `label` and `label_visible` are stored.

### D3: Context Menu Integration

Extend `EdgeContextMenu` with:
- "Show Label" option (when `label_visible` is false)
- "Hide Label" option (when `label_visible` is true)

Uses same pattern as `BlockContextMenu` for consistency.

### D4: React Flow EdgeLabelRenderer

Use React Flow's `EdgeLabelRenderer` component (already imported in `OrthogonalEditableEdge.tsx`) to position the label. This renders labels in a separate layer that doesn't interfere with edge interaction.

### D5: Inline Editing

Reuse existing `EditableLabel` component for double-click editing. Label saves trigger `updateConnectionLabel` action to Python backend.

## Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DiagramCanvas.tsx                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ edgeContextMenu state: { connectionId, labelVisible, ... }  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              EdgeContextMenu.tsx                             │   │
│  │  - Show Label / Hide Label menu item                         │   │
│  │  - onToggleLabel callback                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │           OrthogonalEditableEdge.tsx                         │   │
│  │  - EdgeLabelRenderer with positioned label                   │   │
│  │  - EditableLabel for inline editing                          │   │
│  │  - calculateConnectionLabelPosition() for smart positioning  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ sendAction()
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           widget.py                                  │
│  _handle_toggle_connection_label_visibility(payload)                │
│  _handle_update_connection_label(payload)                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           diagram.py                                 │
│  toggle_connection_label_visibility(connection_id)                  │
│  update_connection_label(connection_id, label)                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           schema.py                                  │
│  ConnectionModel(label: Optional[str], label_visible: bool)         │
└─────────────────────────────────────────────────────────────────────┘
```

## API Changes

### New Actions (widget.py)

| Action | Payload | Description |
|--------|---------|-------------|
| `toggleConnectionLabelVisibility` | `{ connectionId: string }` | Toggle label visibility |
| `updateConnectionLabel` | `{ connectionId: string, label: string }` | Update label text |

### Schema Changes (schema.py)

```python
class ConnectionModel(BaseModel):
    # Existing fields...
    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: list[WaypointModel] = Field(default_factory=list)

    # NEW fields
    label: Optional[str] = None  # Defaults to connection ID if not set
    label_visible: bool = False  # Hidden by default
```

## Complexity Tracking

No constitution violations. Feature follows existing patterns.

## Test Strategy

### Unit Tests (Frontend)
- `connectionLabelPosition.test.ts`: Position calculation algorithm
  - Straight connection: label at center
  - Connection with waypoints: label avoids corners
  - Edge cases: very short segments, long text

### Integration Tests (Python)
- Schema validation: label and label_visible fields serialize/deserialize
- Diagram methods: toggle_connection_label_visibility, update_connection_label

### Manual Verification
- Context menu shows correct option based on visibility state
- Label appears at expected position
- Double-click editing works
- Save/load preserves label text and visibility
