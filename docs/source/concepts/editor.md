# Graphical Editing

The main interface for editing block diagrams in Lynx is a Jupyter widget, which allows interactive editing inline in Jupyter notebooks.

<div class="hero-video-container">
  <video autoplay loop muted playsinline class="hero-video">
    <source src="../_static/landing-demo.webm" type="video/webm">
    Your browser does not support the video tag.
  </video>
  <p class="hero-caption">Basic widget functionality</p>
</div>

This is strongly recommended over programmatic diagram construction - put simply, it is very difficult to design an inutitive API for what is fundamentally a graphical "language".
A convenient workflow is to:

1. Create a diagram in the interactive widget or [initialize from a template](./templates.md)
2. Save the diagram to JSON (can also check into git)
3. Edit parameters and [extract subsystems](./export.md) using Python
4. Use the widget for visualization or further structural changes or visualization, saving changes to the JSON file

<!-- TODO: Add link to YouTube video once it's up -->

## State Synchronization

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
print(diagram["gain"].get_parameter("K"))
```

This allows you to update Python variables used in expressions in the diagram and have the changes automatically propagate to the diagram, or to edit the diagram and have the changes automatically sync to the Python `Diagram` object.

## Static Rendering

For documentation/publication/presentations, you can also create static renderings with `lynx.render(diagram, 'diagram.png')`, which supports both PNG and SVG exports.