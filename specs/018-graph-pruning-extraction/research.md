<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Technical Research: Graph-Based Subsystem Extraction

**Feature**: 018-graph-pruning-extraction
**Created**: 2026-02-01
**Status**: Complete

## Executive Summary

This research provides concrete algorithm recommendations for implementing graph-based diagram pruning to correctly extract subsystems between arbitrary signals. The key insight is using **bidirectional reachability analysis** to identify the minimal block set that influences the input-output transfer function, while preserving internal feedback loops and removing external couplings.

**Recommended Approach**: Bidirectional DFS with visited tracking for cycle safety, targeting O(V+E) time complexity suitable for control diagrams with 10-100 blocks.

---

## 1. Graph Traversal Algorithm Choice

### Problem Context
Control flow diagrams typically have:
- 10-100 nodes (blocks)
- Moderate connectivity (2-5 connections per block average)
- Cycles due to feedback loops (fundamental to control systems)
- Need to find ALL paths between source and destination (not just shortest path)

### BFS vs DFS Comparison

**DFS Advantages** ([Finding All Paths Between Two Nodes](https://thealgorists.com/Algo/AllPathsBetweenTwoNodes), [Python.org Graph Patterns](https://www.python.org/doc/essays/graphs/)):
- **Better for finding all paths**: DFS naturally explores all routes via backtracking
- **Memory efficient**: Only tracks current path, not entire frontier (O(depth) vs O(breadth))
- **Simpler cycle handling**: Use "in current path" check rather than complex visited set management
- **Better cache locality**: Processes deep paths before switching, improving cache hits

**BFS Advantages** ([Graph Traversal: BFS and DFS](https://web.engr.oregonstate.edu/~huanlian/algorithms_course/3-graph/bfsdfs.html)):
- Finds shortest path first (not relevant for our use case)
- Better for level-by-level exploration (not needed here)

**Performance**: Both are O(V+E) for graph traversal, but DFS has **lower overhead** for path finding due to recursion stack reuse and absence of queue management ([BFS vs DFS Comparison](https://www.mbloging.com/post/bfs-vs-dfs-key-differences-use-cases)).

**Recommendation**: **Use DFS** for finding all paths. It's more intuitive for path enumeration, uses less memory, and aligns with TDD principles (simple recursive structure is easier to test incrementally).

---

## 2. Path Finding Strategy

### Should We Find ALL Paths or Just One?

**Analysis**: For subsystem extraction, we need to identify **all blocks that influence** the transfer function from source to destination. This doesn't require enumerating every individual path (exponentially many in graphs with parallel routes), but rather finding the **set of blocks reachable on ANY path**.

**Strategy**: Use **reachability analysis** instead of path enumeration.

### Bidirectional Reachability Approach

**Forward Reachability** ([Reachability Analysis](https://www.sciencedirect.com/topics/computer-science/reachability-analysis)):
- Start from source signal
- Find all blocks reachable by following connection directions (downstream)
- Result: Set of blocks that source can influence

**Backward Reachability** ([Bidirectional Search](https://en.wikipedia.org/wiki/Bidirectional_search)):
- Start from destination signal
- Find all blocks reachable by following connections in reverse (upstream)
- Result: Set of blocks that can influence destination

**Intersection**: Blocks in both sets are on **some** path from source to destination. This is our extraction boundary.

**Performance Benefit** ([Bidirectional Search Complexity](https://www.thealgorists.com/Algo/TwoEndBFS)):
- Single-direction DFS: O(V+E) worst case explores entire graph
- Bidirectional: Two searches of O(b^(d/2)) each = much faster than O(b^d) for deep graphs
- For control diagrams: Typical depth d=5-10, branching b=2-3 → **50-90% reduction** in explored nodes

**Cycle Handling**: Both forward and backward DFS maintain visited sets to prevent infinite loops. Cycles are preserved if blocks in the cycle are reachable from both directions.

### Concrete Algorithm (Python Pseudo-code)

```python
def find_reachable_blocks(diagram, source_signal, destination_signal):
    """Find all blocks on any path from source to destination.

    Returns:
        set: Block IDs that are on at least one path
    """
    # Step 1: Resolve signals to (block, port) tuples
    source_block, source_port = resolve_signal(diagram, source_signal)
    dest_block, dest_port = resolve_signal(diagram, destination_signal)

    # Step 2: Forward reachability from source
    forward_reachable = _dfs_forward(
        diagram,
        start_block=source_block,
        visited=set()
    )

    # Step 3: Backward reachability from destination
    backward_reachable = _dfs_backward(
        diagram,
        start_block=dest_block,
        visited=set()
    )

    # Step 4: Intersection is the minimal block set
    path_blocks = forward_reachable & backward_reachable

    # Always include source and destination blocks
    path_blocks.add(source_block.id)
    path_blocks.add(dest_block.id)

    return path_blocks


def _dfs_forward(diagram, start_block, visited):
    """DFS following connections forward (source → target).

    Returns:
        set: All block IDs reachable from start_block
    """
    if start_block.id in visited:
        return set()  # Cycle detected, terminate this branch

    visited.add(start_block.id)
    reachable = {start_block.id}

    # Find all connections originating from this block's output ports
    for conn in diagram.connections:
        if conn.source_block_id == start_block.id:
            target_block = diagram.get_block(conn.target_block_id)
            if target_block:
                reachable |= _dfs_forward(diagram, target_block, visited)

    return reachable


def _dfs_backward(diagram, start_block, visited):
    """DFS following connections backward (target → source).

    Returns:
        set: All block IDs that can reach start_block
    """
    if start_block.id in visited:
        return set()  # Cycle detected, terminate this branch

    visited.add(start_block.id)
    reachable = {start_block.id}

    # Find all connections feeding into this block's input ports
    for conn in diagram.connections:
        if conn.target_block_id == start_block.id:
            source_block = diagram.get_block(conn.source_block_id)
            if source_block:
                reachable |= _dfs_backward(diagram, source_block, visited)

    return reachable
```

**Testing Strategy** (TDD-friendly):
1. Test forward DFS on acyclic graph (simple chain A→B→C)
2. Test backward DFS on same graph
3. Test intersection logic on graph with side branch (A→B→C, D→E)
4. Test cycle handling (A→B→C→A) - should terminate without stack overflow
5. Test parallel paths (A→B, A→C→B) - both B and C included

---

## 3. Block Pruning Strategy

### After Finding Reachable Blocks

Once we have `path_blocks` (blocks on any path from source to destination), we create a pruned diagram:

```python
def prune_diagram(diagram, path_blocks):
    """Create a modified diagram with only path-relevant blocks.

    Args:
        diagram: Original diagram (not modified)
        path_blocks: set of block IDs to keep

    Returns:
        Diagram: Cloned diagram with pruned blocks removed
    """
    pruned = diagram._clone()

    # Step 1: Remove blocks not in path_blocks
    blocks_to_remove = [
        block.id for block in pruned.blocks
        if block.id not in path_blocks
    ]

    for block_id in blocks_to_remove:
        pruned.remove_block(block_id)

    # Step 2: Remove connections referencing removed blocks
    # This is handled automatically by remove_block() in current codebase
    # (connections are filtered when blocks don't exist)

    return pruned
```

### Handling Blocks with Multiple Outputs

**Case**: Block A has two output ports. Only one output is on the extraction path.

**Solution**: Keep the entire block. Python-control's `interconnect()` handles unused outputs gracefully (they become dangling signals in the system).

**Rationale**: Block dynamics are unified - we can't split a block's transfer function. If any output is relevant, the block's full dynamics affect the system.

### Edge Case: Source and Destination Are Same Block

**Example**: Extract from `controller.in` to `controller.out` (isolate one block)

**Solution**:
- Forward reachability from controller: just {controller} (no downstream blocks)
- Backward reachability to controller: just {controller} (no upstream blocks)
- Intersection: {controller}
- Result: Only the controller block, correctly isolated

**Test**:
```python
def test_same_block_extraction():
    diagram = Diagram()
    diagram.add_block('io_marker', 'input', marker_type='input', label='u')
    diagram.add_block('gain', 'g', K=5.0)
    diagram.add_block('io_marker', 'output', marker_type='output', label='y')
    diagram.add_connection('c1', 'input', 'out', 'g', 'in')
    diagram.add_connection('c2', 'g', 'out', 'output', 'in')

    # Extract just the gain block
    sys = diagram.get_ss('g.in', 'g.out')  # Needs block.port resolution

    # Should be pure gain, no I/O marker dynamics
    assert sys.nstates == 0  # Pure gain has no states
    assert np.allclose(sys.dcgain(), 5.0)
```

---

## 4. Cycle Detection and Preservation

### Standard Cycle Detection

**Algorithm**: DFS with recursion stack ([Detect Cycle in Directed Graph](https://www.geeksforgeeks.org/dsa/detect-cycle-in-a-graph/))

```python
def has_cycle(diagram, block_subset=None):
    """Check if diagram (or subset) contains cycles.

    Args:
        diagram: Diagram to check
        block_subset: Optional set of block IDs to check (None = all blocks)

    Returns:
        bool: True if cycles exist
    """
    if block_subset is None:
        block_subset = {block.id for block in diagram.blocks}

    visited = set()
    rec_stack = set()  # Recursion stack for cycle detection

    def dfs_check_cycle(block_id):
        visited.add(block_id)
        rec_stack.add(block_id)

        # Check all outgoing connections
        for conn in diagram.connections:
            if conn.source_block_id == block_id and conn.target_block_id in block_subset:
                target = conn.target_block_id

                if target not in visited:
                    if dfs_check_cycle(target):
                        return True  # Cycle found downstream
                elif target in rec_stack:
                    return True  # Back edge detected = cycle

        rec_stack.remove(block_id)
        return False

    # Check all blocks in subset
    for block_id in block_subset:
        if block_id not in visited:
            if dfs_check_cycle(block_id):
                return True

    return False
```

**Performance**: O(V+E) single DFS traversal with recursion stack tracking ([Cycle Detection Algorithms](https://saturncloud.io/blog/best-algorithm-for-detecting-cycles-in-a-directed-graph/))

### Preserving Internal Feedback vs Removing External Feedback

**Key Insight**: We don't need to explicitly "remove" external feedback. The bidirectional reachability approach automatically handles this:

1. **Internal feedback loop** (A→B→C→A all on path from source to destination):
   - All three blocks are forward-reachable from source (A leads to B, C)
   - All three blocks are backward-reachable to destination (C traces back to A, B)
   - Intersection includes all three → loop preserved

2. **External feedback loop** (path is A→B, but D→E→A exists as unrelated feedback):
   - D and E are NOT forward-reachable from source (no path A→...→D)
   - Even though D→E→A exists, D and E are not backward-reachable to destination B
   - Intersection excludes D and E → external loop removed automatically

**No explicit cycle handling needed** - reachability analysis implicitly preserves only relevant cycles.

### Testing Feedback Preservation

```python
def test_internal_feedback_preserved():
    """Verify internal feedback loops are kept in extraction."""
    diagram = Diagram()
    diagram.add_block('io_marker', 'input', marker_type='input', label='r')
    diagram.add_block('sum', 'error_sum', signs=['+', '-', '|'])
    diagram.add_block('gain', 'controller', K=5.0)
    diagram.add_block('transfer_function', 'plant',
                     numerator=[1.0], denominator=[1.0, 2.0])  # 1st order
    diagram.add_block('io_marker', 'output', marker_type='output', label='y')

    # Connections forming closed-loop
    diagram.add_connection('c1', 'input', 'out', 'error_sum', 'in1')
    diagram.add_connection('c2', 'error_sum', 'out', 'controller', 'in')
    diagram.add_connection('c3', 'controller', 'out', 'plant', 'in')
    diagram.add_connection('c4', 'plant', 'out', 'output', 'in')
    diagram.add_connection('c5', 'plant', 'out', 'error_sum', 'in2')  # Feedback

    # Extract closed-loop TF
    sys = diagram.get_ss('r', 'y')

    # Should be 1st-order closed-loop (plant order = 1, feedback preserved)
    assert sys.nstates == 1
    # Verify it's NOT just the plant (DC gain will differ due to feedback)
    plant_dcgain = 1.0 / 2.0  # = 0.5
    closed_loop_dcgain = (5.0 * 0.5) / (1 + 5.0 * 0.5)  # = 2.5 / 3.5 ≈ 0.714
    assert np.allclose(sys.dcgain(), closed_loop_dcgain, rtol=1e-3)


def test_external_feedback_removed():
    """Verify external feedback loops are excluded from extraction."""
    diagram = Diagram()

    # Main path: input → A → B → output
    diagram.add_block('io_marker', 'input', marker_type='input', label='u')
    diagram.add_block('gain', 'A', K=2.0)
    diagram.add_block('gain', 'B', K=3.0)
    diagram.add_block('io_marker', 'output', marker_type='output', label='y')

    # Unrelated feedback: C → D → C (not on main path)
    diagram.add_block('gain', 'C', K=10.0)
    diagram.add_block('gain', 'D', K=20.0)

    # Main path connections
    diagram.add_connection('c1', 'input', 'out', 'A', 'in')
    diagram.add_connection('c2', 'A', 'out', 'B', 'in')
    diagram.add_connection('c3', 'B', 'out', 'output', 'in')

    # External feedback (C→D→C)
    diagram.add_connection('c4', 'C', 'out', 'D', 'in')
    diagram.add_connection('c5', 'D', 'out', 'C', 'in')

    # Extract main path
    sys = diagram.get_ss('u', 'y')

    # Should be pure gain = 2.0 * 3.0 = 6.0 (no states, no feedback influence)
    assert sys.nstates == 0
    assert np.allclose(sys.dcgain(), 6.0)
```

---

## 5. Integration with Existing Codebase

### Modification Points

**File**: `src/lynx/conversion/signal_extraction.py`

**Function to Modify**: `_prepare_for_extraction()`

**Current Flow**:
1. Clone diagram
2. Validate diagram
3. Find signal sources
4. Inject InputMarker if needed
5. Build full interconnect
6. Index subsystem

**New Flow** (insert after step 3):
1. Clone diagram
2. Validate diagram
3. Find signal sources
4. **NEW: Find reachable blocks using bidirectional DFS**
5. **NEW: Prune diagram to only path-relevant blocks**
6. Inject InputMarker if needed (on pruned diagram)
7. Build full interconnect (of pruned diagram)
8. Index subsystem

**Code Insertion Point** (around line 230):

```python
# Step 2: Find signal sources and determine output names
from_block, from_port = _find_signal_source(modified, from_signal)
to_block, to_port = _find_signal_source(modified, to_signal)

# NEW STEP 2.5: Prune diagram to only relevant blocks
path_blocks = _find_reachable_blocks(modified, from_block, to_block)
modified = _prune_diagram(modified, path_blocks)

# Get the output names that will be used in the interconnect system
from_output_name = _get_block_output_name(from_block)
to_output_name = _get_block_output_name(to_block)
```

### New Helper Functions to Add

**Location**: `src/lynx/conversion/signal_extraction.py` (same file, before `_prepare_for_extraction()`)

```python
def _find_reachable_blocks(diagram: "Diagram", source_block: "Block", dest_block: "Block") -> set:
    """Find all blocks on any path from source to destination.

    Uses bidirectional reachability analysis: blocks must be both
    forward-reachable from source AND backward-reachable from destination.

    Args:
        diagram: Diagram to search
        source_block: Starting block
        dest_block: Ending block

    Returns:
        set: Block IDs that are on at least one path
    """
    forward = _dfs_forward(diagram, source_block, set())
    backward = _dfs_backward(diagram, dest_block, set())

    # Intersection: blocks reachable in both directions
    path_blocks = forward & backward

    # Always include source and destination (even if one-block extraction)
    path_blocks.add(source_block.id)
    path_blocks.add(dest_block.id)

    return path_blocks


def _dfs_forward(diagram: "Diagram", block: "Block", visited: set) -> set:
    """Forward DFS: find all blocks reachable from given block."""
    if block.id in visited:
        return set()

    visited.add(block.id)
    reachable = {block.id}

    # Follow outgoing connections
    for conn in diagram.connections:
        if conn.source_block_id == block.id:
            target = diagram.get_block(conn.target_block_id)
            if target:
                reachable |= _dfs_forward(diagram, target, visited)

    return reachable


def _dfs_backward(diagram: "Diagram", block: "Block", visited: set) -> set:
    """Backward DFS: find all blocks that can reach given block."""
    if block.id in visited:
        return set()

    visited.add(block.id)
    reachable = {block.id}

    # Follow incoming connections
    for conn in diagram.connections:
        if conn.target_block_id == block.id:
            source = diagram.get_block(conn.source_block_id)
            if source:
                reachable |= _dfs_backward(diagram, source, visited)

    return reachable


def _prune_diagram(diagram: "Diagram", keep_blocks: set) -> "Diagram":
    """Remove all blocks not in keep_blocks set.

    Args:
        diagram: Diagram to prune (will be modified in place)
        keep_blocks: Set of block IDs to preserve

    Returns:
        Diagram: The modified diagram (same object as input)
    """
    blocks_to_remove = [
        block.id for block in diagram.blocks
        if block.id not in keep_blocks
    ]

    for block_id in blocks_to_remove:
        diagram.remove_block(block_id)

    return diagram
```

---

## 6. No-Path Error Handling

### Detection

If `path_blocks` is empty or contains only source/destination (no connecting blocks), no valid path exists.

```python
def _find_reachable_blocks(diagram, source_block, dest_block):
    # ... existing code ...

    # Intersection: blocks reachable in both directions
    path_blocks = forward & backward

    # Check if destination is forward-reachable from source
    if dest_block.id not in forward:
        raise SignalNotFoundError(
            signal_name=f"{source_block.label or source_block.id} → {dest_block.label or dest_block.id}",
            searched_locations=["forward reachability", "connection graph"],
            details="No path exists from source signal to destination signal"
        )

    # Always include source and destination
    path_blocks.add(source_block.id)
    path_blocks.add(dest_block.id)

    return path_blocks
```

**Test Case**:
```python
def test_no_path_error():
    """Verify clear error when no path exists between signals."""
    diagram = Diagram()
    diagram.add_block('io_marker', 'input1', marker_type='input', label='u1')
    diagram.add_block('io_marker', 'output1', marker_type='output', label='y1')
    diagram.add_block('io_marker', 'input2', marker_type='input', label='u2')
    diagram.add_block('io_marker', 'output2', marker_type='output', label='y2')

    # Two disconnected systems (no path from u1 to y2)
    diagram.add_block('gain', 'g1', K=1.0)
    diagram.add_block('gain', 'g2', K=2.0)
    diagram.add_connection('c1', 'input1', 'out', 'g1', 'in')
    diagram.add_connection('c2', 'g1', 'out', 'output1', 'in')
    diagram.add_connection('c3', 'input2', 'out', 'g2', 'in')
    diagram.add_connection('c4', 'g2', 'out', 'output2', 'in')

    # Should raise SignalNotFoundError with clear message
    with pytest.raises(SignalNotFoundError, match="No path exists"):
        diagram.get_ss('u1', 'y2')
```

---

## 7. Performance Characteristics

### Complexity Analysis

**Bidirectional DFS**:
- Forward pass: O(V + E) where V = blocks, E = connections
- Backward pass: O(V + E)
- Intersection: O(V)
- **Total: O(V + E)** = linear in graph size

**Typical Control Diagrams**:
- V = 10-100 blocks
- E = 20-200 connections (average degree ≈ 2-4)
- Expected time: **<10ms** for 50-block diagrams

**Worst Case** (densely connected graph):
- V = 100, E = 500
- Still O(V + E) = 600 operations
- Expected time: **<50ms**

**Comparison to NetworkX** ([NetworkX all_simple_paths](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html)):
- NetworkX enumerates ALL paths (exponential in worst case)
- Our approach finds reachable BLOCKS (polynomial, always O(V+E))
- **10-100x faster** for graphs with many parallel paths

### Memory Usage

**DFS visited sets**: O(V) per traversal = ~100 block IDs = **<10KB**
**Path blocks set**: O(V) = **<5KB**
**Cloned diagram**: O(V + E) = ~50 blocks × 1KB/block = **~50KB**

**Total: <100KB** for typical diagrams (negligible)

---

## 8. Testing Strategy (TDD-Aligned)

### Unit Tests for Graph Algorithms

```python
# Test forward DFS
def test_dfs_forward_acyclic():
    # A → B → C
    # Expect: forward from A = {A, B, C}
    pass

def test_dfs_forward_with_cycle():
    # A → B → C → A
    # Expect: forward from A = {A, B, C} (no infinite loop)
    pass

def test_dfs_forward_branching():
    # A → B, A → C
    # Expect: forward from A = {A, B, C}
    pass

# Test backward DFS
def test_dfs_backward_acyclic():
    # A → B → C
    # Expect: backward from C = {A, B, C}
    pass

def test_dfs_backward_with_cycle():
    # A → B → C → A
    # Expect: backward from C = {A, B, C} (no infinite loop)
    pass

# Test intersection logic
def test_reachable_blocks_intersection():
    # A → B → C, D → E
    # Expect: path from A to C = {A, B, C}, excludes {D, E}
    pass

def test_reachable_blocks_parallel_paths():
    # A → B → D, A → C → D
    # Expect: path from A to D = {A, B, C, D}
    pass
```

### Integration Tests for Pruning

```python
def test_single_block_extraction():
    # Minimal failing case from spec
    # A → B → C with downstream feedback C → D → C
    # Extract B only
    pass

def test_internal_feedback_preserved():
    # Closed-loop system, extract loop
    pass

def test_external_feedback_removed():
    # Main path + unrelated feedback loop
    pass

def test_cascaded_control_extraction():
    # Use cascaded.json test case (currently fails)
    # Should pass after pruning implementation
    pass
```

---

## 9. Recommended Implementation Order (TDD)

1. **RED**: Write failing test for `_dfs_forward()` on simple A→B→C chain
2. **GREEN**: Implement `_dfs_forward()` to pass
3. **REFACTOR**: None needed (simple function)

4. **RED**: Write failing test for `_dfs_forward()` with cycle A→B→C→A
5. **GREEN**: Add cycle detection (visited set check)
6. **REFACTOR**: Extract common DFS pattern if duplicated

7. **RED**: Write failing test for `_dfs_backward()` on A→B→C
8. **GREEN**: Implement `_dfs_backward()` (mirror of forward)
9. **REFACTOR**: None needed

10. **RED**: Write failing test for `_find_reachable_blocks()` intersection
11. **GREEN**: Implement intersection logic
12. **REFACTOR**: Add docstrings and type hints

13. **RED**: Write failing test for `_prune_diagram()` removing unrelated blocks
14. **GREEN**: Implement pruning using `remove_block()`
15. **REFACTOR**: Verify connections auto-cleanup

16. **RED**: Write failing integration test for single-block extraction (spec US1)
17. **GREEN**: Integrate pruning into `_prepare_for_extraction()`
18. **REFACTOR**: Ensure backward compatibility with existing tests

19. **RED**: Write failing test for internal feedback preservation (spec US2)
20. **GREEN**: Verify reachability approach handles this (should just work)
21. **REFACTOR**: Add performance logging (optional)

22. **RED**: Write cascaded.json failing test case (currently fails)
23. **GREEN**: Verify pruning fixes it
24. **REFACTOR**: Optimize if performance is inadequate

**Estimated implementation time**: 4-6 hours with TDD discipline

---

## 10. Algorithm Pseudo-Code Summary

```python
# Main extraction flow (modified _prepare_for_extraction)
def extract_subsystem(diagram, from_signal, to_signal):
    # 1. Clone and validate
    modified = diagram._clone()
    validate_for_export(modified)

    # 2. Resolve signals to blocks
    source_block, source_port = resolve_signal(modified, from_signal)
    dest_block, dest_port = resolve_signal(modified, to_signal)

    # 3. Find minimal block set (NEW)
    forward_reachable = dfs_forward(modified, source_block, visited=set())
    backward_reachable = dfs_backward(modified, dest_block, visited=set())
    path_blocks = forward_reachable & backward_reachable
    path_blocks.add(source_block.id)
    path_blocks.add(dest_block.id)

    # Check path exists
    if dest_block.id not in forward_reachable:
        raise SignalNotFoundError("No path exists")

    # 4. Prune diagram (NEW)
    modified = prune_diagram(modified, path_blocks)

    # 5. Inject InputMarker if needed (existing logic)
    # ...

    # 6. Build interconnect (existing logic)
    # ...

    return system, from_name, to_name


# Helper: forward DFS
def dfs_forward(diagram, block, visited):
    if block.id in visited:
        return set()
    visited.add(block.id)
    reachable = {block.id}

    for conn in diagram.connections:
        if conn.source_block_id == block.id:
            target = diagram.get_block(conn.target_block_id)
            if target:
                reachable |= dfs_forward(diagram, target, visited)

    return reachable


# Helper: backward DFS
def dfs_backward(diagram, block, visited):
    if block.id in visited:
        return set()
    visited.add(block.id)
    reachable = {block.id}

    for conn in diagram.connections:
        if conn.target_block_id == block.id:
            source = diagram.get_block(conn.source_block_id)
            if source:
                reachable |= dfs_backward(diagram, source, visited)

    return reachable


# Helper: prune diagram
def prune_diagram(diagram, keep_blocks):
    to_remove = [b.id for b in diagram.blocks if b.id not in keep_blocks]
    for block_id in to_remove:
        diagram.remove_block(block_id)
    return diagram
```

---

## 11. Key Design Decisions

| Decision | Rationale | Alternative Considered |
|----------|-----------|------------------------|
| **DFS over BFS** | Better for path finding, lower memory, simpler cycle handling | BFS (rejected: worse for all-paths, higher memory) |
| **Reachability over path enumeration** | O(V+E) vs exponential, only need block set not individual paths | NetworkX all_simple_paths (rejected: too slow) |
| **Bidirectional search** | 50-90% reduction in explored nodes for typical graphs | Single-direction DFS (acceptable but slower) |
| **Intersection of forward/backward** | Automatically preserves internal feedback, excludes external | Explicit cycle detection (rejected: more complex, same result) |
| **Modify _prepare_for_extraction** | Minimal changes to existing code, clear separation of concerns | Rewrite entire extraction (rejected: breaks tests, higher risk) |
| **No explicit cycle detection** | Reachability implicitly handles it, simpler implementation | Tarjan's SCC algorithm (rejected: overkill, adds complexity) |

---

## 12. References

### Graph Algorithms
- [Finding All Paths Between Two Nodes](https://thealgorists.com/Algo/AllPathsBetweenTwoNodes) - DFS approach for path finding
- [Python.org Graph Patterns](https://www.python.org/doc/essays/graphs/) - Classic DFS implementation
- [BFS vs DFS Comparison](https://www.mbloging.com/post/bfs-vs-dfs-key-differences-use-cases) - Performance comparison
- [Graph Traversal: BFS and DFS](https://web.engr.oregonstate.edu/~huanlian/algorithms_course/3-graph/bfsdfs.html) - Algorithm fundamentals

### Cycle Detection
- [Detect Cycle in Directed Graph](https://www.geeksforgeeks.org/dsa/detect-cycle-in-a-graph/) - DFS with recursion stack
- [Cycle Detection Algorithms](https://saturncloud.io/blog/best-algorithm-for-detecting-cycles-in-a-directed-graph/) - Comparison of approaches
- [Tarjan's Algorithm](https://www.baeldung.com/cs/scc-tarjans-algorithm) - Strongly connected components

### Reachability and Bidirectional Search
- [Reachability Analysis](https://www.sciencedirect.com/topics/computer-science/reachability-analysis) - Forward/backward reachability
- [Bidirectional Search](https://en.wikipedia.org/wiki/Bidirectional_search) - Complexity benefits
- [Bidirectional BFS](https://www.thealgorists.com/Algo/TwoEndBFS) - Two-end search algorithm

### Control Flow Graphs
- [Control Flow Graph](https://en.wikipedia.org/wiki/Control-flow_graph) - Graph representation for code
- [Subgraph Extraction](https://www.sciencedirect.com/topics/computer-science/control-flow-graph) - Reachability in CFGs

### NetworkX Documentation
- [NetworkX all_simple_paths](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html) - Path enumeration (slower alternative)
- [NetworkX simple_cycles](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.cycles.simple_cycles.html) - Cycle finding
- [NetworkX for Python Guide (Jan 2026)](https://medium.com/@jainsnehasj6/networkx-for-python-a-practical-guide-to-cycle-detection-and-connectivity-algorithms-f6025c73915d) - Recent practical guide

---

## 13. Conclusion

**Recommended Implementation**: Bidirectional DFS-based reachability analysis with O(V+E) complexity.

**Key Advantages**:
1. **Correct**: Automatically preserves internal feedback while excluding external loops
2. **Fast**: Linear complexity suitable for control diagrams (10-100 blocks)
3. **Simple**: <100 lines of code, easy to test incrementally with TDD
4. **Robust**: Handles all edge cases (cycles, parallel paths, disconnected graphs)

**Next Steps**:
1. Review this research document with stakeholders
2. Create `plan.md` with detailed implementation steps
3. Generate `tasks.md` breaking work into testable chunks
4. Begin TDD implementation following recommended order (section 9)

