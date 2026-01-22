# API Reference

Complete reference documentation for Lynx's Python API. All public methods, parameters, and examples are documented here.

## Overview

Lynx provides a simple, intuitive API for creating and analyzing control system diagrams:

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Diagram Management
:link: diagram
:link-type: doc

Create, save, and load diagrams. The central class for all Lynx operations.
:::

:::{grid-item-card} Block Library
:link: blocks
:link-type: doc

Five block types for building control systems: Gain, TransferFunction, StateSpace, Sum, IOMarker.
:::

:::{grid-item-card} Validation
:link: validation
:link-type: doc

Pre-export validation to catch errors: algebraic loops, connectivity, label uniqueness.
:::

:::{grid-item-card} Python-Control Export
:link: export
:link-type: doc

Export diagrams to python-control for analysis and simulation.
:::

::::

## Quick Reference

Common tasks and their corresponding API methods:

| Task | API Method | Example |
|------|------------|---------|
| Create diagram | `lynx.Diagram()` | `diagram = lynx.Diagram()` |
| Add block | `diagram.add_block()` | `diagram.add_block('gain', 'K1', K=5.0)` |
| Add connection | `diagram.add_connection()` | `diagram.add_connection('c1', 'K1', 'out', 'plant', 'in')` |
| Save diagram | `diagram.save()` | `diagram.save('my_diagram.json')` |
| Load diagram | `lynx.Diagram.load()` | `diagram = lynx.Diagram.load('my_diagram.json')` |
| Export transfer function | `diagram.get_tf()` | `sys = diagram.get_tf('r', 'y')` |
| Export state-space | `diagram.get_ss()` | `sys = diagram.get_ss('r', 'y')` |
| Interactive widget | `lynx.edit()` | `lynx.edit(diagram)` |

## Detailed Documentation

```{toctree}
:maxdepth: 2

diagram
blocks
validation
export
```

## API Conventions

### Parameter Types

Lynx uses type hints throughout. Common parameter types:

- **block_type**: `str` - One of: `'gain'`, `'transfer_function'`, `'state_space'`, `'sum'`, `'io_marker'`
- **block_id**: `str` - Unique identifier for a block
- **port_id**: `str` - Port identifier (e.g., `'in'`, `'out'`, `'in1'`, `'in2'`)
- **position**: `dict[str, float]` - `{'x': float, 'y': float}` coordinates

### Return Values

- Methods that modify diagrams typically return `None` (modify in-place)
- Export methods return python-control objects: `TransferFunction` or `StateSpace`
- Load methods return new `Diagram` instances

### Error Handling

Lynx raises descriptive exceptions with context:

- **ValidationError**: Pre-export validation failures (includes `block_id` and `port_id`)
- **SignalNotFoundError**: Signal reference not found during export
- **ValueError**: Invalid parameters or arguments

See {doc}`validation` for details on error handling and recovery.
