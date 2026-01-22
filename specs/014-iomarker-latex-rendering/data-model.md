<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: IOMarker LaTeX Rendering

**Feature**: 014-iomarker-latex-rendering
**Date**: 2026-01-17
**Purpose**: Define entity schemas and data structures

## Entity: IOMarker Block

### Attributes

| Attribute | Type | Required | Default | Description | Constraints |
|-----------|------|----------|---------|-------------|-------------|
| `id` | string | Yes | - | Unique block identifier | Alphanumeric, must be unique across diagram |
| `block_type` | string | Yes | `"io_marker"` | Block type discriminator | Fixed value: `"io_marker"` |
| `marker_type` | string | Yes | `"input"` | Input or Output marker | Enum: `"input"` \| `"output"` |
| `index` | integer | No | Auto-assigned | Visual display ordering (0-based) | >= 0, unique per marker_type, auto-managed |
| `label` | string | No | None | Signal name for python-control export | Optional, used for `get_ss()`/`get_tf()` calls |
| `custom_latex` | string | No | None | Custom LaTeX expression override | Optional, no length limit, must be valid LaTeX |
| `position` | object | No | `{x: 0, y: 0}` | Canvas position | `{x: number, y: number}` |
| `block_label` | string | No | Same as `id` | Block name displayed below block | Optional |
| `label_visible` | boolean | No | `true` | Whether block label is visible | Boolean |
| `flipped` | boolean | No | `false` | Whether block is horizontally flipped | Boolean |
| `width` | number | No | `60` | Block width in pixels | >= 40 |
| `height` | number | No | `48` | Block height in pixels | >= 40 |

### Relationships

| Relationship | Cardinality | Description |
|--------------|-------------|-------------|
| `diagram` | N:1 | Each IOMarker belongs to exactly one Diagram |
| `connections` | N:M | IOMarker can have multiple connections to/from other blocks |
| `ports` | 1:1 | Each IOMarker has exactly 1 port (input marker → output port, output marker → input port) |

### State Transitions

IOMarker blocks do not have explicit state - `index` is automatically managed by Diagram:

```
[Created] → index = None
    ↓
[First Access] → index auto-assigned (alphabetical block ID order)
    ↓
[Manual Change] → index updated, other markers renumbered automatically
    ↓
[Deletion] → marker removed, higher indices cascade down
```

### Invariants

1. **Uniqueness**: For a given `marker_type` ("input" or "output"), all `index` values must be unique
2. **Completeness**: Indices must form a complete sequence [0, 1, 2, ..., N-1] where N = count of markers of that type
3. **Independence**: `label` and `index` are completely independent (no validation coupling)
4. **Type Consistency**: `marker_type` determines port type:
   - `marker_type="input"` → has 1 output port (signals flow out)
   - `marker_type="output"` → has 1 input port (signals flow in)

## Entity: Index Assignment

### Conceptual Model

`index` is not a standalone entity but a managed attribute of IOMarker with special assignment rules:

**Assignment Rules**:
```python
Rule 1: New marker creation
  IF diagram has no markers of this type:
    index = 0
  ELSE:
    index = max(existing_indices_for_type) + 1

Rule 2: Legacy diagram load
  IF marker has no index parameter:
    Collect all markers of same type without indices
    Sort by block ID alphabetically
    Assign indices 0, 1, 2, ... in sorted order

Rule 3: Manual index change
  IF new_index < old_index:  # Downward shift
    For each marker in [new_index, old_index-1]:
      marker.index += 1
    changed_marker.index = new_index
  ELIF new_index > old_index:  # Upward shift
    For each marker in [old_index+1, new_index]:
      marker.index -= 1
    changed_marker.index = new_index

Rule 4: Marker deletion
  deleted_index = marker.index
  For each marker where index > deleted_index:
    marker.index -= 1

Rule 5: Invalid index handling
  IF index < 0 OR index is non-integer:
    index = 0, trigger renumbering
  IF index >= N (where N = count of markers):
    index = N - 1 (clamp), trigger renumbering
```

## JSON Schema

### IOMarker Block Serialization

```json
{
  "id": "input_0",
  "block_type": "io_marker",
  "parameters": [
    {
      "name": "marker_type",
      "value": "input"
    },
    {
      "name": "index",
      "value": 0
    },
    {
      "name": "label",
      "value": "r"
    }
  ],
  "custom_latex": "r_{\\text{ref}}",
  "position": {"x": 100, "y": 200},
  "label": "Reference Input",
  "label_visible": true,
  "flipped": false,
  "width": 60,
  "height": 48,
  "ports": [
    {
      "id": "out",
      "type": "output"
    }
  ]
}
```

### Example: Backward Compatible Legacy Block

```json
{
  "id": "output_1",
  "block_type": "io_marker",
  "parameters": [
    {
      "name": "marker_type",
      "value": "output"
    },
    {
      "name": "label",
      "value": "y"
    }
    // NOTE: No "index" parameter - will be auto-assigned on load
  ],
  "position": {"x": 500, "y": 200},
  "label": "Plant Output",
  "ports": [
    {
      "id": "in",
      "type": "input"
    }
  ]
}
```

## Python Type Definitions

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator

class IOMarkerParameters(BaseModel):
    """IOMarker-specific parameters."""
    marker_type: Literal["input", "output"]
    index: Optional[int] = None  # Auto-assigned if None
    label: Optional[str] = None

    @validator('index')
    def validate_index(cls, v):
        if v is not None and v < 0:
            return 0  # Clamp negative to 0
        if v is not None and not isinstance(v, int):
            return 0  # Treat non-integer as 0
        return v

class IOMarkerBlock(Block):
    """IOMarker block with automatic index management."""
    def __init__(
        self,
        id: str,
        marker_type: Literal["input", "output"],
        index: Optional[int] = None,
        label: Optional[str] = None,
        position: Optional[dict] = None,
        block_label: Optional[str] = None,
        custom_latex: Optional[str] = None,
    ):
        super().__init__(
            id=id,
            block_type="io_marker",
            position=position,
            label=block_label,
        )
        self.custom_latex = custom_latex
        self.add_parameter("marker_type", marker_type)
        if index is not None:
            self.add_parameter("index", index)
        if label is not None:
            self.add_parameter("label", label)
```

## TypeScript Type Definitions

```typescript
// IOMarker block data interface
interface IOMarkerData {
  parameters: Array<{
    name: 'marker_type' | 'index' | 'label';
    value: string | number;
  }>;
  ports: Array<{
    id: string;
    type: 'input' | 'output';
  }>;
  label?: string;           // Block label (displayed below block)
  flipped?: boolean;
  label_visible?: boolean;
  width?: number;
  height?: number;
}

// Custom LaTeX attribute (stored on Block, not in parameters)
interface Block {
  id: string;
  block_type: string;
  parameters: Parameter[];
  custom_latex?: string;  // Optional LaTeX override
  // ... other fields
}

// Helper to extract index from parameters
function getIndex(block: Block): number {
  const indexParam = block.parameters?.find(p => p.name === 'index');
  return indexParam?.value ?? 0;  // Default 0 if missing
}

// Helper to extract marker type
function getMarkerType(block: Block): 'input' | 'output' {
  const typeParam = block.parameters?.find(p => p.name === 'marker_type');
  return (typeParam?.value as 'input' | 'output') ?? 'input';
}
```

## Validation Rules

### Backend Validation (Python)

```python
def validate_iomarker_indices(diagram: Diagram) -> List[str]:
    """Validate IOMarker index integrity.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    for marker_type in ['input', 'output']:
        markers = [
            b for b in diagram.blocks.values()
            if b.block_type == 'io_marker'
            and b.get_parameter('marker_type').value == marker_type
        ]

        # Get indices
        indices = [m.get_parameter('index').value for m in markers if m.get_parameter('index')]

        # Check uniqueness
        if len(indices) != len(set(indices)):
            errors.append(f"Duplicate {marker_type} marker indices found")

        # Check completeness (0, 1, 2, ..., N-1)
        if indices and set(indices) != set(range(len(indices))):
            errors.append(f"{marker_type} marker indices have gaps or out-of-range values")

    return errors
```

**Note**: Validation is defensive only - automatic renumbering ensures invariants are maintained. Validation is used for:
1. Detecting corrupted JSON diagrams
2. Testing renumbering algorithm correctness
3. Debugging edge cases

### Frontend Validation

**None required** - Frontend defers to Python backend for all validation and renumbering logic.

## Migration Strategy

### Existing Diagrams (No Index Parameter)

**Scenario**: User loads diagram created before this feature

**Behavior**:
1. Diagram loads successfully (backward compatible)
2. IOMarkers without `index` parameter are detected
3. Indices auto-assigned on first access using block ID alphabetical order
4. Next save persists indices to JSON
5. User sees no disruption or warnings

**Code**:
```python
def _ensure_index(self, block: Block) -> int:
    """Ensure block has index parameter, assign if missing."""
    index_param = block.get_parameter('index')
    if index_param is None:
        # Auto-assign based on current state
        marker_type = block.get_parameter('marker_type').value
        index = self._auto_assign_index(marker_type)
        block.add_parameter('index', index)
        return index
    return index_param.value
```

### Diagram Updates

**No breaking changes** - JSON schema is backward compatible:
- New fields (`index`, `custom_latex`) are optional
- Existing fields unchanged
- Diagrams can be opened in older Lynx versions (indices ignored)

## Performance Considerations

### Index Operations Complexity

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| Get index | O(1) | Direct parameter access |
| Auto-assign index | O(N) | N = markers of same type |
| Renumber (shift) | O(M) | M = markers affected by shift |
| Renumber (delete) | O(K) | K = markers with index > deleted |
| Validate indices | O(N) | N = total markers |

**Worst Case**: O(N) for diagrams with N markers of one type
**Expected**: O(5-20) for typical diagrams

### Memory Footprint

**Per IOMarker Block**:
- Base attributes: ~200 bytes
- `index` parameter: +16 bytes (int)
- `custom_latex` parameter: +variable (typically 10-50 chars = 10-50 bytes)
- **Total**: ~230-270 bytes per block

**100 IOMarker Diagram**: ~25 KB memory overhead (negligible)

---

## Summary

- **Core Entity**: IOMarker block with automatic index management
- **Key Innovation**: `index` and `label` are independent (visual ordering vs. export naming)
- **Backward Compatibility**: Automatic index assignment for legacy diagrams
- **Validation**: Defensive only - renumbering maintains invariants automatically
- **Performance**: O(N) operations acceptable for typical diagram sizes (5-20 markers)
