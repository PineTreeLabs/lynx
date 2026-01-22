<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: LaTeX Block Rendering

**Feature**: 002-latex-block-rendering
**Date**: 2026-01-04

## Overview

This feature extends the existing Block data model with LaTeX rendering capabilities. The Python `Block` base class gains a single new property (`custom_latex`) that controls whether blocks display default mathematical notation or user-provided LaTeX.

## Entities

### Block (Extended)

**Type**: Python class (`lynx.blocks.base.Block`)
**Purpose**: Base class for all control system blocks
**Modification**: Add optional custom LaTeX override property

**New Attribute**:

```python
custom_latex: Optional[str]
```

**Properties**:
- **Type**: `traitlets.Unicode(default_value=None, allow_none=True)`
- **Default**: `None` (use default block-specific LaTeX)
- **Validation**: None (invalid LaTeX handled at render time)
- **Persistence**: Serialized to JSON via existing diagram persistence
- **Sync**: Automatically synchronized to frontend via traitlets

**Behavior**:
- When `None` or empty string: Block renders default LaTeX (type-specific)
- When non-empty string: Block renders custom LaTeX content only
- Setting to `None` reverts to default rendering
- UI checkbox state derives from property: checked if non-None and non-empty

**Examples**:
```python
# Default rendering (symbolic state-space)
block = StateSpaceBlock(id="ss1", A=[[0, 1], [-1, -2]], B=[[1], [0]], C=[[1, 0]], D=[[0]])
assert block.custom_latex is None
# Renders: ẋ = Ax + Bu, y = Cx + Du

# Custom rendering
block.custom_latex = r"K_p + \frac{K_i}{s}"
# Renders: Kₚ + Kᵢ/s

# Revert to default
block.custom_latex = None
# Renders: ẋ = Ax + Bu, y = Cx + Du again
```

---

### BlockData (Frontend Interface)

**Type**: TypeScript interface
**Purpose**: React component props for block rendering
**Modification**: No schema change (uses existing `parameters` array)

**Access Pattern**:
```typescript
interface BlockData {
  parameters: Array<{ name: string; value: any }>;
  // ... existing fields ...
}

// Custom LaTeX accessed as parameter
const customLatex = data.parameters?.find(p => p.name === "custom_latex")?.value;
```

**Notes**:
- `custom_latex` flows through existing parameter sync mechanism
- No new traitlet sync infrastructure needed
- Frontend treats as optional parameter (undefined = use default)

---

## LaTeX Content Types

### Default LaTeX (Generated)

**Source**: Block type + parameters
**Generation**: Computed on-demand in frontend
**Storage**: Not persisted (regenerated from block parameters)

**Block-Specific Formats**:

#### StateSpaceBlock
```typescript
// Always symbolic notation
const defaultLatex = String.raw`
\dot{x} = Ax + Bu \\
y = Cx + Du
`;
```

#### TransferFunctionBlock
```typescript
// Polynomial form with formatted coefficients
// Example: numerator=[1, 2.5, 0.00123], denominator=[1, 0.5, 1234]
const defaultLatex = String.raw`
\frac{s^2 + 2.5s + 1.23 \times 10^{-3}}{s^2 + 0.5s + 1.23 \times 10^3}
`;
```

#### GainBlock
```typescript
// Formatted numerical value
// Example: gain=123.456
const defaultLatex = "123"; // 3 sig figs
```

**Formatting Rules** (see research.md for implementation):
- Numbers: 3 significant figures
- Exponential notation when |x| < 0.01 or |x| ≥ 1000
- Polynomial terms in descending powers
- Multiplication operators explicit (using `\times`)

### Custom LaTeX (User-Provided)

**Source**: User input (UI or Python API)
**Validation**: None at input time (KaTeX validates at render)
**Storage**: Persisted in `Block.custom_latex` property
**Constraints**: Must be valid KaTeX syntax (subset of LaTeX)

**Error Handling**:
- Invalid syntax → KaTeX throws error → caught by LaTeXRenderer
- Fallback: Display "Invalid LaTeX" placeholder + error message below input
- User can edit/fix without losing work

---

## State Transitions

### Custom LaTeX Lifecycle

```
┌─────────────┐
│   Default   │  block.custom_latex = None
│  Rendering  │  (shows type-specific LaTeX)
└──────┬──────┘
       │
       │ User enables custom LaTeX
       │ (checkbox checked + text entered)
       ↓
┌─────────────┐
│   Custom    │  block.custom_latex = "user string"
│  Rendering  │  (shows custom LaTeX only)
└──────┬──────┘
       │
       │ User disables custom LaTeX
       │ (checkbox unchecked OR property set to None)
       ↓
┌─────────────┐
│   Default   │  block.custom_latex = None
│  Rendering  │  (shows type-specific LaTeX)
└─────────────┘
```

**Invariants**:
1. `custom_latex == None` ⟺ checkbox unchecked ⟺ default rendering active
2. `custom_latex != None and custom_latex != ""` ⟺ checkbox checked ⟺ custom rendering active
3. Setting `custom_latex = ""` equivalent to `None` (both trigger default rendering)

---

## Data Persistence

### JSON Schema Extension

Existing diagram JSON schema unchanged. `custom_latex` persists as standard block parameter:

```json
{
  "blocks": [
    {
      "id": "gain1",
      "type": "gain",
      "parameters": [
        {"name": "K", "value": 10.5},
        {"name": "custom_latex", "value": "K_p"}  // NEW (optional)
      ],
      "position": {"x": 100, "y": 200}
    }
  ]
}
```

**Backward Compatibility**:
- Diagrams without `custom_latex` load normally (default rendering)
- Blocks without custom LaTeX → `custom_latex` parameter absent (equivalent to `None`)
- No migration needed for existing diagrams

---

## Validation Rules

### Python-Side
- **Type**: String or None
- **Constraints**: None (accepts any string)
- **Rationale**: LaTeX syntax too complex for Python validation, frontend handles errors

### Frontend-Side
- **Render-Time**: KaTeX validates syntax
- **Invalid LaTeX**:
  - KaTeX throws exception → caught by error boundary
  - Fallback UI shown ("Invalid LaTeX" + error message)
  - Original input preserved for editing

### Data Integrity
- **Empty String**: Treated as None (default rendering)
- **Whitespace-Only**: Treated as empty (default rendering)
- **Special Characters**: Passed through unchanged to KaTeX
- **Unicode**: Supported (LaTeX \u escapes or direct Unicode)

---

## Relationships

### Block ↔ Parameters
- **Cardinality**: 1 Block : N Parameters
- **New Parameter**: `custom_latex` (optional)
- **Access**: Via existing `parameters` array in BlockData

### Block ↔ Default LaTeX
- **Cardinality**: 1 Block : 1 Default LaTeX String
- **Generation**: Computed from block type + parameters
- **Caching**: None (lightweight computation, regenerated on render)

### Block ↔ Custom LaTeX
- **Cardinality**: 1 Block : 0..1 Custom LaTeX String
- **Storage**: `Block.custom_latex` property
- **Override**: When present, replaces default entirely

---

## Key Design Decisions

1. **Single Property**: One `custom_latex` property (not separate enable flag)
   - Simpler API: `block.custom_latex = "..."` vs. `block.use_custom = True; block.custom_latex = "..."`
   - Less state to synchronize
   - Clear semantics: None = default, string = custom

2. **Frontend Generation**: Default LaTeX computed in TypeScript, not Python
   - Reduces Python-JS data transfer
   - Keeps formatting logic near rendering code
   - Python only stores overrides

3. **No Validation**: Accept any string, validate at render time
   - LaTeX syntax complex and evolving
   - KaTeX provides better error messages than custom validator
   - Users can fix errors immediately (error shown in UI)

4. **Parameter Array**: Use existing sync mechanism
   - No new infrastructure
   - Consistent with other block properties
   - Automatic persistence

---

## Migration Path

**From**: Blocks without LaTeX (current state)
**To**: Blocks with LaTeX rendering (this feature)

**Steps**: None required
- Existing blocks: `custom_latex` parameter absent → renders defaults
- New blocks: `custom_latex = None` by default → renders defaults
- User customization: Sets `custom_latex` explicitly when needed

**Rollback**: Remove KaTeX dependency, ignore `custom_latex` parameter
- Diagrams still load (parameter ignored)
- No data loss (custom_latex preserved in JSON)
- Can roll forward later without data migration
