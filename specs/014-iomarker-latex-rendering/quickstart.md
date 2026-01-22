<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: IOMarker LaTeX Rendering

**Feature**: 014-iomarker-latex-rendering
**Date**: 2026-01-17
**Purpose**: Test scenarios and validation workflows for TDD implementation

## Test Scenario Categories

1. **Automatic Index Display** (User Story 1 - P1)
2. **Custom LaTeX Override** (User Story 2 - P2)
3. **Manual Index Control with Automatic Renumbering** (User Story 3 - P3)
4. **Backward Compatibility** (Edge Cases)
5. **Performance & Scale** (Success Criteria)

---

## TS-001: Automatic Index Display

### TS-001.1: Create Multiple Input Markers

**Objective**: Verify automatic index assignment for new InputMarkers

**Test Steps**:
1. Create empty diagram
2. Add InputMarker with id="in0"
3. Add InputMarker with id="in1"
4. Add InputMarker with id="in2"

**Expected Results**:
- `in0` has index=0, displays "0"
- `in1` has index=1, displays "1"
- `in2` has index=2, displays "2"
- All rendered via LaTeXRenderer component

**Assertions** (pytest):
```python
def test_auto_index_assignment_inputs():
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')
    diagram.add_block('io_marker', 'in2', marker_type='input')

    assert diagram.blocks['in0'].get_parameter('index').value == 0
    assert diagram.blocks['in1'].get_parameter('index').value == 1
    assert diagram.blocks['in2'].get_parameter('index').value == 2
```

**Assertions** (Vitest):
```typescript
test('InputMarkers display auto-assigned indices', () => {
  const blocks = [
    { id: 'in0', parameters: [{ name: 'index', value: 0 }] },
    { id: 'in1', parameters: [{ name: 'index', value: 1 }] },
    { id: 'in2', parameters: [{ name: 'index', value: 2 }] },
  ];

  blocks.forEach((block, i) => {
    const { getByText } = render(<IOMarkerBlock data={block} />);
    expect(getByText(String(i))).toBeInTheDocument();
  });
});
```

---

### TS-001.2: Independent Input/Output Sequences

**Objective**: Verify InputMarker and OutputMarker indices are independent

**Test Steps**:
1. Create diagram
2. Add InputMarker "in0", InputMarker "in1"
3. Add OutputMarker "out0", OutputMarker "out1"

**Expected Results**:
- Input markers: in0=0, in1=1
- Output markers: out0=0, out1=1
- Both sequences start at 0 independently

**Assertions**:
```python
def test_independent_index_sequences():
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')
    diagram.add_block('io_marker', 'out0', marker_type='output')
    diagram.add_block('io_marker', 'out1', marker_type='output')

    # Inputs: 0, 1
    assert diagram.blocks['in0'].get_parameter('index').value == 0
    assert diagram.blocks['in1'].get_parameter('index').value == 1

    # Outputs: 0, 1 (independent)
    assert diagram.blocks['out0'].get_parameter('index').value == 0
    assert diagram.blocks['out1'].get_parameter('index').value == 1
```

---

## TS-002: Custom LaTeX Override

### TS-002.1: Enable Custom LaTeX

**Objective**: Verify custom LaTeX overrides default index display

**Test Steps**:
1. Create InputMarker with index=0
2. Enable "Render custom block contents" checkbox
3. Enter LaTeX: `r`
4. Verify block displays "r" instead of "0"

**Expected Results**:
- Block displays "r" (LaTeX rendered)
- Index still stored as 0 in backend
- Custom LaTeX persists on save/reload

**Assertions**:
```typescript
test('Custom LaTeX overrides index display', async () => {
  const block = {
    id: 'in0',
    parameters: [{ name: 'index', value: 0 }],
    custom_latex: 'r',
  };

  const { getByText, queryByText } = render(<IOMarkerBlock data={block} />);

  expect(getByText('r')).toBeInTheDocument();
  expect(queryByText('0')).not.toBeInTheDocument();
});
```

---

### TS-002.2: Invalid LaTeX Handling

**Objective**: Verify graceful degradation for invalid LaTeX

**Test Steps**:
1. Create InputMarker with index=0
2. Enable custom LaTeX
3. Enter invalid LaTeX: `\invalid{syntax`
4. Verify "Invalid LaTeX" placeholder shown

**Expected Results**:
- Block displays "Invalid LaTeX" (error message)
- No crash or blank block
- User can correct LaTeX expression

**Assertions**:
```typescript
test('Invalid LaTeX shows error message', () => {
  const block = {
    id: 'in0',
    parameters: [{ name: 'index', value: 0 }],
    custom_latex: '\\invalid{syntax',
  };

  const { getByText } = render(<IOMarkerBlock data={block} />);
  expect(getByText('Invalid LaTeX')).toBeInTheDocument();
});
```

---

### TS-002.3: Empty LaTeX Graceful Degradation

**Objective**: Verify empty custom LaTeX field shows index (clarification answer)

**Test Steps**:
1. Create InputMarker with index=0
2. Enable "Render custom block contents" checkbox
3. Leave LaTeX field empty
4. Verify block displays "0" (index fallback)

**Expected Results**:
- Block displays "0" (same as unchecked)
- No blank block
- Graceful degradation

**Assertions**:
```typescript
test('Empty custom LaTeX shows index', () => {
  const block = {
    id: 'in0',
    parameters: [{ name: 'index', value: 0 }],
    custom_latex: '',  // Empty string
  };

  const { getByText } = render(<IOMarkerBlock data={block} />);
  expect(getByText('0')).toBeInTheDocument();
});
```

---

## TS-003: Manual Index Control with Automatic Renumbering

### TS-003.1: Downward Shift Renumbering

**Objective**: Verify automatic renumbering when index changed to lower value

**Test Steps**:
1. Create InputMarkers: in0(index=0), in1(index=1), in2(index=2)
2. Change in2's index from 2 → 0
3. Verify automatic renumbering: in2=0, in0=1, in1=2

**Expected Results**:
- in2 takes index 0
- Original in0 shifts to index 1
- Original in1 shifts to index 2
- No validation errors shown

**Assertions**:
```python
def test_downward_shift_renumbering():
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')
    diagram.add_block('io_marker', 'in2', marker_type='input')

    # Initial: in0=0, in1=1, in2=2
    # Change in2: 2 → 0
    diagram.update_block_parameter('in2', 'index', 0)

    # Assert renumbering
    assert diagram.blocks['in2'].get_parameter('index').value == 0
    assert diagram.blocks['in0'].get_parameter('index').value == 1
    assert diagram.blocks['in1'].get_parameter('index').value == 2
```

---

### TS-003.2: Upward Shift Renumbering

**Objective**: Verify automatic renumbering when index changed to higher value

**Test Steps**:
1. Create InputMarkers: in0(index=0), in1(index=1), in2(index=2)
2. Change in0's index from 0 → 2
3. Verify automatic renumbering: in1=0, in2=1, in0=2

**Expected Results**:
- in0 takes index 2
- Original in1 shifts to index 0
- Original in2 shifts to index 1
- No validation errors shown

**Assertions**:
```python
def test_upward_shift_renumbering():
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')
    diagram.add_block('io_marker', 'in2', marker_type='input')

    # Initial: in0=0, in1=1, in2=2
    # Change in0: 0 → 2
    diagram.update_block_parameter('in0', 'index', 2)

    # Assert renumbering
    assert diagram.blocks['in1'].get_parameter('index').value == 0
    assert diagram.blocks['in2'].get_parameter('index').value == 1
    assert diagram.blocks['in0'].get_parameter('index').value == 2
```

---

### TS-003.3: Delete Marker Cascade Renumbering

**Objective**: Verify automatic renumbering when marker deleted

**Test Steps**:
1. Create InputMarkers: in0(0), in1(1), in2(2), in3(3)
2. Delete in1 (index 1)
3. Verify cascade: in0=0, in2=1, in3=2

**Expected Results**:
- in1 removed from diagram
- in2 index decrements 2→1
- in3 index decrements 3→2
- in0 unchanged at 0

**Assertions**:
```python
def test_delete_cascade_renumbering():
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')
    diagram.add_block('io_marker', 'in2', marker_type='input')
    diagram.add_block('io_marker', 'in3', marker_type='input')

    # Delete in1 (index 1)
    diagram.delete_block('in1')

    # Assert cascade
    assert diagram.blocks['in0'].get_parameter('index').value == 0
    assert diagram.blocks['in2'].get_parameter('index').value == 1
    assert diagram.blocks['in3'].get_parameter('index').value == 2
    assert 'in1' not in diagram.blocks
```

---

### TS-003.4: Out-of-Range Index Clamping

**Objective**: Verify out-of-range manual index is clamped to valid range

**Test Steps**:
1. Create InputMarkers: in0(0), in1(1)
2. Try to set in0's index to 10 (out of range)
3. Verify clamped to max valid index (1) and renumbering triggered

**Expected Results**:
- in0 clamped to index 1
- in1 shifted to index 0
- No crash or invalid state

**Assertions**:
```python
def test_out_of_range_index_clamping():
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')

    # Try to set in0 to index 10 (out of range, max valid is 1)
    diagram.update_block_parameter('in0', 'index', 10)

    # Assert clamped and renumbered
    assert diagram.blocks['in0'].get_parameter('index').value == 1
    assert diagram.blocks['in1'].get_parameter('index').value == 0
```

---

### TS-003.5: Negative Index Handling

**Objective**: Verify negative index treated as 0 and triggers renumbering

**Test Steps**:
1. Create InputMarkers: in0(0), in1(1)
2. Try to set in1's index to -5
3. Verify treated as 0 and renumbering triggered

**Expected Results**:
- in1 index set to 0 (negative clamped)
- in0 shifted to index 1
- No crash

**Assertions**:
```python
def test_negative_index_handling():
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')

    # Set in1 to -5 (invalid, should become 0)
    diagram.update_block_parameter('in1', 'index', -5)

    # Assert clamped to 0 and renumbered
    assert diagram.blocks['in1'].get_parameter('index').value == 0
    assert diagram.blocks['in0'].get_parameter('index').value == 1
```

---

## TS-004: Backward Compatibility

### TS-004.1: Load Legacy Diagram (No Index Parameter)

**Objective**: Verify legacy diagrams load and auto-assign indices

**Test Steps**:
1. Create JSON diagram with 3 IOMarkers (no `index` parameter)
2. Block IDs: "ref", "dist", "actuator" (alphabetical: actuator, dist, ref)
3. Load diagram
4. Verify indices auto-assigned: actuator=0, dist=1, ref=2

**Expected Results**:
- Diagram loads without errors
- Indices assigned alphabetically by block ID
- Next save persists indices to JSON

**Test Data** (JSON):
```json
{
  "blocks": [
    {
      "id": "ref",
      "block_type": "io_marker",
      "parameters": [
        {"name": "marker_type", "value": "input"},
        {"name": "label", "value": "r"}
      ]
    },
    {
      "id": "dist",
      "block_type": "io_marker",
      "parameters": [
        {"name": "marker_type", "value": "input"},
        {"name": "label", "value": "d"}
      ]
    },
    {
      "id": "actuator",
      "block_type": "io_marker",
      "parameters": [
        {"name": "marker_type", "value": "input"},
        {"name": "label", "value": "u"}
      ]
    }
  ]
}
```

**Assertions**:
```python
def test_legacy_diagram_auto_index_assignment():
    # Load diagram from JSON (no indices)
    diagram = Diagram.from_json(legacy_json)

    # Indices assigned alphabetically by block ID
    assert diagram.blocks['actuator'].get_parameter('index').value == 0
    assert diagram.blocks['dist'].get_parameter('index').value == 1
    assert diagram.blocks['ref'].get_parameter('index').value == 2
```

---

### TS-004.2: Save Legacy Diagram Persists Indices

**Objective**: Verify saved diagram includes assigned indices

**Test Steps**:
1. Load legacy diagram (no indices)
2. Access diagram (triggers auto-assignment)
3. Save diagram to JSON
4. Verify saved JSON includes `index` parameters

**Expected Results**:
- Saved JSON contains `{"name": "index", "value": N}` for each IOMarker
- Future loads don't need re-assignment
- Backward compatible (old Lynx versions ignore index)

**Assertions**:
```python
def test_save_persists_indices():
    diagram = Diagram.from_json(legacy_json)
    diagram.blocks['ref']  # Access triggers auto-assignment

    saved_json = diagram.to_json()

    # Assert indices present in saved JSON
    for block in saved_json['blocks']:
        if block['block_type'] == 'io_marker':
            index_param = next(p for p in block['parameters'] if p['name'] == 'index')
            assert index_param is not None
            assert isinstance(index_param['value'], int)
```

---

## TS-005: Performance & Scale

### TS-005.1: LaTeX Rendering Performance (50 blocks)

**Objective**: Verify LaTeX rendering meets <50ms per block target

**Test Steps**:
1. Create diagram with 50 IOMarkers (25 inputs, 25 outputs)
2. Each has custom LaTeX (e.g., `x_0`, `x_1`, ..., `x_{24}`)
3. Measure rendering time for all blocks

**Expected Results**:
- Average rendering time <50ms per block
- Total time <2.5 seconds for 50 blocks
- No visual lag or jank

**Assertions** (Vitest performance test):
```typescript
test('LaTeX rendering performance for 50 blocks', async () => {
  const blocks = Array.from({ length: 50 }, (_, i) => ({
    id: `marker_${i}`,
    parameters: [{ name: 'index', value: i }],
    custom_latex: `x_{${i}}`,
  }));

  const start = performance.now();

  blocks.forEach(block => {
    render(<IOMarkerBlock data={block} />);
  });

  const elapsed = performance.now() - start;
  const avgPerBlock = elapsed / blocks.length;

  expect(avgPerBlock).toBeLessThan(50); // <50ms per block
});
```

---

### TS-005.2: Index Renumbering Performance (100 markers)

**Objective**: Verify renumbering meets <20ms target for large diagrams

**Test Steps**:
1. Create diagram with 100 InputMarkers
2. Change marker at index 50 to index 0 (downward shift)
3. Measure renumbering time

**Expected Results**:
- Renumbering completes in <20ms
- All 50 affected markers updated correctly
- No UI blocking or lag

**Assertions**:
```python
import time

def test_renumbering_performance_large_diagram():
    diagram = Diagram()

    # Create 100 InputMarkers
    for i in range(100):
        diagram.add_block('io_marker', f'in{i}', marker_type='input')

    # Measure downward shift renumbering
    start = time.perf_counter()
    diagram.update_block_parameter('in50', 'index', 0)
    elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

    assert elapsed < 20  # <20ms target
    assert diagram.blocks['in50'].get_parameter('index').value == 0
```

---

## TS-006: Integration Tests

### TS-006.1: Full Workflow (Create → Edit → Save → Load)

**Objective**: End-to-end test of complete user workflow

**Test Steps**:
1. Create diagram with 3 InputMarkers
2. Enable custom LaTeX on marker 0: `r`
3. Manually change marker 2 index to 0
4. Save diagram to JSON
5. Reload diagram from JSON
6. Verify all state preserved

**Expected Results**:
- Indices renumbered correctly after manual change
- Custom LaTeX persists across save/load
- Renumbered indices persist correctly
- No data loss

**Assertions**:
```python
def test_full_workflow_create_edit_save_load():
    # Create
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')
    diagram.add_block('io_marker', 'in1', marker_type='input')
    diagram.add_block('io_marker', 'in2', marker_type='input')

    # Edit: Add custom LaTeX to in0
    diagram.blocks['in0'].custom_latex = 'r'

    # Edit: Change in2 index to 0 (triggers renumbering)
    diagram.update_block_parameter('in2', 'index', 0)

    # Save
    json_data = diagram.to_json()

    # Load
    diagram2 = Diagram.from_json(json_data)

    # Verify indices
    assert diagram2.blocks['in2'].get_parameter('index').value == 0
    assert diagram2.blocks['in0'].get_parameter('index').value == 1
    assert diagram2.blocks['in1'].get_parameter('index').value == 2

    # Verify custom LaTeX
    assert diagram2.blocks['in0'].custom_latex == 'r'
```

---

## Test Execution Order (TDD)

### Phase 1: Backend (Python) - RED Phase

1. TS-001.1: Auto index assignment
2. TS-001.2: Independent sequences
3. TS-003.1: Downward shift
4. TS-003.2: Upward shift
5. TS-003.3: Delete cascade
6. TS-003.4: Out-of-range clamping
7. TS-003.5: Negative index handling
8. TS-004.1: Legacy diagram load
9. TS-004.2: Save persists indices
10. TS-005.2: Renumbering performance

**All tests must FAIL before implementation begins**

### Phase 2: Backend (Python) - GREEN Phase

Implement renumbering logic in `diagram.py` and `io_marker.py` to make tests pass

### Phase 3: Frontend (TypeScript) - RED Phase

1. TS-001.1: Display indices
2. TS-002.1: Custom LaTeX override
3. TS-002.2: Invalid LaTeX handling
4. TS-002.3: Empty LaTeX graceful degradation
5. TS-005.1: LaTeX rendering performance

**All tests must FAIL before implementation begins**

### Phase 4: Frontend (TypeScript) - GREEN Phase

Implement IOMarkerBlock.tsx and IOMarkerParameterEditor.tsx changes

### Phase 5: Integration - REFACTOR Phase

1. TS-006.1: Full workflow integration test
2. Code review and refactoring
3. Performance optimization if needed

---

## Validation Checklist

After all tests pass:

- [ ] All 16 test scenarios pass (10 backend, 6 frontend)
- [ ] Code coverage ≥80% for modified files
- [ ] Performance targets met (<50ms LaTeX, <20ms renumbering)
- [ ] Backward compatibility verified (legacy diagrams load correctly)
- [ ] No regression in existing block functionality
- [ ] Documentation updated (CLAUDE.md, Active Technologies section)

---

## Next Steps

Use these test scenarios to drive TDD implementation in `/speckit.tasks`
