# Diagram Validation

Lynx validates diagrams both in the editor widget and before exporting to python-control.
In the editor the validation status is displayed in the lower right corner with a green ✅ for all checks passing, yellow ⚠️ for warnings, and red ❌ for errors.

1. **System Boundaries**: Every diagram must have at least one input marker and one output marker; without these, there's no well-defined system to export.
2. **Label Uniqueness**: Duplicate labels raise errors, either on blocks or connections.
3. **Port Connectivity**: All input ports must be connected (outputs are optional).
4. **Algebraic Loops**: Signal loops must be broken by an integrator in order to maintain causality in the diagram.

The error message includes:
- **Block ID**: Which block has the issue
- **Port ID**: Which port is problematic
- **Guidance**: What needs to be fixed

Common fixes:
1. **Missing input connection**: Add connection from upstream block
2. **Missing IOMarker**: Add InputMarker or OutputMarker to define system boundary
3. **Duplicate labels**: Rename blocks/connections to ensure uniqueness


## Example ValidationError

```python
# Forgot to connect controller input
diagram.add_block('gain', 'controller', K=5.0)
diagram.add_block('transfer_function', 'plant',
                  num=[2.0], den=[1.0, 3.0])
diagram.add_connection('c1', 'controller', 'out', 'plant', 'in')

try:
    sys = diagram.get_tf('r', 'y')
except lynx.ValidationError as e:
    print(e)
    # Block 'controller' input port 'in' is not connected
```
