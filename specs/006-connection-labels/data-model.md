<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Connection Labels

**Feature**: 006-connection-labels
**Date**: 2026-01-12

## Entity Changes

### Connection (Extended)

The existing `Connection` entity is extended with two new attributes for label support.

#### Python Dataclass (`src/lynx/diagram.py`)

```python
@dataclass
class Connection:
    """Connection between two block ports.

    Attributes:
        id: Unique connection identifier
        source_block_id: ID of source block
        source_port_id: ID of source port (output)
        target_block_id: ID of target block
        target_port_id: ID of target port (input)
        waypoints: Ordered list of intermediate routing points
        label: User-defined label text (defaults to connection ID if None)
        label_visible: Whether the label is displayed (default: False)
    """

    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: List[Dict[str, float]] = field(default_factory=list)
    label: Optional[str] = None  # NEW
    label_visible: bool = False  # NEW
```

#### Pydantic Schema (`src/lynx/schema.py`)

```python
class ConnectionModel(BaseModel):
    """Connection schema - edge between two block ports."""

    model_config = ConfigDict(extra="forbid")

    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: list[WaypointModel] = Field(default_factory=list)
    label: Optional[str] = None  # NEW: User-defined label text
    label_visible: bool = False  # NEW: Whether label is displayed
```

## Field Specifications

### label

| Property | Value |
|----------|-------|
| Type | `Optional[str]` |
| Default | `None` |
| Constraints | None (any text allowed) |
| Display Default | When `None`, UI displays connection ID |
| Persistence | Stored in JSON when set |

### label_visible

| Property | Value |
|----------|-------|
| Type | `bool` |
| Default | `False` |
| Constraints | Boolean only |
| Behavior | Controls whether label is rendered |
| Persistence | Always stored in JSON |

## Serialization Format

### JSON Schema

```json
{
  "id": "conn_123",
  "source_block_id": "gain_1",
  "source_port_id": "out",
  "target_block_id": "sum_1",
  "target_port_id": "in1",
  "waypoints": [
    {"x": 200, "y": 100},
    {"x": 200, "y": 150}
  ],
  "label": "velocity",
  "label_visible": true
}
```

### Backward Compatibility

Existing diagrams without `label` and `label_visible` fields will:
- Default `label` to `None` (displays as connection ID)
- Default `label_visible` to `False` (hidden)

No migration required - Pydantic handles defaults automatically.

## State Transitions

### Label Visibility

```
┌─────────────┐     toggleConnectionLabelVisibility()     ┌─────────────┐
│   Hidden    │ ─────────────────────────────────────────→ │   Visible   │
│ (default)   │                                            │             │
│             │ ←───────────────────────────────────────── │             │
└─────────────┘     toggleConnectionLabelVisibility()     └─────────────┘
```

### Label Text

```
┌─────────────┐     updateConnectionLabel(text)           ┌─────────────┐
│   Default   │ ─────────────────────────────────────────→ │   Custom    │
│ (conn ID)   │                                            │   (text)    │
│             │                                            │             │
└─────────────┘                                            └─────────────┘
```

## Validation Rules

1. **Connection ID Uniqueness**: Unchanged - connection IDs must be unique within diagram
2. **Label Text**: No validation - any string allowed (including empty string)
3. **Label Visible**: Boolean only - no other values accepted

## React Flow Data Mapping

### connectionToEdge() Function

```typescript
function connectionToEdge(conn: DiagramConnection): Edge {
  return {
    id: conn.id,
    source: conn.source_block_id,
    sourceHandle: conn.source_port_id,
    target: conn.target_block_id,
    targetHandle: conn.target_port_id,
    type: "orthogonal",
    data: {
      waypoints: conn.waypoints || [],
      label: conn.label,              // NEW
      label_visible: conn.label_visible || false,  // NEW
    },
    // ... marker config
  };
}
```

### OrthogonalEdgeData Interface

```typescript
interface OrthogonalEdgeData {
  waypoints?: Waypoint[];
  label?: string;           // NEW
  label_visible?: boolean;  // NEW
}
```

## Method Additions

### Diagram Class (`src/lynx/diagram.py`)

```python
def toggle_connection_label_visibility(self, connection_id: str) -> bool:
    """Toggle connection label visibility (with undo support).

    Args:
        connection_id: Connection identifier

    Returns:
        True if connection was found and toggled, False otherwise
    """

def update_connection_label(self, connection_id: str, label: str) -> bool:
    """Update connection label text (with undo support).

    Args:
        connection_id: Connection identifier
        label: New label text

    Returns:
        True if connection was found and updated, False otherwise
    """
```

## Index/Query Patterns

No new indices needed. Connections are accessed by ID using linear scan (diagrams typically have <50 connections).
