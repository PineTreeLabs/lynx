<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Graph-Based Subsystem Extraction

**Feature**: 018-graph-pruning-extraction
**Created**: 2026-02-01

## Overview

This feature operates on in-memory Diagram objects and does not introduce persistent data structures. The entities below represent transient computational structures used during extraction.

## Entities

### ConnectionGraph

**Purpose**: Directed graph representation of diagram topology for analysis

**Attributes**:
- `nodes`: Set of block IDs (str) representing graph vertices
- `forward_edges`: Dict[str, List[str]] - adjacency list for forward traversal (block_id → [connected_block_ids])
- `backward_edges`: Dict[str, List[str]] - reverse adjacency list for backward traversal

**Relationships**:
- Built from Diagram.blocks and Diagram.connections
- Used by path finding algorithms
- Discarded after pruning completes

**Validation Rules**:
- Every edge (connection) must reference valid nodes (blocks)
- Graph may contain cycles (feedback loops are valid)
- Nodes and edges derived from validated Diagram (no independent validation needed)

**Lifecycle**: Created → used for reachability analysis → discarded

---

### ReachabilityResult

**Purpose**: Container for bidirectional reachability analysis output

**Attributes**:
- `forward_reachable`: Set[str] - block IDs reachable forward from source
- `backward_reachable`: Set[str] - block IDs reachable backward from destination
- `path_blocks`: Set[str] - intersection of forward and backward reachable sets
- `source_block_id`: str - ID of block outputting source signal
- `dest_block_id`: str - ID of block outputting destination signal

**Relationships**:
- Produced by `_find_reachable_blocks()` function
- Consumed by `_prune_diagram()` function
- References block IDs from original Diagram

**Validation Rules**:
- `source_block_id` MUST be in `forward_reachable`
- `dest_block_id` MUST be in `backward_reachable`
- `path_blocks` MUST be non-empty (otherwise no valid path exists)
- `path_blocks` MUST contain both source and destination block IDs

**State Transitions**:
1. Initial: Empty sets
2. Forward DFS: Populates `forward_reachable`
3. Backward DFS: Populates `backward_reachable`
4. Intersection: Computes `path_blocks`

---

### PrunedDiagram

**Purpose**: Modified clone of original Diagram with only relevant blocks for extraction

**Attributes**:
- Inherits all attributes from `Diagram` class
- `blocks`: Subset of original blocks (only those in `path_blocks`)
- `connections`: Subset of original connections (only those between kept blocks)

**Relationships**:
- Cloned from original Diagram via `diagram._clone()`
- Blocks removed using `diagram.remove_block(block_id)`
- Passed to existing `_prepare_for_extraction()` for interconnect building

**Validation Rules**:
- Must contain at least source and destination blocks
- All connections must reference existing blocks (auto-enforced by remove_block)
- Must pass existing diagram validation (InputMarker, OutputMarker, connectivity)

**Lifecycle**:
1. Clone original Diagram
2. Remove blocks not in `path_blocks`
3. Pass to interconnect builder
4. Discarded after extraction completes

---

## Data Flow

```
Original Diagram
    ↓
Signal Resolution (existing)
    ↓
Build ConnectionGraph
    ↓
Bidirectional DFS
    ↓
ReachabilityResult
    ↓
Clone & Prune → PrunedDiagram
    ↓
Interconnect Building (existing)
    ↓
Extracted Transfer Function
```

## Notes

- No persistent storage required
- All entities are transient (lifetime ~10-500ms during extraction)
- Graph structures use native Python collections (set, dict, list)
- No external graph library dependencies (NetworkX not needed)
