<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: Simulink-Style Port Markers Testing Scenarios

**Feature**: 003-simulink-port-markers
**Date**: 2026-01-05
**Phase**: 1 (Design)
**Purpose**: Manual and automated test scenarios to validate port marker functionality

## Overview

This guide provides step-by-step test scenarios for validating the Simulink-style port markers feature. Tests are organized by user story priority and cover both automated unit tests and manual visual verification.

---

## Prerequisites

### Development Environment Setup

1. **Install dependencies**:
   ```bash
   cd js
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Run tests**:
   ```bash
   # Run all tests
   npm test

   # Run with UI
   npm run test:ui

   # Run with coverage
   npm run test:coverage
   ```

4. **Open Jupyter notebook** (for manual testing):
   ```bash
   jupyter notebook examples/test_diagram.ipynb
   ```

---

## Automated Tests

### Unit Tests: PortMarker Component

**File**: `js/src/components/PortMarker.test.tsx`

#### Test Suite 1: Visibility Logic

```typescript
describe('PortMarker Visibility', () => {
  test('renders triangle when port is unconnected and not drag target', () => {
    // Given
    const { container } = render(
      <PortMarker direction="input" isConnected={false} isDragTarget={false} />
    );

    // Then
    expect(container.querySelector('polygon')).toBeInTheDocument();
  });

  test('hides triangle when port is connected', () => {
    // Given
    const { container } = render(
      <PortMarker direction="input" isConnected={true} isDragTarget={false} />
    );

    // Then
    expect(container.querySelector('polygon')).not.toBeInTheDocument();
  });

  test('hides triangle when port is drag target', () => {
    // Given
    const { container } = render(
      <PortMarker direction="input" isConnected={false} isDragTarget={true} />
    );

    // Then
    expect(container.querySelector('polygon')).not.toBeInTheDocument();
  });

  test('hides triangle when both connected and drag target', () => {
    // Given
    const { container } = render(
      <PortMarker direction="input" isConnected={true} isDragTarget={true} />
    );

    // Then
    expect(container.querySelector('polygon')).not.toBeInTheDocument();
  });
});
```

#### Test Suite 2: Triangle Geometry

```typescript
describe('PortMarker Geometry', () => {
  test('renders left-pointing triangle for input port', () => {
    // Given
    const { container } = render(
      <PortMarker direction="input" isConnected={false} />
    );

    // Then
    const polygon = container.querySelector('polygon');
    expect(polygon).toHaveAttribute('points', '10,0 0,5 10,10');
  });

  test('renders right-pointing triangle for output port', () => {
    // Given
    const { container } = render(
      <PortMarker direction="output" isConnected={false} />
    );

    // Then
    const polygon = container.querySelector('polygon');
    expect(polygon).toHaveAttribute('points', '0,0 10,5 0,10');
  });

  test('respects custom size prop', () => {
    // Given
    const { container } = render(
      <PortMarker direction="output" isConnected={false} size={20} />
    );

    // Then
    const polygon = container.querySelector('polygon');
    expect(polygon).toHaveAttribute('points', '0,0 20,10 0,20');
  });
});
```

#### Test Suite 3: Styling

```typescript
describe('PortMarker Styling', () => {
  test('applies primary-600 stroke color', () => {
    // Given
    const { container } = render(
      <PortMarker direction="input" isConnected={false} />
    );

    // Then
    const polygon = container.querySelector('polygon');
    expect(polygon).toHaveStyle('stroke: var(--color-primary-600)');
  });

  test('accepts custom className', () => {
    // Given
    const { container } = render(
      <PortMarker direction="input" isConnected={false} className="custom-marker" />
    );

    // Then
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('custom-marker');
  });
});
```

### Unit Tests: usePortConnected Hook

**File**: `js/src/hooks/usePortMarkerVisibility.test.ts`

```typescript
describe('usePortConnected Hook', () => {
  test('returns false when no edges connect to port', () => {
    // Given
    const edges = [];
    const { result } = renderHook(() =>
      usePortConnected('block-1', 'in', edges)
    );

    // Then
    expect(result.current).toBe(false);
  });

  test('returns true when edge connects to input port', () => {
    // Given
    const edges = [{
      id: 'e1',
      source: 'block-0',
      sourceHandle: 'out',
      target: 'block-1',
      targetHandle: 'in'
    }];
    const { result } = renderHook(() =>
      usePortConnected('block-1', 'in', edges)
    );

    // Then
    expect(result.current).toBe(true);
  });

  test('returns true when edge connects to output port', () => {
    // Given
    const edges = [{
      id: 'e1',
      source: 'block-1',
      sourceHandle: 'out',
      target: 'block-2',
      targetHandle: 'in'
    }];
    const { result } = renderHook(() =>
      usePortConnected('block-1', 'out', edges)
    );

    // Then
    expect(result.current).toBe(true);
  });

  test('ignores edges connected to other ports', () => {
    // Given
    const edges = [{
      id: 'e1',
      source: 'block-0',
      sourceHandle: 'out',
      target: 'block-2',
      targetHandle: 'in'
    }];
    const { result } = renderHook(() =>
      usePortConnected('block-1', 'in', edges)
    );

    // Then
    expect(result.current).toBe(false);
  });
});
```

---

## Manual Test Scenarios

### User Story 1: Visual Port Identification (P1)

#### Scenario 1.1: Unconnected Block Markers

**Test Steps**:
1. Open test notebook and create new diagram
2. Add a Gain block to canvas
3. Observe the block without making any connections

**Expected Results**:
- ✅ Input port (left side) displays left-pointing triangle marker
- ✅ Output port (right side) displays right-pointing triangle marker
- ✅ Markers positioned on block edge, centered on ports
- ✅ Markers use indigo color (primary-600)

**Pass Criteria**: All 4 expected results visible

---

#### Scenario 1.2: Multiple Block Types

**Test Steps**:
1. Add one of each block type: Gain, TransferFunction, StateSpace, Sum, IOMarker
2. Observe all blocks on canvas

**Expected Results**:
- ✅ Gain: Left input triangle, right output triangle
- ✅ TransferFunction: Left input triangle, right output triangle
- ✅ StateSpace: Left input triangle, right output triangle
- ✅ Sum: 4 input triangles (top, left, bottom, right), 1 output triangle (center right)
- ✅ IOMarker (input): Right output triangle only
- ✅ IOMarker (output): Left input triangle only

**Pass Criteria**: All markers present with correct orientation per block type

---

### User Story 2: Connection State Visibility (P2)

#### Scenario 2.1: Connect Two Blocks

**Test Steps**:
1. Add two Gain blocks (Gain1, Gain2)
2. Verify markers visible on all ports
3. Connect Gain1 output to Gain2 input
4. Observe marker visibility

**Expected Results**:
- ✅ Before connection: All 4 ports show markers (2 per block)
- ✅ After connection: Gain1 output marker disappears
- ✅ After connection: Gain2 input marker disappears
- ✅ After connection: Gain1 input marker still visible (unconnected)
- ✅ After connection: Gain2 output marker still visible (unconnected)

**Pass Criteria**: Only connected ports hide markers, unconnected ports retain markers

---

#### Scenario 2.2: Delete Connection

**Test Steps**:
1. Starting from Scenario 2.1 end state (two connected blocks)
2. Select the connection edge
3. Press Delete or use context menu to remove connection
4. Observe marker visibility

**Expected Results**:
- ✅ Gain1 output marker reappears
- ✅ Gain2 input marker reappears
- ✅ All 4 ports now show markers again

**Pass Criteria**: Markers immediately reappear on both disconnected ports

---

#### Scenario 2.3: Block with Mixed Connections

**Test Steps**:
1. Add a Sum block (4 inputs + 1 output)
2. Connect only 2 of the 4 input ports
3. Leave 2 input ports and output port unconnected

**Expected Results**:
- ✅ Connected input ports: Markers hidden
- ✅ Unconnected input ports: Markers visible
- ✅ Output port: Marker visible (unconnected)

**Pass Criteria**: Markers selectively visible based on per-port connection state

---

### User Story 3: Horizontal Flip Orientation (P3)

#### Scenario 3.1: Flip Unconnected Block

**Test Steps**:
1. Add a Gain block
2. Verify markers: left-pointing input, right-pointing output
3. Right-click block → select "Flip"
4. Observe marker orientation

**Expected Results**:
- ✅ Before flip: Input marker on left edge pointing left, output marker on right edge pointing right
- ✅ After flip: Input marker on RIGHT edge pointing RIGHT (into block interior)
- ✅ After flip: Output marker on LEFT edge pointing LEFT (away from block)
- ✅ Directional semantics maintained (input always points in, output always points out)

**Pass Criteria**: Markers move to opposite edges but maintain correct directional semantics

---

#### Scenario 3.2: Flip Connected Block

**Test Steps**:
1. Connect two Gain blocks (Gain1 → Gain2)
2. Flip Gain2 (right block)
3. Observe marker behavior

**Expected Results**:
- ✅ Gain2 input marker remains hidden (still connected)
- ✅ Gain2 output marker (now on left edge) points left (away from block)
- ✅ No markers appear on connected ports despite flip

**Pass Criteria**: Flip doesn't make hidden markers reappear, orientation correct for visible markers

---

### Edge Cases & Clarifications

#### Scenario E1: Drag-and-Drop Hover

**Test Steps**:
1. Add two Gain blocks
2. Start dragging from Gain1 output port
3. Hover over Gain2 input port WITHOUT releasing
4. Observe Gain2 input marker

**Expected Results**:
- ✅ While hovering: Gain2 input marker disappears (destination marker hidden during hover)
- ✅ Gain1 output marker remains visible during drag (source marker stays visible)
- ✅ If drag canceled: Gain2 input marker reappears

**Pass Criteria**: Destination marker disappears on hover, source marker remains during drag

---

#### Scenario E2: Rapid Connect/Disconnect

**Test Steps**:
1. Add two Gain blocks
2. Rapidly connect and disconnect them 5 times in quick succession (within 2 seconds)
3. Observe marker behavior

**Expected Results**:
- ✅ Markers toggle visibility on each action (may flicker)
- ✅ Final state matches connection state (if connected, hidden; if not, visible)
- ✅ No visual glitches or stuck markers

**Pass Criteria**: Markers update immediately on each action, no stale state

---

#### Scenario E3: Very Small Block

**Test Steps**:
1. Create a diagram, save to JSON
2. Manually edit JSON to set a Gain block to very small size (20x20px)
3. Load diagram
4. Observe marker rendering

**Expected Results**:
- ✅ Markers render at full 10px size regardless of block size
- ✅ Markers may overlap block content (acceptable per spec clarification)
- ✅ No visual corruption or missing markers

**Pass Criteria**: Markers render at full fixed size, overlap if necessary

---

## Performance Validation

### Scenario P1: Large Diagram

**Test Steps**:
1. Create diagram with 50 blocks
2. Leave all blocks unconnected (100 visible markers)
3. Pan and zoom canvas
4. Measure frame rate

**Expected Results**:
- ✅ Smooth 60fps panning/zooming
- ✅ All markers visible and correctly oriented
- ✅ No lag or stutter during interaction

**Pass Criteria**: Frame rate stays above 30fps during interaction

---

### Scenario P2: Connection Toggle Performance

**Test Steps**:
1. Add two Gain blocks
2. Use browser DevTools Performance tab
3. Record while connecting/disconnecting 10 times
4. Analyze marker visibility update latency

**Expected Results**:
- ✅ Marker visibility updates within 50ms of connection state change
- ✅ No excessive re-renders of unaffected components

**Pass Criteria**: Latency <50ms per spec success criteria

---

## Test Execution Checklist

Before merging feature:

### Automated Tests
- [ ] All PortMarker component tests pass
- [ ] All usePortConnected hook tests pass
- [ ] Code coverage >80% for new components

### Manual Visual Tests
- [ ] US1 Scenario 1.1: Unconnected markers visible
- [ ] US1 Scenario 1.2: All block types correct
- [ ] US2 Scenario 2.1: Connect hides markers
- [ ] US2 Scenario 2.2: Disconnect shows markers
- [ ] US2 Scenario 2.3: Mixed connections correct
- [ ] US3 Scenario 3.1: Flip orientation correct
- [ ] US3 Scenario 3.2: Flip with connections correct
- [ ] E1: Drag hover hides destination
- [ ] E2: Rapid toggle no glitches
- [ ] E3: Small blocks render correctly

### Performance Tests
- [ ] P1: Large diagram 60fps
- [ ] P2: Toggle latency <50ms

### Regression Tests
- [ ] Existing connection functionality unchanged
- [ ] Existing flip functionality unchanged
- [ ] No breaking changes to block rendering

---

## Debugging Tips

### Marker Not Visible

1. Check React DevTools: Is `isConnected` prop true when it shouldn't be?
2. Inspect edges array: Does an edge reference this port incorrectly?
3. Check CSS: Is parent Handle opacity/visibility hiding marker?

### Wrong Orientation

1. Verify `direction` prop matches port type (input/output)
2. Check `isFlipped` value in block component
3. Inspect triangle points calculation in geometry utility

### Performance Issues

1. Use React DevTools Profiler to identify unnecessary re-renders
2. Add `React.memo()` to PortMarker if needed
3. Check if edges array is being recreated unnecessarily

---

## Success Criteria Validation

Map test scenarios to spec success criteria:

| Success Criterion | Test Scenario(s) | Measurement |
|-------------------|------------------|-------------|
| SC-001: Identify port direction <1 second | US1 1.1, 1.2 | Visual verification |
| SC-002: Markers disappear <100ms | US2 2.1, P2 | DevTools Performance |
| SC-003: 100% flip correctness | US3 3.1, 3.2 | Manual verification |
| SC-004: 30% error reduction | (Requires telemetry) | Post-deployment metric |

---

This quickstart provides comprehensive coverage of all user stories, edge cases, and performance targets defined in the specification.
