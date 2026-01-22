<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Python-Control Export

**Feature**: 012-python-control-export
**Date**: 2026-01-15
**Purpose**: End-to-end test scenarios for validating export functionality

## Overview

This document provides concrete examples for testing the python-control export feature. Each scenario demonstrates a complete workflow from diagram creation to simulation, serving as both acceptance tests and user documentation.

---

## Scenario 1: Simple Feedback Loop (User Story 1, P1)

**Test Goal**: Verify basic block conversion and connection mapping

### Setup

```python
import lynx
import control as ct
import numpy as np

# Create diagram
diagram = lynx.Diagram()

# Add system input (reference signal)
input_marker = diagram.add_block(
    block_type='io_marker',
    id='ref_input',
    marker_type='input',
    label='r',
    position={'x': 0, 'y': 100}
)

# Add error sum junction (reference - output)
error_sum = diagram.add_block(
    block_type='sum',
    id='error_sum',
    signs=['+', '-', '|'],  # Top: reference (+), Left: feedback (-), Bottom: unused
    position={'x': 100, 'y': 100}
)

# Add controller (Proportional gain)
controller = diagram.add_block(
    block_type='gain',
    id='controller',
    K=5.0,
    position={'x': 200, 'y': 100}
)

# Add plant (first-order system)
plant = diagram.add_block(
    block_type='transfer_function',
    id='plant',
    numerator=[2.0],
    denominator=[1.0, 3.0],  # 2/(s+3)
    position={'x': 300, 'y': 100}
)

# Add system output
output_marker = diagram.add_block(
    block_type='io_marker',
    id='output',
    marker_type='output',
    label='y',
    position={'x': 400, 'y': 100}
)

# Connect blocks
diagram.add_connection('c1', 'ref_input', 'out', 'error_sum', 'in1')  # Reference
diagram.add_connection('c2', 'error_sum', 'out', 'controller', 'in')  # Error
diagram.add_connection('c3', 'controller', 'out', 'plant', 'in')      # Control
diagram.add_connection('c4', 'plant', 'out', 'output', 'in')          # Output
diagram.add_connection('c5', 'plant', 'out', 'error_sum', 'in2')      # Feedback (negative)
```

### Execute Export

```python
# Export to python-control
sys = diagram.to_interconnect()

# Verify system properties
print(f"System type: {type(sys)}")  # Should be InterconnectedSystem
print(f"Number of inputs: {sys.ninputs}")   # Should be 1
print(f"Number of outputs: {sys.noutputs}") # Should be 1
```

### Run Simulation

```python
# Step response
t = np.linspace(0, 5, 500)
t_out, y_out = ct.step_response(sys, t)

# Verify behavior
print(f"Final value: {y_out[-1]}")  # Should approach 10/(3+10) = 0.769
print(f"Settling time: {t_out[np.where(np.abs(y_out - y_out[-1]) < 0.02)[0][0]]}")
```

### Expected Results

- ✅ Export completes without errors
- ✅ System has 1 input, 1 output
- ✅ Step response shows stable feedback behavior
- ✅ Final value ≈ 0.769 (closed-loop DC gain)
- ✅ No oscillation (first-order plant + proportional control)

---

## Scenario 2: Sum Block Sign Handling (User Story 2, P2)

**Test Goal**: Verify correct signal negation for sum block subtraction

### Setup

```python
import lynx
import control as ct

diagram = lynx.Diagram()

# System inputs
input_a = diagram.add_block('io_marker', 'input_a', marker_type='input', label='a', position={'x': 0, 'y': 50})
input_b = diagram.add_block('io_marker', 'input_b', marker_type='input', label='b', position={'x': 0, 'y': 150})

# Test all sign combinations
sum_all_positive = diagram.add_block('sum', 'sum1', signs=['+', '+', '+'], position={'x': 100, 'y': 50})
sum_mixed_signs = diagram.add_block('sum', 'sum2', signs=['+', '-', '+'], position={'x': 100, 'y': 150})
sum_two_inputs = diagram.add_block('sum', 'sum3', signs=['+', '|', '-'], position={'x': 100, 'y': 250})

# Gains to differentiate signals
gain_a = diagram.add_block('gain', 'gain_a', K=2.0, position={'x': 200, 'y': 50})
gain_b = diagram.add_block('gain', 'gain_b', K=3.0, position={'x': 200, 'y': 150})

# Outputs
output_1 = diagram.add_block('io_marker', 'out1', marker_type='output', label='sum1_out', position={'x': 300, 'y': 50})
output_2 = diagram.add_block('io_marker', 'out2', marker_type='output', label='sum2_out', position={'x': 300, 'y': 150})
output_3 = diagram.add_block('io_marker', 'out3', marker_type='output', label='sum3_out', position={'x': 300, 'y': 250})

# Connect sum1 (all positive): a + b + a
diagram.add_connection('c1', 'input_a', 'out', 'sum1', 'in1')
diagram.add_connection('c2', 'input_b', 'out', 'sum1', 'in2')
diagram.add_connection('c3', 'input_a', 'out', 'sum1', 'in3')
diagram.add_connection('c4', 'sum1', 'out', 'gain_a', 'in')
diagram.add_connection('c5', 'gain_a', 'out', 'out1', 'in')

# Connect sum2 (mixed signs): a - b + a
diagram.add_connection('c6', 'input_a', 'out', 'sum2', 'in1')
diagram.add_connection('c7', 'input_b', 'out', 'sum2', 'in2')
diagram.add_connection('c8', 'input_a', 'out', 'sum2', 'in3')
diagram.add_connection('c9', 'sum2', 'out', 'gain_b', 'in')
diagram.add_connection('c10', 'gain_b', 'out', 'out2', 'in')

# Connect sum3 (two inputs, skipped middle): a - b
diagram.add_connection('c11', 'input_a', 'out', 'sum3', 'in1')
diagram.add_connection('c12', 'input_b', 'out', 'sum3', 'in2')
diagram.add_connection('c13', 'sum3', 'out', 'out3', 'in')
```

### Execute Export

```python
sys = diagram.to_interconnect()

# Inspect connections (internal testing)
# Should see negation on sum2.in2 and sum3.in2
```

### Run Simulation

```python
import numpy as np

# Input signals: step functions
t = np.linspace(0, 1, 100)
u = np.array([[1.0], [2.0]])  # a=1.0, b=2.0 (constant)

t_out, y_out = ct.input_output_response(sys, t, u)

# Verify outputs
# sum1 output: 2 * (1 + 2 + 1) = 8.0
# sum2 output: 3 * (1 - 2 + 1) = 0.0
# sum3 output: (1 - 2) = -1.0

print(f"Sum1 (all positive): {y_out[0, -1]} (expected: 8.0)")
print(f"Sum2 (mixed signs): {y_out[1, -1]} (expected: 0.0)")
print(f"Sum3 (two inputs): {y_out[2, -1]} (expected: -1.0)")
```

### Expected Results

- ✅ Sum1 (all positive): output = 8.0
- ✅ Sum2 (mixed signs): output = 0.0 (proves negation works)
- ✅ Sum3 (skipped middle): output = -1.0 (proves port mapping works)

---

## Scenario 3: Validation Errors (User Story 3, P3)

**Test Goal**: Verify clear error messages for invalid diagrams

### Test 3.1: Unconnected Input Port

```python
import lynx
import pytest

diagram = lynx.Diagram()

# Add blocks but forget to connect them
input_1 = diagram.add_block('io_marker', 'input', marker_type='input', position={'x': 0, 'y': 0})
gain_1 = diagram.add_block('gain', 'gain1', K=2.0, position={'x': 100, 'y': 0})
output_1 = diagram.add_block('io_marker', 'output', marker_type='output', position={'x': 200, 'y': 0})

# Only connect input → gain, forget gain → output
diagram.add_connection('c1', 'input', 'out', 'gain1', 'in')
# Missing: diagram.add_connection('c2', 'gain1', 'out', 'output', 'in')

# Attempt export
with pytest.raises(lynx.ValidationError) as exc_info:
    diagram.to_interconnect()

# Verify error message
assert 'output' in str(exc_info.value).lower()
assert 'in' in str(exc_info.value)
assert 'not connected' in str(exc_info.value).lower()
print(f"Error message: {exc_info.value}")
```

**Expected Error**: `"Validation failed: Block 'output' input port 'in' is not connected"`

### Test 3.2: Missing InputMarker

```python
diagram = lynx.Diagram()

# No InputMarker!
gain_1 = diagram.add_block('gain', 'gain1', K=2.0, position={'x': 100, 'y': 0})
output_1 = diagram.add_block('io_marker', 'output', marker_type='output', position={'x': 200, 'y': 0})
diagram.add_connection('c1', 'gain1', 'out', 'output', 'in')

with pytest.raises(lynx.ValidationError) as exc_info:
    diagram.to_interconnect()

assert 'InputMarker' in str(exc_info.value)
print(f"Error message: {exc_info.value}")
```

**Expected Error**: `"Validation failed: Diagram has no InputMarker blocks. Add at least one system input."`

### Test 3.3: Missing OutputMarker

```python
diagram = lynx.Diagram()

# No OutputMarker!
input_1 = diagram.add_block('io_marker', 'input', marker_type='input', position={'x': 0, 'y': 0})
gain_1 = diagram.add_block('gain', 'gain1', K=2.0, position={'x': 100, 'y': 0})
diagram.add_connection('c1', 'input', 'out', 'gain1', 'in')

with pytest.raises(lynx.ValidationError) as exc_info:
    diagram.to_interconnect()

assert 'OutputMarker' in str(exc_info.value)
print(f"Error message: {exc_info.value}")
```

**Expected Error**: `"Validation failed: Diagram has no OutputMarker blocks. Add at least one system output."`

### Expected Results

- ✅ All validation errors raise `lynx.ValidationError`
- ✅ Error messages identify specific problem
- ✅ Error messages include block ID and/or port ID
- ✅ Users can fix diagram based on error message alone

---

## Scenario 4: State-Space Block (User Story 1, Extended)

**Test Goal**: Verify StateSpace block conversion

### Setup

```python
import lynx
import control as ct
import numpy as np

diagram = lynx.Diagram()

# System input
input_1 = diagram.add_block('io_marker', 'input', marker_type='input', label='u', position={'x': 0, 'y': 0})

# State-space block: simple integrator
# dx/dt = u, y = x
# A = [[0]], B = [[1]], C = [[1]], D = [[0]]
ss_block = diagram.add_block(
    block_type='state_space',
    id='integrator',
    A=[[0.0]],
    B=[[1.0]],
    C=[[1.0]],
    D=[[0.0]],
    position={'x': 100, 'y': 0}
)

# System output
output_1 = diagram.add_block('io_marker', 'output', marker_type='output', label='y', position={'x': 200, 'y': 0})

# Connect
diagram.add_connection('c1', 'input', 'out', 'integrator', 'in')
diagram.add_connection('c2', 'integrator', 'out', 'output', 'in')
```

### Execute Export

```python
sys = diagram.to_interconnect()

# Verify it's a state-space system
print(f"System type: {type(sys)}")
print(f"Number of states: {sys.nstates}")  # Should be 1
```

### Run Simulation

```python
# Step response: integrator ramp output
t = np.linspace(0, 5, 500)
t_out, y_out = ct.step_response(sys, t)

# Verify ramp behavior
expected_slope = 1.0  # Integrating a unit step
actual_slope = (y_out[-1] - y_out[0]) / (t_out[-1] - t_out[0])
print(f"Ramp slope: {actual_slope} (expected: {expected_slope})")
assert np.isclose(actual_slope, expected_slope, rtol=0.1)
```

### Expected Results

- ✅ StateSpace block converts to `ct.ss()`
- ✅ System has 1 state
- ✅ Step response shows integrator behavior (ramp output)
- ✅ Slope ≈ 1.0

---

## Scenario 5: Performance Test (Success Criteria SC-003)

**Test Goal**: Verify <100ms export time for 50-block diagram

### Setup

```python
import lynx
import time

diagram = lynx.Diagram()

# Create a 50-block chain
input_1 = diagram.add_block('io_marker', 'input', marker_type='input', position={'x': 0, 'y': 0})

prev_block = 'input'
prev_port = 'out'

for i in range(48):  # 48 gain blocks + 1 input + 1 output = 50 total
    block_id = f'gain_{i}'
    block = diagram.add_block('gain', block_id, K=1.0 + i*0.01, position={'x': 100 + i*10, 'y': 0})
    diagram.add_connection(f'c_{i}', prev_block, prev_port, block_id, 'in')
    prev_block = block_id
    prev_port = 'out'

output_1 = diagram.add_block('io_marker', 'output', marker_type='output', position={'x': 600, 'y': 0})
diagram.add_connection('c_final', prev_block, prev_port, 'output', 'in')
```

### Execute Export

```python
# Measure export time
start = time.perf_counter()
sys = diagram.to_interconnect()
elapsed = time.perf_counter() - start

print(f"Export time for 50 blocks: {elapsed*1000:.1f} ms")
print(f"Pass/Fail: {'PASS' if elapsed < 0.1 else 'FAIL'}")
```

### Expected Results

- ✅ Export completes in <100ms
- ✅ System has 50 subsystems
- ✅ Chain of 48 gains produces correct overall gain product

---

## Scenario 6: Complex Feedback Loop (Integration Test)

**Test Goal**: Verify correct behavior for realistic control system

### Setup: PID Controller with Second-Order Plant

```python
import lynx
import control as ct
import numpy as np

diagram = lynx.Diagram()

# Reference input
ref = diagram.add_block('io_marker', 'ref', marker_type='input', label='r', position={'x': 0, 'y': 100})

# Error sum
error = diagram.add_block('sum', 'error', signs=['+', '-', '|'], position={'x': 80, 'y': 100})

# PID controller (simplified: just P + D)
# Proportional gain
kp = diagram.add_block('gain', 'Kp', K=10.0, position={'x': 160, 'y': 80})

# Derivative path (s * Kd approximated as high-pass filter)
kd_gain = diagram.add_block('gain', 'Kd', K=5.0, position={'x': 160, 'y': 120})
derivative = diagram.add_block('transfer_function', 'derivative',
                                numerator=[1.0, 0.0],
                                denominator=[0.01, 1.0],  # s / (0.01s + 1)
                                position={'x': 240, 'y': 120})

# Sum PID outputs
control_sum = diagram.add_block('sum', 'control_sum', signs=['+', '+', '|'], position={'x': 320, 'y': 100})

# Plant: second-order system
# 1 / (s^2 + 2s + 1) = 1 / (s+1)^2
plant = diagram.add_block('transfer_function', 'plant',
                          numerator=[1.0],
                          denominator=[1.0, 2.0, 1.0],
                          position={'x': 400, 'y': 100})

# Output
output = diagram.add_block('io_marker', 'output', marker_type='output', label='y', position={'x': 500, 'y': 100})

# Connections
diagram.add_connection('c1', 'ref', 'out', 'error', 'in1')
diagram.add_connection('c2', 'error', 'out', 'Kp', 'in')
diagram.add_connection('c3', 'error', 'out', 'Kd', 'in')
diagram.add_connection('c4', 'Kd', 'out', 'derivative', 'in')
diagram.add_connection('c5', 'Kp', 'out', 'control_sum', 'in1')
diagram.add_connection('c6', 'derivative', 'out', 'control_sum', 'in2')
diagram.add_connection('c7', 'control_sum', 'out', 'plant', 'in')
diagram.add_connection('c8', 'plant', 'out', 'output', 'in')
diagram.add_connection('c9', 'plant', 'out', 'error', 'in2')  # Negative feedback
```

### Execute Export

```python
sys = diagram.to_interconnect()
```

### Run Simulation

```python
t = np.linspace(0, 5, 500)
t_out, y_out = ct.step_response(sys, t)

# Verify closed-loop performance
overshoot = (np.max(y_out) - y_out[-1]) / y_out[-1] * 100
settling_idx = np.where(np.abs(y_out - y_out[-1]) < 0.02)[0]
settling_time = t_out[settling_idx[0]] if len(settling_idx) > 0 else None

print(f"Overshoot: {overshoot:.1f}%")
print(f"Settling time (2%): {settling_time:.2f} s")
print(f"Final value: {y_out[-1]:.3f}")
```

### Expected Results

- ✅ Export completes without errors
- ✅ Closed-loop system is stable
- ✅ Step response shows PID damping effect
- ✅ Final value ≈ 1.0 (unity feedback with no steady-state error for step)

---

## Summary of Test Coverage

| Scenario | User Story | Purpose | Pass Criteria |
|----------|-----------|---------|---------------|
| 1. Simple Feedback Loop | US1 (P1) | Basic export + simulation | Stable response, correct DC gain |
| 2. Sum Block Signs | US2 (P2) | Sign negation handling | Correct arithmetic with +/- signs |
| 3. Validation Errors | US3 (P3) | Error detection | Clear, actionable error messages |
| 4. State-Space Block | US1 (Extended) | SS conversion | Integrator behavior verified |
| 5. Performance Test | SC-003 | Export speed | <100ms for 50 blocks |
| 6. Complex Feedback | Integration | Real control system | Stable PID response |

**Total Scenarios**: 6 (covers all P1-P3 user stories + success criteria)

---

## Usage for Testing

### Unit Tests

Extract individual components for unit testing:

```python
# Test block conversion
def test_gain_conversion():
    diagram = lynx.Diagram()
    input_1 = diagram.add_block('io_marker', 'in', marker_type='input')
    gain = diagram.add_block('gain', 'g1', K=5.0)
    output = diagram.add_block('io_marker', 'out', marker_type='output')
    diagram.add_connection('c1', 'in', 'out', 'g1', 'in')
    diagram.add_connection('c2', 'g1', 'out', 'out', 'in')

    sys = diagram.to_interconnect()

    # Verify DC gain = 5.0
    t, y = ct.step_response(sys, np.linspace(0, 10, 100))
    assert np.isclose(y[-1], 5.0, rtol=0.01)
```

### Integration Tests

Use full scenarios 1-6 as integration tests in `tests/integration/test_python_control_integration.py`

### Manual Testing (Jupyter Notebook)

Copy scenarios into Jupyter notebook for interactive exploration:

```python
# In Jupyter:
%matplotlib inline
import matplotlib.pyplot as plt

# Run Scenario 1
# ... (paste scenario code)

# Plot results
plt.plot(t_out, y_out)
plt.xlabel('Time (s)')
plt.ylabel('Output')
plt.title('Closed-Loop Step Response')
plt.grid(True)
plt.show()
```

---

## Notes for Implementation

1. **All scenarios must pass** before feature is considered complete
2. **Export errors** should be caught and re-tested with corrected diagrams
3. **Performance scenario** should run on CI to catch regressions
4. **Complex feedback** scenario validates sum block sign handling in realistic context
5. **Validation errors** scenario ensures user experience quality (FR-013)
