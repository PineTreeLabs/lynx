<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Collapsible Block Library

**Branch**: `009-collapsible-block-library` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-collapsible-block-library/spec.md`

## Summary

Transform the BlockPalette component from an always-visible panel to a hover-expandable element. By default, display a compact "Blocks" icon in the upper left corner. On mouse hover, expand to show the full library panel with all block buttons. On mouse leave (after a brief delay), collapse back to the icon. This maximizes canvas real estate while maintaining easy block access.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend)
**Primary Dependencies**: React 19.2.3, Tailwind CSS v4
**Storage**: N/A (UI-only feature, no persistence)
**Testing**: Vitest 2.1.8 with React Testing Library 16.1.0
**Target Platform**: Browser (Jupyter widget via anywidget)
**Project Type**: Web application (React frontend component)
**Performance Goals**: Expand/collapse animation <200ms
**Constraints**: Must work within React Flow canvas overlay, maintain z-index hierarchy
**Scale/Scope**: Single component modification (BlockPalette.tsx)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity Over Features | ✅ PASS | Minimal change to existing component, uses native CSS transitions |
| II. Python Ecosystem First | ✅ PASS | UI-only change, no Python backend changes required |
| III. Test-Driven Development | ✅ PASS | Will write tests first for expand/collapse behavior |
| IV. Clean Separation of Concerns | ✅ PASS | Purely presentation layer change, no business logic affected |
| V. User Experience Standards | ✅ PASS | Improves UX by maximizing canvas space while maintaining accessibility |

**Gate Result**: All principles satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/009-collapsible-block-library/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal - UI state only)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
js/src/
├── palette/
│   └── BlockPalette.tsx    # PRIMARY: Add hover expand/collapse behavior
├── hooks/
│   └── useHoverExpand.ts   # NEW: Custom hook for hover delay logic (optional)
└── test/
    └── setup.ts            # Existing test setup
```

**Structure Decision**: Single component modification with possible extraction of hover logic to a reusable hook. Existing test infrastructure in place.

## Complexity Tracking

> No violations. Implementation follows simplicity principle.

## Architecture Decision

### Approach: CSS Transitions with React State

The collapsible behavior will be implemented using:

1. **React `useState`** to track `isExpanded` boolean
2. **Mouse event handlers** (`onMouseEnter`, `onMouseLeave`) on the container
3. **`setTimeout`/`useRef`** for collapse delay to prevent flickering
4. **CSS Tailwind transitions** for smooth animations (opacity, max-height, or transform)

### Why This Approach

- **Simplicity**: No additional dependencies required
- **Performance**: CSS transitions are GPU-accelerated
- **Maintainability**: Self-contained in single component
- **Consistency**: Matches existing Tailwind styling patterns

### Component Structure

```
<div onMouseEnter onMouseLeave>
  {/* Always visible: Collapsed header with "Blocks" text */}
  <div className="collapsed-header">Blocks</div>

  {/* Conditionally visible: Button panel */}
  <div className={`button-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
    {/* Existing buttons */}
  </div>
</div>
```

## Key Implementation Details

### 1. Collapse Delay Logic

```typescript
const COLLAPSE_DELAY_MS = 200; // Prevents accidental closure
const collapseTimeoutRef = useRef<number | null>(null);

const handleMouseEnter = () => {
  if (collapseTimeoutRef.current) {
    clearTimeout(collapseTimeoutRef.current);
    collapseTimeoutRef.current = null;
  }
  setIsExpanded(true);
};

const handleMouseLeave = () => {
  collapseTimeoutRef.current = setTimeout(() => {
    setIsExpanded(false);
  }, COLLAPSE_DELAY_MS);
};
```

### 2. CSS Transition Classes (Tailwind)

```css
/* Collapsed state */
.collapsed {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: all 150ms ease-out;
}

/* Expanded state */
.expanded {
  max-height: 300px; /* or auto with JS */
  opacity: 1;
  transition: all 150ms ease-in;
}
```

### 3. Touch Device Support (Edge Case)

For touch devices without hover, implement click-to-toggle:
- First tap on collapsed icon: expand
- Tap outside panel: collapse
- This matches edge case behavior specified in spec

## Test Strategy

Tests will be written FIRST (TDD per constitution):

1. **Default state test**: Panel renders collapsed by default
2. **Hover expand test**: Panel expands on mouseEnter
3. **Hover collapse test**: Panel collapses on mouseLeave (after delay)
4. **No flicker test**: Rapid enter/leave doesn't cause flickering
5. **Button functionality test**: Buttons remain clickable when expanded
6. **Styling consistency test**: Collapsed icon matches panel styling
