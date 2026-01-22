<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Python-Control Export

**Feature**: 012-python-control-export
**Date**: 2026-01-15

## Overview

This feature transforms Lynx diagram entities into python-control system objects. Since it's a pure transformation (no persistence), the "data model" describes the mapping between Lynx entities and python-control entities, plus any intermediate data structures used during export.

---

## Entity Mappings

### Lynx → python-control Block Mappings

| Lynx Block Type | Lynx Parameters | python-control Constructor | python-control Type |
|-----------------|-----------------|----------------------------|---------------------|
| **GainBlock** | `K: float` | `ct.tf(K, 1, name=id, inputs=['in'], outputs=['out'])` | TransferFunction |
| **TransferFunctionBlock** | `numerator: List[float]`<br>`denominator: List[float]` | `ct.tf(num, den, name=id, inputs=['in'], outputs=['out'])` | TransferFunction |
| **StateSpaceBlock** | `A: List[List[float]]`<br>`B: List[List[float]]`<br>`C: List[List[float]]`<br>`D: List[List[float]]` | `ct.ss(A, B, C, D, name=id, inputs=['in'], outputs=['out'])` | StateSpace |
| **SumBlock** | `signs: List[str]`<br>(values: `"+"`, `"-"`, `"\|"`) | `ct.summing_junction(inputs=[port_ids], output='out', name=id)` | InputOutputSystem |
| **InputMarker** | `label: Optional[str]` | → `inplist` entry: `f'{id}.out'` | (not a subsystem) |
| **OutputMarker** | `label: Optional[str]` | → `outlist` entry: `f'{id}.in'` | (not a subsystem) |

**Notes**:
- All blocks use `name=block.id` for signal routing
- SISO blocks use fixed port names: `inputs=['in']`, `outputs=['out']`
- Sum blocks have variable input ports (`in1`, `in2`, `in3`) based on non-`"|"` signs

---

### Connection Transformation

**Lynx Connection**:
```python
{
    "id": "conn1",
    "source_block_id": "gain_1",
    "source_port_id": "out",
    "target_block_id": "tf_2",
    "target_port_id": "in"
}
```

**python-control Connection**:
```python
['gain_1.out', 'tf_2.in']
```

**Transformation Rule**:
```python
source_signal = f"{conn.source_block_id}.{conn.source_port_id}"
target_signal = f"{conn.target_block_id}.{conn.target_port_id}"

# Handle Sum block negation
if target_block.type == 'sum':
    sign = get_sign_for_port(target_block, conn.target_port_id)
    if sign == '-':
        source_signal = f'-{source_signal}'

connection = [source_signal, target_signal]
```

---

## Intermediate Data Structures

### ValidationResult (Internal)

Used during validation phase to collect errors before raising exception.

**Fields**:
- `is_valid: bool` - Overall validation status
- `errors: List[str]` - Collected error messages
- `warnings: List[str]` - Non-blocking issues (empty for this feature)

**Usage**:
```python
def _validate_for_export(self) -> ValidationResult:
    errors = []

    # Check system boundaries
    if not any(b.type == 'io_marker' and b.get_parameter('marker_type') == 'input'
               for b in self.blocks):
        errors.append("Diagram has no InputMarker blocks. Add at least one system input.")

    # ... more checks

    return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=[])
```

---

### SignalName (Conceptual Type)

Not a concrete class, but a pattern for signal identifiers.

**Format**: `'block_id.port_id'` or `'-block_id.port_id'` (with negation)

**Examples**:
- `'gain_1.out'` - Output signal from gain block
- `'sum_1.in2'` - Second input to sum block
- `'-gain_1.out'` - Negated output (for sum block subtraction)
- `'input_marker_1.out'` - Input marker output (goes in `inplist`)

**Validation Rules**:
- Must match pattern `^-?[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$`
- Block ID must exist in diagram
- Port ID must exist on that block
- Negation (`-` prefix) only valid for connections to Sum block negative inputs

---

## State Transitions

### Export Process State Machine

```text
┌─────────────┐
│   Initial   │ (Diagram object with blocks + connections)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Validation    │ Check boundaries, connections, completeness
└──────┬──────────┘
       │
       ├─ INVALID → raise ValidationError
       │
       ▼ VALID
┌──────────────────┐
│ Block Conversion │ Lynx blocks → python-control subsystems
└──────┬───────────┘
       │
       ▼
┌────────────────────┐
│ Connection Mapping │ Lynx connections → signal pairs
└──────┬─────────────┘
       │
       ▼
┌──────────────────┐
│  I/O Extraction  │ InputMarker/OutputMarker → inplist/outlist
└──────┬───────────┘
       │
       ▼
┌────────────────────┐
│   interconnect()   │ Build python-control InterconnectedSystem
└──────┬─────────────┘
       │
       ├─ ERROR → wrap and re-raise with context
       │
       ▼ SUCCESS
┌──────────────────────┐
│ InterconnectedSystem │ Ready for simulation
└──────────────────────┘
```

**Error Recovery**:
- **Validation failure**: User fixes diagram, re-exports (no partial state)
- **python-control error**: Indicates Lynx bug or python-control version issue, user reports

---

## Validation Rules

### System Boundary Rules (FR-011, FR-012)

**Rule**: `must_have_input_markers`
- **Check**: `any(block for block in diagram.blocks if is_input_marker(block))`
- **Error**: `"Diagram has no InputMarker blocks. Add at least one system input."`

**Rule**: `must_have_output_markers`
- **Check**: `any(block for block in diagram.blocks if is_output_marker(block))`
- **Error**: `"Diagram has no OutputMarker blocks. Add at least one system output."`

### Port Connection Rules (FR-010)

**Rule**: `all_inputs_connected`
- **Check**: For each block (except InputMarker), for each input port, verify connection exists
- **Implementation**:
  ```python
  for block in diagram.blocks:
      if block.type == 'io_marker' and block.get_parameter('marker_type') == 'input':
          continue  # InputMarkers don't need connected inputs

      for port in block._ports:
          if port.type == 'input':
              connected = any(
                  conn.target_block_id == block.id and conn.target_port_id == port.id
                  for conn in diagram.connections
              )
              if not connected:
                  errors.append(f"Block '{block.id}' input port '{port.id}' is not connected")
  ```

### Sum Block Sign Rules

**Rule**: `sum_sign_mapping_valid`
- **Check**: For each Sum block connection, verify sign extraction succeeds
- **Error**: If `get_sign_for_port()` raises, indicates internal consistency error (should never happen in practice)

---

## Type Definitions (Python)

```python
from typing import List, Tuple, Optional
from control import TransferFunction, StateSpace, InputOutputSystem, InterconnectedSystem

# Type aliases for clarity
SignalName = str  # 'block_id.port_id' or '-block_id.port_id'
Connection = Tuple[SignalName, SignalName]  # [source, target] pair
Subsystem = TransferFunction | StateSpace | InputOutputSystem

class ValidationError(Exception):
    """Raised when diagram validation fails before export."""
    def __init__(self, message: str, block_id: Optional[str] = None,
                 port_id: Optional[str] = None):
        self.block_id = block_id
        self.port_id = port_id
        super().__init__(message)

class DiagramExportError(Exception):
    """Base exception for diagram export failures."""
    pass
```

---

## Relationships

### Block → Subsystem (1:1 or 1:0)

- Each Lynx block (except I/O markers) maps to exactly one python-control subsystem
- I/O markers don't create subsystems (extracted to inplist/outlist instead)

### Connection → Signal Pair (1:1)

- Each Lynx connection maps to exactly one python-control connection `[source, target]`
- Negation modifier applied based on target block sign configuration

### Diagram → InterconnectedSystem (1:1)

- Each valid Lynx diagram exports to exactly one python-control InterconnectedSystem
- Invalid diagrams raise ValidationError, no partial export

---

## Invariants

1. **Signal Name Uniqueness**: All signal names (`block_id.port_id`) must be unique within a diagram
   - Guaranteed by Lynx: block IDs are unique, port IDs unique per block

2. **Connection Validity**: All connections reference existing blocks and ports
   - Guaranteed by Lynx: `add_connection()` validates before adding

3. **Sum Block Port Consistency**: Sum block ports match signs configuration
   - Guaranteed by Lynx: `SumBlock.__init__()` creates ports based on signs
   - Export validates: `get_sign_for_port()` must succeed for all Sum connections

4. **System Boundary Completeness**: At least one input and one output marker
   - Validated by export: raises ValidationError if violated

---

## Performance Characteristics

### Space Complexity

- **Subsystems list**: O(n) where n = number of blocks
- **Connections list**: O(m) where m = number of connections
- **I/O lists**: O(k) where k = number of I/O markers
- **Total**: O(n + m + k) ≈ O(n) for typical diagrams

### Time Complexity

- **Validation**: O(n + m) - iterate all blocks and connections once
- **Block conversion**: O(n) - one subsystem per block
- **Connection mapping**: O(m) - one signal pair per connection
- **I/O extraction**: O(k) - one entry per marker
- **interconnect() call**: O(n + m) - python-control internal complexity
- **Total**: O(n + m) linear in diagram size

**Measured Performance** (expected):
- 50 blocks + 60 connections: ~70ms
- 100 blocks + 120 connections: ~140ms
- Dominated by python-control object creation overhead

---

## Example Transformation

### Input: Lynx Diagram (Simple Feedback Loop)

**Blocks**:
- `input_1`: InputMarker (label="r")
- `error_sum`: SumBlock (signs=["+", "-", "|"])
- `controller`: GainBlock (K=10.0)
- `plant`: TransferFunctionBlock (numerator=[1], denominator=[1, 2, 1])
- `output_1`: OutputMarker (label="y")

**Connections**:
1. `input_1.out` → `error_sum.in1` (reference signal)
2. `error_sum.out` → `controller.in` (error signal)
3. `controller.out` → `plant.in` (control signal)
4. `plant.out` → `output_1.in` (output signal)
5. `plant.out` → `error_sum.in2` (feedback signal, negative)

### Output: python-control InterconnectedSystem

```python
import control as ct

# Subsystems
input_marker = ct.tf(1, 1, name='input_1', inputs=['in'], outputs=['out'])  # Identity
error_sum = ct.summing_junction(inputs=['in1', 'in2'], output='out', name='error_sum')
controller = ct.tf(10.0, 1, name='controller', inputs=['in'], outputs=['out'])
plant = ct.tf([1], [1, 2, 1], name='plant', inputs=['in'], outputs=['out'])
output_marker = ct.tf(1, 1, name='output_1', inputs=['in'], outputs=['out'])  # Identity

# Connections (note negation on feedback connection)
connections = [
    ['input_1.out', 'error_sum.in1'],
    ['error_sum.out', 'controller.in'],
    ['controller.out', 'plant.in'],
    ['plant.out', 'output_1.in'],
    ['-plant.out', 'error_sum.in2'],  # Negative feedback
]

# System I/O
inplist = ['input_1.out']  # System input: reference signal
outlist = ['output_1.in']  # System output: controlled variable

# Build interconnected system
sys = ct.interconnect(
    [input_marker, error_sum, controller, plant, output_marker],
    connections=connections,
    inplist=inplist,
    outlist=outlist
)

# Ready for simulation
t, y = ct.step_response(sys)
```

---

## Data Model Summary

This feature's "data model" is primarily a **transformation schema** rather than persistent entities:

1. **Mapping rules** define Lynx → python-control conversions
2. **Validation rules** ensure diagram completeness
3. **Intermediate structures** (`ValidationResult`, `SignalName` pattern) support the export process
4. **Exception types** provide structured error reporting

The export operation is **stateless** and **idempotent**: same Lynx diagram always produces equivalent python-control system (modulo python-control's internal object IDs).
