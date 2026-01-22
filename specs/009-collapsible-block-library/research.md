<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Collapsible Block Library

**Feature**: 009-collapsible-block-library
**Date**: 2026-01-13

## Research Summary

This feature has no unresolved technical unknowns. All required technologies are already in use in the codebase.

## Decisions

### 1. Animation Approach

**Decision**: Use CSS transitions with Tailwind utility classes

**Rationale**:
- Already using Tailwind CSS v4 throughout the project
- CSS transitions are GPU-accelerated for smooth 60fps animations
- No additional dependencies required
- Consistent with existing hover effects in the codebase (e.g., button hover states)

**Alternatives considered**:
- Framer Motion: Rejected - adds unnecessary dependency for simple expand/collapse
- React Spring: Rejected - overkill for linear transitions
- CSS Animations (@keyframes): Considered but transitions are simpler for two-state changes

### 2. State Management

**Decision**: Local React `useState` within BlockPalette component

**Rationale**:
- Collapse state is purely UI concern, not shared with Python backend
- No other components need to know about expand/collapse state
- Keeps component self-contained and testable

**Alternatives considered**:
- Context API: Rejected - no other components need this state
- Zustand/Redux: Rejected - over-engineering for single boolean
- URL state: Rejected - expand/collapse shouldn't persist or be shareable

### 3. Collapse Delay Implementation

**Decision**: `setTimeout` with `useRef` cleanup pattern

**Rationale**:
- Standard React pattern for debounced state changes
- `useRef` prevents stale closure issues
- Cleanup on unmount prevents memory leaks
- ~200ms delay matches industry standard for hover menus

**Alternatives considered**:
- `useDebouncedCallback` hook: Considered but adds dependency for simple case
- CSS-only delay: Rejected - doesn't handle rapid enter/leave correctly
- `requestAnimationFrame`: Rejected - not time-based, harder to configure

### 4. Touch Device Behavior

**Decision**: Click-to-toggle with tap-outside-to-collapse

**Rationale**:
- Hover doesn't exist on touch devices, need fallback
- Click toggle is intuitive mobile pattern
- Can detect touch via `'ontouchstart' in window` or media query

**Alternatives considered**:
- Long press: Rejected - less discoverable
- Always expanded on mobile: Rejected - defeats purpose of space saving
- Swipe gesture: Rejected - complexity not justified

## Existing Code Patterns

From `BlockPalette.tsx` analysis:
- Component uses Tailwind classes for all styling
- Already has `transition-colors` class on buttons for hover effects
- Positioned with `absolute top-2 left-2 z-10`
- Uses consistent styling: `bg-white border-2 border-slate-300 rounded-lg shadow-lg`

These patterns will be preserved in the collapsed state header.

## No Further Research Required

All technical decisions align with existing codebase patterns. Ready for Phase 1.
