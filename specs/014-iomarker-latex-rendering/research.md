<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: IOMarker LaTeX Rendering

**Feature**: 014-iomarker-latex-rendering
**Date**: 2026-01-17
**Purpose**: Resolve technical unknowns and document design decisions

## Research Questions

### RQ-001: Automatic Index Renumbering Algorithm

**Question**: What algorithm should be used for Simulink-style automatic renumbering when indices change?

**Decision**: Sequential shift algorithm with separate passes for upward and downward shifts

**Rationale**:
- **Downward shift** (change index N → M where M < N): Start from M and shift all markers in range [M, N-1] up by 1
- **Upward shift** (change index N → M where M > N): Start from N+1 and shift all markers in range [N+1, M] down by 1
- **Deletion** (delete index N): Shift all markers with index > N down by 1
- **Addition**: Assign index = max(existing_indices) + 1, or 0 if no markers exist

**Example - Downward shift**:
```
Before: [0: A, 1: B, 2: C]
Change C (index 2) → 0
After:  [0: C, 1: A, 2: B]

Algorithm:
1. Remove C from index 2
2. Shift A: 0→1, B: 1→2 (ascending order to avoid collisions)
3. Insert C at index 0
```

**Example - Deletion**:
```
Before: [0: A, 1: B, 2: C, 3: D]
Delete B (index 1)
After:  [0: A, 1: C, 2: D]

Algorithm:
1. Delete B
2. Decrement indices: C: 2→1, D: 3→2
```

**Alternatives Considered**:
- In-place swaps: More complex, harder to test, risk of collisions
- Rebuild from scratch: O(N log N) instead of O(N), unnecessary overhead
- Deferred renumbering: Violates real-time update requirement

**Implementation Notes**:
- Use Python sorted() with key=lambda to ensure deterministic shift order
- TypeScript updates via optimistic UI (immediate local update, sync to Python afterward)
- No race conditions - renumbering is synchronous operation in Diagram class

---

### RQ-002: Backward Compatibility Strategy

**Question**: How should diagrams with IOMarkers lacking the `index` parameter be handled on load?

**Decision**: Auto-assign indices on first access using block ID alphabetical order

**Rationale**:
- **Clarification answer**: Block ID alphabetical order (deterministic, reproducible)
- **Lazy assignment**: Indices assigned when diagram is loaded/accessed, not retroactively modified in storage
- **Persistence**: Once assigned, indices persist in subsequent saves

**Algorithm**:
```python
def _ensure_indices(diagram, marker_type):
    """Assign missing indices for markers of given type."""
    markers = [b for b in diagram.blocks.values()
               if b.block_type == 'io_marker'
               and b.get_parameter('marker_type').value == marker_type
               and b.get_parameter('index') is None]

    # Sort by block ID alphabetically
    markers.sort(key=lambda b: b.id)

    # Assign indices 0, 1, 2, ...
    for i, marker in enumerate(markers):
        marker.add_parameter('index', i)
```

**Alternatives Considered**:
- File order: Not deterministic (JSON dict ordering varies)
- Creation timestamp: Not available in existing diagrams
- Canvas position: Too fragile (positions change during editing)

**Migration Path**:
- No explicit migration script needed
- Diagrams load correctly on first access
- Save operation persists indices to JSON
- Users see no disruption

---

### RQ-003: LaTeX Default Rendering for Indices

**Question**: How should numeric indices (0, 1, 2, ...) be rendered in LaTeX?

**Decision**: Plain numeric strings passed directly to LaTeXRenderer (e.g., "0", "1", "2")

**Rationale**:
- **Simplicity**: No need for LaTeX math mode ($0$, $1$, etc.) - KaTeX handles plain numbers
- **Consistency**: Matches how other blocks render simple numeric values
- **Auto-scaling**: LaTeXRenderer already handles font sizing and scaling

**Rendering Code**:
```typescript
// IOMarkerBlock.tsx
const displayContent = useCustomLatex && customLatex
  ? customLatex
  : String(index); // "0", "1", "2", ...

<LaTeXRenderer latex={displayContent} />
```

**Alternatives Considered**:
- Math mode wrappers ($0$): Unnecessary complexity, no visual benefit
- Custom font styling: Breaks consistency with other blocks
- SVG text rendering: Reinvents LaTeXRenderer, violates reuse principle

---

### RQ-004: Parameter Panel Layout

**Question**: What is the optimal layout for IOMarker parameter panel with new fields?

**Decision**: Three-section vertical layout matching existing block patterns

**Layout**:
```
┌─────────────────────────────────────┐
│ [✓] Render custom block contents   │ ← Checkbox (top section)
│                                     │
│ Custom LaTeX Expression             │ ← Textarea (conditionally visible)
│ ┌─────────────────────────────────┐ │
│ │ r                               │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤ ← Divider
│ Label                               │ ← Text input (middle section)
│ ┌─────────────────────────────────┐ │
│ │ reference                       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Index                               │ ← Number input (bottom section)
│ ┌─────────────────────────────────┐ │
│ │ 0                               │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Rationale**:
- **Top section**: Custom LaTeX (matches Gain/TransferFunction/StateSpace pattern)
- **Middle section**: Label for python-control export (existing, preserved)
- **Bottom section**: Index for manual control (new, advanced feature)
- **Type field removed**: Visually obvious from port orientation (FR-004)

**Alternatives Considered**:
- Index before Label: Less logical (index is derived, label is user-specified)
- Horizontal layout: Wastes space, harder to scan vertically
- Tabs/accordion: Over-engineered for 3 simple fields

---

### RQ-005: Frontend-Backend Index Synchronization

**Question**: How should index changes propagate between TypeScript frontend and Python backend?

**Decision**: Optimistic UI updates with immediate backend sync via `updateBlockParameter` action

**Flow**:
```
1. User changes index in parameter panel
   ↓
2. Frontend updates local React state immediately (optimistic)
   ↓
3. Frontend sends updateBlockParameter('index', newValue) to Python
   ↓
4. Python Diagram.update_block_parameter() executes renumbering
   ↓
5. Python sends full block state update back to frontend
   ↓
6. Frontend reconciles (replace optimistic state with Python truth)
```

**Implementation**:
```typescript
// IOMarkerParameterEditor.tsx
const handleIndexChange = (newIndex: number) => {
  setIndexValue(newIndex); // Optimistic
  onUpdate(block.id, 'index', newIndex); // Sync to Python
};
```

```python
# diagram.py
def update_block_parameter(self, block_id, param_name, value):
    block = self.blocks[block_id]
    block.update_parameter(param_name, value)

    # Trigger automatic renumbering if index changed
    if param_name == 'index' and block.block_type == 'io_marker':
        self._renumber_markers(block)
```

**Rationale**:
- **Responsive UX**: Immediate visual feedback (no waiting for Python round-trip)
- **Consistency**: Backend is source of truth, handles complex renumbering logic
- **Error resilience**: If renumbering fails, backend state overwrites optimistic update

**Alternatives Considered**:
- Synchronous blocking: Poor UX (100-200ms latency)
- Frontend-only renumbering: Violates separation of concerns, duplicates logic
- Debounced updates: Adds complexity, violates immediate renumbering requirement

---

## Best Practices

### BP-001: LaTeX Error Handling

**Practice**: Display "Invalid LaTeX" placeholder without crashing (FR-014, FR-017)

**Existing Implementation** (from GainBlock):
```typescript
// LaTeXRenderer.tsx (existing)
try {
  katex.render(latex, container, options);
} catch (error) {
  container.textContent = "Invalid LaTeX";
}
```

**Application to IOMarker**: No changes needed - reuse existing LaTeXRenderer component

---

### BP-002: Empty LaTeX Graceful Degradation

**Practice**: Show index when custom LaTeX checkbox enabled but field empty (FR-008)

**Clarification answer**: Display index (same as unchecked)

**Implementation**:
```typescript
const displayContent = (useCustomLatex && customLatex.trim())
  ? customLatex
  : String(index);
```

**Rationale**: Prevents blank blocks, maintains visual continuity

---

### BP-003: Test Coverage for Renumbering Edge Cases

**Practice**: Comprehensive pytest tests for renumbering algorithm

**Critical Test Cases**:
1. Downward shift with 3+ markers
2. Upward shift with 3+ markers
3. Delete from middle of sequence
4. Delete first/last marker
5. Add to empty diagram
6. Add to diagram with existing markers
7. Invalid indices (negative, non-integer, out-of-range)
8. Concurrent operations (rapid add/delete)
9. Mixed Input/Output markers (independent sequences)
10. Large diagrams (50+ markers, performance check)

**Test Structure**:
```python
def test_renumber_downward_shift():
    """Test shifting marker to lower index triggers upward cascade."""
    diagram = Diagram()
    diagram.add_block('io_marker', 'in0', marker_type='input')  # index 0
    diagram.add_block('io_marker', 'in1', marker_type='input')  # index 1
    diagram.add_block('io_marker', 'in2', marker_type='input')  # index 2

    # Change in2 from index 2 → 0
    diagram.update_block_parameter('in2', 'index', 0)

    # Assert: in2=0, in0=1, in1=2
    assert diagram.blocks['in2'].get_parameter('index').value == 0
    assert diagram.blocks['in0'].get_parameter('index').value == 1
    assert diagram.blocks['in1'].get_parameter('index').value == 2
```

---

## Technology Decisions Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Index rendering | LaTeXRenderer (existing) | Reuse, consistency, auto-scaling |
| Custom LaTeX hook | useCustomLatex (existing) | Proven pattern from other blocks |
| Renumbering logic | Python Diagram class | Backend source of truth, testable |
| Frontend sync | Optimistic UI updates | Responsive UX, eventual consistency |
| Index assignment | Block ID alphabetical sort | Deterministic, backward compatible |
| Test framework | pytest (backend), Vitest (frontend) | Existing infrastructure, TDD support |

---

## Open Implementation Questions

**None** - All technical unknowns resolved via research and clarifications.

---

## Next Steps

Proceed to **Phase 1: Design & Contracts** to generate:
1. data-model.md (IOMarker entity schema)
2. quickstart.md (test scenarios for TDD)
3. Update agent context files
