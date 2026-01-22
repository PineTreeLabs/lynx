# Validation

Lynx performs comprehensive validation before exporting diagrams to python-control. This ensures diagrams are well-formed and mathematically valid.

## Validation Layers

Validation occurs in three layers:

1. **System Boundary Checks**: At least one InputMarker and one OutputMarker
2. **Label Uniqueness**: Warnings for duplicate block or connection labels
3. **Port Connectivity**: All non-InputMarker input ports must be connected

## Automatic Validation

Validation runs automatically when calling export methods:

```python
# Validation happens here
sys = diagram.get_tf('r', 'y')  # Raises ValidationError if invalid
sys = diagram.get_ss('r', 'y')  # Raises ValidationError if invalid
```

You don't need to manually call validation.

## ValidationError

When validation fails, Lynx raises `ValidationError` with detailed context:

```python
from lynx import ValidationError

try:
    sys = diagram.get_tf('r', 'y')
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Block ID: {e.block_id}")
    print(f"Port ID: {e.port_id}")
```

### Error Attributes

- **message**: Human-readable error description
- **block_id**: ID of the block causing the error (if applicable)
- **port_id**: ID of the port causing the error (if applicable)

## Common Validation Errors

### 1. Missing System Boundaries

**Error**: "Diagram must have at least one InputMarker and one OutputMarker"

**Cause**: No IOMarker blocks, or all markers are the same type

**Fix**: Add at least one input and one output marker

```python
# Before (invalid)
diagram.add_block('gain', 'K1', K=5.0)
diagram.add_block('transfer_function', 'plant', numerator=[1.0], denominator=[1.0, 1.0])

# After (valid)
diagram.add_block('io_marker', 'r', marker_type='input', label='r')
diagram.add_block('gain', 'K1', K=5.0)
diagram.add_block('transfer_function', 'plant', numerator=[1.0], denominator=[1.0, 1.0])
diagram.add_block('io_marker', 'y', marker_type='output', label='y')
```

### 2. Unconnected Input Port

**Error**: "Port 'in' of block 'plant' is not connected"

**Cause**: Block has an input port with no incoming connection

**Fix**: Connect the port or remove the block

```python
# Before (invalid) - plant has no input connection
diagram.add_block('io_marker', 'r', marker_type='input', label='r')
diagram.add_block('transfer_function', 'plant', numerator=[1.0], denominator=[1.0, 1.0])
# Missing connection!

# After (valid)
diagram.add_block('io_marker', 'r', marker_type='input', label='r')
diagram.add_block('transfer_function', 'plant', numerator=[1.0], denominator=[1.0, 1.0])
diagram.add_connection('c1', 'r', 'out', 'plant', 'in')  # Connect input
```

### 3. Algebraic Loop

**Error**: "Algebraic loop detected in block 'sum1'"

**Cause**: Feedback loop with no dynamics (no transfer function or integrator in the loop)

**Fix**: Add dynamics to the loop or remove the direct feedthrough

```python
# Before (invalid) - pure gain feedback creates algebraic loop
diagram.add_block('sum', 'error', signs=['+', '-', '|'])
diagram.add_block('gain', 'K1', K=5.0)
diagram.add_block('gain', 'K2', K=2.0)
diagram.add_connection('c1', 'error', 'out', 'K1', 'in')
diagram.add_connection('c2', 'K1', 'out', 'K2', 'in')
diagram.add_connection('c3', 'K2', 'out', 'error', 'in2')  # Direct feedback - algebraic loop!

# After (valid) - add dynamics
diagram.add_block('sum', 'error', signs=['+', '-', '|'])
diagram.add_block('gain', 'K1', K=5.0)
diagram.add_block('transfer_function', 'plant',  # Add dynamics here
                  numerator=[1.0], denominator=[1.0, 1.0])
diagram.add_connection('c1', 'error', 'out', 'K1', 'in')
diagram.add_connection('c2', 'K1', 'out', 'plant', 'in')
diagram.add_connection('c3', 'plant', 'out', 'error', 'in2')  # Now valid
```

### 4. Duplicate Labels

**Warning**: "Duplicate block label 'controller' found"

**Cause**: Multiple blocks or connections with the same label

**Fix**: Use unique labels for all blocks and connections

```python
# Before (warning)
diagram.add_block('gain', 'K1', K=5.0, label='controller')
diagram.add_block('gain', 'K2', K=2.0, label='controller')  # Duplicate!

# After (no warning)
diagram.add_block('gain', 'K1', K=5.0, label='controller_1')
diagram.add_block('gain', 'K2', K=2.0, label='controller_2')
```

Note: Duplicate labels issue warnings but don't block export. However, signal references may be ambiguous.

## Pre-Export Validation Workflow

Best practice for complex diagrams:

```python
import lynx
from lynx import ValidationError

# Build diagram
diagram = lynx.Diagram()
# ... add blocks and connections ...

# Validate before analysis
try:
    # Attempt export (triggers validation)
    sys = diagram.get_tf('r', 'y')
    print("✓ Diagram is valid!")

    # Proceed with analysis
    import control as ct
    ct.bode_plot(sys)

except ValidationError as e:
    print(f"✗ Validation failed: {e}")
    print(f"  Block: {e.block_id}, Port: {e.port_id}")

    # Fix the issue...
    if e.port_id:
        print(f"  Check connections for block '{e.block_id}' port '{e.port_id}'")
```

## Validation Checklist

Before exporting, ensure:

- [ ] At least one InputMarker (`marker_type='input'`)
- [ ] At least one OutputMarker (`marker_type='output'`)
- [ ] All non-InputMarker input ports have connections
- [ ] All connections reference valid blocks and ports
- [ ] No algebraic loops (feedback paths have dynamics)
- [ ] Unique labels for all blocks and connections (optional, but recommended)

## SignalNotFoundError

Separate from `ValidationError`, this exception occurs when the specified signal references don't exist:

```python
from lynx import SignalNotFoundError

try:
    sys = diagram.get_tf('nonexistent', 'y')  # 'nonexistent' not found
except SignalNotFoundError as e:
    print(f"Signal not found: {e.signal_name}")
    print(f"Searched: {e.searched_locations}")
```

### Error Attributes

- **signal_name**: The signal reference that wasn't found
- **searched_locations**: List of places searched (IOMarker labels, connection labels, block outputs)

## See Also

- {doc}`export` - Signal reference patterns and subsystem extraction
- {doc}`diagram` - Building valid diagrams
- {doc}`../getting-started/quickstart` - Quick examples
