---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Basic Feedback Control

This example demonstrates a simple feedback control system with a proportional controller and first-order plant.

## System Overview

We'll create a unity feedback system with:
- **Controller**: Proportional gain K = 5
- **Plant**: First-order system $G(s) = \frac{2}{s+3}$
- **Feedback**: Unity negative feedback

## Setup

```{code-cell} ipython3
import lynx
import control as ct
import numpy as np
import matplotlib.pyplot as plt
```

## Create Diagram

Build the feedback loop using Lynx's block diagram API:

```{code-cell} ipython3
# Create empty diagram
diagram = lynx.Diagram()

# Add blocks
diagram.add_block('io_marker', 'r', marker_type='input', label='r', position={'x': 0, 'y': 0})
diagram.add_block('sum', 'error', signs=['+', '-', '|'], position={'x': 80, 'y': 0})
diagram.add_block('gain', 'controller', K=5.0, position={'x': 180, 'y': 0})
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0], denominator=[1.0, 3.0],
                  position={'x': 300, 'y': 0})
diagram.add_block('io_marker', 'y', marker_type='output', label='y', position={'x': 420, 'y': 0})

# Add connections
diagram.add_connection('c1', 'r', 'out', 'error', 'in1')
diagram.add_connection('c2', 'error', 'out', 'controller', 'in')
diagram.add_connection('c3', 'controller', 'out', 'plant', 'in')
diagram.add_connection('c4', 'plant', 'out', 'y', 'in')
diagram.add_connection('c5', 'plant', 'out', 'error', 'in2')  # Feedback

print("✓ Diagram created successfully")
```

## Export to Python-Control

Extract the closed-loop transfer function from r to y:

```{code-cell} ipython3
# Export closed-loop transfer function
sys = diagram.get_tf('r', 'y')

print(f"Closed-loop transfer function:")
print(sys)
print(f"\nDC Gain: {ct.dcgain(sys):.4f}")
```

## Step Response

Analyze the system's step response:

```{code-cell} ipython3
# Compute step response
t = np.linspace(0, 3, 500)
t_out, y_out = ct.step_response(sys, t)

# Plot
plt.figure(figsize=(10, 5))
plt.plot(t_out, y_out, linewidth=2)
plt.axhline(y=ct.dcgain(sys), color='r', linestyle='--', alpha=0.5, label=f'DC Gain = {ct.dcgain(sys):.3f}')
plt.grid(True, alpha=0.3)
plt.xlabel('Time (s)')
plt.ylabel('Output')
plt.title('Closed-Loop Step Response')
plt.legend()
plt.tight_layout()
plt.show()

print(f"Final value: {y_out[-1]:.4f}")
print(f"Settling time (2%): ~{t_out[np.where(np.abs(y_out - y_out[-1]) < 0.02 * y_out[-1])[0][0]]:.2f}s")
```

## Frequency Response

Plot the Bode diagram to understand frequency domain behavior:

```{code-cell} ipython3
# Bode plot
plt.figure(figsize=(10, 8))
ct.bode_plot(sys, dB=True, Hz=False)
plt.tight_layout()
plt.show()
```

## Analysis

The closed-loop transfer function is:

$$T(s) = \frac{KG(s)}{1 + KG(s)} = \frac{10}{s + 13}$$

Key observations:
- **DC Gain**: 10/13 ≈ 0.769 (steady-state error of ~23%)
- **Bandwidth**: ~13 rad/s (first-order system)
- **Settling time**: ~0.3s (4 time constants of 1/13)

## Next Steps

- Try increasing the controller gain K to reduce steady-state error
- Add an integrator to eliminate steady-state error (see PID example)
- Experiment with different plant dynamics
