# Python-Control Export

Export Lynx diagrams to python-control for analysis, simulation, and controller design.

## Export Methods

Lynx provides two primary export methods:

```python
# Transfer function representation
sys_tf = diagram.get_tf('from_signal', 'to_signal')

# State-space representation
sys_ss = diagram.get_ss('from_signal', 'to_signal')
```

Both methods:
- Take two signal references (from and to)
- Return python-control objects (`TransferFunction` or `StateSpace`)
- Perform validation before export (raises `ValidationError` if invalid)

For more information see {doc}`../concepts/export`.

## See Also

- {doc}`diagram` - Building diagrams
- {doc}`blocks` - IOMarker block details
- {doc}`validation` - Error handling and validation
- {doc}`../examples/cruise-control` - Workflow including export
