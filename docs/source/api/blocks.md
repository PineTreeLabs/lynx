# Block Types

Lynx provides five block types for building control system diagrams. Each block type has specific parameters and use cases.

## Block Comparison

| Block Type | Key Parameters | Ports |
|------------|----------------|-------|
| **Gain** | `K` (float) | 1 input, 1 output |
| **TransferFunction** | `num`, `den` (arrays) | 1 input, 1 output |
| **StateSpace** | `A`, `B`, `C`, `D` (matrices) | 1+ inputs, 1+ outputs |
| **Sum** | `signs` (list: +/-/\|) | 3 inputs max, 1 output |
| **InputMarker** | `label`, `index` | 1 output |
| **OutputMarker** | `label`, `index` | 1 input |


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
