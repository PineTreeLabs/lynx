<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Block Resizing

**Feature**: 007-block-resizing
**Date**: 2026-01-12

## Entity Changes

### Block (Extended)

The existing `Block` base class in `src/lynx/blocks/base.py` is extended with dimension attributes.

#### New Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | `Optional[float]` | `None` | Block width in pixels. When `None`, uses block-type default. |
| `height` | `Optional[float]` | `None` | Block height in pixels. When `None`, uses block-type default. |

#### Block Type Defaults

| Block Type | Default Width | Default Height | Min Width | Min Height |
|------------|---------------|----------------|-----------|------------|
| `gain` | 120 | 80 | 60 | 40 |
| `sum` | 56 | 56 | 40 | 40 |
| `transfer_function` | 100 | 50 | 80 | 40 |
| `state_space` | 100 | 60 | 80 | 40 |
| `io_marker` | 60 | 48 | 60 | 40 |

#### Validation Rules

1. **Minimum Size**: `width >= MIN_WIDTH[block_type]` and `height >= MIN_HEIGHT[block_type]`
2. **Positive Values**: `width > 0` and `height > 0` when specified
3. **Backward Compatibility**: `None` values fall back to defaults on serialization

### BaseBlockModel (Pydantic Schema)

The `BaseBlockModel` in `src/lynx/schema.py` is extended for JSON serialization.

```python
class BaseBlockModel(BaseModel):
    # Existing fields...
    id: str
    type: str
    position: dict[str, float]
    label: Optional[str]
    flipped: bool
    custom_latex: Optional[str]
    label_visible: bool
    parameters: list[ParameterModel]
    ports: list[PortModel]

    # New fields for resizing
    width: Optional[float] = None   # Block width in pixels
    height: Optional[float] = None  # Block height in pixels
```

#### Serialization Behavior

- **Load with `None`**: Uses block-type default dimensions
- **Save with value**: Persists explicit dimensions
- **Backward compatibility**: Old diagrams without dimensions load correctly

### DiagramModel (Unchanged)

No changes to `DiagramModel`. Block dimensions are part of block serialization.

## State Transitions

### Resize Interaction State Machine

```
IDLE
  ↓ (user selects block)
SELECTED [resize handles visible]
  ↓ (user starts dragging handle)
RESIZING [updating dimensions in real-time]
  ↓ (user releases mouse)
SELECTED [dimensions persisted to Python]
  ↓ (user clicks elsewhere)
IDLE
```

### Dimension Update Flow

```
User drags handle
       ↓
React component calls handleResize(width, height)
       ↓
Optimistic update: setNodes() in React state
       ↓
sendAction('update_block_dimensions', {block_id, width, height})
       ↓
Python: Diagram.update_block_dimensions()
       ↓
Python: _save_state() for undo
       ↓
Python: block.width = width, block.height = height
       ↓
Python: _clear_waypoints_for_block(block_id)
       ↓
Traitlet sync: diagram_state updated
       ↓
React receives updated state (no-op if matches optimistic)
```

## Interface Contracts

### Frontend → Backend Message

```typescript
interface UpdateBlockDimensionsPayload {
  block_id: string;
  width: number;
  height: number;
}
```

**Action Name**: `update_block_dimensions`

### Backend Method

```python
def update_block_dimensions(
    self,
    block_id: str,
    width: float,
    height: float
) -> bool:
    """Update block dimensions (with undo support).

    Clears waypoints for all connections involving this block,
    forcing the frontend to auto-route after resize.

    Args:
        block_id: Block identifier
        width: New width in pixels
        height: New height in pixels

    Returns:
        True if block was found and updated, False otherwise
    """
```

## TypeScript Interfaces

### Block Data Extension

```typescript
// Existing interface extended
interface BlockData {
  parameters: Array<{ name: string; value: any }>;
  ports: Array<{ id: string; type: string }>;
  label?: string;
  flipped?: boolean;
  custom_latex?: string;
  label_visible?: boolean;
  width?: number;   // New: block width in pixels
  height?: number;  // New: block height in pixels
}
```

### Resize Constants

```typescript
// Default dimensions per block type
export const BLOCK_DEFAULTS = {
  gain: { width: 120, height: 80, minWidth: 60, minHeight: 40 },
  sum: { width: 56, height: 56, minWidth: 40, minHeight: 40 },
  transfer_function: { width: 100, height: 50, minWidth: 80, minHeight: 40 },
  state_space: { width: 100, height: 60, minWidth: 80, minHeight: 40 },
  io_marker: { width: 60, height: 48, minWidth: 60, minHeight: 40 },
} as const;
```

## Migration

### Backward Compatibility

1. **Existing diagrams**: Load without `width`/`height` fields; use defaults
2. **New diagrams**: May include explicit dimensions
3. **Mixed scenarios**: Partial dimensions (only width or height) use defaults for missing

### Forward Compatibility

Old Lynx versions will ignore `width`/`height` fields (Pydantic `extra="forbid"` should be updated to `extra="ignore"` if needed, but current schema should handle gracefully).

## Relationships

```
Block
  ├── position: {x, y}      # Canvas location
  ├── width: float?         # NEW: Custom width (optional)
  ├── height: float?        # NEW: Custom height (optional)
  ├── parameters: [...]     # Block-specific settings
  ├── ports: [...]          # Connection points
  └── (other attributes)

Connection
  ├── source_block_id ──────┐
  ├── target_block_id ──────┼── References Block
  └── waypoints: [...]      # Cleared on block resize
```
