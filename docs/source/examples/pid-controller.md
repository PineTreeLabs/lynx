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

# PI Controller Design

This example demonstrates PI controller tuning for a second-order plant.

## System Overview

Plant: $G(s) = \frac{1}{s^2 + 2s + 1}$ (underdamped second-order system)

```{code-cell} ipython3
import lynx
import control as ct
import numpy as np
import matplotlib.pyplot as plt
```

## Create PI Feedback System

```{code-cell} ipython3
diagram = lynx.Diagram()

# System boundaries
diagram.add_block('io_marker', 'r', marker_type='input', label='r', position={'x': 0, 'y': 0})
diagram.add_block('io_marker', 'y', marker_type='output', label='y', position={'x': 500, 'y': 0})

# Error calculation
diagram.add_block('sum', 'error', signs=['+', '-', '|'], position={'x': 60, 'y': 0})

# PI controller: C(s) = Kp + Ki/s (simpler than full PID)
# Implementing as: C(s) = (Kp*s + Ki) / s
Kp, Ki = 10.0, 5.0
diagram.add_block('transfer_function', 'pid',
                  numerator=[Kp, Ki],
                  denominator=[1.0, 0.0],
                  position={'x': 180, 'y': 0})

# Plant: G(s) = 1/(s^2 + 2s + 1)
diagram.add_block('transfer_function', 'plant',
                  numerator=[1.0],
                  denominator=[1.0, 2.0, 1.0],
                  position={'x': 320, 'y': 0})

# Connections
diagram.add_connection('c1', 'r', 'out', 'error', 'in1')
diagram.add_connection('c2', 'error', 'out', 'pid', 'in')
diagram.add_connection('c3', 'pid', 'out', 'plant', 'in')
diagram.add_connection('c4', 'plant', 'out', 'y', 'in')
diagram.add_connection('c5', 'plant', 'out', 'error', 'in2')

print(f"PI gains: Kp={Kp}, Ki={Ki}")
```

## Analyze Closed-Loop Response

```{code-cell} ipython3
sys = diagram.get_tf('r', 'y')

t = np.linspace(0, 5, 1000)
t_out, y_out = ct.step_response(sys, t)

plt.figure(figsize=(10, 5))
plt.plot(t_out, y_out, linewidth=2, label='PI Response')
plt.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='Setpoint')
plt.grid(True, alpha=0.3)
plt.xlabel('Time (s)')
plt.ylabel('Output')
plt.title('PI Closed-Loop Step Response')
plt.legend()
plt.tight_layout()
plt.show()

print(f"DC Gain: {ct.dcgain(sys):.4f}")
print(f"Overshoot: {(np.max(y_out) - 1.0) * 100:.1f}%")
```

## Key Insights

- **Integral action** (Ki) eliminates steady-state error
- **Proportional gain** (Kp) affects speed of response
- **Note**: For derivative action (Kd), use a filtered derivative to keep the controller proper

Try adjusting the gains to explore the tradeoffs!
