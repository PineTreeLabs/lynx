# Core Concepts

This guide explains the fundamental concepts behind Lynx's design: diagrams, blocks, connections, and how they work together to model control systems.

## Diagram

A **Diagram** is the top-level container for your control system. It holds all blocks and connections, and provides methods for:

- Adding/removing blocks and connections
- Exporting to python-control systems
- Saving/loading to JSON files
- Validation before export

```python
import lynx

# Create an empty diagram
diagram = lynx.Diagram()

# Diagrams are serializable
diagram.save('my_system.json')
diagram_loaded = lynx.Diagram.load('my_system.json')
```

### Diagram as Data

Lynx diagrams are **pure data structures** - they can be:
- Created programmatically in Python
- Saved to/loaded from JSON files
- Edited interactively with `lynx.edit(diagram)`
- Exported to python-control for analysis

## Block

A **Block** represents a computational unit in your control system. Each block has:

- **Type**: Defines behavior (Gain, TransferFunction, StateSpace, Sum, IOMarker)
- **Parameters**: Configuration specific to the block type
- **Ports**: Input and output connection points
- **Label**: Optional human-readable identifier (not the same as block ID)

### Block Types Overview

| Block Type | Use Case | Parameters | Ports |
|------------|----------|------------|-------|
| **Gain** | Scalar multiplication, controller gains | `K` (gain value) | `in` → `out` |
| **TransferFunction** | LTI systems in s-domain | `numerator`, `denominator` (coefficient arrays) | `in` → `out` |
| **StateSpace** | MIMO systems, state feedback | `A`, `B`, `C`, `D` (matrices) | `in` → `out` |
| **Sum** | Adding/subtracting signals | `signs` (list: `"+"`, `"-"`, `"|"` for each quadrant) | `in1`, `in2`, `in3` → `out` |
| **IOMarker** | System boundaries for export | `marker_type` (`'input'` or `'output'`), `label` | `out` (InputMarker) or `in` (OutputMarker) |

### When to Use Each Block

**Gain** blocks are ideal for:
- Simple controller gains (P, I, D components)
- Unit conversions or scaling factors
- Quick prototyping before implementing full controllers

**TransferFunction** blocks are best for:
- Plant models from system identification
- Classical control design (lead/lag compensators, PID)
- Single-input single-output (SISO) systems in frequency domain

**StateSpace** blocks excel at:
- Multi-input multi-output (MIMO) systems
- State feedback control
- Systems derived from physical models (Newton's laws, circuit equations)
- Observer design

**Sum** blocks are used for:
- Error calculation (reference - output)
- Combining multiple signals (feedforward + feedback)
- Weighted sums with different signs per input

**IOMarker** blocks define:
- System boundaries for subsystem extraction
- Named signals for `diagram.get_ss()` and `diagram.get_tf()` calls
- Documentation of system inputs and outputs

### Creating Blocks

```python
# Gain block: K = 5
diagram.add_block('gain', 'controller', K=5.0)

# Transfer function: G(s) = 2/(s+3)
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0],
                  denominator=[1.0, 3.0])

# State-space: x_dot = Ax + Bu, y = Cx + Du
import numpy as np
A = np.array([[0, 1], [0, 0]])
B = np.array([[0], [1]])
C = np.array([[1, 0]])
D = np.array([[0]])
diagram.add_block('state_space', 'plant', A=A, B=B, C=C, D=D)

# Sum block with 2 inputs (top: +, left: -)
diagram.add_block('sum', 'error', signs=['+', '-', '|'])

# Input/Output markers
diagram.add_block('io_marker', 'r', marker_type='input', label='r')
diagram.add_block('io_marker', 'y', marker_type='output', label='y')
```

## Connection

A **Connection** represents a directed signal flow from one block's output port to another block's input port.

### Connection Anatomy

```python
diagram.add_connection(
    'connection_id',  # Unique identifier
    'source_block',   # Source block ID
    'source_port',    # Output port ID (e.g., 'out')
    'target_block',   # Target block ID
    'target_port'     # Input port ID (e.g., 'in', 'in1', 'in2')
)
```

### Connection Rules

1. **One output to many inputs** is allowed (signal fanout)
2. **Many outputs to one input** is NOT allowed (use Sum block to combine)
3. **All input ports must be connected** before export (except InputMarker blocks)
4. **Output ports can remain unconnected** (signals computed but not used)

### Example: Feedback Loop

```python
# Forward path: r -> error -> controller -> plant -> y
diagram.add_connection('c1', 'r', 'out', 'error', 'in1')
diagram.add_connection('c2', 'error', 'out', 'controller', 'in')
diagram.add_connection('c3', 'controller', 'out', 'plant', 'in')
diagram.add_connection('c4', 'plant', 'out', 'y', 'in')

# Feedback path: plant output -> error input (negative feedback)
diagram.add_connection('c5', 'plant', 'out', 'error', 'in2')
```

## Port

A **Port** is a typed connection point on a block. Every port has:

- **Direction**: Input or output
- **Port ID**: Identifier like `'in'`, `'out'`, `'in1'`, `'in2'`
- **Block**: The block it belongs to

### Port Conventions

- **Single-input blocks** (Gain, TransferFunction, StateSpace): Use `'in'` and `'out'`
- **Multi-input blocks** (Sum): Use `'in1'`, `'in2'`, `'in3'` for top, left, bottom quadrants
- **IOMarkers**: InputMarker has `'out'` only, OutputMarker has `'in'` only

## Signal References for Export

When you export a subsystem with `diagram.get_ss(from_signal, to_signal)` or `diagram.get_tf(from_signal, to_signal)`, Lynx needs to identify which signals to use. Signal references follow a **3-tier priority system**:

### 1. IOMarker Labels (Highest Priority)

Use the `label` parameter from InputMarker or OutputMarker blocks:

```python
diagram.add_block('io_marker', 'ref_marker', marker_type='input', label='r')
diagram.add_block('io_marker', 'out_marker', marker_type='output', label='y')

# Export using IOMarker labels (recommended)
sys = diagram.get_tf('r', 'y')
```

**Best practice**: Use IOMarker labels for all system boundaries and subsystem extraction.

### 2. Connection Labels (Medium Priority)

Reference labeled connections between blocks:

```python
diagram.add_connection('error_conn', 'sum', 'out', 'controller', 'in',
                       label='error')

# Export using connection label
sys = diagram.get_ss('r', 'error')
```

**Use case**: Extracting internal signals without adding extra IOMarker blocks.

### 3. Block.Port Notation (Lowest Priority)

Explicit reference using `block_label.output_port` format:

```python
# Export using block label + port
sys = diagram.get_ss('controller.out', 'plant.out')
```

**Important**:
- Must use block **label** (not block ID)
- Must reference **output** ports only (signals are outputs, not inputs)
- Requires explicit `.out` suffix (bare block labels no longer supported)

### Signal Resolution Example

```python
# All three signals are valid for export:
# - 'r' (IOMarker label - highest priority)
# - 'error' (connection label)
# - 'controller.out' (block.port notation)

# Get transfer function from reference to error
sys_re = diagram.get_tf('r', 'error')

# Get transfer function from error to plant output
sys_ey = diagram.get_tf('error', 'plant.out')

# Full closed-loop transfer function
sys_ry = diagram.get_tf('r', 'y')
```

## Validation

Before exporting to python-control, Lynx performs **three layers of validation**:

### Layer 1: System Boundaries

Every diagram must have:
- **At least one InputMarker** (system input)
- **At least one OutputMarker** (system output)

Without these, there's no well-defined system to export.

### Layer 2: Label Uniqueness

Lynx checks for duplicate labels and issues warnings:
- Duplicate block labels
- Duplicate connection labels

**Important**: These are warnings, not errors. The export will proceed, but ambiguous references may cause unexpected behavior.

### Layer 3: Port Connectivity

All input ports must be connected, except:
- **InputMarker blocks** (they define system inputs)
- Ports on blocks that are not part of the signal path being extracted

### Example ValidationError

```python
# Forgot to connect controller input
diagram.add_block('gain', 'controller', K=5.0)
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0], denominator=[1.0, 3.0])
diagram.add_connection('c1', 'controller', 'out', 'plant', 'in')

try:
    sys = diagram.get_tf('r', 'y')
except lynx.ValidationError as e:
    print(e)
    # "Validation failed: input port 'in' on block 'controller' is not connected"
```

### Fixing Validation Errors

The error message includes:
- **Block ID**: Which block has the issue
- **Port ID**: Which port is problematic
- **Guidance**: What needs to be fixed

Common fixes:
1. **Missing input connection**: Add connection from upstream block
2. **Missing IOMarker**: Add InputMarker or OutputMarker to define system boundary
3. **Duplicate labels**: Rename blocks/connections to ensure uniqueness

## Interactive Widget

The relationship between Python code and the interactive widget:

```python
# 1. Create diagram programmatically
diagram = lynx.Diagram()
diagram.add_block('gain', 'K', K=5.0)
diagram.add_block('transfer_function', 'G',
                  numerator=[2.0], denominator=[1.0, 3.0])
diagram.add_connection('c1', 'K', 'out', 'G', 'in')

# 2. Launch interactive widget
lynx.edit(diagram)

# 3. User makes changes in UI:
#    - Drag blocks to new positions
#    - Edit parameters in property panel
#    - Add/remove connections
#    - Adjust routing waypoints

# 4. Changes are bidirectionally synced
# The diagram object is updated automatically!
print(diagram.blocks['K'].parameters['K'])  # May have changed if user edited it
```

### Use Cases

**Visual verification**:
- Check that programmatic diagram construction is correct
- Verify signal routing and connection topology

**Manual layout adjustments**:
- Position blocks for clear visualization
- Adjust connection routing for readability

**Exploratory design**:
- Quickly try different topologies
- Add/remove blocks interactively
- Experiment with parameter values

**Documentation**:
- Generate clean block diagrams for papers/presentations
- Export screenshots with `lynx.edit(diagram).export_png('diagram.png')`

## Next Steps

Now that you understand Lynx's core concepts:

- {doc}`quickstart` - Quick reference for creating diagrams
- {doc}`../api/index` - Full API documentation
- {doc}`../examples/index` - Learn through executable examples
- Try designing your own control system!
