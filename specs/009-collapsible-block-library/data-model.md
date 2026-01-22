<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Collapsible Block Library

**Feature**: 009-collapsible-block-library
**Date**: 2026-01-13

## Overview

This feature is UI-only and does not introduce new persistent data entities. The expand/collapse state is ephemeral React component state.

## Component State

### BlockPalette Local State

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `isExpanded` | `boolean` | `false` | Whether the panel is currently expanded |
| `collapseTimeoutRef` | `React.RefObject<number \| null>` | `null` | Reference to pending collapse timeout for cleanup |

### Constants

| Name | Type | Value | Description |
|------|------|-------|-------------|
| `COLLAPSE_DELAY_MS` | `number` | `200` | Milliseconds to wait before collapsing after mouse leave |
| `TRANSITION_DURATION_MS` | `number` | `150` | CSS transition duration for animations |

## No Database Changes

- No new tables or columns
- No Python model changes
- No JSON schema changes
- Expand/collapse state is not persisted between sessions

## Styling Tokens (Existing)

The collapsed header will reuse existing design tokens:

| Token | Value | Usage |
|-------|-------|-------|
| `bg-white` | `#ffffff` | Panel background |
| `border-slate-300` | `#cbd5e1` | Border color |
| `text-slate-700` | `#334155` | "Blocks" text color |
| `rounded-lg` | `0.5rem` | Border radius |
| `shadow-lg` | Standard | Drop shadow |
