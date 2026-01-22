<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Static Diagram Render

**Branch**: `008-static-diagram-render` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-static-diagram-render/spec.md`

## Summary

Implement a `lynx.render(diagram, path, **kwargs)` function that exports block diagrams as static images (PNG or SVG) by leveraging the existing React frontend rendering. The function will use a frontend capture approach where the JavaScript side renders the diagram in a "capture mode" (hiding UI chrome), then serializes or rasterizes the result and returns it to Python via traitlets. This guarantees visual fidelity with the interactive widget.

## Technical Context

**Language/Version**: TypeScript 5.9 (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget, html-to-image (new), KaTeX 0.16.27
**Storage**: File system (PNG/SVG output files)
**Testing**: Vitest (frontend), pytest (backend)
**Target Platform**: Jupyter notebooks, Python scripts
**Project Type**: Web application (frontend + backend via anywidget)
**Performance Goals**: Render completes in under 5 seconds for diagrams with up to 50 blocks
**Constraints**: Must work without visible widget display; transparent background support
**Scale/Scope**: Single diagram export per call; typical diagrams 1-50 blocks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity Over Features | PASS | Single function API, leverages existing rendering |
| II. Python Ecosystem First | PASS | Python function API, outputs to standard formats |
| III. Test-Driven Development | PASS | Tests required before implementation |
| IV. Clean Separation | PASS | Render logic separate from interactive widget |
| V. User Experience Standards | PASS | Simple `lynx.render()` call, immediate results |

No constitution violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/008-static-diagram-render/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Existing structure (web application with anywidget)
src/lynx/
├── __init__.py          # Add render() export
├── widget.py            # LynxWidget class (existing)
├── diagram.py           # Diagram class (existing)
├── render.py            # NEW: Static render function
└── static/              # Bundled JS (existing)

js/src/
├── index.tsx            # Widget entry point (existing)
├── DiagramCanvas.tsx    # Main canvas (existing)
├── capture/             # NEW: Capture mode components
│   ├── CaptureCanvas.tsx    # Minimal canvas for capture
│   └── captureUtils.ts      # SVG/PNG export utilities
└── utils/
    └── traitletSync.ts  # Add capture action handlers

tests/
├── python/
│   └── test_render.py   # NEW: Python render tests
└── js/                  # Vitest tests (existing structure)
```

**Structure Decision**: Extends existing web application structure. New render functionality is added as a Python module (`render.py`) that coordinates with new JavaScript capture components.

## Complexity Tracking

No constitution violations requiring justification.

## Design Decisions

### D1: Frontend Capture Approach

**Decision**: Use the existing React frontend to render diagrams, then capture via DOM serialization.

**Rationale**:
- Guarantees visual fidelity with interactive widget
- Reuses all existing block rendering code (GainBlock, SumBlock, etc.)
- No need to reimplement SVG generation in Python
- LaTeX rendering (KaTeX) is already working in frontend

**Alternatives Rejected**:
- Pure Python SVG generation: Would require reimplementing all block shapes, LaTeX handling
- Headless browser (Playwright): Heavy dependency, slower startup, complex setup

### D2: Capture Communication Flow

**Decision**: Python → JS (capture request) → JS renders → JS returns data → Python writes file

**Flow**:
1. Python `render()` creates temporary widget with diagram state
2. Python sets `_capture_request` traitlet with parameters (format, dimensions, transparent)
3. JS receives request, renders to off-screen canvas in capture mode
4. For SVG: JS serializes React Flow viewport SVG directly
5. For PNG: JS uses html-to-image library to rasterize
6. JS sets `_capture_result` traitlet with base64-encoded data
7. Python receives result, decodes, writes to file

### D3: Capture Mode Rendering

**Decision**: Create a minimal `CaptureCanvas` component that renders diagram without UI chrome.

**Removed Elements**:
- BlockPalette (block library sidebar)
- ParameterPanel (parameter editor)
- Controls (zoom buttons, settings)
- Background grid dots
- Context menus
- Selection handles and resize handles

**Preserved Elements**:
- All block shapes (Gain triangle, Sum circle, etc.)
- Block labels (below blocks)
- LaTeX content
- Orthogonal connections with arrowheads
- Port markers (triangular arrowheads on unconnected ports)
- Connection labels (when visible)

### D4: Content Bounds Calculation

**Decision**: Calculate bounding box from all block positions and dimensions, add padding.

**Algorithm**:
1. Iterate all blocks, compute min/max x,y considering block dimensions
2. Include connection waypoints in bounds (may extend beyond blocks)
3. Add configurable padding (default 20px)
4. Use this as viewport for capture

### D5: Dimension Handling

**Decision**: Support width-only, height-only, both, or auto-fit modes.

| Input | Behavior |
|-------|----------|
| `width=W, height=H` | Output exactly WxH, scale content to fit |
| `width=W` only | Calculate height from content aspect ratio |
| `height=H` only | Calculate width from content aspect ratio |
| Neither | Use content bounds + padding as dimensions |

### D6: Library Choice for PNG Export

**Decision**: Use `html-to-image` npm package for DOM-to-PNG conversion.

**Rationale**:
- Well-maintained, widely used (3M+ weekly downloads)
- Supports transparent backgrounds natively
- Works with SVG foreignObject (needed for KaTeX text)
- Handles React Flow's SVG structure correctly

**Alternative**: `dom-to-image` - less maintained, issues with foreignObject

## API Design

### Python API

```python
def render(
    diagram: Diagram,
    path: str,
    *,
    width: int | None = None,
    height: int | None = None,
    transparent: bool = False,
) -> None:
    """
    Export diagram as a static image.

    Args:
        diagram: The Diagram instance to render
        path: Output file path. Extension determines format (.png or .svg)
        width: Output width in pixels. If None, auto-calculated.
        height: Output height in pixels. If None, auto-calculated.
        transparent: If True, background is transparent. Default False (white).

    Raises:
        ValueError: If diagram has no blocks
        ValueError: If file extension is not .png or .svg
        IOError: If path is not writable
    """
```

### JavaScript Capture Interface

```typescript
// Capture request (Python → JS)
interface CaptureRequest {
  format: "png" | "svg";
  width: number | null;
  height: number | null;
  transparent: boolean;
  timestamp: number;  // For deduplication
}

// Capture result (JS → Python)
interface CaptureResult {
  success: boolean;
  data: string;  // Base64-encoded PNG or SVG string
  error?: string;
  timestamp: number;
}
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| KaTeX rendering issues in capture | Low | High | Test with complex LaTeX; fallback to text if needed |
| Large diagrams exceed memory | Low | Medium | Document size limits; test with 50+ blocks |
| Transparent background not working in PNG | Medium | Medium | Test html-to-image with transparent flag |
| Capture timing issues (render not complete) | Medium | High | Add render-complete detection; retry logic |

## Implementation Phases

### Phase 1: Core Infrastructure
- Add `_capture_request` and `_capture_result` traitlets to widget
- Create `CaptureCanvas.tsx` component (diagram-only rendering)
- Implement capture request handler in JS
- Basic SVG export (serialization)

### Phase 2: PNG Export
- Integrate html-to-image library
- Implement PNG rasterization
- Support transparent backgrounds

### Phase 3: Dimension & Fit Options
- Content bounds calculation
- Viewport scaling for custom dimensions
- Auto-fit with padding

### Phase 4: Python API & Error Handling
- `lynx.render()` function implementation
- File writing and format detection
- Error handling (empty diagram, invalid path, etc.)

### Phase 5: Testing & Polish
- Unit tests for capture utilities
- Integration tests for full render pipeline
- Performance testing with large diagrams
