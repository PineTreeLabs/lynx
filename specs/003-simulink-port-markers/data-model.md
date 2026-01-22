<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Simulink-Style Port Markers

**Feature**: 003-simulink-port-markers
**Date**: 2026-01-05
**Phase**: 1 (Design)

## Overview

This document defines the data structures and state model for triangular port markers. Since this is a purely visual feature with no persistent state changes, the "data model" describes the runtime React component props and derived state.

## Entities

### PortMarker (Frontend Component)

A triangular SVG visual indicator rendered inside a React Flow Handle component.

**Properties**:

| Property | Type | Required | Description | Validation |
|----------|------|----------|-------------|------------|
| `direction` | `"input" \| "output"` | Yes | Port type - determines triangle orientation | Must be one of two values |
| `isConnected` | `boolean` | Yes | Connection state - controls visibility | Derived from edges array |
| `isFlipped` | `boolean` | No | Block flip state - inherits from block | Default: `false` |
| `isDragTarget` | `boolean` | No | Whether this port is being hovered during connection drag | Default: `false` |
| `size` | `number` | No | Triangle height in pixels | Default: `10`, must be positive |
| `className` | `string` | No | Additional CSS classes | Optional styling override |

**State Transitions**:

```
Visible States:
- VISIBLE: isConnected=false AND !isDragTarget
- HIDDEN_CONNECTED: isConnected=true
- HIDDEN_DRAG: isDragTarget=true (during hover)
- HIDDEN_BOTH: isConnected=true AND isDragTarget=true (edge case during reconnect)
```

**Lifecycle**:
1. Component mounts when block renders
2. Visibility recalculates when `isConnected` or `isDragTarget` changes
3. Orientation recalculates when `isFlipped` changes
4. Component unmounts when block is deleted

**Relationships**:
- **Parent**: React Flow `Handle` component (1:1 - each Handle has one PortMarker)
- **Block**: Associated with a block via Handle's parent block component (N:1 - block has multiple markers)
- **Edges**: Visibility derived from edges array (M:N - edges connect ports)

---

### PortConnectionState (Derived State)

Runtime state tracking port connection status. Not persisted - derived from React Flow edges array.

**Properties**:

| Property | Type | Description |
|----------|------|-------------|
| `blockId` | `string` | Block identifier (React Flow node ID) |
| `portId` | `string` | Port identifier ("in", "out", "in1", etc.) |
| `isConnected` | `boolean` | Whether any edge connects to this port |
| `connectedEdges` | `Edge[]` | Array of edges connected to this port (for debugging) |

**Derivation Logic**:
```typescript
function derivePortConnectionState(
  blockId: string,
  portId: string,
  allEdges: Edge[]
): PortConnectionState {
  const connectedEdges = allEdges.filter(edge =>
    (edge.source === blockId && edge.sourceHandle === portId) ||
    (edge.target === blockId && edge.targetHandle === portId)
  );

  return {
    blockId,
    portId,
    isConnected: connectedEdges.length > 0,
    connectedEdges,
  };
}
```

**Usage**: Consumed by `usePortConnected` hook to provide `isConnected` prop to PortMarker.

---

### TriangleGeometry (Internal Utility)

SVG polygon points calculation for triangle rendering.

**Properties**:

| Property | Type | Description |
|----------|------|-------------|
| `size` | `number` | Triangle height/base in pixels |
| `direction` | `"input" \| "output"` | Points left or right |
| `isEquilateral` | `boolean` | True for equilateral, false for isosceles |

**Output**:
```typescript
interface TrianglePoints {
  points: string; // SVG polygon points attribute, e.g., "0,0 10,5 0,10"
  viewBox: string; // SVG viewBox, e.g., "0 0 10 10"
}
```

**Geometry Calculation** (Equilateral):
```
Input port (left-pointing):
  - Vertex 1: (size, 0)           // Top right
  - Vertex 2: (0, size/2)         // Left point
  - Vertex 3: (size, size)        // Bottom right

Output port (right-pointing):
  - Vertex 1: (0, 0)              // Top left
  - Vertex 2: (size, size/2)      // Right point
  - Vertex 3: (0, size)           // Bottom left
```

**Isosceles Variant** (if needed during implementation):
```
Scale X-axis independently to make narrower/wider triangles
```

---

## State Management

### Component-Level State

**PortMarker Component**:
- No internal state - purely presentational
- All state passed via props
- Renders SVG based on props

**Block Components** (GainBlock, SumBlock, etc.):
- Maintain `isFlipped` state (existing, from `useFlippableBlock` hook)
- Derive `isConnected` via `usePortConnected(blockId, portId)` hook
- Pass props to PortMarker

### Application-Level State

**DiagramCanvas**:
- `edges: Edge[]` - React Flow edge state (source of truth for connections)
- `connectionInProgress: boolean` - Tracks active connection drag
- `dragTargetHandleId: string | null` - Which handle is being hovered during drag

**No Backend State Changes**:
- Python backend diagram model unchanged
- No new persistence fields in JSON diagram files
- Connection tracking already exists in `diagram.connections[]`

---

## Data Flow

```
User Action (connect blocks)
  ↓
DiagramCanvas.onConnect() → Python backend
  ↓
Python updates diagram.connections
  ↓
Traitlet sync → edges[] updated in React
  ↓
usePortConnected() hook detects change
  ↓
PortMarker receives isConnected=true prop
  ↓
PortMarker renders with visibility=false
```

```
User Action (drag connection)
  ↓
DiagramCanvas.onConnectStart() → setConnectionInProgress(true)
  ↓
Mouse hovers over Handle → React Flow sets isConnectableEnd=true
  ↓
Handle passes isDragTarget=true to PortMarker
  ↓
PortMarker renders with visibility=false (hover state)
  ↓
User drops connection or cancels
  ↓
DiagramCanvas.onConnectEnd() → setConnectionInProgress(false)
  ↓
PortMarker visibility returns to connection-based logic
```

---

## Validation Rules

### PortMarker Props Validation

1. **Direction**: Must be exactly "input" or "output" (TypeScript enforces at compile time)
2. **Size**: If provided, must be positive number >0 (runtime check with console.warn)
3. **isConnected**: Boolean only (TypeScript enforces)
4. **isFlipped**: Boolean only (TypeScript enforces)

### Runtime Invariants

1. **Mutual Exclusivity**: A port CANNOT have both isConnected=true and have a visible marker
   - Enforced by: `visible = !isConnected && !isDragTarget`

2. **Flip Consistency**: When block flips, ALL port markers must update orientation
   - Enforced by: Props passed from parent block, single isFlipped source of truth

3. **Edge Consistency**: If edge exists in edges[], corresponding ports MUST show isConnected=true
   - Enforced by: usePortConnected() hook directly queries edges array

---

## Performance Considerations

### Render Optimization

- **PortMarker**: Pure functional component, no internal state
- **Memoization**: Not needed unless profiling shows issues (unlikely with <100 markers)
- **SVG Caching**: Browser handles SVG optimization, no manual caching needed

### Update Frequency

- **Connection changes**: Infrequent (user action)
- **Drag hover**: Frequent during drag (60fps target)
- **Flip changes**: Rare (user action via context menu)

**Bottleneck Analysis**: None expected. React Flow already optimizes 1000+ nodes at 60fps.

---

## Type Definitions (TypeScript)

```typescript
// components/PortMarker.tsx
export interface PortMarkerProps {
  direction: "input" | "output";
  isConnected: boolean;
  isFlipped?: boolean;
  isDragTarget?: boolean;
  size?: number;
  className?: string;
}

// hooks/usePortMarkerVisibility.ts
export interface PortConnectionState {
  blockId: string;
  portId: string;
  isConnected: boolean;
  connectedEdges: Edge[];
}

// utils/portMarkerGeometry.ts
export interface TrianglePoints {
  points: string;
  viewBox: string;
}

export interface TriangleGeometryOptions {
  size: number;
  direction: "input" | "output";
  isEquilateral?: boolean;
}
```

---

## Summary

This data model describes a **purely presentational feature** with no persistent state. All state is derived at runtime from existing React Flow edges and block flip state. The design emphasizes:

1. **Simplicity**: No new backend models or persistence
2. **Derivation**: Connection state derived from edges array (single source of truth)
3. **Composition**: PortMarker wraps SVG, Handle wraps PortMarker, Block owns Handles
4. **Type Safety**: TypeScript enforces prop contracts at compile time
