<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Diagram Label Indexing

**Feature Branch**: `017-diagram-label-indexing`
**Date**: 2026-01-24
**Phase**: 1 (Design)

## Overview

This feature extends the existing Diagram class with dictionary-style indexing capability. Reuses existing ValidationError exception for duplicate label detection. No new data structures, exception classes, or schema changes required.

## Entities

### 1. ValidationError (EXISTING - REUSED)

**Type**: Exception class (existing in diagram.py)
**Inherits From**: DiagramExportError
**Purpose**: Raised when diagram validation fails (including duplicate label detection)

**Existing Attributes**:
- message (str): Error message describing the validation failure
- block_id (Optional[str]): Block identifier where error occurred
- port_id (Optional[str]): Port identifier where error occurred

**Usage for Duplicate Labels**:
```python
raise ValidationError(
    f"Label {label!r} appears on {len(block_ids)} blocks: {block_ids}",
    block_id=block_ids[0] if block_ids else None
)
```

**Example**:
```python
>>> raise ValidationError(
...     "Label 'plant' appears on 3 blocks: ['block_1', 'block_2', 'block_3']",
...     block_id='block_1'
... )
ValidationError: Label 'plant' appears on 3 blocks: ['block_1', 'block_2', 'block_3']
```

**Message Format for Duplicate Labels**:
```python
f"Label {label!r} appears on {len(block_ids)} blocks: {block_ids}"
```

**Lifecycle**: Instantiated and raised by Diagram.__getitem__() when duplicate labels detected

---

### 2. Diagram (MODIFIED)

**Type**: Existing class
**Location**: `src/lynx/diagram.py`
**Modifications**: Add `__getitem__` method, enhance `update_block_parameter` method

**New Method: `__getitem__(self, label: str) -> Block`**

**Purpose**: Enable dictionary-style indexing by block label

**Parameters**:
- `label` (str): The label attribute to search for (case-sensitive)

**Returns**:
- `Block`: The unique block with matching label

**Raises**:
- `TypeError`: If label is not a string
- `KeyError`: If no block has the specified label
- `ValidationError`: If multiple blocks have the specified label

**Algorithm**:
```
1. Validate type: if not isinstance(label, str), raise TypeError
2. Build matches: iterate self.blocks, collect (block_id, block) where block.label == label
3. Skip unlabeled: ignore blocks where block.label is None or empty string
4. Check match count:
   - 0 matches: raise KeyError(f"No block found with label: {label!r}")
   - 1 match: return the block
   - 2+ matches: raise ValidationError(message with count and block IDs, block_id=first match)
```

**Performance**:
- Time Complexity: O(n) where n = number of blocks
- Space Complexity: O(k) where k = number of matching blocks (typically 0 or 1)
- Expected latency: <1ms for n ≤ 1000

**State Changes**: None (read-only operation)

**Side Effects**: None (pure function)

---

**Enhanced Method: `update_block_parameter(self, block_or_id: Union[Block, str], param_name: str, value: Any) -> None`**

**Purpose**: Update block parameter with flexible input type (backward compatible enhancement)

**Parameters**:
- `block_or_id` (Union[Block, str]): Block object OR block ID string (previously only str)
- `param_name` (str): Parameter name to update
- `value` (Any): New parameter value

**Returns**: None

**Modification**: Enhanced to accept Block objects in addition to string IDs

**Algorithm**:
```
1. Extract ID: block_id = block_or_id.id if isinstance(block_or_id, Block) else block_or_id
2. [Existing logic unchanged from here]
```

**Performance**: O(1) - adds single isinstance() check (~1ns)

**Backward Compatibility**: 100% - existing code using string IDs works unchanged

**Usage Patterns**:
```python
# Pattern 1: Via block object (new)
diagram.update_block_parameter(diagram["plant"], "K", 5.0)

# Pattern 2: Via string ID (existing, still works)
diagram.update_block_parameter("plant_id", "K", 5.0)
```

---

### 3. Block (MODIFIED)

**Type**: Existing base class
**Location**: `src/lynx/blocks/base.py`
**Modifications**: Add parent reference and set_parameter method

**New Attribute: `_diagram: Optional[weakref.ref]`**

**Purpose**: Maintain weak reference to parent diagram for parameter updates

**Type**: `Optional[weakref.ref['Diagram']]`

**Lifecycle**:
- Set to None on initialization (before add_block)
- Set to weakref(diagram) when added to diagram via add_block()
- Returns None when parent diagram deleted (weakref behavior)
- Excluded from serialization (runtime-only)

---

**New Method: `set_parameter(self, param_name: str, value: Any) -> None`**

**Purpose**: Update block parameter and sync to parent diagram

**Parameters**:
- `param_name` (str): Parameter name to update
- `value` (Any): New parameter value

**Returns**: None

**Raises**:
- `RuntimeError`: If block not attached to diagram (_diagram is None)
- `RuntimeError`: If parent diagram has been deleted (weakref() returns None)
- Propagates exceptions from diagram.update_block_parameter()

**Algorithm**:
```
1. Check if _diagram is None → RuntimeError("Block not attached to diagram")
2. Dereference weakref: diagram = self._diagram()
3. Check if diagram is None → RuntimeError("Parent diagram has been deleted")
4. Delegate: diagram.update_block_parameter(self.id, param_name, value)
```

**Performance**: O(1) - just a delegation call

**State Changes**: None on block itself (delegates to diagram's existing logic)

**Side Effects**: Triggers diagram's parameter sync mechanism (widget updates, port regeneration, etc.)

---

**Existing Attribute: `label: Optional[str]`**

**Notes**:
- label attribute already exists on all block types
- Optional: can be None (unlabeled blocks)
- Mutable: can change via parameter updates
- Persisted: included in JSON serialization

---

## Relationships

```
Diagram (1) --contains--> (*) Block
    |                      |
    |                      +--> _diagram: weakref --> Diagram (weak reference)
    |                      +--> set_parameter() --> delegates to Diagram.update_block_parameter()
    |
    +--> __getitem__(label: str) --> Block (1, if unique)
    |    +--> raises --> TypeError (if label not string)
    |    +--> raises --> KeyError (if label not found)
    |    +--> raises --> ValidationError (if label not unique)
    |
    +--> update_block_parameter(block_or_id: Union[Block, str], ...) --> syncs to widget
         +--> accepts Block objects (new)
         +--> accepts string IDs (existing, backward compatible)

ValidationError --inherits--> DiagramExportError --inherits--> Exception
```

---

## Data Validation Rules

### LabelNotUniqueError Construction
1. `label` must be a non-empty string
2. `block_ids` must be a list with length ≥ 2

### Diagram.__getitem__ Input Validation
1. `label` must be of type `str` (enforced by TypeError)
2. `label` can be empty string (will result in KeyError since unlabeled blocks are skipped)

### Label Matching Rules
1. Match is case-sensitive: "Plant" ≠ "plant"
2. Match is exact: "plant" ≠ "plant " (trailing space)
3. None and empty string are treated as "no label" (skipped)
4. Special characters allowed: "plant-1", "α_controller", "r'" all valid labels

---

## State Transitions

**None** - This is a query operation with no state changes.

The Diagram object state remains unchanged after `__getitem__` call:
- blocks dictionary unchanged
- connections unchanged
- No caching or index updates

---

## Persistence

**No schema changes required**:
- Labels already persist via Block.label attribute in JSON
- LabelNotUniqueError is a runtime exception (not persisted)
- No new fields added to Pydantic schemas

**Backward Compatibility**:
- Existing diagrams without labels continue to work
- `diagram["label"]` will raise KeyError if no blocks have labels
- No migration needed

---

## Error Scenarios

| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Type mismatch | `diagram[123]` | `TypeError: Label must be a string, got int` |
| Type mismatch | `diagram[None]` | `TypeError: Label must be a string, got NoneType` |
| Missing label | `diagram["nonexistent"]` | `KeyError: No block found with label: 'nonexistent'` |
| Empty diagram | `diagram["any"]` | `KeyError: No block found with label: 'any'` |
| Unlabeled block | `diagram[""]` | `KeyError: No block found with label: ''` |
| Duplicate labels | `diagram["plant"]` (2 blocks) | `ValidationError: Label 'plant' appears on 2 blocks: ['block_1', 'block_2']` |
| Unique label | `diagram["controller"]` | Returns Block object with label "controller" |

---

## Testing Strategy

**Unit Tests Required** (TDD approach):

**US1 - Label Indexing:**
1. ✅ TypeError for integer key
2. ✅ TypeError for None key
3. ✅ TypeError for object key
4. ✅ KeyError for missing label
5. ✅ KeyError for empty diagram
6. ✅ KeyError for empty string label
7. ✅ Successful retrieval with unique label
8. ✅ Unlabeled blocks (None) are skipped
9. ✅ Case-sensitive matching ("Plant" vs "plant")
10. ✅ Special characters in labels

**US2 - Duplicate Detection:**
11. ✅ ValidationError for 2 duplicate labels (verify count and IDs)
12. ✅ ValidationError for 3+ duplicate labels
13. ✅ Unique label succeeds when duplicates exist elsewhere

**US3 - Parameter Updates:**
14. ✅ Block.set_parameter() syncs to diagram and widget
15. ✅ RuntimeError when block not attached to diagram
16. ✅ RuntimeError when parent diagram deleted
17. ✅ update_block_parameter accepts Block objects
18. ✅ update_block_parameter still accepts string IDs (backward compat)
19. ✅ Serialization excludes _diagram attribute

**Integration Tests** (optional):
- Label indexing → parameter update → widget sync
- Label indexing after label parameter update
- Combined with python-control export workflow
- Block removal clears parent reference

---

## API Examples

### Basic Usage (US1)
```python
from lynx import Diagram

diagram = Diagram()
diagram.add_block('gain', 'ctrl', K=5.0, label='controller')
diagram.add_block('transfer_function', 'plt',
                 numerator=[1.0], denominator=[1.0, 1.0], label='plant')

# Access by label
controller = diagram["controller"]
plant = diagram["plant"]

print(controller.K)  # 5.0
print(plant.numerator)  # [1.0]
```

### Error Handling (US1, US2)
```python
from lynx.diagram import ValidationError

# Handle missing labels
try:
    block = diagram["nonexistent"]
except KeyError as e:
    print(f"Label not found: {e}")

# Handle duplicate labels
try:
    block = diagram["duplicate"]
except ValidationError as e:
    print(f"Ambiguous label: {e}")
    # Error message includes block IDs for debugging
```

### Type Safety (US1)
```python
# Non-string keys raise TypeError
try:
    block = diagram[123]
except TypeError as e:
    print(e)  # "Label must be a string, got int"
```

### Parameter Updates (US3)
```python
# Natural OOP style using block object
plant = diagram["plant"]
plant.set_parameter("K", 10.0)  # Syncs to diagram and widget

# Chained access
diagram["controller"].set_parameter("K", 5.0)

# Enhanced update_block_parameter (accepts Block objects)
diagram.update_block_parameter(diagram["plant"], "K", 20.0)

# Backward compatible (still accepts IDs)
diagram.update_block_parameter("ctrl", "K", 3.0)

# Batch updates
for label in ["plant", "controller"]:
    block = diagram[label]
    diagram.update_block_parameter(block, "K", 1.0)
```

### Orphaned Block Handling (US3)
```python
from lynx.blocks.gain import GainBlock

# Block not yet added to diagram
orphan = GainBlock(id="orphan", K=1.0)
try:
    orphan.set_parameter("K", 5.0)
except RuntimeError as e:
    print(e)  # "Block not attached to diagram"
```

---

## Open Questions

**None** - All design decisions resolved in research phase.
