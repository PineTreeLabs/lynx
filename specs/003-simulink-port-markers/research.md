<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Technical Research: Simulink-Style Port Markers

**Feature**: 003-simulink-port-markers
**Date**: 2026-01-05
**Phase**: 0 (Research & Technical Decisions)

## Overview

This document captures technical decisions and research findings for implementing Simulink-style triangular port markers to replace the current circular dot markers on block ports.

## Research Questions & Decisions

### Q1: Does frontend have test infrastructure? If yes, what framework?

**Decision**: YES - Vitest 2.1.8 with React Testing Library

**Findings**:
- **Test Framework**: Vitest 2.1.8 (`vitest` package in devDependencies)
- **Testing Library**: @testing-library/react 16.1.0 + @testing-library/jest-dom 6.6.4
- **Test Environment**: jsdom 25.0.1 (browser environment simulation)
- **Coverage Tool**: vitest built-in coverage with v8 provider
- **Setup File**: `/js/src/test/setup.ts` - configures React 19 act polyfill and cleanup

**Existing Tests**:
- `/js/src/utils/latexGeneration.test.ts` - LaTeX generation utilities (38 tests)
- `/js/src/utils/numberFormatting.test.ts` - Number formatting (18 tests)
- `/js/src/components/LaTeXRenderer.test.tsx.todo` - Placeholder for React component tests

**Test Commands**:
- `npm test` - Run all tests
- `npm run test:ui` - Visual test UI
- `npm run test:coverage` - Generate coverage report

**Rationale**: TDD workflow APPLIES for this feature. Component tests should be written first following the established vitest pattern.

**Impact on Plan**: Update Constitution Check Principle III to PASS. Tests required before implementation.

---

### Q2: How should triangular markers integrate with React Flow's Handle system?

**Decision**: Wrap Handle component with custom SVG children for triangle rendering

**Research Findings**:

**Current Handle Implementation** (from codebase exploration):
```typescript
// Example from GainBlock.tsx
<Handle
  type="target"
  position={getHandlePosition("left", isFlipped)}
  id="in"
  className="!bg-primary-600 !w-2 !h-2 z-10"
/>
```

**React Flow Handle Customization Options**:
1. **CSS-only approach**: Use `className` to style handles (current approach for dots)
2. **Children approach**: React Flow Handles accept children for custom rendering
3. **Custom node approach**: Completely replace Handle with custom connection points

**Chosen Approach**: #2 - Children approach

**Rationale**:
- Maintains React Flow's connection detection and drag-and-drop UX
- Allows SVG triangle rendering inside Handle
- Minimal changes to existing block components
- No need to reimplement connection logic

**Implementation Pattern**:
```typescript
<Handle
  type="target"
  position={getHandlePosition("left", isFlipped)}
  id="in"
  className="!bg-transparent" // Hide default circle
>
  <PortMarker
    direction="input"
    isConnected={isPortConnected("in")}
    isFlipped={isFlipped}
  />
</Handle>
```

**Alternatives Considered**:
- **CSS-only**: Rejected - CSS `clip-path` triangles don't provide fine-grained rotation control for flip semantics
- **Custom nodes**: Rejected - Adds complexity by reimplementing React Flow's connection system

---

### Q3: How to determine port connection state for visibility control?

**Decision**: Derive from React Flow's edges array using port ID matching

**Research Findings**:

**Current Connection State** (from DiagramCanvas.tsx):
- `edges[]` - React Flow edge state (line 116-127)
- Each edge has: `source`, `sourceHandle`, `target`, `targetHandle`
- Edges array updates on every connection add/remove
- Already synchronized with Python backend via traitlets

**Connection Detection Logic**:
```typescript
function isPortConnected(blockId: string, portId: string, edges: Edge[]): boolean {
  return edges.some(edge =>
    (edge.source === blockId && edge.sourceHandle === portId) ||
    (edge.target === blockId && edge.targetHandle === portId)
  );
}
```

**Where to Implement**:
- **Option A**: Custom hook `usePortMarkerVisibility(blockId, portId, edges)`
- **Option B**: Prop passed from parent block component
- **Option C**: Context provider with edge state

**Chosen Approach**: Option A - Custom hook

**Rationale**:
- Encapsulates logic in reusable hook
- Follows existing pattern (see `useFlippableBlock`, `useBlockLabel`)
- Easy to test independently
- Blocks remain simple - just call hook and pass boolean to PortMarker

**Implementation**:
```typescript
// hooks/usePortMarkerVisibility.ts
export function usePortConnected(blockId: string, portId: string) {
  const edges = useEdges(); // React Flow hook
  return edges.some(edge =>
    (edge.source === blockId && edge.sourceHandle === portId) ||
    (edge.target === blockId && edge.targetHandle === portId)
  );
}
```

---

### Q4: How to handle drag-and-drop hover state for destination marker hiding?

**Decision**: Use React Flow's `onConnectStart` and `onConnectEnd` events with hover detection

**Research Findings**:

**React Flow Connection Events** (from React Flow docs + DiagramCanvas.tsx):
- `onConnectStart(event, { nodeId, handleId, handleType })` - Fired when drag starts
- `onConnect(connection)` - Fired when connection succeeds
- `onConnectEnd(event)` - Fired when drag ends (success or cancel)
- Handle components receive `isConnectableStart` and `isConnectableEnd` props during drag

**Hover Detection**:
- React Flow doesn't expose hover events directly
- Can use Handle's `isConnectableEnd` prop (true when valid connection target during drag)
- Can track drag state in DiagramCanvas and pass to blocks

**Chosen Approach**: Use `isConnectableEnd` prop on Handle + connection state tracking

**Implementation Strategy**:
```typescript
// DiagramCanvas.tsx - track connection drag state
const [connectionInProgress, setConnectionInProgress] = useState(false);

onConnectStart={() => setConnectionInProgress(true)}
onConnectEnd={() => setConnectionInProgress(false)}

// Block component - pass to PortMarker
<Handle isConnectableEnd={true}>
  <PortMarker
    visible={!isConnected && !(connectionInProgress && isTargetOfDrag)}
  />
</Handle>
```

**Alternatives Considered**:
- **Mouse enter/leave events**: Rejected - conflicts with React Flow's drag system
- **Custom drag handler**: Rejected - too complex, reimplements React Flow logic

**Note**: Clarification from spec states destination marker should disappear on hover. React Flow's `isConnectableEnd` provides this signal.

---

### Q5: What are best practices for SVG triangle rendering in React components?

**Decision**: Inline SVG with `<polygon>` element, 10px equilateral triangle with configurable rotation

**Research**:

**Triangle Geometry** (from spec clarifications):
- Size: 10px equilateral triangle (base and height ~10px)
- Shape: Equilateral initially, flexible to isosceles if needed
- Orientation: Points left (input) or right (output), rotates with flip

**SVG Rendering Approaches**:
1. `<polygon>` with points attribute - simple, performant
2. `<path>` with d attribute - more flexible, slightly more complex
3. CSS clip-path - limited browser support for complex transforms

**Chosen Approach**: `<polygon>` with calculated points

**Equilateral Triangle Coordinates** (10px, pointing right):
```typescript
// Right-pointing (output port)
// Base at left edge, point at right
const points = "0,0 10,5 0,10"; // (x1,y1 x2,y2 x3,y3)

// Left-pointing (input port) - mirror
const points = "10,0 0,5 10,10";
```

**Rotation for Flip**:
- Flip horizontal: CSS `transform: scaleX(-1)` (inherited from block flip)
- Alternative: Recalculate points (more explicit but redundant with block flip)

**Color & Styling**:
- Stroke: `var(--color-primary-600)` (indigo #465082)
- Fill: `none` or `transparent` (outline only, like Simulink)
- Stroke width: 1.5px (visible but not heavy)

**Best Practice Rationale**:
- Polygon is simplest SVG primitive for triangles
- Points calculation is straightforward
- Leverages existing block flip transform (no redundant rotation logic)
- Matches theme system via CSS custom properties

---

### Q6: Performance considerations for marker rendering

**Decision**: No special optimization needed - standard React rendering sufficient

**Analysis**:

**Rendering Load**:
- Typical diagram: 10-50 blocks (from Technical Context)
- Ports per block: 1-5 (most blocks 2, Sum block 5)
- Total markers: ~20-100 SVG triangles
- Update frequency: Only on connection add/remove (infrequent)

**Performance Targets** (from spec):
- <100ms marker rendering latency
- <50ms visibility toggle
- 60fps during drag operations

**React Flow Baseline**:
- React Flow handles 1000+ nodes at 60fps
- 100 SVG triangles negligible compared to full block rendering

**Optimization Not Needed**:
- No virtualization required (small count)
- No memoization needed (props change only on connection events)
- React Flow already optimizes edge updates

**Monitoring**:
- If performance issues arise, add `React.memo()` to PortMarker
- React DevTools Profiler can measure render times

**Rationale**: Over-optimization is premature. Standard React rendering meets performance targets.

---

## Technology Decisions Summary

| Decision Point | Choice | Rationale |
|----------------|--------|-----------|
| **Test Framework** | Vitest 2.1.8 + React Testing Library | Already configured, TDD workflow applies |
| **Handle Integration** | React Flow Handle with SVG children | Maintains connection UX, minimal changes |
| **Connection Detection** | Custom hook reading edges array | Follows existing pattern, testable |
| **Hover State** | React Flow `isConnectableEnd` prop | Built-in, no custom drag logic needed |
| **SVG Rendering** | `<polygon>` with inline points | Simple, performant, standard SVG |
| **Performance Strategy** | Standard React rendering | Sufficient for scale, optimize if needed |

---

## Implementation Risks & Mitigations

### Risk 1: React Flow Handle children not supported

**Likelihood**: Low
**Impact**: High
**Mitigation**: Verified in React Flow v11 docs - children ARE supported. Fallback: Use CSS `::before`/`::after` pseudo-elements.

### Risk 2: Marker visibility flicker during rapid connect/disconnect

**Likelihood**: Medium (per spec clarification, no debouncing)
**Impact**: Low (visual only, user explicitly accepted this)
**Mitigation**: Document as known behavior. If user feedback negative, add 16ms RAF debounce.

### Risk 3: Marker overlap with block content on small blocks

**Likelihood**: Low (blocks have minimum size constraints)
**Impact**: Low (per clarification, acceptable to overlap)
**Mitigation**: None needed - spec explicitly allows overlap.

---

## Next Steps

1. **Phase 1**: Create data-model.md (PortMarker state model)
2. **Phase 1**: Create contracts/PortMarker.yaml (component interface)
3. **Phase 1**: Create quickstart.md (test scenarios)
4. **Phase 1**: Run update-agent-context.sh
5. **Phase 2**: Generate tasks.md with TDD workflow (tests first)

---

## References

- React Flow Documentation: https://reactflow.dev/api-reference/components/handle
- Vitest Documentation: https://vitest.dev/
- Existing codebase tests: `/js/src/utils/*.test.ts`
- Block implementations: `/js/src/blocks/*.tsx`
- Theme system: `/js/src/styles.css`
