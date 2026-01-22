<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Editable Orthogonal Routing

**Feature**: 004-editable-orthogonal-routing
**Date**: 2026-01-06

## Overview

This document provides manual test scenarios for validating the editable orthogonal routing feature.

---

## Prerequisites

1. Jupyter notebook or JupyterLab running
2. Lynx widget installed and working
3. A diagram with at least 2-3 connected blocks

---

## Test Scenarios

### Scenario 1: Basic Segment Dragging

**Setup**: Create a simple diagram with two blocks connected by one connection.

```python
from lynx import LynxWidget

widget = LynxWidget()

# Add two blocks
widget.add_block("gain", "gain_1", K=2.0, position={"x": 100, "y": 200})
widget.add_block("io_marker", "output_1", marker_type="output", label="y", position={"x": 400, "y": 200})

# Connect them
widget.add_connection("gain_1", "out", "output_1", "in")

widget
```

**Test Steps**:
1. Click on the connection line to select it
2. Observe the connection becomes highlighted (thicker line, accent color)
3. Hover over a horizontal segment
4. Observe the cursor changes to vertical resize (↕)
5. Click and drag the segment up or down
6. Observe real-time preview of the new path
7. Release the mouse button
8. Verify the segment stays at the new position

**Expected Result**: Connection is routed through the new position, maintaining 90-degree angles.

---

### Scenario 2: Vertical Segment Dragging

**Setup**: Same as Scenario 1, but position blocks to create a vertical segment.

```python
widget.add_block("gain", "gain_1", K=2.0, position={"x": 200, "y": 100})
widget.add_block("io_marker", "output_1", marker_type="output", label="y", position={"x": 200, "y": 400})
widget.add_connection("gain_1", "out", "output_1", "in")
```

**Test Steps**:
1. Select the connection
2. Hover over a vertical segment
3. Observe cursor changes to horizontal resize (↔)
4. Drag the segment left or right
5. Release

**Expected Result**: Vertical segment moves horizontally, path maintains orthogonal routing.

---

### Scenario 3: Persistence (Save/Load)

**Setup**: Create a diagram and customize routing.

**Test Steps**:
1. Create a diagram with connections
2. Drag segments to customize routing
3. Save the diagram: `widget.save("test_routing.json")`
4. Close and recreate the widget
5. Load the diagram: `widget.load("test_routing.json")`

**Expected Result**: Custom routing is restored exactly as saved.

---

### Scenario 4: Undo/Redo

**Setup**: Diagram with at least one connection.

**Test Steps**:
1. Drag a segment to a new position
2. Press Ctrl+Z (Cmd+Z on Mac)
3. Verify segment returns to original position
4. Press Ctrl+Y (Cmd+Shift+Z on Mac)
5. Verify segment returns to the dragged position

**Expected Result**: Routing changes integrate with undo/redo system.

---

### Scenario 5: Reset to Auto

**Setup**: Connection with custom waypoints.

**Test Steps**:
1. Customize a connection's routing (drag segments)
2. Select the connection
3. Trigger "Reset to Auto" (context menu or button)
4. Verify connection returns to automatic routing

**Expected Result**: Waypoints are cleared, default routing algorithm takes over.

---

### Scenario 6: Grid Snapping

**Setup**: Grid snap enabled (default).

**Test Steps**:
1. Drag a segment to an arbitrary position
2. Release the mouse
3. Observe the segment snaps to the nearest 20px grid line

**Expected Result**: Waypoints align to 20px grid.

---

### Scenario 7: Block Movement with Waypoints

**Setup**: Connection with custom waypoints.

**Test Steps**:
1. Customize a connection's routing
2. Move one of the connected blocks to a new position
3. Observe the connection routing

**Expected Result**: Waypoints remain at absolute positions; connection re-routes through them.

---

### Scenario 8: Block Deletion Cascade

**Setup**: Connection with custom waypoints.

**Test Steps**:
1. Customize routing for a connection
2. Delete one of the connected blocks
3. Verify the connection (and its waypoints) are removed

**Expected Result**: Connection and waypoints are deleted together.

---

### Scenario 9: Visual Feedback States

**Test Steps**:
1. Observe default connection (not selected): normal line
2. Hover over connection: slight highlight, cursor changes
3. Click to select: thicker line, accent color
4. Start dragging: preview path in accent, original dimmed
5. Release: new path renders normally

**Expected Result**: Clear visual feedback throughout interaction.

---

### Scenario 10: Performance with Many Connections

**Setup**: Create diagram with 50+ connections.

```python
# Create a grid of blocks
for i in range(10):
    for j in range(5):
        widget.add_block("gain", f"gain_{i}_{j}", K=1.0,
                        position={"x": i*120, "y": j*100})

# Connect adjacent blocks
for i in range(9):
    for j in range(5):
        widget.add_connection(f"gain_{i}_{j}", "out", f"gain_{i+1}_{j}", "in")
```

**Test Steps**:
1. Select a connection and drag a segment
2. Observe drag performance (should be smooth)
3. Repeat for several connections

**Expected Result**: No perceptible lag during drag operations.

---

## Automated Test Coverage

The following automated tests should be implemented:

### Unit Tests (TypeScript)
- `orthogonalRouting.test.ts`: Path calculation with various waypoint configurations
- `OrthogonalEditableEdge.test.tsx`: Component rendering and interaction

### Unit Tests (Python)
- `test_connection_routing.py`: Waypoint persistence, serialization, update methods

### Contract Tests
- `test_routing_sync.py`: Frontend-backend action/state synchronization

---

## Known Limitations

1. **No automatic block avoidance**: Users must manually route around blocks
2. **No parallel connection offset**: Multiple connections between same blocks may overlap
3. **Orthogonal only**: No diagonal or curved routing options
