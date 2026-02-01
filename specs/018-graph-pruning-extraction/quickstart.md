<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Graph-Based Subsystem Extraction

**Feature**: 018-graph-pruning-extraction
**Created**: 2026-02-01

## Test Scenarios

### Scenario 1: Single Block Extraction (US1 - P1)

**Setup**: Minimal diagram demonstrating the current bug

```python
import lynx
import control as ct

# Create diagram: u → gain(K=2) → [signal_x] → plant(1/s) → y
#                                                   ↓
#                                        feedback_loop (unrelated)
diagram = lynx.Diagram()

diagram.add_block("io_marker", "input", marker_type="input", label="u",
                 position={"x": 0, "y": 0})
diagram.add_block("gain", "controller", K=2.0, label="controller",
                 position={"x": 100, "y": 0})
diagram.add_block("transfer_function", "plant",
                 num=[1.0], den=[1.0, 0.0], label="plant",
                 position={"x": 200, "y": 0})
diagram.add_block("io_marker", "output", marker_type="output", label="y",
                 position={"x": 300, "y": 0})

# Unrelated feedback block downstream
diagram.add_block("gain", "feedback_gain", K=0.5, label="feedback",
                 position={"x": 250, "y": 100})

diagram.add_connection("c1", "input", "out", "controller", "in")
diagram.add_connection("c2", "controller", "out", "plant", "in", label="signal_x")
diagram.add_connection("c3", "plant", "out", "output", "in")
diagram.add_connection("c4", "plant", "out", "feedback_gain", "in")  # Downstream feedback
diagram.add_connection("c5", "feedback_gain", "out", "plant", "in")  # Creates coupling
```

**Expected Behavior (BEFORE fix)**:
```python
tf = diagram.get_tf("signal_x", "y")
# INCORRECT: Returns 2nd-order system due to plant + feedback_gain coupling
# Order: 2 (should be 1)
```

**Expected Behavior (AFTER fix)**:
```python
tf = diagram.get_tf("signal_x", "y")
# CORRECT: Returns 1st-order system (just the plant: 1/s)
# Order: 1
# Verifiable: ct.minreal(tf) matches ct.tf([1.0], [1.0, 0.0])
```

**Acceptance Criteria**:
- Extracted TF order is 1 (matches isolated plant)
- DC gain is infinite (integrator pole at origin)
- State count is 1 (no coupling from feedback_gain)

---

### Scenario 2: Internal Feedback Preservation (US2 - P2)

**Setup**: Inner loop with external cascade

```python
diagram = lynx.Diagram()

# External cascade controller
diagram.add_block("io_marker", "ext_input", marker_type="input", label="r",
                 position={"x": 0, "y": 0})
diagram.add_block("gain", "outer_controller", K=3.0, label="outer",
                 position={"x": 50, "y": 0})

# Inner loop (controller + plant with feedback)
diagram.add_block("sum", "inner_sum", signs=["+", "-", "|"], label="error_sum",
                 position={"x": 150, "y": 0})
diagram.add_block("gain", "inner_controller", K=5.0, label="inner_ctrl",
                 position={"x": 250, "y": 0})
diagram.add_block("transfer_function", "inner_plant",
                 num=[1.0], den=[1.0, 2.0], label="inner_plant",
                 position={"x": 350, "y": 0})

diagram.add_block("io_marker", "output", marker_type="output", label="y",
                 position={"x": 450, "y": 0})

# Connections
diagram.add_connection("c1", "ext_input", "out", "outer_controller", "in")
diagram.add_connection("c2", "outer_controller", "out", "inner_sum", "in1", label="inner_ref")
diagram.add_connection("c3", "inner_sum", "out", "inner_controller", "in")
diagram.add_connection("c4", "inner_controller", "out", "inner_plant", "in")
diagram.add_connection("c5", "inner_plant", "out", "output", "in")
diagram.add_connection("c6", "inner_plant", "out", "inner_sum", "in2")  # Inner feedback
```

**Expected Behavior (AFTER fix)**:
```python
# Extract just the inner loop
tf_inner = diagram.get_tf("inner_ref", "y")

# Should include: inner_sum, inner_controller, inner_plant, and feedback c6
# Should exclude: outer_controller (upstream of extraction boundary)
# Closed-loop TF: (5) / (s + 2 + 5) = 5 / (s + 7)

tf_expected = ct.tf([5.0], [1.0, 7.0])
assert ct.minreal(tf_inner) == tf_expected
```

**Acceptance Criteria**:
- Extracted TF includes inner loop blocks and their feedback connection
- Extracted TF excludes outer_controller (upstream)
- State count is 1 (closed-loop inner system)
- DC gain is 5/7

---

### Scenario 3: Parallel Paths (US3 - P3)

**Setup**: Feedforward + feedback paths

```python
diagram = lynx.Diagram()

diagram.add_block("io_marker", "input", marker_type="input", label="u",
                 position={"x": 0, "y": 0})
diagram.add_block("sum", "sum1", signs=["+", "+", "|"], label="combiner",
                 position={"x": 100, "y": 0})

# Feedforward path
diagram.add_block("gain", "ff_gain", K=1.0, label="feedforward",
                 position={"x": 50, "y": -50})

# Feedback path
diagram.add_block("gain", "fb_gain", K=0.5, label="feedback",
                 position={"x": 50, "y": 50})

diagram.add_block("io_marker", "output", marker_type="output", label="y",
                 position={"x": 200, "y": 0})

# Unrelated side branch
diagram.add_block("gain", "side_branch", K=0.1, label="unrelated",
                 position={"x": 150, "y": 100})

# Connections
diagram.add_connection("c1", "input", "out", "ff_gain", "in")
diagram.add_connection("c2", "input", "out", "fb_gain", "in")
diagram.add_connection("c3", "ff_gain", "out", "sum1", "in1")
diagram.add_connection("c4", "fb_gain", "out", "sum1", "in2")
diagram.add_connection("c5", "sum1", "out", "output", "in")
diagram.add_connection("c6", "sum1", "out", "side_branch", "in")  # Not on path
```

**Expected Behavior (AFTER fix)**:
```python
tf = diagram.get_tf("u", "y")

# Should include: ff_gain, fb_gain, sum1 (all on parallel paths)
# Should exclude: side_branch (downstream, not on path)
# DC gain: 1.0 + 0.5 = 1.5

assert ct.dcgain(tf) == 1.5
```

**Acceptance Criteria**:
- Both parallel paths included in extraction
- Side branch excluded
- DC gain is 1.5 (sum of path gains)

---

## Edge Cases

### Edge Case 1: Same Block Extraction

```python
# Extract from controller input to controller output
tf = diagram.get_tf("controller_in", "controller_out")
# Should return just the controller's TF
```

### Edge Case 2: No Path Exists

```python
# Try to extract between disconnected blocks
try:
    tf = diagram.get_tf("isolated_input", "unrelated_output")
except lynx.SignalNotFoundError as e:
    assert "No path exists" in str(e)
```

### Edge Case 3: Algebraic Loop (if encountered)

```python
# Diagram validation should catch this before extraction
diagram = create_algebraic_loop_diagram()
try:
    tf = diagram.get_tf("u", "y")
except lynx.ValidationError as e:
    assert "algebraic loop" in str(e).lower()
```

---

## Performance Benchmarks

```python
import time

# Test extraction time for various diagram sizes
for num_blocks in [10, 20, 50, 100]:
    diagram = create_cascaded_diagram(num_blocks)

    start = time.perf_counter()
    tf = diagram.get_tf("input_signal", "output_signal")
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"{num_blocks} blocks: {elapsed_ms:.1f}ms")
    assert elapsed_ms < 500  # SC-002: <500ms for 50 blocks

# Expected results (after optimization):
# 10 blocks: <50ms
# 20 blocks: <100ms
# 50 blocks: <250ms
# 100 blocks: <800ms
```

---

## Validation

All scenarios above should be implemented as pytest test cases following TDD:

1. Write failing test for Scenario 1 (single block extraction)
2. Implement minimal graph pruning to pass
3. Write failing test for Scenario 2 (internal feedback)
4. Extend pruning to handle feedback preservation
5. Write failing test for Scenario 3 (parallel paths)
6. Verify bidirectional reachability captures all paths
7. Add edge case tests

**Test file locations**:
- Unit tests: `tests/python/unit/test_graph_pruning.py`
- Integration tests: `tests/python/integration/test_pruned_extraction.py`
