<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Editable Orthogonal Routing

**Feature**: 004-editable-orthogonal-routing
**Date**: 2026-01-06

## Overview

This document defines the data model changes required to support editable orthogonal routing with persistent waypoints.

---

## Entity Changes

### Connection (Extended)

The existing `Connection` entity is extended with an optional `waypoints` field.

**Current Fields** (unchanged):
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique connection identifier |
| `source_block_id` | string | ID of source block |
| `source_port_id` | string | ID of source port (output) |
| `target_block_id` | string | ID of target block |
| `target_port_id` | string | ID of target port (input) |

**New Field**:
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `waypoints` | `Waypoint[]` | `[]` | Ordered list of intermediate routing points |

### Waypoint (New)

A coordinate point that the connection path must pass through.

| Field | Type | Description |
|-------|------|-------------|
| `x` | number | Absolute canvas X coordinate |
| `y` | number | Absolute canvas Y coordinate |

**Constraints**:
- Coordinates are in canvas coordinate space (same as block positions)
- Values should be multiples of grid size (20px) after snapping
- Waypoints are ordered: path goes source → waypoint[0] → waypoint[1] → ... → target

---

## Schema Updates

### Python (Pydantic)

```python
# src/lynx/schema.py

class WaypointModel(BaseModel):
    """Waypoint schema - intermediate routing point."""

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class ConnectionModel(BaseModel):
    """Connection schema - edge between two block ports."""

    model_config = ConfigDict(extra="forbid")

    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: list[WaypointModel] = Field(default_factory=list)  # NEW
```

### Python (Dataclass)

```python
# src/lynx/diagram.py

@dataclass
class Connection:
    """Connection between two block ports."""

    id: str
    source_block_id: str
    source_port_id: str
    target_block_id: str
    target_port_id: str
    waypoints: List[Dict[str, float]] = field(default_factory=list)  # NEW

    def to_dict(self) -> Dict[str, Any]:
        """Serialize connection to dictionary."""
        return {
            "id": self.id,
            "source_block_id": self.source_block_id,
            "source_port_id": self.source_port_id,
            "target_block_id": self.target_block_id,
            "target_port_id": self.target_port_id,
            "waypoints": self.waypoints,  # NEW
        }
```

### TypeScript (Frontend)

```typescript
// js/src/utils/traitletSync.ts

interface Waypoint {
  x: number;
  y: number;
}

interface Connection {
  id: string;
  source_block_id: string;
  source_port_id: string;
  target_block_id: string;
  target_port_id: string;
  waypoints?: Waypoint[];  // NEW (optional for backward compatibility)
}

// Edge data for React Flow
interface OrthogonalEdgeData {
  waypoints?: Waypoint[];
}
```

---

## Serialization Format

### JSON Diagram File

```json
{
  "version": "1.0.0",
  "blocks": [...],
  "connections": [
    {
      "id": "conn_1",
      "source_block_id": "gain_1",
      "source_port_id": "out",
      "target_block_id": "sum_1",
      "target_port_id": "in1",
      "waypoints": [
        {"x": 300, "y": 200},
        {"x": 300, "y": 150},
        {"x": 400, "y": 150}
      ]
    },
    {
      "id": "conn_2",
      "source_block_id": "sum_1",
      "source_port_id": "out",
      "target_block_id": "output_1",
      "target_port_id": "in",
      "waypoints": []
    }
  ]
}
```

### Backward Compatibility

- **Loading old diagrams**: Missing `waypoints` field defaults to `[]` (auto-routing)
- **Saving with old software**: Software without waypoint support will silently drop the field
- **Version field**: Remains `"1.0.0"` (additive change, not breaking)

---

## State Transitions

### Waypoint Lifecycle

```
[Auto-Routed] ──(user drags segment)──> [Custom Waypoints]
     ↑                                          │
     │                                          │
     └────────(reset to auto)──────────────────┘
```

### Connection State

| State | waypoints | Description |
|-------|-----------|-------------|
| Auto-routed | `[]` | Default algorithm calculates path |
| Custom | `[{x,y}, ...]` | Path routes through specified waypoints |

---

## Validation Rules

1. **Coordinate Range**: Waypoint coordinates should be reasonable canvas values (not NaN, Infinity)
2. **Order Preserved**: Waypoints maintain insertion order
3. **No Duplicates**: Adjacent identical waypoints are auto-merged
4. **Grid Alignment**: After dragging, waypoints are snapped to 20px grid

---

## Related Changes

### Diagram Class Methods (New)

```python
# src/lynx/diagram.py

def update_connection_waypoints(
    self,
    connection_id: str,
    waypoints: List[Dict[str, float]]
) -> bool:
    """Update waypoints for a connection (with undo support).

    Args:
        connection_id: Connection identifier
        waypoints: New waypoints list

    Returns:
        True if connection was found and updated
    """
```

### Widget Action Handler (New)

```python
# src/lynx/widget.py

def _handle_update_connection_routing(self, payload: Dict[str, Any]) -> None:
    """Handle updateConnectionRouting action from frontend."""
```
