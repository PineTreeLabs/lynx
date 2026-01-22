<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Connection Labels

**Feature**: 006-connection-labels
**Date**: 2026-01-12

## Test Scenarios

### Scenario 1: Show Connection Label via Context Menu

**Setup**:
1. Create a diagram with at least one connection between two blocks

**Steps**:
1. Right-click on a connection
2. Observe context menu appears with "Show Label" option
3. Click "Show Label"

**Expected Result**:
- Label appears along the connection path
- Label text shows the connection ID (e.g., "conn_123")
- Label is positioned near the horizontal center of the connection

---

### Scenario 2: Hide Connection Label via Context Menu

**Setup**:
1. Create a diagram with a connection
2. Show the connection's label (via context menu)

**Steps**:
1. Right-click on the connection with visible label
2. Observe context menu shows "Hide Label" option (not "Show Label")
3. Click "Hide Label"

**Expected Result**:
- Label disappears from view
- Context menu option reverts to "Show Label" on next right-click

---

### Scenario 3: Edit Connection Label

**Setup**:
1. Create a diagram with a connection
2. Show the connection's label

**Steps**:
1. Double-click on the visible label
2. Observe inline text editor appears
3. Type a new label (e.g., "velocity")
4. Press Enter

**Expected Result**:
- Label updates to show "velocity"
- Label persists after deselection

**Alternative: Cancel Edit**:
1. Double-click on label
2. Type new text
3. Press Escape

**Expected Result**:
- Edit is cancelled
- Original label text is restored

---

### Scenario 4: Persist Label State on Save/Load

**Setup**:
1. Create a diagram with multiple connections
2. Show labels on some connections, hide others
3. Edit some label text

**Steps**:
1. Save the diagram to a JSON file
2. Close/reload the diagram (or create new widget)
3. Load the saved JSON file

**Expected Result**:
- All label visibility states are restored exactly as saved
- All custom label text is preserved
- Labels that were hidden remain hidden
- Labels that were shown remain shown with their custom text

---

### Scenario 5: Smart Label Positioning

**Setup**:
1. Create a connection with custom waypoints (drag a segment to create corners)

**Steps**:
1. Show the connection's label

**Expected Result**:
- Label appears near the horizontal center of the connection
- Label does NOT overlap any corner waypoints
- If centered position would overlap a corner, label shifts left or right

---

### Scenario 6: Label Repositions on Routing Change

**Setup**:
1. Create a connection with a visible label
2. Note the label position

**Steps**:
1. Move one of the connected blocks

**Expected Result**:
- Connection re-routes automatically
- Label repositions to maintain horizontal center (or avoid new corners)
- Label visibility and text are unchanged

---

## Quick Verification Checklist

| Feature | Test |
|---------|------|
| Default hidden | New connections have no visible label |
| Show via menu | Right-click → "Show Label" displays label |
| Hide via menu | Right-click → "Hide Label" hides label |
| Menu text | Menu shows "Show" or "Hide" based on current state |
| Double-click edit | Double-click label opens inline editor |
| Enter saves | Pressing Enter saves edited text |
| Escape cancels | Pressing Escape discards changes |
| Persistence | Save/load preserves label and visibility |
| Font match | Connection labels use same font as block labels |
| Position center | Label appears at horizontal center of connection |
| Avoids corners | Label shifts to avoid overlapping waypoints |

## Code Verification Points

### Python Backend

```python
# Verify schema fields exist
from lynx.schema import ConnectionModel
conn = ConnectionModel(
    id="test",
    source_block_id="a",
    source_port_id="out",
    target_block_id="b",
    target_port_id="in"
)
assert conn.label is None
assert conn.label_visible == False

# Verify diagram methods exist
from lynx.diagram import Diagram
d = Diagram()
# ... add blocks and connection ...
d.toggle_connection_label_visibility("conn_id")
d.update_connection_label("conn_id", "test label")
```

### Frontend

```typescript
// Verify edge data includes label fields
const edge = connectionToEdge(connection);
expect(edge.data.label).toBeDefined();
expect(edge.data.label_visible).toBeDefined();

// Verify positioning function exists
import { calculateConnectionLabelPosition } from './utils/connectionLabelPosition';
const position = calculateConnectionLabelPosition(segments, "test");
expect(position.x).toBeNumber();
expect(position.y).toBeNumber();
```
