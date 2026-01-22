# Diagram Class

The `Diagram` class is the central object for creating and managing control system diagrams in Lynx.

## Overview

A diagram contains:
- **Blocks**: Computational units (Gain, TransferFunction, StateSpace, Sum, IOMarker)
- **Connections**: Directed edges between block ports
- **Metadata**: Labels, positions, and parameters

All modifications are performed in-place. Diagrams can be saved to and loaded from JSON files.

## Creating Diagrams

```python
import lynx

# Create empty diagram
diagram = lynx.Diagram()

# Load existing diagram
diagram = lynx.Diagram.load('my_diagram.json')
```

## Adding Blocks

Use `add_block()` to add blocks to your diagram:

```python
# Syntax: add_block(block_type, block_id, **parameters)

# Gain block
diagram.add_block('gain', 'controller', K=5.0, position={'x': 100, 'y': 50})

# Transfer function: G(s) = 2/(s+3)
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0],
                  denominator=[1.0, 3.0],
                  position={'x': 200, 'y': 50})

# State-space block with A, B, C, D matrices
import numpy as np
A = np.array([[-1, 0], [0, -2]])
B = np.array([[1], [1]])
C = np.array([[1, 0]])
D = np.array([[0]])
diagram.add_block('state_space', 'ss_system',
                  A=A, B=B, C=C, D=D,
                  position={'x': 300, 'y': 50})

# Sum block with configurable signs
diagram.add_block('sum', 'error_sum',
                  signs=['+', '-', '|'],  # top, left, bottom
                  position={'x': 50, 'y': 50})

# I/O markers for system boundaries
diagram.add_block('io_marker', 'r', marker_type='input', label='r', position={'x': 0, 'y': 50})
diagram.add_block('io_marker', 'y', marker_type='output', label='y', position={'x': 400, 'y': 50})
```

## Adding Connections

Use `add_connection()` to connect block ports:

```python
# Syntax: add_connection(connection_id, source_block, source_port, target_block, target_port)

# Basic connection
diagram.add_connection('c1', 'controller', 'out', 'plant', 'in')

# Connection with label (useful for export)
diagram.add_connection('c2', 'plant', 'out', 'y', 'in', label='output_signal')

# Feedback connection
diagram.add_connection('c3', 'plant', 'out', 'error_sum', 'in2')
```

## Saving and Loading

```python
# Save to JSON file
diagram.save('my_control_system.json')

# Load from JSON file
loaded_diagram = lynx.Diagram.load('my_control_system.json')
```

JSON format is human-readable and version-controlled friendly.

## Exporting to Python-Control

Extract transfer functions or state-space representations:

```python
import control as ct

# Export closed-loop transfer function
sys_tf = diagram.get_tf('r', 'y')  # From input 'r' to output 'y'

# Export state-space representation
sys_ss = diagram.get_ss('r', 'y')

# Analyze with python-control
bode = ct.bode_plot(sys_tf)
nyquist = ct.nyquist_plot(sys_tf)
```

See {doc}`export` for details on signal reference patterns.

## Interactive Widget

Launch the interactive Jupyter widget:

```python
# In Jupyter notebook
lynx.edit(diagram)
```

This opens a visual editor where you can:
- Drag blocks to reposition
- Edit parameters via properties panel
- Add/remove connections
- View block labels and LaTeX rendering

Changes in the widget sync back to the Python object.

## Complete Example

```python
import lynx
import control as ct
import numpy as np

# Create PID feedback control system
diagram = lynx.Diagram()

# Add blocks
diagram.add_block('io_marker', 'r', marker_type='input', label='r', position={'x': 0, 'y': 0})
diagram.add_block('sum', 'error', signs=['+', '-', '|'], position={'x': 80, 'y': 0})
diagram.add_block('gain', 'Kp', K=10.0, label='Proportional', position={'x': 150, 'y': 0})
diagram.add_block('transfer_function', 'plant',
                  numerator=[1.0], denominator=[1.0, 2.0, 1.0],
                  position={'x': 250, 'y': 0})
diagram.add_block('io_marker', 'y', marker_type='output', label='y', position={'x': 350, 'y': 0})

# Connect blocks
diagram.add_connection('c1', 'r', 'out', 'error', 'in1')
diagram.add_connection('c2', 'error', 'out', 'Kp', 'in')
diagram.add_connection('c3', 'Kp', 'out', 'plant', 'in')
diagram.add_connection('c4', 'plant', 'out', 'y', 'in')
diagram.add_connection('c5', 'plant', 'out', 'error', 'in2')  # Feedback

# Save
diagram.save('pid_system.json')

# Export and analyze
sys = diagram.get_tf('r', 'y')
t, y = ct.step_response(sys, np.linspace(0, 10, 1000))
print(f"Settling time: {ct.step_info(sys)['SettlingTime']:.2f}s")
```

## API Reference

```{eval-rst}
.. currentmodule:: lynx

.. autosummary::
   :toctree: generated/
   :nosignatures:

   Diagram.add_block
   Diagram.add_connection
   Diagram.remove_block
   Diagram.remove_connection
   Diagram.update_block_parameter
   Diagram.save
   Diagram.load
   Diagram.get_tf
   Diagram.get_ss
   edit
```

## See Also

- {doc}`blocks` - Detailed block type reference
- {doc}`export` - Signal references and subsystem extraction
- {doc}`validation` - Pre-export validation
