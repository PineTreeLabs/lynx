# Core Concepts

This guide explains the fundamental concepts behind Lynx's design and how they work together to model control systems.

The basic objects in a block diagram are the **diagram**, which contains **blocks** representing computational units or subsystems, and **connections** between the blocks representing signal flows.

## Diagram

A **Diagram** is the top-level container for your control system. It holds all blocks and connections, and provides methods for:

- Adding/removing blocks and connections
- Validating diagram structure
- Editing parameters
- Exporting to `python-control` system objects (state-space/transfer function)
- Saving/loading to JSON files

```python
import lynx

# Create an empty diagram
diagram = lynx.Diagram()

# Load from a pre-made template
diagram = lynx.Diagram.from_template("feedback_tf")

# Diagrams are serializable
diagram.save('my_system.json')
diagram_loaded = lynx.Diagram.load('my_system.json')
```

Lynx diagrams are **pure Python data structures** - they can be created programmatically in Python (not recommended), saved to/loaded from JSON, or edited interactively in Jupyter notebooks (recommended) with:

```python
lynx.edit(diagram)
```

## Block

A **Block** has the usual control system diagram semantics. Each block has:

- **Type**: Defines behavior (Gain, TransferFunction, StateSpace, Sum, IOMarker)
- **Parameters**: Configuration specific to the block type
- **Ports**: Input and output connection points
- **Label**: Optional human-readable identifier

### Ports

A **Port** is a typed connection point on a block. Every port has:

- **Direction**: Input or output
- **Port ID**: Identifier like `'in'`, `'out'`, `'in1'`, `'in2'`
- **Block**: The block it belongs to

Single-input/output blocks (Gain, TransferFunction, StateSpace) have `'in'` and `'out'` ports, while multi-input blocks (Sum) use `'in1'`, `'in2'`, etc. IOMarker blocks have one port, either `'out'` or `'in'` for input and output markers, respectively.

### Block Types Overview

| Block Type | Parameters | Ports |
|------------|------------|-------|
| **Gain** | `K` (gain value) | `in` → `out` |
| **TransferFunction** | `num`, `den` (coefficient arrays) | `in` → `out` |
| **StateSpace** | `A`, `B`, `C`, `D` (matrices) | `in` → `out` |
| **Sum** | `signs` (list: `"+"`, `"-"`, `"\|"` for each quadrant) | `in1`, `in2`, `in3` → `out` |
| **IOMarker** | `marker_type` (`'input'` or `'output'`), `label` | `out` (InputMarker) or `in` (OutputMarker) |

### Creating Blocks

```python
# Gain block: K = 5
diagram.add_block('gain', 'controller', K=5.0)

# Transfer function: G(s) = 2/(s+3)
diagram.add_block('transfer_function', 'plant',
                  num=[2.0],
                  den=[1.0, 3.0])

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

```python
diagram.add_connection(
    'connection_id',  # Unique identifier
    'source_block',   # Source block ID
    'source_port',    # Output port ID (e.g., 'out')
    'target_block',   # Target block ID
    'target_port',    # Input port ID (e.g., 'in', 'in1', 'in2')
    label="signal",   # Optional signal name
)
```

### Connection Rules

1. **One output to many inputs** is allowed (signal fanout)
2. **Many outputs to one input** is NOT allowed (use Sum block to combine)
3. **All input ports must be connected** before export
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


## Next Steps

Now that you understand the basic block diagram components, continue on with:


- {doc}`editor` - Quick intro to the graphical editor
- {doc}`templates` - Pre-built control system architectures
- {doc}`export` - Interoperability with the Python control systems library
- {doc}`validation` - Checks for diagram consistency


```{toctree}
:maxdepth: 2
:caption: Contents
:hidden:

editor
templates
export
validation
```
