<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Diagram Label Indexing

**Feature Branch**: `017-diagram-label-indexing`
**Date**: 2026-01-24
**Phase**: 1 (Design)

## Overview

This quickstart demonstrates how to use dictionary-style label indexing to access blocks in a Lynx diagram. After implementing this feature, engineers can retrieve blocks using readable labels instead of tracking block IDs.

---

## Scenario 1: Basic Label Indexing (US1-P1)

**User Story**: Access blocks by their meaningful labels for more readable code

**Setup**:
```python
from lynx import Diagram

# Create a simple feedback control system
diagram = Diagram()
diagram.add_block('io_marker', 'r_marker', marker_type='input', label='r')
diagram.add_block('sum', 'error', signs=['+', '-', '|'])
diagram.add_block('gain', 'controller_gain', K=5.0, label='controller')
diagram.add_block('transfer_function', 'plant_tf',
                 numerator=[2.0], denominator=[1.0, 3.0, 2.0],
                 label='plant')
diagram.add_block('io_marker', 'y_marker', marker_type='output', label='y')

# Add connections
diagram.add_connection('c1', 'r_marker', 'out', 'error', 'in1')
diagram.add_connection('c2', 'error', 'out', 'controller_gain', 'in')
diagram.add_connection('c3', 'controller_gain', 'out', 'plant_tf', 'in')
diagram.add_connection('c4', 'plant_tf', 'out', 'y_marker', 'in')
diagram.add_connection('c5', 'plant_tf', 'out', 'error', 'in2')  # Feedback
```

**Test: Access blocks by label**
```python
# Old way (using block IDs)
controller = diagram.blocks['controller_gain']
plant = diagram.blocks['plant_tf']

# New way (using labels)
controller = diagram["controller"]
plant = diagram["plant"]

# Verify correct blocks retrieved
assert controller.K == 5.0
assert plant.numerator == [2.0]
assert plant.denominator == [1.0, 3.0, 2.0]
```

**Expected Result**: ✅ Blocks retrieved successfully, code is more readable

**Success Criteria**: SC-001 satisfied (1-line access with bracket notation)

---

## Scenario 2: Error Handling - Missing Label (US1-P1)

**User Story**: Helpful error messages when label doesn't exist

**Setup**: Use diagram from Scenario 1

**Test: Attempt to access non-existent label**
```python
try:
    sensor = diagram["sensor"]
    assert False, "Should have raised KeyError"
except KeyError as e:
    # Verify error message includes the label
    assert "sensor" in str(e)
    print(f"Error: {e}")
    # Output: KeyError: No block found with label: 'sensor'
```

**Expected Result**: ✅ KeyError raised with label name in message

**Success Criteria**: SC-003 satisfied (100% of KeyErrors include requested label)

---

## Scenario 3: Error Handling - Duplicate Labels (US2-P2)

**User Story**: Detect and report ambiguous label access attempts

**Setup**:
```python
from lynx import Diagram
from lynx.diagram import ValidationError

# Create diagram with duplicate labels
diagram = Diagram()
diagram.add_block('gain', 'gain1', K=1.0, label='sensor')
diagram.add_block('gain', 'gain2', K=2.0, label='sensor')
diagram.add_block('gain', 'gain3', K=3.0, label='sensor')
diagram.add_block('gain', 'gain4', K=4.0, label='controller')  # Unique label
```

**Test: Attempt to access duplicate label**
```python
# Unique label works fine
controller = diagram["controller"]
assert controller.K == 4.0

# Duplicate label raises ValidationError
try:
    sensor = diagram["sensor"]
    assert False, "Should have raised ValidationError"
except ValidationError as e:
    # Verify error message includes count and block IDs
    error_msg = str(e)
    assert "sensor" in error_msg
    assert "3 blocks" in error_msg
    assert "gain1" in error_msg
    assert "gain2" in error_msg
    assert "gain3" in error_msg
    print(f"Error: {e}")
    # Output: ValidationError: Label 'sensor' appears on 3 blocks: ['gain1', 'gain2', 'gain3']
```

**Expected Result**: ✅ ValidationError raised with count and block IDs

**Success Criteria**: SC-002 satisfied (explicit error with actionable information)

---

## Scenario 4: Type Safety - Non-String Keys (Edge Case)

**User Story**: Clear error messages for type mismatches

**Setup**: Use diagram from Scenario 1

**Test: Attempt to index with non-string keys**
```python
# Integer key
try:
    block = diagram[123]
    assert False, "Should have raised TypeError"
except TypeError as e:
    assert "string" in str(e).lower()
    assert "int" in str(e).lower()
    print(f"Error: {e}")
    # Output: TypeError: Label must be a string, got int

# None key
try:
    block = diagram[None]
    assert False, "Should have raised TypeError"
except TypeError as e:
    assert "string" in str(e).lower()
    assert "NoneType" in str(e).lower()
    print(f"Error: {e}")
    # Output: TypeError: Label must be a string, got NoneType

# Object key
try:
    block = diagram[object()]
    assert False, "Should have raised TypeError"
except TypeError as e:
    assert "string" in str(e).lower()
    assert "object" in str(e).lower()
```

**Expected Result**: ✅ TypeError raised with expected and actual types

**Success Criteria**: FR-002 satisfied (TypeError for non-string keys)

---

## Scenario 5: Unlabeled Blocks (Edge Case)

**User Story**: Unlabeled blocks don't interfere with label indexing

**Setup**:
```python
from lynx import Diagram

diagram = Diagram()
# Blocks without labels
diagram.add_block('gain', 'unlabeled1', K=1.0)  # No label
diagram.add_block('gain', 'unlabeled2', K=2.0, label=None)  # Explicit None
diagram.add_block('gain', 'unlabeled3', K=3.0, label='')  # Empty string

# Block with label
diagram.add_block('gain', 'labeled', K=4.0, label='controller')
```

**Test: Unlabeled blocks are skipped**
```python
# Labeled block works
controller = diagram["controller"]
assert controller.K == 4.0

# Empty string label doesn't match unlabeled blocks
try:
    block = diagram[""]
    assert False, "Should have raised KeyError"
except KeyError as e:
    assert "No block found" in str(e)

# None is not a valid string label (TypeError)
try:
    block = diagram[None]
    assert False, "Should have raised TypeError"
except TypeError as e:
    assert "string" in str(e).lower()
```

**Expected Result**: ✅ Unlabeled blocks skipped, no false matches

**Success Criteria**: FR-006 satisfied (skip blocks with None or empty string labels)

---

## Scenario 6: Integration with Python-Control Export

**User Story**: Combine label indexing with existing diagram analysis workflows

**Setup**: Use diagram from Scenario 1 (feedback control system)

**Test: Modify parameters using label indexing, then export**
```python
import control as ct

# Modify controller gain using label indexing
diagram["controller"].K = 10.0

# Verify change persisted
assert diagram["controller"].K == 10.0

# Export to python-control (existing feature)
sys = diagram.get_ss('r', 'y')

# Analyze closed-loop system
t, y = ct.step_response(sys, T=5.0)

# Verify controller gain affected response
assert y[-1] > 0.8  # Higher gain = better tracking (assuming stable)
```

**Expected Result**: ✅ Label indexing integrates seamlessly with existing API

**Success Criteria**: No breaking changes, backward compatible

---

## Scenario 7: Case Sensitivity and Special Characters (Edge Case)

**User Story**: Label matching follows standard Python string semantics

**Setup**:
```python
from lynx import Diagram

diagram = Diagram()
diagram.add_block('gain', 'g1', K=1.0, label='Plant')  # Capital P
diagram.add_block('gain', 'g2', K=2.0, label='plant')  # Lowercase p
diagram.add_block('gain', 'g3', K=3.0, label='plant-1')  # Hyphen
diagram.add_block('gain', 'g4', K=4.0, label='α_controller')  # Unicode
diagram.add_block('gain', 'g5', K=5.0, label="r'")  # Quote in label
```

**Test: Case-sensitive and special character handling**
```python
# Case-sensitive matching
assert diagram["Plant"].K == 1.0
assert diagram["plant"].K == 2.0

# Special characters work
assert diagram["plant-1"].K == 3.0
assert diagram["α_controller"].K == 4.0
assert diagram["r'"].K == 5.0

# Case mismatch raises KeyError
try:
    block = diagram["PLANT"]  # All caps
    assert False, "Should have raised KeyError"
except KeyError:
    pass  # Expected
```

**Expected Result**: ✅ Case-sensitive matching, special characters supported

**Success Criteria**: FR-003 satisfied (exact case-sensitive match)

---

## Scenario 8: Empty Diagram (Edge Case)

**User Story**: Graceful error handling for empty diagrams

**Setup**:
```python
from lynx import Diagram

diagram = Diagram()  # Empty, no blocks
```

**Test: Index into empty diagram**
```python
try:
    block = diagram["anything"]
    assert False, "Should have raised KeyError"
except KeyError as e:
    assert "anything" in str(e)
    assert "No block found" in str(e)
```

**Expected Result**: ✅ KeyError raised with label name

**Success Criteria**: FR-004 satisfied (KeyError for missing label)

---

## Scenario 9: Natural Parameter Updates (US3-P3)

**User Story**: Update parameters naturally via block objects without accessing IDs

**Setup**: Use diagram from Scenario 1 (feedback control system)

**Test 1: Block.set_parameter() method**
```python
# Retrieve block via label
plant = diagram["plant"]

# Update parameter naturally
plant.set_parameter("K", 10.0)

# Verify update persisted
assert plant.K == 10.0
assert diagram.blocks['plant_tf'].K == 10.0  # Also updated in diagram

# Chained access
diagram["controller"].set_parameter("K", 15.0)
assert diagram["controller"].K == 15.0
```

**Test 2: Enhanced update_block_parameter (accepts Block objects)**
```python
# Via block object
diagram.update_block_parameter(diagram["plant"], "K", 20.0)
assert diagram["plant"].K == 20.0

# Backward compatible (still accepts IDs)
diagram.update_block_parameter("controller_gain", "K", 25.0)
assert diagram["controller"].K == 25.0

# Batch updates
for label in ["plant", "controller"]:
    block = diagram[label]
    diagram.update_block_parameter(block, "K", 1.0)

assert diagram["plant"].K == 1.0
assert diagram["controller"].K == 1.0
```

**Test 3: Orphaned block error handling**
```python
from lynx.blocks.gain import GainBlock

# Block not yet added to diagram
orphan = GainBlock(id="orphan", K=1.0)

try:
    orphan.set_parameter("K", 5.0)
    assert False, "Should have raised RuntimeError"
except RuntimeError as e:
    assert "not attached" in str(e).lower()

# Add to diagram, then works
diagram.add_block('gain', 'orphan_block', K=2.0, label='orphan')
orphan_in_diagram = diagram["orphan"]
orphan_in_diagram.set_parameter("K", 5.0)  # Works now
assert orphan_in_diagram.K == 5.0
```

**Test 4: Deleted diagram error handling**
```python
import weakref

# Create diagram and block
temp_diagram = Diagram()
temp_diagram.add_block('gain', 'temp', K=1.0, label='temp')
temp_block = temp_diagram["temp"]

# Keep reference, delete diagram
weak_ref = weakref.ref(temp_diagram)
del temp_diagram

# Weakref should be dead
assert weak_ref() is None

# Parameter update should fail
try:
    temp_block.set_parameter("K", 5.0)
    assert False, "Should have raised RuntimeError"
except RuntimeError as e:
    assert "deleted" in str(e).lower()
```

**Expected Result**: ✅ All parameter update patterns work correctly, orphaned blocks handled gracefully

**Success Criteria**: SC-005, SC-006, SC-007 satisfied

---

## Performance Validation

**Test**: Verify O(1) practical performance for 1000 blocks

```python
import time
from lynx import Diagram

# Create large diagram
diagram = Diagram()
for i in range(1000):
    diagram.add_block('gain', f'block_{i}', K=float(i), label=f'label_{i}')

# Measure lookup time
start = time.perf_counter()
for _ in range(100):  # 100 iterations
    block = diagram["label_500"]  # Middle of range
end = time.perf_counter()

avg_time_ms = (end - start) / 100 * 1000
print(f"Average lookup time: {avg_time_ms:.3f} ms")

# Verify performance requirement
assert avg_time_ms < 10.0, f"Lookup too slow: {avg_time_ms} ms"
```

**Expected Result**: ✅ Lookup completes in <10ms (well within O(1) for n=1000)

**Success Criteria**: SC-004 satisfied (constant time for up to 1000 blocks)

---

## Summary

All user stories and edge cases covered:
- ✅ **US1-P1**: Basic label indexing works
- ✅ **US2-P2**: Duplicate labels detected and reported
- ✅ **US3-P3**: Natural parameter updates via block objects
- ✅ **Edge Cases**: Type safety, unlabeled blocks, empty diagrams, case sensitivity, special characters, orphaned blocks
- ✅ **Integration**: Works with existing python-control export
- ✅ **Performance**: Meets O(1) practical requirement

**Next Steps**:
1. Write failing tests for each scenario (TDD RED phase)
2. Implement features in priority order:
   - `Diagram.__getitem__` (US1)
   - ValidationError for duplicates (US2)
   - `Block._diagram` weakref + `set_parameter()` (US3)
   - Enhanced `update_block_parameter` (US3)
3. Run tests until green (TDD GREEN phase)
4. Refactor if needed (TDD REFACTOR phase)
