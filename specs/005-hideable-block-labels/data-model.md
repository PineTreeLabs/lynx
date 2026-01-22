<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Hideable Block Labels

**Feature**: 005-hideable-block-labels
**Date**: 2026-01-12

## Entity Changes

### Block (Modified)

The `Block` entity gains a new attribute to control label visibility.

#### New Attribute

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label_visible` | `boolean` | `false` | Whether the block's label is displayed |

#### Complete Block Schema (with new field)

```typescript
interface Block {
  // Existing fields
  id: string;                    // Unique block identifier
  type: string;                  // Block type (gain, sum, etc.)
  position: { x: number; y: number };  // Canvas position
  label: string;                 // User-facing label text (defaults to id)
  flipped: boolean;              // Horizontal flip state
  custom_latex?: string;         // Optional custom LaTeX override
  parameters: Parameter[];       // Block-specific parameters
  ports: Port[];                 // Input/output ports

  // NEW field
  label_visible: boolean;        // Whether label is displayed (default: false)
}
```

#### Python Implementation

```python
# src/lynx/blocks/base.py
class Block:
    def __init__(
        self,
        id: str,
        block_type: str,
        position: Optional[Dict[str, float]] = None,
        label: Optional[str] = None,
        flipped: bool = False,
        custom_latex: Optional[str] = None,
        label_visible: bool = False,  # NEW
    ) -> None:
        ...
        self.label_visible = label_visible  # NEW
```

```python
# src/lynx/schema.py
class BaseBlockModel(BaseModel):
    ...
    label_visible: bool = False  # NEW - defaults to hidden
```

## State Transitions

```
                   toggleLabelVisibility
                         action
label_visible=false ←─────────────────→ label_visible=true
    (hidden)                              (visible)
```

The transition is:
- **Bidirectional**: Same action toggles between states
- **Immediate**: No intermediate states
- **Undoable**: Each toggle pushes to undo stack

## Validation Rules

| Rule | Description |
|------|-------------|
| Type | Must be boolean |
| Default | `false` (hidden) |
| Required | No (defaults apply) |

## Relationships

```
Block
├── label: string         (the label text content)
├── label_visible: bool   (whether to display the label)
└── [other attributes]
```

The `label` field continues to store the text content. The new `label_visible` field only controls display.

## JSON Serialization

### Example: Block with Hidden Label (default)

```json
{
  "id": "gain_1",
  "type": "gain",
  "position": { "x": 100, "y": 200 },
  "label": "gain_1",
  "flipped": false,
  "label_visible": false,
  "parameters": [{ "name": "K", "value": 2.0 }],
  "ports": [
    { "id": "in", "type": "input" },
    { "id": "out", "type": "output" }
  ]
}
```

### Example: Block with Visible Label

```json
{
  "id": "gain_1",
  "type": "gain",
  "position": { "x": 100, "y": 200 },
  "label": "My Custom Label",
  "flipped": false,
  "label_visible": true,
  "parameters": [{ "name": "K", "value": 2.0 }],
  "ports": [
    { "id": "in", "type": "input" },
    { "id": "out", "type": "output" }
  ]
}
```

## Backward Compatibility

Old diagrams without `label_visible` field will:
1. Load successfully (Pydantic default applies)
2. Have `label_visible = false` (labels hidden)
3. Save with the new field included

This is intentional per the spec: "hidden by default".
