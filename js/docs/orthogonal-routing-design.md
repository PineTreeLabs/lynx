<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Orthogonal Routing Design Document

This document describes the orthogonal (90-degree) connection routing system for Lynx block diagrams.

---

## Part 1: Behavioral Specification

This section defines **what** the routing system must do, independent of implementation.

### 1.1 Overview

Connections between blocks are rendered as orthogonal paths—lines that travel only horizontally or vertically, turning at 90-degree angles.

### 1.2 Terminology

| Term                | Definition                                                        |
| ------------------- | ----------------------------------------------------------------- |
| **Port**            | Connection point on a block (input or output)                     |
| **Port Position**   | Which face of the block the port is on (Left, Right, Top, Bottom) |
| **Segment**         | A single horizontal or vertical line in the path                  |
| **Waypoint**        | An intermediate corner point where the path bends                 |
| **Auto-routed**     | Path computed automatically (no stored waypoints)                 |
| **Manually edited** | Path with user-created waypoints                                  |

### 1.3 Port Connection Requirements

#### 1.3.1 Exit Direction

Connections must exit ports perpendicular to the block face:

| Port Position | Exit Direction           |
| ------------- | ------------------------ |
| Right         | Rightward (increasing X) |
| Left          | Leftward (decreasing X)  |
| Top           | Upward (decreasing Y)    |
| Bottom        | Downward (increasing Y)  |

#### 1.3.2 Approach Direction

Connections must enter target ports perpendicular to the block face:

| Port Position | Approach Direction                   |
| ------------- | ------------------------------------ |
| Left          | From the left (segment moving right) |
| Right         | From the right (segment moving left) |
| Top           | From above (segment moving down)     |
| Bottom        | From below (segment moving up)       |

### 1.4 Block Avoidance

- **Clearance margin**: 20 pixels around all block bounding boxes
- **No crossing**: Path segments must not pass through any block interior
- **All blocks**: Paths avoid ALL blocks in the diagram, not just source/target

### 1.5 Path Optimization

When multiple valid paths exist, prefer:

1. **Fewer turns** (each 90° bend is penalized)
2. **Shorter total length**
3. **Alignment with port direction** at both ends

### 1.6 Segment Editing

When a user drags a segment:

- **Horizontal segments** move only vertically (up/down)
- **Vertical segments** move only horizontally (left/right)
- Dragging creates or updates waypoints
- Adjacent segments adjust to maintain connectivity

### 1.7 Waypoint Behavior

| Scenario                        | Behavior                                                    |
| ------------------------------- | ----------------------------------------------------------- |
| Auto-routed (no waypoints)      | Computed fresh on every render                              |
| Manually edited (has waypoints) | Use stored waypoints, persist to Python                     |
| Block moved                     | Clear waypoints for connected edges, revert to auto-routing |
| Segment dragged                 | Create/update waypoints, persist on drag end                |

### 1.8 Waypoint Simplification

After editing, waypoints are cleaned up:

1. **Alignment**: Coordinates within 15px of neighbor snap together
2. **Collinearity removal**: Three collinear waypoints reduce to two

Example:

```
Before: (100,100) → (100,103) → (200,103)  [tiny 3px jog]
After:  (100,100) → (200,100)               [single segment]
```

### 1.9 Expected Path Shapes

#### Forward Connection (Right → Left, target to the right)

```
Source[out]────┐
               │
               └────[in]Target
```

#### Backwards Connection (Right → Left, target to the left)

```
Source[out]────┐
               │  (goes around both blocks)
┌──────────────┘
│
└────[in]Target
```

#### Multi-block Avoidance

```
Source[out]─────┐
                │ [Block A]
          ┌─────┘
          │
          └─────────[in]Target
```

---

## Part 2: Algorithm Description

This section describes **how** the routing is implemented.

### 2.1 Architecture Overview

The implementation uses a **visibility graph algorithm with Dijkstra pathfinding**.

```
calculateOrthogonalPath()
    │
    ├── waypoints.length === 0?
    │   └── findOrthogonalPath()           ← Visibility graph routing
    │       ├── generateRouteNodesWithSourceTarget()
    │       ├── buildVisibilityGraphWithConstraints()
    │       └── dijkstraWithTurns()
    │
    └── waypoints.length > 0?
        └── Route through waypoints         ← Simple H-V routing
```

### 2.2 Key Data Structures

```typescript
interface Point {
  x: number;
  y: number;
}
interface Waypoint {
  x: number;
  y: number;
}
interface Segment {
  from: Point;
  to: Point;
  orientation: "horizontal" | "vertical";
}
interface BlockBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}
interface RouteNode {
  id: string;
  point: Point;
  type: "source" | "target" | "corner";
}
interface RouteEdge {
  to: RouteNode;
  distance: number;
  orientation: SegmentOrientation;
}
```

### 2.3 Constants

| Constant       | Value | Purpose                        |
| -------------- | ----- | ------------------------------ |
| `BLOCK_MARGIN` | 20px  | Clearance around blocks        |
| `TURN_PENALTY` | 50px  | Cost penalty for each 90° turn |
| `PORT_OFFSET`  | 20px  | Extension distance from ports  |

### 2.4 Visibility Graph Algorithm

#### Step 1: Generate Grid Nodes

Create nodes at the intersection of all relevant X and Y coordinates:

**X coordinates from:**

- Source port X
- Target port X
- Source exit point X (port X ± margin, based on port direction)
- Target approach point X
- All block corners X (with margin expansion)

**Y coordinates from:**

- Same pattern as X

**Result:** A grid of `|X| × |Y|` potential routing nodes.

#### Step 2: Build Visibility Graph

For each pair of nodes:

1. **Check orthogonality**: Only connect nodes sharing same X or same Y
2. **Check block crossing**: Reject edges that pass through any block interior
3. **Apply directional constraints**:
   - From source: edge must go in port's exit direction
   - To target: edge must come from port's approach direction
4. **Exclude source/target blocks** from collision check for their respective edges

#### Step 3: Dijkstra with Turn Penalty

Search over `(node, direction)` state pairs:

```
Cost = distance + turnCost + alignmentCost

where:
  turnCost = TURN_PENALTY if direction changed from previous edge
  alignmentCost = TURN_PENALTY if final edge doesn't match target port direction
```

This naturally minimizes both path length and number of turns.

#### Step 4: Convert to Segments

The Dijkstra path (list of nodes) is converted directly to segments. No additional "exit" or "approach" segments are added—the directional constraints ensure the path already exits and approaches correctly.

### 2.5 Directional Constraints

The key insight that eliminates "spike" bugs: source and target nodes are constrained at the graph level.

**Source constraint** (`isValidExitDirection`):

```
Right port: first edge must have to.x > from.x
Left port:  first edge must have to.x < from.x
Bottom:     first edge must have to.y > from.y
Top:        first edge must have to.y < from.y
```

**Target constraint** (`isValidApproachDirection`):

```
Left port:  final edge must come from left (from.x < to.x)
Right port: final edge must come from right (from.x > to.x)
Top port:   final edge must come from above (from.y < to.y)
Bottom:     final edge must come from below (from.y > to.y)
```

### 2.6 Block Collision Detection

```typescript
function segmentCrossesBlock(a: Point, b: Point, block: BlockBounds): boolean {
  // Horizontal segment at y=a.y
  if (a.y === b.y) {
    // Must be STRICTLY inside block's Y range
    if (y <= blockTop || y >= blockBottom) return false;
    // X range must overlap
    if (maxX <= blockLeft || minX >= blockRight) return false;
    return true;
  }
  // Vertical segment (symmetric logic)
  ...
}
```

**Key**: Segments touching block boundaries exactly do NOT count as crossing. This allows routing along block edges.

### 2.7 Waypoint Routing (Manual Edits)

When waypoints exist, use simpler routing:

1. Exit source perpendicular (source → sourceExt)
2. Route sourceExt → waypoint[0] using H-V or V-H
3. Route between consecutive waypoints
4. Route waypoint[n-1] → targetExt
5. Enter target perpendicular (targetExt → target)

This simpler approach works because waypoints define explicit bend points—no block avoidance needed (user chose the path).

### 2.8 Segment Editing

#### updateWaypointsFromDrag

**No existing waypoints:**

```typescript
if (horizontal segment dragged) {
  // Create two waypoints at new Y, using source/target X
  return [{ x: source.x, y: newY }, { x: target.x, y: newY }];
}
if (vertical segment dragged) {
  // Create two waypoints at new X, using source/target Y
  return [{ x: newX, y: source.y }, { x: newX, y: target.y }];
}
```

**Existing waypoints:**

- Find waypoints near the dragged segment (within 30px tolerance)
- Update their coordinate in the drag direction

#### simplifyWaypoints

```typescript
function simplifyWaypoints(waypoints, tolerance = 15) {
  // Phase 1: Snap coordinates within tolerance to previous waypoint
  aligned = waypoints.map(wp => ({
    x: |wp.x - prev.x| < tolerance ? prev.x : wp.x,
    y: |wp.y - prev.y| < tolerance ? prev.y : wp.y
  }));

  // Phase 2: Remove collinear points
  result = [aligned[0]];
  for (i = 1; i < length-1; i++) {
    if (!collinear(prev, curr, next)) {
      result.push(curr);
    }
  }
  result.push(aligned[last]);
  return result;
}
```

### 2.9 Complexity Analysis

| Operation               | Complexity  | Notes                                         |
| ----------------------- | ----------- | --------------------------------------------- |
| Grid generation         | O(b)        | b = number of blocks                          |
| Node count              | O(b²)       | Grid is X × Y coordinates                     |
| Graph construction      | O(n² × b)   | n = nodes, check each pair against all blocks |
| Dijkstra search         | O(n² log n) | Priority queue with n² states                 |
| Waypoint simplification | O(w)        | w = number of waypoints                       |

**Typical performance**: For 20 blocks, ~40 X coords × 40 Y coords = 1600 nodes. Graph construction dominates at ~50ms worst case. In practice, <10ms for most diagrams.

### 2.10 File Structure

| File                         | Purpose                                          |
| ---------------------------- | ------------------------------------------------ |
| `orthogonalRouting.ts`       | All routing algorithms and utilities             |
| `OrthogonalEditableEdge.tsx` | React component, calls `calculateOrthogonalPath` |
| `DiagramCanvas.tsx`          | Clears waypoints on drag start                   |

### 2.11 Key Functions

| Function                              | Purpose                                               |
| ------------------------------------- | ----------------------------------------------------- |
| `calculateOrthogonalPath`             | Main entry point, dispatches to appropriate algorithm |
| `findOrthogonalPath`                  | Visibility graph routing for auto-routed connections  |
| `generateRouteNodesWithSourceTarget`  | Creates grid nodes                                    |
| `buildVisibilityGraphWithConstraints` | Creates edges with directional constraints            |
| `dijkstraWithTurns`                   | Shortest path with turn penalty                       |
| `segmentCrossesBlock`                 | Collision detection                                   |
| `updateWaypointsFromDrag`             | Handle segment drag editing                           |
| `simplifyWaypoints`                   | Clean up waypoints after editing                      |

---

## Appendix A: Comparison with Previous Heuristic Algorithm

The previous implementation used pattern-based heuristics:

| Aspect          | Old (Heuristic)                   | New (Visibility Graph) |
| --------------- | --------------------------------- | ---------------------- |
| Block avoidance | Only source/target                | All blocks             |
| Approach        | Pattern matching (H-H, V-V, etc.) | Graph search           |
| Exit/approach   | Separate unconditional segments   | Constraints in graph   |
| Complexity      | O(1)                              | O(n² × b)              |
| Robustness      | Edge case bugs (spikes)           | Provably optimal       |
| Code size       | ~400 lines, many conditionals     | ~300 lines, modular    |

**Why the change?** The heuristic approach had a "spike bug" where unconditional exit segments could conflict with the computed path, creating visual artifacts. The visibility graph approach eliminates this by making exit/approach constraints part of the graph structure.

---

## Appendix B: Visual Examples

### Example 1: Auto-routed Forward Connection

```
┌────────┐           ┌────────┐
│ Source ●───────────│────────│
└────────┘     │     │ Target │
               └─────│────────│──●
                     └────────┘
```

### Example 2: Auto-routed Backwards Connection

```
┌────────┐     ┌────────┐
│ Target │     │ Source │
│        ●←─┐  │        │●
└────────┘  │  └────────┘│
            └────────────┘
```

### Example 3: Avoiding Intermediate Block

```
Source●──────┐
             │  ┌────────┐
             │  │Block A │
             └──│────────│──┐
                └────────┘  │
                            ●Target
```
