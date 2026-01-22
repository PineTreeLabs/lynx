<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Lynx Block Diagram Widget

**Feature**: 001-lynx-jupyter-widget
**Date**: 2025-12-25

## Overview

This document defines the core entities, their attributes, relationships, and validation rules for the Lynx block diagram widget. The data model supports SISO control system diagrams with five block types, connections, and parameters.

## Entity Diagram

```
Diagram
 ├──* Block
 │    ├── id: string (UUID)
 │    ├── type: enum (TF, SS, Gain, Sum, IO)
 │    ├── position: {x: number, y: number}
 │    ├──* Parameter
 │    │    ├── name: string
 │    │    ├── expression: string (optional)
 │    │    └── value: any (number, array, matrix)
 │    ├──* Port
 │         ├── id: string
 │         ├── type: enum (input, output)
 │         └── label: string (optional)
 └──* Connection
      ├── id: string (UUID)
      ├── sourceBlockId: string
      ├── sourcePortId: string
      ├── targetBlockId: string
      └── targetPortId: string
```

## Core Entities

### Diagram

**Purpose**: Top-level container for a complete block diagram.

**Attributes**:
- `version`: string - JSON schema version (e.g., "1.0.0")
- `blocks`: Block[] - List of all blocks in diagram
- `connections`: Connection[] - List of all connections between blocks
- `metadata`: object (optional) - User-defined metadata (name, description, created date, etc.)

**Relationships**:
- Has many Blocks (1:N)
- Has many Connections (1:N)

**Validation Rules**:
- Must have at least one Input block and one Output block for "export-ready" status
- May have disconnected blocks (warning, but allowed)
- No duplicate block IDs
- No duplicate connection IDs

**State Transitions**:
- Empty → Has Blocks → Has Connections → Export-Ready
- Any state → Saved (via diagram.save())
- Saved → Loaded (via Diagram.load())

**JSON Example**:
```json
{
  "version": "1.0.0",
  "metadata": {
    "name": "PID Controller",
    "created": "2025-12-25T10:00:00Z"
  },
  "blocks": [...],
  "connections": [...]
}
```

---

### Block

**Purpose**: Visual element representing a control system component.

**Attributes**:
- `id`: string (UUID) - Unique identifier
- `type`: enum - One of: "transfer_function", "state_space", "gain", "sum", "io_marker"
- `position`: {x: number, y: number} - Canvas coordinates
- `parameters`: Parameter[] - Block-specific parameters
- `ports`: Port[] - Input/output connection points
- `label`: string (optional) - User-defined block label

**Relationships**:
- Belongs to Diagram (N:1)
- Has many Parameters (1:N)
- Has many Ports (1:N)
- Connected via Connections (N:N through Connection entity)

**Validation Rules**:
- ID must be unique within diagram
- Type must be one of five allowed types
- Position coordinates must be non-negative
- Parameters must match type requirements (see Block Type Specifications below)

**Block Type Specifications**:

#### Transfer Function Block
**Parameters**:
- `numerator`: number[] - Polynomial coefficients (descending powers of s)
- `denominator`: number[] - Polynomial coefficients (descending powers of s)

**Ports**:
- 1 input port
- 1 output port

**Validation**:
- Numerator and denominator must be non-empty arrays
- Denominator cannot be all zeros
- At least one coefficient must be non-zero

**Example**:
```json
{
  "id": "block-1",
  "type": "transfer_function",
  "position": {"x": 100, "y": 200},
  "parameters": [
    {"name": "numerator", "value": [5, 3]},
    {"name": "denominator", "value": [1, 2, 1]}
  ],
  "ports": [
    {"id": "in", "type": "input"},
    {"id": "out", "type": "output"}
  ]
}
```

#### State Space Block
**Parameters**:
- `A`: matrix - State matrix
- `B`: matrix - Input matrix
- `C`: matrix - Output matrix
- `D`: matrix - Feedthrough matrix

**Storage**: Each matrix parameter uses hybrid storage:
```json
{
  "name": "A",
  "expression": "np.eye(2)",
  "value": [[1, 0], [0, 1]]
}
```

**Ports**:
- 1 input port
- 1 output port

**Validation**:
- Matrix dimensions must be compatible (A: n×n, B: n×m, C: p×n, D: p×m for SISO: m=1, p=1)
- Matrices must be numeric

#### Gain Block
**Parameters**:
- `K`: number - Scalar gain value

**Ports**:
- 1 input port
- 1 output port

**Validation**:
- K must be a finite number

#### Sum Block
**Parameters**:
- `signs`: string[] - Array of "+" or "-" for each input port

**Ports**:
- N input ports (2+ required)
- 1 output port

**Validation**:
- Must have at least 2 input ports
- Number of signs must match number of input ports
- Each sign must be "+" or "-"

**Example**:
```json
{
  "id": "sum-1",
  "type": "sum",
  "parameters": [
    {"name": "signs", "value": ["+", "-"]}
  ],
  "ports": [
    {"id": "in1", "type": "input", "label": "+"},
    {"id": "in2", "type": "input", "label": "-"},
    {"id": "out", "type": "output"}
  ]
}
```

#### Input/Output Marker Block
**Parameters**:
- `label`: string (optional) - Name of input/output signal

**Ports**:
- Input marker: 1 output port
- Output marker: 1 input port

**Validation**:
- Label should be unique among all I/O markers (warning if duplicate)

---

### Connection

**Purpose**: Directed link between two blocks representing signal flow.

**Attributes**:
- `id`: string (UUID) - Unique identifier
- `sourceBlockId`: string - ID of source block
- `sourcePortId`: string - ID of source port
- `targetBlockId`: string - ID of target block
- `targetPortId`: string - ID of target port

**Relationships**:
- Belongs to Diagram (N:1)
- Connects two Blocks via their Ports

**Validation Rules** (CRITICAL - Control Theory Constraints):
1. **One Connection Per Input Port**: Each input port can have at most one incoming connection
2. **Unlimited Output Fan-Out**: Output ports can connect to multiple input ports
3. **No Self-Loops** (implicit): sourceBlockId ≠ targetBlockId
4. **Valid Port Types**: Source port must be "output", target port must be "input"
5. **No Algebraic Loops**: Feedback cycles must contain at least one dynamic block (transfer function or state space)

**JSON Example**:
```json
{
  "id": "conn-1",
  "sourceBlockId": "block-1",
  "sourcePortId": "out",
  "targetBlockId": "block-2",
  "targetPortId": "in"
}
```

---

### Port

**Purpose**: Connection point on a block (input or output).

**Attributes**:
- `id`: string - Unique identifier within block
- `type`: enum - "input" or "output"
- `label`: string (optional) - Display label (e.g., "+" or "-" for sum junctions)

**Relationships**:
- Belongs to Block (N:1)
- Referenced by Connections

**Validation Rules**:
- Port ID must be unique within block
- Type must be "input" or "output"

---

### Parameter

**Purpose**: Configurable value on a block.

**Attributes**:
- `name`: string - Parameter name (e.g., "numerator", "K", "A")
- `value`: any - Resolved value (number, array, matrix)
- `expression`: string (optional) - Original Python expression (for matrix parameters)

**Relationships**:
- Belongs to Block (N:1)

**Hybrid Storage** (for matrix parameters):
- Store both `expression` (what user entered) and `value` (resolved result)
- On save: Evaluate expression, store both
- On load: Try to re-evaluate expression; if fails, use stored value with warning

**Validation Rules**:
- Name must match expected parameter for block type
- Value must be valid for parameter type (number, array, matrix)
- Expression (if present) must be valid Python when evaluated

**JSON Example (scalar)**:
```json
{"name": "K", "value": 5.0}
```

**JSON Example (matrix with hybrid storage)**:
```json
{
  "name": "A",
  "expression": "np.eye(2)",
  "value": [[1, 0], [0, 1]]
}
```

---

## Validation Result Entity

**Purpose**: Outcome of diagram validation check.

**Attributes**:
- `isValid`: boolean - Overall validation result
- `errors`: ValidationError[] - Blocking errors that prevent export
- `warnings`: ValidationWarning[] - Non-blocking issues (e.g., disconnected blocks)
- `isExportReady`: boolean - Has at least one input and one output block

**ValidationError**:
- `code`: string - Error code (e.g., "ALGEBRAIC_LOOP", "DUPLICATE_INPUT_CONNECTION")
- `message`: string - Human-readable error message
- `affectedBlocks`: string[] - IDs of blocks involved
- `affectedConnections`: string[] - IDs of connections involved

**ValidationWarning**:
- `code`: string - Warning code (e.g., "DISCONNECTED_BLOCK")
- `message`: string - Human-readable warning message
- `affectedBlocks`: string[] - IDs of blocks involved

---

## Control Theory Validation Rules

### Algebraic Loop Detection

**Rule**: NO feedback cycles containing only Gain and Sum blocks.

**Algorithm**:
1. Build directed graph from connections
2. Detect cycles using depth-first search
3. For each cycle, check if it contains at least one dynamic block (Transfer Function or State Space)
4. If cycle has only Gain/Sum blocks → ERROR

**Error Message**: "Algebraic loop detected: Feedback loops must contain at least one dynamic block (Transfer Function or State Space)"

### Connection Constraints

**Rule 1: One Connection Per Input Port**
- Each input port can have at most one incoming connection
- Attempting second connection → ERROR

**Rule 2: Unlimited Output Fan-Out**
- Output ports can connect to multiple input ports (allowed)

**Rule 3: Valid Port Types**
- Connection source must be output port
- Connection target must be input port

### System Completeness

**Rule**: For export-ready status, diagram must have:
- At least one Input marker block
- At least one Output marker block

**If missing**: Warning (diagram can still be saved, but not exported)

---

## JSON Schema Version Management

**Current Version**: "1.0.0"

**Forward Compatibility Strategy**:
- Ignore unknown fields when loading older diagrams
- Provide sensible defaults for missing required fields

**Backward Compatibility Strategy**:
- Include version in all saved JSON files
- Deserializer checks version and applies appropriate loading logic

**Version Bump Rules**:
- MAJOR: Breaking changes (removed required fields, incompatible type changes)
- MINOR: New optional fields, new block types
- PATCH: Bug fixes, clarifications

**Example Version Evolution**:
- 1.0.0: Initial MVP
- 1.1.0: Add new block type (e.g., delay block) - Minor bump
- 2.0.0: Change parameter structure - Major bump

---

## Relationships Summary

```
Diagram 1──* Block
Diagram 1──* Connection
Block 1──* Parameter
Block 1──* Port
Connection N──1 Port (source)
Connection N──1 Port (target)
```

**Key Constraints**:
- Diagram owns all blocks and connections
- Blocks cannot exist outside a diagram
- Connections reference blocks by ID (foreign key relationship)
- Parameters and ports belong to specific blocks

---

## State Management (Traitlet Synchronization)

**Python → JavaScript** (Read-only in frontend):
- Diagram state (blocks, connections)
- Validation results
- Parameter values (including evaluated matrix values)

**JavaScript → Python** (User actions):
- Block added/deleted/moved
- Connection created/deleted
- Parameter edited
- Save triggered
- Load triggered

**Sync Pattern**: Bidirectional via traitlets. Python is source of truth for validation and persistence.
