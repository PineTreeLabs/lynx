# Block Types

Lynx provides five block types for building control system diagrams. Each block type has specific parameters and use cases.

## Block Comparison

| Block Type | Use Case | Key Parameters | Ports |
|------------|----------|----------------|-------|
| **Gain** | Scalar multiplication, controller gains | `K` (float) | 1 input, 1 output |
| **TransferFunction** | LTI systems in s-domain, plant models | `numerator`, `denominator` (arrays) | 1 input, 1 output |
| **StateSpace** | MIMO systems, state feedback | `A`, `B`, `C`, `D` (matrices) | 1+ inputs, 1+ outputs |
| **Sum** | Adding/subtracting signals, error calculation | `signs` (list: +/-/\|) | 3 inputs max, 1 output |
| **IOMarker** | System boundaries, signal labels | `marker_type`, `label` | 1 input OR 1 output |

## Gain Block

Multiplies input by constant gain K.

### Parameters

- **K** (`float`): Gain value (default: 1.0)
- **label** (`str`, optional): Block label for display
- **custom_latex** (`str`, optional): Custom LaTeX for rendering
- **position** (`dict`, optional): `{'x': float, 'y': float}`

### Example

```python
# Proportional controller with K=5
diagram.add_block('gain', 'controller', K=5.0, label='P Controller')

# Negative gain
diagram.add_block('gain', 'inverter', K=-1.0)

# Custom LaTeX
diagram.add_block('gain', 'alpha', K=0.5, custom_latex=r'\alpha')
```

### Transfer Function

Mathematical representation: $G(s) = K$

## TransferFunction Block

Represents LTI systems in Laplace domain: $G(s) = \frac{N(s)}{D(s)}$

### Parameters

- **numerator** (`list[float]`): Numerator coefficients (descending powers of s)
- **denominator** (`list[float]`): Denominator coefficients (descending powers of s)
- **label** (`str`, optional): Block label
- **custom_latex** (`str`, optional): Custom LaTeX for rendering
- **position** (`dict`, optional): Position coordinates

### Example

```python
# First-order system: G(s) = 2/(s+3)
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0],
                  denominator=[1.0, 3.0])

# Second-order system: G(s) = (s+1)/(s^2 + 2s + 1)
diagram.add_block('transfer_function', 'filter',
                  numerator=[1.0, 1.0],
                  denominator=[1.0, 2.0, 1.0])

# Pure integrator: G(s) = 1/s
diagram.add_block('transfer_function', 'integrator',
                  numerator=[1.0],
                  denominator=[1.0, 0.0])
```

### LaTeX Rendering

- Numerator and denominator automatically render as polynomial fractions
- Coefficients shown with 3 significant figures
- Exponential notation for very small/large values

## StateSpace Block

Represents systems in state-space form:

$$
\begin{align}
\dot{x} &= Ax + Bu \\\\
y &= Cx + Du
\end{align}
$$

### Parameters

- **A** (`np.ndarray`): State matrix (n×n)
- **B** (`np.ndarray`): Input matrix (n×m)
- **C** (`np.ndarray`): Output matrix (p×n)
- **D** (`np.ndarray`): Feedthrough matrix (p×m)
- **label** (`str`, optional): Block label
- **custom_latex** (`str`, optional): Custom LaTeX for rendering
- **position** (`dict`, optional): Position coordinates

### Example

```python
import numpy as np

# 2-state system
A = np.array([[-1, 0], [0, -2]])
B = np.array([[1], [1]])
C = np.array([[1, 0]])
D = np.array([[0]])

diagram.add_block('state_space', 'ss_plant',
                  A=A, B=B, C=C, D=D,
                  label='State Space Plant')

# MIMO system (2 inputs, 2 outputs)
A = np.array([[-1, 1], [-1, -1]])
B = np.array([[1, 0], [0, 1]])
C = np.array([[1, 0], [0, 1]])
D = np.zeros((2, 2))

diagram.add_block('state_space', 'mimo_system',
                  A=A, B=B, C=C, D=D)
```

### Port Naming

For MIMO systems:
- Input ports: `in1`, `in2`, ..., `inM`
- Output ports: `out1`, `out2`, ..., `outP`

## Sum Block

Adds or subtracts up to 3 signals based on configured signs.

### Parameters

- **signs** (`list[str]`): Port signs for [top, left, bottom] positions
  - `"+"`: Addition
  - `"-"`: Subtraction
  - `"|"`: Port disabled (no port at this position)
- **label** (`str`, optional): Block label
- **position** (`dict`, optional): Position coordinates

### Port Configuration

Ports are created based on `signs` parameter:
- Index 0 (top): `in1`
- Index 1 (left): `in2`
- Index 2 (bottom): `in3`
- Output: always `out`

### Example

```python
# Error calculation: e = r - y
diagram.add_block('sum', 'error',
                  signs=['+', '-', '|'])  # Top: +r, Left: -y, Bottom: disabled

# Three-input sum: out = a + b - c
diagram.add_block('sum', 'three_way',
                  signs=['+', '+', '-'])

# Two-input addition
diagram.add_block('sum', 'adder',
                  signs=['+', '+', '|'])
```

### Interactive Configuration

In the Jupyter widget, click quadrants to cycle signs: + → - → | → +

## IOMarker Block

Marks system input/output boundaries and provides signal labels for export.

### Parameters

- **marker_type** (`str`): `'input'` or `'output'`
- **label** (`str`): Signal name for export (e.g., `'r'`, `'y'`)
- **index** (`int`, optional): Index for automatic LaTeX numbering
- **custom_latex** (`str`, optional): Custom LaTeX override
- **position** (`dict`, optional): Position coordinates

### Example

```python
# System inputs
diagram.add_block('io_marker', 'ref', marker_type='input', label='r')
diagram.add_block('io_marker', 'dist', marker_type='input', label='d')

# System outputs
diagram.add_block('io_marker', 'output', marker_type='output', label='y')
diagram.add_block('io_marker', 'error_out', marker_type='output', label='e')
```

### Export Usage

IOMarker labels are the **highest priority** signal references:

```python
# Export from 'r' to 'y' using IOMarker labels
sys = diagram.get_tf('r', 'y')
```

See {doc}`export` for signal reference priority rules.

## API Reference

```{eval-rst}
.. currentmodule:: lynx.blocks

.. autosummary::
   :toctree: generated/
   :nosignatures:

   GainBlock
   TransferFunctionBlock
   StateSpaceBlock
   SumBlock
   InputMarker
   OutputMarker
```

## See Also

- {doc}`diagram` - Adding blocks to diagrams
- {doc}`export` - Using IOMarker labels for export
- {doc}`../examples/index` - Block usage examples
