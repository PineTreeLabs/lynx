# Graphical Editing

The Python code and the interactive widget have bidirectional syncing:

```python
# 1. Create diagram programmatically
diagram = lynx.Diagram()
diagram.add_block('gain', 'K', K=5.0)
diagram.add_block('transfer_function', 'G',
                  num=[2.0], den=[1.0, 3.0])
diagram.add_connection('c1', 'K', 'out', 'G', 'in')

# 2. Launch interactive widget
lynx.edit(diagram)

# 3. Makes changes in UI:
#    - Drag blocks to new positions
#    - Edit parameters in property panel
#    - Add/remove connections
#    - Adjust routing waypoints

# 4. The diagram object is updated automatically
print(diagram.blocks['K'].parameters['K'])  # May have changed if user edited it
```

### Use Cases

**Visual verification**:
- Check that programmatic diagram construction is correct
- Verify signal routing and connection topology

**Manual layout adjustments**:
- Position blocks for clear visualization
- Adjust connection routing for readability

**Exploratory design**:
- Quickly try different topologies
- Add/remove blocks interactively
- Experiment with parameter values

**Documentation**:
- Generate clean block diagrams for papers/presentations
- Export screenshots with `lynx.edit(diagram).export_png('diagram.png')`