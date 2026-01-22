# Python-Control Export

Export Lynx diagrams to python-control for analysis, simulation, and controller design.

## Export Methods

Lynx provides two primary export methods:

```python
# Transfer function representation
sys_tf = diagram.get_tf('from_signal', 'to_signal')

# State-space representation
sys_ss = diagram.get_ss('from_signal', 'to_signal')
```

Both methods:
- Take two signal references (from and to)
- Return python-control objects (`TransferFunction` or `StateSpace`)
- Perform validation before export (raises `ValidationError` if invalid)

## Signal Reference System

Lynx uses a 3-tier priority system for signal references:

### Priority 1: IOMarker Labels (Highest)

The recommended approach. Use the `label` parameter from InputMarker/OutputMarker blocks:

```python
# Define IOMarkers with labels
diagram.add_block('io_marker', 'ref', marker_type='input', label='r')
diagram.add_block('io_marker', 'output', marker_type='output', label='y')

# Export using IOMarker labels
sys = diagram.get_tf('r', 'y')  # ← Uses IOMarker labels
```

**Benefits**:
- Clear system boundaries
- Unambiguous references
- Required for validation

### Priority 2: Connection Labels

Reference labeled connections between blocks:

```python
# Add connection with label
diagram.add_connection('c1', 'plant', 'out', 'sensor', 'in', label='measurement')

# Export using connection label
sys = diagram.get_ss('r', 'measurement')  # ← Uses connection label
```

**Use case**: Extracting subsystems at internal signals

### Priority 3: Block.Port Notation (Lowest)

Explicit reference using `block_label.output_port`:

```python
# Reference block output directly
sys = diagram.get_tf('controller.out', 'plant.out')
```

**Notes**:
- Must use block **label** (not ID) if label is set
- Must use **output** ports only (signals are outputs, not inputs)
- Use dot notation: `block_label.port_id`

## Complete Examples

### Basic Closed-Loop Transfer Function

```python
import lynx
import control as ct

# Create feedback control loop
diagram = lynx.Diagram()

# Add blocks with IOMarkers
diagram.add_block('io_marker', 'r', marker_type='input', label='r')
diagram.add_block('sum', 'error', signs=['+', '-', '|'])
diagram.add_block('gain', 'controller', K=5.0)
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0], denominator=[1.0, 3.0])
diagram.add_block('io_marker', 'y', marker_type='output', label='y')

# Connect
diagram.add_connection('c1', 'r', 'out', 'error', 'in1')
diagram.add_connection('c2', 'error', 'out', 'controller', 'in')
diagram.add_connection('c3', 'controller', 'out', 'plant', 'in')
diagram.add_connection('c4', 'plant', 'out', 'y', 'in')
diagram.add_connection('c5', 'plant', 'out', 'error', 'in2')  # Feedback

# Export closed-loop transfer function
sys = diagram.get_tf('r', 'y')

# Analyze
print(f"DC Gain: {ct.dcgain(sys):.3f}")
ct.step_response(sys)
```

### Subsystem Extraction

Extract a portion of the diagram between arbitrary signals:

```python
# Extract subsystem from controller output to sensor output
sys_subsystem = diagram.get_ss('controller.out', 'sensor.out')

# Or using connection labels
diagram.add_connection('c_control', 'controller', 'out', 'plant', 'in', label='control_signal')
diagram.add_connection('c_measure', 'sensor', 'out', 'filter', 'in', label='measurement')

sys_subsystem = diagram.get_ss('control_signal', 'measurement')
```

### Sum Block Sign Handling

Sum blocks correctly handle negative feedback:

```python
# Create feedback loop with subtraction
diagram.add_block('sum', 'error', signs=['+', '-', '|'])  # Top: +, Left: -

# Connections
diagram.add_connection('c1', 'r', 'out', 'error', 'in1')      # Positive
diagram.add_connection('c2', 'plant', 'out', 'error', 'in2')  # Negative (feedback)

# Export: Lynx automatically applies negative sign
sys = diagram.get_tf('r', 'y')
```

The exported system correctly represents:
$$e = r - y$$

No manual negation needed!

## Internal Implementation

The export methods use python-control's interconnection capabilities internally to build the full system model before extracting the desired subsystem. Most users should use `get_tf()` and `get_ss()` for their export needs.

## Validation Before Export

All export methods validate the diagram first. See {doc}`validation` for details on:

- Required IOMarkers (at least 1 input and 1 output)
- Port connectivity requirements
- Label uniqueness warnings
- Error handling and recovery

## Integration with Python-Control

Once exported, use the full python-control API:

```python
import control as ct
import numpy as np

# Export system
sys = diagram.get_tf('r', 'y')

# Time-domain analysis
t = np.linspace(0, 10, 1000)
t_out, y_out = ct.step_response(sys, t)
impulse_out = ct.impulse_response(sys, t)

# Frequency-domain analysis
ct.bode_plot(sys, dB=True)
ct.nyquist_plot(sys)
ct.nichols_plot(sys)

# Stability analysis
poles = ct.poles(sys)
zeros = ct.zeros(sys)
margins = ct.stability_margins(sys)

# Controller design
K, S, E = ct.lqr(sys.A, sys.B, Q, R)  # For state-space systems
```

## Signal Reference Resolution Examples

```python
# Priority demonstration
diagram.add_block('io_marker', 'input', marker_type='input', label='r')
diagram.add_block('gain', 'K1', K=5.0, label='controller')
diagram.add_connection('c1', 'K1', 'out', 'plant', 'in', label='control_signal')

# All three references:
sys1 = diagram.get_tf('r', 'y')                    # Priority 1: IOMarker label
sys2 = diagram.get_tf('control_signal', 'y')       # Priority 2: Connection label
sys3 = diagram.get_tf('controller.out', 'y')       # Priority 3: Block.port notation

# sys2 and sys3 extract different subsystems than sys1
```

## Common Patterns

### Pattern 1: Full Closed-Loop Analysis

```python
# Use IOMarker labels for full system
sys = diagram.get_tf('r', 'y')
```

### Pattern 2: Open-Loop Analysis

```python
# Break loop, measure plant only
sys_plant = diagram.get_tf('controller.out', 'sensor.in')
```

### Pattern 3: Sensitivity Function

```python
# S = e/r (error sensitivity)
sys_S = diagram.get_tf('r', 'error.out')  # If error sum has label='error'
```

### Pattern 4: Complementary Sensitivity

```python
# T = y/r (closed-loop transfer function)
sys_T = diagram.get_tf('r', 'y')
```

## API Reference

```{eval-rst}
.. currentmodule:: lynx

.. autosummary::
   :toctree: generated/
   :nosignatures:

   Diagram.get_tf
   Diagram.get_ss
```

## See Also

- {doc}`diagram` - Building diagrams
- {doc}`blocks` - IOMarker block details
- {doc}`validation` - Error handling and validation
- {doc}`../examples/index` - Export examples
