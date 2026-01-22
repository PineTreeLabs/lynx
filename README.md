<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Lynx - Block Diagram Widget for Control Systems

<!-- <img src="js/src/assets/lynx-logo.png" alt="Lynx logo" width="380" height="380"> -->

**Lightweight block diagram editor GUI for control systems in Jupyter notebooks**

Lynx is a Jupyter widget that enables interactive creation and editing of block diagrams for linear SISO control systems. Designed for controls engineers working in Jupyter environments.

## Features

- **Interactive Canvas**: Drag-and-drop block diagram editing
- **Control Theory Blocks**: Transfer Function, State Space, Gain, Sum Junction, I/O markers
- **Real-Time Validation**: Algebraic loop detection, connection constraints
- **Git-Friendly Persistence**: Human-readable JSON format
- **Python Integration**: Use numpy expressions for parameters, export to python-control
- **SISO Systems**: Focus on linear single-input, single-output control systems

For more details, see the [documentation site](https://pinetreelabs.github.io/lynx/)

## Quick Start

The easiest way to install from pip:

```bash
pip install lynx-nb
```

### Source build

#### Backend installation

```bash
# Using UV (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

#### Frontend Setup

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
```
