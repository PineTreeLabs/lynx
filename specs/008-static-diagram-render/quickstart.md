<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Static Diagram Render

**Feature**: 008-static-diagram-render
**Date**: 2026-01-13

## Basic Usage

### Export to PNG

```python
import lynx
from lynx import Diagram, GainBlock

# Create a diagram
diagram = Diagram()
diagram.add_block("gain", id="g1", position={"x": 100, "y": 100}, K=2.5)
diagram.add_block("sum", id="s1", position={"x": 250, "y": 100}, signs=["+", "-"])
diagram.add_connection("c1", "g1", "out", "s1", "in_0")

# Export to PNG
lynx.render(diagram, "my_diagram.png")
```

### Export to SVG

```python
# Export to SVG (same API, different extension)
lynx.render(diagram, "my_diagram.svg")
```

## Options

### Custom Dimensions

```python
# Fixed width and height
lynx.render(diagram, "output.png", width=1200, height=800)

# Fixed width only (height auto-calculated)
lynx.render(diagram, "output.png", width=1200)

# Fixed height only (width auto-calculated)
lynx.render(diagram, "output.png", height=600)
```

### Transparent Background

```python
# PNG with transparent background
lynx.render(diagram, "output.png", transparent=True)

# SVG with transparent background
lynx.render(diagram, "output.svg", transparent=True)
```

### Combined Options

```python
# Large transparent PNG
lynx.render(diagram, "output.png", width=1920, height=1080, transparent=True)
```

## Test Scenarios

### Scenario 1: Basic PNG Export

**Steps**:
1. Create a simple diagram with 2 blocks and 1 connection
2. Call `lynx.render(diagram, "test1.png")`
3. Verify file exists and opens as valid PNG
4. Verify blocks and connections are visible

**Expected**: PNG file created with diagram content, white background

### Scenario 2: SVG Export with LaTeX

**Steps**:
1. Create diagram with TransferFunction block containing polynomials
2. Call `lynx.render(diagram, "test2.svg")`
3. Open SVG in browser and scale to 4x
4. Verify LaTeX renders correctly and scales cleanly

**Expected**: SVG file with crisp vector graphics at any scale

### Scenario 3: Custom Dimensions

**Steps**:
1. Create diagram with 3 blocks
2. Export with `width=800, height=600`
3. Check output dimensions in image viewer

**Expected**: Output image is exactly 800x600 pixels

### Scenario 4: Transparent Background

**Steps**:
1. Create simple diagram
2. Export with `transparent=True`
3. Open in image editor with colored background
4. Verify background shows through around diagram

**Expected**: Only diagram elements visible, background is transparent

### Scenario 5: Auto-fit Content

**Steps**:
1. Create diagram with blocks at positions (0,0) and (500, 400)
2. Export without specifying dimensions
3. Verify output is cropped to content with small margins
4. No excessive whitespace around diagram

**Expected**: Image bounds match content bounds (plus padding)

### Scenario 6: Empty Diagram Error

**Steps**:
1. Create empty diagram (no blocks)
2. Call `lynx.render(diagram, "test.png")`

**Expected**: `ValueError("Cannot render empty diagram: no blocks to display")`

### Scenario 7: Invalid Format Error

**Steps**:
1. Create valid diagram
2. Call `lynx.render(diagram, "test.jpg")`

**Expected**: `ValueError("Unsupported file format. Use .png or .svg")`

### Scenario 8: All Block Types

**Steps**:
1. Create diagram with one of each block type:
   - GainBlock with K=1.5
   - SumBlock with signs ["+", "-", "|"]
   - TransferFunctionBlock with numerator [1], denominator [1, 2, 1]
   - StateSpaceBlock with 2x2 matrices
   - IOMarker (input and output)
2. Connect all blocks in a chain
3. Export to PNG and SVG

**Expected**: All blocks render correctly with proper shapes and labels

### Scenario 9: Port Markers Visible

**Steps**:
1. Create diagram with unconnected block (e.g., single Gain block)
2. Export to PNG
3. Verify triangular port markers are visible on unconnected ports

**Expected**: Port markers (triangular arrowheads) appear on unconnected ports

### Scenario 10: Large Diagram Performance

**Steps**:
1. Create diagram with 50 blocks programmatically
2. Time the `lynx.render()` call
3. Verify output renders correctly

**Expected**: Render completes in under 5 seconds

## Common Issues

### Widget Not Displaying

If `lynx.render()` hangs, ensure you're running in a Jupyter environment or have IPython available. The function needs to display the widget temporarily to render.

### SVG Not Rendering in Editor

SVG files use foreignObject for HTML content (like KaTeX). Some vector editors (Illustrator, Inkscape) may not render these correctly. For best compatibility:
- Use PNG for print/editing workflows
- Use SVG for web embedding where browsers handle it correctly

### Memory Issues with Very Large Diagrams

For diagrams with 100+ blocks, consider:
- Reducing output dimensions
- Using SVG format (smaller file size)
- Splitting into multiple diagrams
