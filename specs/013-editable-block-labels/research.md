<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research Notes: Editable Block Labels in Parameter Panel

**Date**: 2026-01-16
**Feature**: 013-editable-block-labels
**Phase**: 0 (Research & Technical Decisions)

## Overview

This document captures technical research and design decisions for adding label editing capability to the Parameter Panel. All unknowns from the Technical Context have been resolved through codebase exploration.

---

## Decision 1: Label Editor Component Placement

**Context**: Where should the label editor appear in the Parameter Panel UI?

**Decision**: Add label editor as first section in the scrollable content area, before block-specific parameter editors.

**Rationale**:
- **User priority**: Block identification (label) is more fundamental than parameter values, so it should appear first
- **Visual hierarchy**: Placing it at the top maintains consistency with the removed "Type:" line location
- **No layout disruption**: Existing scrollable area can accommodate label field with no height increase (SC-005 constraint)
- **Code simplicity**: Parameter Panel already has header (with close button) and scrollable content area - label editor fits naturally in content area

**Alternatives Considered**:
1. **Header placement** (rejected): Header currently has title + close button with tight spacing; adding input would require layout redesign and increase panel height
2. **After parameter editors** (rejected): Label is more important than individual parameters, should not be buried below them
3. **Replace entire header** (rejected): Would lose "Edit Block Parameters" title and close button functionality

**Implementation Notes**:
- Label editor gets its own section with bottom border separator (like custom LaTeX sections in parameter editors)
- Follows existing visual patterns: same input styling as parameter fields
- `mb-3 pb-3 border-b` classes for separation (established pattern in GainParameterEditor)

---

## Decision 2: Label Editor Component Design

**Context**: Should we create a new component or reuse EditableLabel?

**Decision**: Create new `LabelEditor` component, not reuse `EditableLabel`.

**Rationale**:
- **Different interaction model**:
  - EditableLabel: double-click to enter edit mode (optimized for canvas labels)
  - LabelEditor: always editable input field (optimized for form-based editing)
- **Different visual requirements**:
  - EditableLabel: inline display with hover states, dynamic width
  - LabelEditor: standard form input with fixed width, label text above
- **Reuse logic, not UI**: Extract shared behavior via `useBlockLabel` hook (already exists)
- **Code clarity**: Two components with distinct purposes easier to maintain than one component with dual modes

**Alternatives Considered**:
1. **Reuse EditableLabel with mode prop** (rejected): Would add conditional logic and complicate both use cases; violates single responsibility principle
2. **Inline input in ParameterPanel** (rejected): Component extraction enables isolated testing and reuse if needed elsewhere

**Implementation Notes**:
```typescript
// LabelEditor.tsx interface
interface LabelEditorProps {
  blockId: string;
  initialLabel: string;
  onUpdate: (blockId: string, parameterName: string, value: string) => void;
}
```
- Uses `useBlockLabel()` hook for state management and save logic
- Calls `onUpdate(blockId, "label", trimmedValue)` to match ParameterEditorProps pattern
- Text input with Enter/blur/Escape handling (follows GainParameterEditor pattern)

---

## Decision 3: Label Validation and Normalization

**Context**: How should special characters and whitespace be handled?

**Decision**: Normalize whitespace in `LabelEditor`, validate in Python `diagram.update_block_label()`.

**Rationale**:
- **Frontend normalization**: Replace newlines/tabs with spaces, trim leading/trailing whitespace (FR-005, FR-011)
  - User feedback immediate (no round-trip to Python)
  - Consistent with existing parameter input behavior
- **Backend validation**: Empty/whitespace-only labels revert to block ID (FR-006)
  - Python is source of truth for business rules
  - Backend already handles this in `update_block_label()` (lines 938-957)
- **Character handling**: Accept all printable Unicode, strip control characters
  - Modern browsers handle Unicode correctly in text inputs
  - Control character stripping happens in Python via `str.strip()` and whitespace normalization

**Alternatives Considered**:
1. **Client-side validation only** (rejected): Python must enforce business rules for data integrity (direct Python API usage)
2. **Regex-based character filtering** (rejected): Overly restrictive, no user need to limit character sets (labels are for human readability)
3. **Maxlength constraint** (rejected): No spec requirement, no current limit on canvas labels, would add unnecessary constraint

**Implementation Notes**:
```typescript
// Frontend (LabelEditor.tsx)
const normalizeLabel = (value: string): string => {
  return value
    .replace(/[\n\t]/g, ' ')  // Replace newlines/tabs with spaces
    .trim();                   // Trim leading/trailing whitespace
};

const handleSave = () => {
  const normalized = normalizeLabel(labelValue);
  onUpdate(blockId, "label", normalized);
};
```

Python validation (already exists):
```python
# diagram.py (lines 938-957)
def update_block_label(self, block_id: str, label: str) -> bool:
    block = self._blocks.get(block_id)
    if not block:
        return False
    self._save_state()  # Undo support
    block.label = label if label.strip() else block.id  # Empty → ID
    return True
```

---

## Decision 4: Action Type Reuse

**Context**: Should we reuse existing `updateBlockLabel` action or create a new one?

**Decision**: Reuse existing `updateBlockLabel` action (no changes to Python backend).

**Rationale**:
- **Principle I (Simplicity)**: Existing action handles label updates perfectly, creating new action would duplicate functionality
- **Zero backend changes**: `_handle_update_block_label()` in widget.py already does exactly what we need (lines 427-438)
- **Consistent behavior**: Canvas double-click editing and Parameter Panel editing will behave identically (same Python code path)
- **Undo/redo support**: Existing action already integrates with undo system via `diagram._save_state()`

**Alternatives Considered**:
1. **New `updateBlockLabelFromPanel` action** (rejected): Would duplicate `_handle_update_block_label()` code with no benefit
2. **Extend `updateParameter` action** (rejected): Label is NOT a parameter (it's a top-level Block attribute like `custom_latex`), would blur conceptual boundaries

**Implementation Notes**:
```typescript
// LabelEditor.tsx
import { sendAction } from '../../utils/traitletSync';

const handleSave = (newLabel: string) => {
  const normalized = normalizeLabel(newLabel);
  sendAction(model, "updateBlockLabel", {
    blockId: block.id,
    label: normalized
  });
};
```

Backend (no changes):
```python
# widget.py (lines 427-438) - UNCHANGED
def _handle_update_block_label(self, payload: Dict[str, Any]) -> None:
    block_id = payload.get("blockId", "")
    new_label = payload.get("label", "")
    if self.diagram.update_block_label(block_id, new_label):
        self._update_diagram_state()
```

---

## Decision 5: Input Focus and Panel Closure Behavior

**Context**: What happens if user is editing label when Parameter Panel closes?

**Decision**: Allow React cleanup (uncommitted edits lost unless blur fires), document in edge cases.

**Rationale**:
- **Existing pattern**: ParameterPanel uses React lifecycle for cleanup (no special handling for focused inputs)
- **User expectations**: Standard form behavior - closing a form without saving loses uncommitted changes
- **Spec acceptance**: Edge case already documented in spec (line 68) with this behavior
- **Simplicity**: No need for "unsaved changes" warnings or forced blur events
- **Consistency**: Matches parameter editor behavior (K value input has same behavior)

**Alternatives Considered**:
1. **Force blur on panel close** (rejected): Would require onBeforeClose callback pattern, adds complexity for minimal benefit
2. **Warn about unsaved changes** (rejected): Over-engineered for single text field, disrupts UX for rare edge case
3. **Auto-save on keypress** (rejected): Would bypass validation, create excessive Python round-trips

**Implementation Notes**:
- No special handling required in LabelEditor component
- Standard React unmount behavior handles cleanup
- Test coverage: verify label NOT updated if panel closed mid-edit without blur/Enter

---

## Decision 6: Testing Strategy

**Context**: What test coverage is needed for TDD compliance?

**Decision**: Unit tests for LabelEditor component + integration tests for full sync flow + edge case tests in Python.

**Test Coverage Plan**:

### Frontend Unit Tests (LabelEditor.test.tsx)
```typescript
describe('LabelEditor', () => {
  // Basic functionality
  test('renders with initial label value')
  test('calls onUpdate when Enter pressed')
  test('calls onUpdate when input blurs')
  test('cancels edit when Escape pressed')

  // Whitespace handling (FR-005, FR-011)
  test('trims leading/trailing whitespace on save')
  test('normalizes newlines to spaces')
  test('normalizes tabs to spaces')

  // Edge cases
  test('prevents save of empty label (relies on Python)')
  test('supports standard text editing controls (select-all, copy/paste)')
  test('handles long labels with horizontal scroll')
});
```

### Frontend Integration Tests (ParameterPanel.test.tsx)
```typescript
describe('ParameterPanel with label editor', () => {
  test('shows label editor for Gain blocks')
  test('shows label editor for TransferFunction blocks')
  test('shows label editor for StateSpace blocks')
  test('shows label editor for IOMarker blocks')
  test('label editor appears before parameter editors')
  test('no height increase from adding label editor (SC-005)')
});
```

### Backend Tests (test_diagram.py extensions)
```python
def test_update_block_label_empty_reverts_to_id():
    """FR-006: Empty label reverts to block ID"""

def test_update_block_label_whitespace_only_reverts_to_id():
    """FR-006: Whitespace-only label reverts to block ID"""

def test_update_block_label_with_unicode():
    """FR-011: Accept printable Unicode characters"""

def test_update_block_label_duplicate_labels_allowed():
    """Edge case: Multiple blocks can have same label"""
```

**TDD Workflow**:
1. Write failing test for LabelEditor basic rendering
2. Implement minimal LabelEditor component (pass test)
3. Write failing test for Enter key handling
4. Implement Enter key handler (pass test)
5. Repeat for blur, Escape, whitespace normalization
6. Write integration tests (Parameter Panel + label editor)
7. Write backend edge case tests (if not already covered)
8. Refactor for code quality (GREEN → REFACTOR)

---

## Summary of Technical Decisions

| Decision | Choice | Impact |
|----------|--------|--------|
| **Placement** | First section in scrollable content area | No height increase, maintains visual hierarchy |
| **Component** | New `LabelEditor` component | Clear separation from canvas `EditableLabel` |
| **Validation** | Frontend normalization + backend validation | Immediate feedback + data integrity |
| **Action** | Reuse `updateBlockLabel` | Zero backend changes, leverages existing undo support |
| **Focus behavior** | Standard React cleanup | Consistent with existing parameter editors |
| **Testing** | Unit + integration + backend edge cases | TDD-compliant, comprehensive coverage |

All NEEDS CLARIFICATION items from Technical Context resolved. Ready for Phase 1 (data model + contracts).
