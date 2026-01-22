<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Lynx - Block Diagram Widget for Control Systems

<img src="js/src/assets/lynx-logo.png" alt="Lynx logo" width="380" height="380">

**Lightweight block diagram GUI for control systems in Jupyter notebooks**

Lynx is a Jupyter widget that enables interactive creation and editing of control system block diagrams using drag-and-drop. Designed for controls engineers working in Jupyter environments.

## Features

- 🎯 **Interactive Canvas**: Drag-and-drop block diagram editing
- 🧮 **Control Theory Blocks**: Transfer Function, State Space, Gain, Sum Junction, I/O markers
- ✅ **Real-Time Validation**: Algebraic loop detection, connection constraints
- 💾 **Git-Friendly Persistence**: Human-readable JSON format
- 🐍 **Python Integration**: Use numpy expressions for parameters
- 📊 **SISO Systems**: Focus on single-input, single-output control systems

## Quick Start

### Installation

```bash
# Using UV (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### Frontend Setup

```bash
cd js
npm install
npm run build
```

### Jupyter Kernel Setup

```bash
# Install Jupyter kernel for this project
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=lynx
```

### Basic Usage

```python
import lynx
import numpy as np

# Create a diagram
diagram = lynx.Diagram()

# Launch interactive editor (displays in Jupyter)
lynx.edit(diagram)

# Customize widget height
lynx.edit(diagram, height=450)
```

### Creating a Simple Feedback Control System

```python
# The widget provides drag-and-drop interface for:
# 1. Adding blocks from the palette (Gain, Sum, Transfer Function, etc.)
# 2. Connecting blocks by dragging between ports
# 3. Editing parameters by selecting blocks
# 4. Real-time validation of diagram

# Save diagram to JSON (git-friendly format)
diagram.save('my_control_system.json')

# Load diagram in a new session
loaded_diagram = lynx.Diagram.load('my_control_system.json')

# Edit the loaded diagram (recovers previous state)
lynx.edit(loaded_diagram)
```

### Using Matrix Expressions

```python
# Define state-space matrices in your notebook
A = np.array([[0, 1], [-2, -3]])
B = np.array([[0], [1]])
C = np.array([[1, 0]])
D = np.array([[0]])

# Create State Space block via UI
# - In parameter panel, enter: A (references the numpy variable)
# - Widget evaluates expression and stores both expression and value
# - On save/load, diagram preserves variable references

# View diagram validation in real-time
# - Red errors for algebraic loops (feedback without dynamics)
# - Yellow warnings for disconnected blocks
# - Green checkmark when diagram is valid
```

See [quickstart.md](specs/001-lynx-jupyter-widget/quickstart.md) for detailed setup and development workflow.

## Development

### Running Tests

**Python**:
```bash
pytest --cov=lynx
```

**JavaScript**:
```bash
cd js
npm run test
```

### Code Quality

```bash
# Python
black src/ tests/
ruff check src/ tests/
mypy src/

# JavaScript
cd js
npm run format
npm run lint
```

## Project Structure

```
lynx/
├── src/lynx/          # Python package (UV src layout)
├── js/                # Frontend (React + TypeScript)
├── tests/             # Test suites
├── specs/             # Feature specifications
└── pyproject.toml     # UV-managed config
```

## Documentation

- [Feature Specification](specs/001-lynx-jupyter-widget/spec.md)
- [Implementation Plan](specs/001-lynx-jupyter-widget/plan.md)
- [Developer Guide](specs/001-lynx-jupyter-widget/quickstart.md)
- [Data Model](specs/001-lynx-jupyter-widget/data-model.md)

## Requirements

- Python 3.11+
- Node.js 18+
- Jupyter (JupyterLab, classic notebook, or VSCode)

## License

ISC

## Contributing

This project follows Test-Driven Development. See [quickstart.md](specs/001-lynx-jupyter-widget/quickstart.md) for development workflow.
