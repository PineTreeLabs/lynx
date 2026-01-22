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

# State-Space Control Design

This example demonstrates state feedback control using pole placement.

## System Model

Consider a double integrator plant:
$$\dot{x} = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix} x + \begin{bmatrix} 0 \\ 1 \end{bmatrix} u$$
$$y = \begin{bmatrix} 1 & 0 \end{bmatrix} x$$

```{code-cell} ipython3
import lynx
import control as ct
import numpy as np
import matplotlib.pyplot as plt
```

## Design State Feedback Gain

```{code-cell} ipython3
# Plant matrices
A = np.array([[0, 1], [0, 0]])
B = np.array([[0], [1]])
C = np.array([[1, 0]])
D = np.array([[0]])

# Design state feedback for desired poles at -2 ± 2j
desired_poles = [-2+2j, -2-2j]
K = ct.place(A, B, desired_poles)

print(f"State feedback gain K = {K}")
print(f"Closed-loop poles: {np.linalg.eigvals(A - B @ K)}")
```

## Create Closed-Loop System in Lynx

```{code-cell} ipython3
diagram = lynx.Diagram()

# Reference input
diagram.add_block('io_marker', 'r', marker_type='input', label='r', position={'x': 0, 'y': 0})

# State-space plant
diagram.add_block('state_space', 'plant', A=A, B=B, C=C, D=D, position={'x': 200, 'y': 0})

# State feedback gain (Note: In practice, you'd implement this with gain blocks for each state)
# For simplicity, we use a gain block representing the feedback
diagram.add_block('gain', 'feedback', K=-K[0,0], position={'x': 100, 'y': 0})

# Output
diagram.add_block('io_marker', 'y', marker_type='output', label='y', position={'x': 320, 'y': 0})

# Connections
diagram.add_connection('c1', 'r', 'out', 'feedback', 'in')
diagram.add_connection('c2', 'feedback', 'out', 'plant', 'in')
diagram.add_connection('c3', 'plant', 'out', 'y', 'in')

print("✓ State feedback system created")
```

## Simulate Step Response

```{code-cell} ipython3
# Note: For full state feedback, you would typically use python-control directly
# This simplified example shows the concept

# Closed-loop system
A_cl = A - B @ K
sys_cl = ct.ss(A_cl, B, C, D)

t = np.linspace(0, 5, 500)
t_out, y_out = ct.step_response(sys_cl, t)

plt.figure(figsize=(10, 5))
plt.plot(t_out, y_out, linewidth=2)
plt.grid(True, alpha=0.3)
plt.xlabel('Time (s)')
plt.ylabel('Output')
plt.title('State Feedback Closed-Loop Response')
plt.tight_layout()
plt.show()

print(f"Damping ratio: ~0.7 (from pole location)")
print(f"Natural frequency: ~2.8 rad/s")
```

## Key Advantages

- **Arbitrary pole placement** for stable, controllable systems
- **Multi-variable control** (MIMO systems)
- **Optimal control** possible with LQR design

State-space methods are powerful for complex control problems!
