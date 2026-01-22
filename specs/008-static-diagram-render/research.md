<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Static Diagram Render

**Feature**: 008-static-diagram-render
**Date**: 2026-01-13

## Research Topics

### R1: Frontend Capture Libraries for DOM-to-Image

**Question**: Which JavaScript library should be used to capture rendered DOM content as PNG?

**Research Findings**:

| Library | Weekly Downloads | Last Update | foreignObject Support | Notes |
|---------|------------------|-------------|----------------------|-------|
| html-to-image | 3M+ | Active | Yes | Most popular, well-maintained |
| dom-to-image | 500K+ | 2019 | Partial | Legacy, known issues |
| html2canvas | 4M+ | Active | No (rasterizes) | Works differently, less accurate for SVG |
| modern-screenshot | 100K+ | Active | Yes | Newer, simpler API |

**Decision**: Use `html-to-image`

**Rationale**:
- Most widely used and actively maintained
- Excellent support for SVG foreignObject (critical for KaTeX LaTeX rendering)
- Native transparent background support via `backgroundColor: 'transparent'`
- Works well with React Flow's SVG-based rendering
- TypeScript types included

**Alternatives Considered**:
- `dom-to-image`: Rejected due to maintenance status and foreignObject issues
- `html2canvas`: Rejected because it rasterizes differently, may lose SVG fidelity
- `modern-screenshot`: Viable alternative but less battle-tested

**Integration Pattern**:
```typescript
import { toPng, toSvg } from 'html-to-image';

// PNG export
const dataUrl = await toPng(element, {
  backgroundColor: transparent ? 'transparent' : '#ffffff',
  width: targetWidth,
  height: targetHeight,
});

// SVG export
const svgString = await toSvg(element, {
  backgroundColor: transparent ? 'transparent' : '#ffffff',
});
```

---

### R2: React Flow Viewport Control for Capture

**Question**: How to render React Flow at specific dimensions without user interaction?

**Research Findings**:

React Flow provides several APIs for viewport control:
1. `fitView()` - Fits all nodes in viewport
2. `setViewport({ x, y, zoom })` - Programmatic viewport control
3. `getViewport()` / `getNodes()` - Read current state
4. `fitBounds(bounds, options)` - Fit specific bounds

**Decision**: Use `fitBounds()` with calculated content bounds

**Rationale**:
- Allows precise control over what's visible
- Can calculate bounds from node positions and dimensions
- Supports padding parameter for margins

**Implementation Approach**:
```typescript
// Calculate content bounds
const bounds = getNodesBounds(nodes);

// Add padding
const paddedBounds = {
  x: bounds.x - padding,
  y: bounds.y - padding,
  width: bounds.width + padding * 2,
  height: bounds.height + padding * 2,
};

// Fit viewport to bounds
reactFlowInstance.fitBounds(paddedBounds, { padding: 0 });
```

---

### R3: anywidget Traitlet Communication for Binary Data

**Question**: How to efficiently transfer image data (PNG bytes) from JavaScript to Python via traitlets?

**Research Findings**:

anywidget traitlets support:
1. `Unicode` - String data (good for SVG, base64)
2. `Bytes` - Binary data (less common, serialization overhead)
3. `Dict` - Structured data with strings

**Decision**: Use base64-encoded strings in `Dict` traitlet

**Rationale**:
- Base64 is universally supported, no serialization edge cases
- PNG files are typically small (<1MB for diagrams)
- Dict allows structured response with success/error fields
- Matches existing `_action` pattern in widget

**Data Flow**:
```python
# Python side
_capture_request = traitlets.Dict().tag(sync=True)
_capture_result = traitlets.Dict().tag(sync=True)

# JavaScript side
model.set('_capture_result', {
  success: true,
  data: btoa(String.fromCharCode(...pngBytes)),  // base64
  timestamp: Date.now()
});
```

**Decoding in Python**:
```python
import base64
png_bytes = base64.b64decode(result['data'])
```

---

### R4: Rendering Without Visible Widget Display

**Question**: Can the widget render and capture without being displayed in a notebook cell?

**Research Findings**:

anywidget lifecycle:
1. Widget created in Python → traitlets initialized
2. Widget displayed via `_repr_mimebundle_` → JS loads, renders to DOM
3. Traitlet changes sync bidirectionally

**Challenge**: JavaScript needs DOM element to render React Flow

**Solutions Researched**:
1. **Hidden widget with CSS**: Render but hide with `display: none` - React Flow may not render correctly
2. **Off-screen rendering**: Use `visibility: hidden` + `position: absolute` - Better, DOM still exists
3. **In-memory rendering**: React's `renderToString` - Won't work (no browser APIs)
4. **Headless browser**: Playwright/Puppeteer - Heavy dependency

**Decision**: Use off-screen hidden widget approach

**Rationale**:
- React Flow needs actual DOM to render
- `visibility: hidden` allows full rendering without being visible
- Much simpler than headless browser
- Works in Jupyter and script contexts (with display())

**Implementation**:
```python
def render(diagram, path, **kwargs):
    # Create widget with capture mode flag
    widget = LynxWidget(diagram, _capture_mode=True)

    # Display triggers JS rendering (required for React Flow)
    from IPython.display import display
    display(widget)

    # Send capture request
    widget._capture_request = {...}

    # Wait for result
    # ... polling or callback ...

    # Write file
    with open(path, 'wb') as f:
        f.write(base64.b64decode(widget._capture_result['data']))

    # Close widget
    widget.close()
```

**CSS for Capture Mode**:
```css
.lynx-widget.capture-mode {
  position: absolute;
  left: -9999px;
  visibility: hidden;
}
```

---

### R5: SVG Export Strategy

**Question**: How to export React Flow diagram as clean SVG?

**Research Findings**:

React Flow renders to:
```html
<div class="react-flow">
  <div class="react-flow__viewport">
    <svg>
      <!-- Edges (connections) -->
    </svg>
    <div class="react-flow__nodes">
      <!-- Node elements (blocks) -->
    </div>
  </div>
</div>
```

**Challenge**: Nodes are div elements, not SVG

**Options**:
1. **html-to-image toSvg()**: Creates SVG with foreignObject containing HTML
2. **Extract native SVG**: Get edges SVG + manually convert nodes
3. **React Flow's built-in**: No built-in SVG export

**Decision**: Use `html-to-image.toSvg()` for complete capture

**Rationale**:
- Captures everything including HTML nodes via foreignObject
- Works with KaTeX rendered content
- Simpler than manual conversion
- Output is valid SVG that can be opened in browsers/editors

**Note**: SVG with foreignObject may not work in all vector editors (e.g., Illustrator). For maximum compatibility, PNG is recommended. SVG is best for web embedding or viewing in browsers.

---

### R6: Content Bounds Calculation

**Question**: How to calculate the bounding box that contains all diagram elements?

**Research Findings**:

React Flow provides `getNodesBounds(nodes)`:
```typescript
const bounds = getNodesBounds(nodes);
// Returns: { x, y, width, height }
```

**Additional Considerations**:
1. Block labels extend below blocks (need to account for)
2. Port markers extend outside blocks (small, ~10px)
3. Connection waypoints may curve outside node bounds
4. Arrowhead markers add small extension at targets

**Decision**: Use `getNodesBounds()` with additional padding

**Rationale**:
- React Flow's built-in handles node positions and sizes
- Adding 40px padding accounts for labels, markers, waypoints
- Simpler than calculating every edge case

**Implementation**:
```typescript
const DEFAULT_PADDING = 40; // Accounts for labels, markers, etc.

function calculateContentBounds(nodes: Node[]): Rect {
  const bounds = getNodesBounds(nodes);
  return {
    x: bounds.x - DEFAULT_PADDING,
    y: bounds.y - DEFAULT_PADDING,
    width: bounds.width + DEFAULT_PADDING * 2,
    height: bounds.height + DEFAULT_PADDING * 2,
  };
}
```

---

## Summary of Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| DOM-to-Image library | html-to-image | Best foreignObject support, well-maintained |
| Viewport control | fitBounds() API | Precise control, supports padding |
| Data transfer | Base64 in Dict traitlet | Universal, simple, matches existing patterns |
| Headless rendering | Off-screen hidden widget | Simpler than headless browser, works with React Flow |
| SVG export | html-to-image toSvg() | Complete capture including HTML nodes |
| Bounds calculation | getNodesBounds() + padding | Built-in API, padding handles edge cases |

## Dependencies to Add

**JavaScript (package.json)**:
```json
"dependencies": {
  "html-to-image": "^1.11.11"
}
```

**Python**: No new dependencies required (base64, pathlib are stdlib)
