<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Diagram Templates

This directory contains pre-built diagram templates as JSON files. Templates are loaded at module import time using `importlib.resources.files()`, which works correctly with all Python package installation methods.

## Available Templates

- `open_loop_tf.json` - Open-loop w/ transfer function plant
- `open_loop_ss.json` - Open-loop w/ state-space plant
- `feedback_tf.json` - Feedback control loop (transfer function plant)
- `feedback_ss.json` - Feedback control loop (state-space plant)
- `feedforward_tf.json` - Feedforward control (transfer function plant)
- `feedforward_ss.json` - Feedforward control (state-space plant)
- `filtered_tf.json` - Feedback control loop with filters on reference and output
- `cascaded.json` - Cascaded control system

## Usage

```python
import lynx

# Load a template by name
diagram = lynx.Diagram.from_template('feedback_tf')
```
