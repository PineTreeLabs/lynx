<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Lynx Examples

This directory contains example Jupyter notebooks demonstrating Lynx's capabilities for control system design.

## Getting Started

1. Install Lynx (see main README.md)
2. Launch Jupyter: `jupyter lab` or `jupyter notebook`
3. Open any example notebook
4. Run cells sequentially

## Example Notebooks

### 01_simple_feedback.ipynb
**Level**: Beginner
**Topics**: Basic feedback control, keyboard shortcuts, save/load

Learn how to:
- Create diagrams using the visual editor
- Use keyboard shortcuts (G, S, T, I, O)
- Connect blocks with drag-and-drop
- Save and load diagrams to JSON
- Validate control system diagrams

**System**: Input → Sum → Transfer Function → Output with Gain feedback

---

### 02_pid_controller.ipynb
**Level**: Intermediate
**Topics**: PID control, transfer function design, parameter tuning

Learn how to:
- Implement PID controllers with separate P, I, D paths
- Use transfer functions for integral (1/s) and derivative (s) terms
- Tune controller gains interactively
- Design multi-path control systems

**System**: Full PID controller with derivative filtering and second-order plant

---

### 03_state_feedback.ipynb
**Level**: Advanced
**Topics**: State-space models, matrix expressions, variable references

Learn how to:
- Use state-space blocks for modern control design
- Reference numpy variables in matrix parameters (e.g., `A`, `B`, `K`)
- Leverage hybrid storage (expression + value)
- Design state feedback controllers
- Handle missing variables on load (fallback to stored values)

**System**: State feedback control with state-space plant and gain matrix

---

## Common Patterns

### Creating Diagrams Programmatically

```python
import lynx

widget = lynx.LynxWidget()
diagram = widget.diagram

# Add blocks
block = diagram.add_block("gain", position={"x": 100, "y": 200}, K="5.0")

# Add connections
diagram.add_connection(source_id, "out", target_id, "in")

# Update display
widget.update()

# Display widget
widget
```

### Keyboard Shortcuts

- **G** - Add Gain block
- **S** - Add Sum junction
- **T** - Add Transfer Function
- **I** - Add Input marker
- **O** - Add Output marker
- **Delete/Backspace** - Delete selected element
- **Ctrl+Z / Cmd+Z** - Undo
- **Ctrl+Y / Cmd+Shift+Z** - Redo

### Saving and Loading

```python
# Save
diagram.save("my_diagram.json")

# Load
diagram = lynx.Diagram.load("my_diagram.json")
widget = lynx.LynxWidget()
widget.diagram = diagram
widget.update()
```

## Validation

Lynx automatically validates diagrams for:
- **Algebraic loops** (ERROR): Feedback without dynamics
- **System completeness** (WARNING): Missing input/output markers
- **Disconnected blocks** (WARNING): Isolated components

Check the validation status icon in the bottom-right corner of the widget.

## Additional Resources

- **Main README**: ../README.md
- **Quickstart Guide**: ../specs/001-lynx-jupyter-widget/quickstart.md
- **Data Model**: ../specs/001-lynx-jupyter-widget/data-model.md

## Contributing Examples

Have a useful control system example? Contributions welcome!

1. Create a well-documented notebook
2. Follow the existing format (markdown explanations + code)
3. Test all cells run successfully
4. Submit a pull request
