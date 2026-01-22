# Quickstart

This guide will walk you through creating your first Lynx control system diagram: a simple feedback control loop with a proportional controller and first-order plant.

## Installation

The recommended way to install Lynx is via pip:

```bash
pip install lynx-nb
```

## Interactive Editor

Launch a Jupyter notebook:

```python
import lynx
import control
import numpy as np
```

The easiest way to build a diagram is with the inline editor:

```python
diagram = lynx.Diagram()  # Empty diagram
lynx.edit(diagram)  # Launch the Jupyter widget
```

This opens an interactive view where you can:
- Pan and zoom
- Add blocks and make connections
- Edit parameters via the properties panel
- Drag blocks to reposition

When you're done you can save the diagram to a JSON:

```python
# Serialize the diagram, including positions, connections, and parameters
diagram.save("demo.json")

# Load the diagram
diagram = lynx.Diagram.load("demo.json")
```

:::{note}
The editor has access to the full notebook environment, so any variables or valid Python expressions you type can be evaluated to a block parameter.
:::


## Programmatic Construction

Alternatively, diagrams can be constructed programmatically.
For example, the following code defines a simple feedback control loop:

```python
diagram = lynx.Diagram()  # Empty diagram

# Add input/output markers
diagram.add_block('io_marker', 'r', marker_type='input', label='r',
                  position={'x': 0, 'y': 0})  # Reference
diagram.add_block('io_marker', 'y', marker_type='output', label='y',
                  position={'x': 500, 'y': 0})  # Output

# Add controller
diagram.add_block('gain', 'controller', K=5.0,
                  position={'x': 150, 'y': 0})

# Add plant: 2/(s+3)
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0],
                  denominator=[1.0, 3.0],
                  position={'x': 300, 'y': 0})

# Add summing junction for error calculation
diagram.add_block('sum', 'error_sum',
                  signs=['+', '-', '|'],  # Top: +, Left: -, Bottom: disabled
                  position={'x': 75, 'y': 0})

# Forward path
diagram.add_connection('c1', 'r', 'out', 'error_sum', 'in1')
diagram.add_connection('c2', 'error_sum', 'out', 'controller', 'in', label='e')
diagram.add_connection('c3', 'controller', 'out', 'plant', 'in', label='u')
diagram.add_connection('c4', 'plant', 'out', 'y', 'in')

# Feedback path
diagram.add_connection('c5', 'plant', 'out', 'error_sum', 'in2')
```

The diagram can be handled in exactly the same way:

```python
# Save to JSON file
diagram.save('demo.json')
```


## Export and Analyze

You can also extract python-control [transfer function](https://python-control.readthedocs.io/en/0.10.2/generated/control.TransferFunction.html) or [state-space](https://python-control.readthedocs.io/en/0.10.2/generated/control.StateSpace.html#control.StateSpace) representations between any two labeled signals or I/O markers:

```python
G = diagram.get_ss('u', 'y')  # Plant as state-space model
S = diagram.get_tf('r', 'e')  # Sensitivity transfer function
```

This is the core of the ecosystem interoperability, making it seamless to inject parameters from code and extract subsystems back into the workflow.

```python
# Extract closed-loop transfer function from r to y
sys = diagram.get_tf('r', 'y')

# Analyze step response
t = np.linspace(0, 5, 500)
t_out, y_out = control.step_response(sys, t)

# Print DC gain and settling time
print(f"DC Gain: {y_out[-1]:.3f}")
print(f"Final value: {y_out[-1]}")
```


## Next Steps

- {doc}`../examples/index`: Learn through more advanced examples
- {doc}`../api/index`: Explore all available blocks and methods
