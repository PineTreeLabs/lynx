<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Hideable Block Labels

**Feature**: 005-hideable-block-labels
**Date**: 2026-01-12

## Overview

This document captures technical research and decisions made during planning. Since this feature follows established patterns in the codebase, no major unknowns required external research.

## Research Topics

### 1. Block Attribute Pattern

**Question**: How should `label_visible` be added to the block data model?

**Finding**: The codebase has an established pattern for block-level visual attributes:

| Attribute | Type | Default | Purpose |
|-----------|------|---------|---------|
| `flipped` | `bool` | `false` | Horizontal flip for visual layout |
| `custom_latex` | `str | None` | `None` | Custom LaTeX override |
| `label` | `str | None` | `id` | User-facing label text |

**Decision**: Add `label_visible: bool = False` following the same pattern.

**Rationale**:
- Consistent with existing attributes
- Default `False` meets spec requirement "hidden by default"
- Boolean is simplest possible type

**Alternatives Considered**:
- Put in parameters dict → Rejected: parameters are for control system values
- CSS-only hiding → Rejected: state wouldn't persist, undo/redo wouldn't work

### 2. Context Menu Integration

**Question**: How to add the Show/Hide Label option to BlockContextMenu?

**Finding**: `BlockContextMenu.tsx` already has conditional menu items:

```typescript
// Existing pattern for Flip option
{onFlip && (
  <button onClick={() => { onFlip(); onClose(); }} ... >
    Flip Horizontal
  </button>
)}
```

**Decision**: Add a similar pattern for label toggle:

```typescript
// Always show (all blocks have labels)
<button onClick={() => { onToggleLabel?.(); onClose(); }} ... >
  {labelVisible ? "Hide Label" : "Show Label"}
</button>
```

**Rationale**:
- Follows existing component pattern
- Dynamic text based on current state
- Always available (unlike Flip which is conditional)

### 3. Action Handler Pattern

**Question**: How should the Python backend handle the toggle action?

**Finding**: `diagram.py` has `flip_block()` as a reference pattern:

```python
def flip_block(self, block_id: str) -> bool:
    """Flip a block's horizontal orientation."""
    block = self._find_block(block_id)
    if not block:
        return False

    block.flipped = not block.flipped
    self._push_undo_state()
    return True
```

**Decision**: Create `toggle_label_visibility()` following the same pattern:

```python
def toggle_label_visibility(self, block_id: str) -> bool:
    """Toggle a block's label visibility."""
    block = self._find_block(block_id)
    if not block:
        return False

    block.label_visible = not block.label_visible
    self._push_undo_state()
    return True
```

**Rationale**:
- Consistent with existing codebase
- Undo/redo support via `_push_undo_state()`
- Returns success boolean for error handling

### 4. Frontend Conditional Rendering

**Question**: How to show/hide the label in block components?

**Finding**: All 5 block components render `<EditableLabel>` at the bottom:

```typescript
// Current pattern in GainBlock.tsx
<EditableLabel
  value={blockLabel}
  onSave={handleLabelSave}
  className="text-xs text-slate-600 mt-1 font-mono"
/>
```

**Decision**: Wrap in conditional based on `label_visible`:

```typescript
{data.label_visible && (
  <EditableLabel
    value={blockLabel}
    onSave={handleLabelSave}
    className="text-xs text-slate-600 mt-1 font-mono"
  />
)}
```

**Rationale**:
- No DOM element when hidden (clean)
- Preserves all existing editing behavior when visible
- Consistent across all 5 block types

**Alternatives Considered**:
- CSS `display: none` → Works but adds unnecessary DOM
- Opacity 0 → Confusing, label still takes space

### 5. Backward Compatibility

**Question**: What happens to existing saved diagrams?

**Finding**: Pydantic handles missing fields gracefully with defaults:

```python
class BaseBlockModel(BaseModel):
    label_visible: bool = False  # New field with default
```

**Decision**: Rely on Pydantic's default value handling.

**Rationale**:
- Existing diagrams load successfully (missing field → `False`)
- Default `False` matches spec requirement
- No migration script needed

### 6. Copy/Paste Behavior

**Question**: Should `label_visible` be preserved when copying blocks?

**Finding**: Block copy includes all attributes via `to_dict()` serialization.

**Decision**: Yes, include `label_visible` in `to_dict()` output.

**Rationale**:
- Follows spec requirement: "preserve label visibility state when blocks are copied and pasted"
- Consistent with how `flipped` and other attributes work

## Summary

No external research was required. All technical decisions follow established patterns in the codebase:

1. **Attribute**: Top-level boolean `label_visible = False`
2. **Context Menu**: Dynamic "Show/Hide Label" text
3. **Backend**: `toggle_label_visibility()` method
4. **Frontend**: Conditional `<EditableLabel>` rendering
5. **Compatibility**: Pydantic defaults handle missing field
6. **Copy/Paste**: Included in serialization automatically
