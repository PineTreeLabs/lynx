<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Static Diagram Render

**Feature Branch**: `008-static-diagram-render`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "Implement frontend capture approach to support static rendering via lynx.render(diagram, **kwargs) function with SVG/PNG formats, output dimensions, and transparent background option"

## Clarifications

### Session 2026-01-13

- Q: What should happen when rendering an empty diagram? → A: Raise a clear error (e.g., "Cannot render empty diagram: no blocks to display")

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Export Diagram as PNG Image (Priority: P1)

A user has created a control system diagram in Lynx and wants to include it in a report, presentation, or documentation. They call `lynx.render(diagram, "output.png")` from their Python code and receive a PNG image file of their diagram. The image shows only the diagram content (blocks and connections) without any UI controls, toolbars, or block library panels.

**Why this priority**: PNG is the most universally compatible format for embedding in documents, presentations, and web content. This represents the primary use case for static rendering.

**Independent Test**: Can be fully tested by creating a simple diagram with 2-3 connected blocks and calling `lynx.render(diagram, "test.png")`. Delivers immediate value by enabling users to export diagrams for documentation.

**Acceptance Scenarios**:

1. **Given** a diagram with connected blocks, **When** the user calls `lynx.render(diagram, "output.png")`, **Then** a PNG image file is created containing only the diagram content.
2. **Given** a rendered PNG, **When** the user views the image, **Then** they see all blocks with their correct shapes, labels, and parameter values.
3. **Given** a rendered PNG, **When** the user views the image, **Then** no UI elements (toolbar, block library, parameter panel) are visible.
4. **Given** a diagram with LaTeX content in blocks, **When** the user exports to PNG, **Then** the LaTeX equations render correctly in the image.
5. **Given** a diagram with orthogonal connections, **When** the user exports to PNG, **Then** all connections appear with correct routing and arrowheads.

---

### User Story 2 - Export Diagram as SVG Image (Priority: P1)

A user wants to export their diagram as a scalable vector graphic for high-quality printing or web embedding. They call `lynx.render(diagram, "output.svg")` and receive an SVG file that can be scaled to any size without quality loss.

**Why this priority**: SVG is essential for high-quality documentation, academic papers, and vector graphics workflows. It's equally important as PNG for different use cases.

**Independent Test**: Can be fully tested by exporting a diagram to SVG and opening it in a browser or vector graphics editor, verifying that all elements scale cleanly.

**Acceptance Scenarios**:

1. **Given** a diagram with connected blocks, **When** the user calls `lynx.render(diagram, "output.svg")`, **Then** an SVG file is created containing the diagram content.
2. **Given** a rendered SVG, **When** the user scales the image to 4x size, **Then** all lines, shapes, and text remain crisp without pixelation.
3. **Given** a rendered SVG, **When** the user opens it in a vector editor, **Then** the elements are editable vector shapes (not embedded raster images).

---

### User Story 3 - Specify Output Dimensions (Priority: P2)

A user needs their diagram image at specific dimensions for their document layout. They call `lynx.render(diagram, "output.png", width=1200, height=800)` to produce an image at the exact pixel dimensions required.

**Why this priority**: Custom dimensions are critical for professional documentation workflows where images must fit specific layouts. This builds on the basic export functionality.

**Independent Test**: Can be tested by exporting the same diagram at different dimensions and verifying the output file dimensions match the requested values.

**Acceptance Scenarios**:

1. **Given** a diagram, **When** the user calls `lynx.render(diagram, "out.png", width=1200, height=800)`, **Then** the output image is exactly 1200x800 pixels.
2. **Given** specified dimensions, **When** the diagram is rendered, **Then** the diagram content is scaled to fit within the specified dimensions while maintaining aspect ratio.
3. **Given** only width specified (e.g., `width=1200`), **When** the diagram is rendered, **Then** the height is calculated automatically to maintain aspect ratio.
4. **Given** only height specified (e.g., `height=600`), **When** the diagram is rendered, **Then** the width is calculated automatically to maintain aspect ratio.
5. **Given** no dimensions specified, **When** the diagram is rendered, **Then** sensible default dimensions are used based on the diagram content bounds.

---

### User Story 4 - Transparent Background Option (Priority: P2)

A user wants to overlay their diagram on a colored background in their presentation or create a diagram with no background for compositing. They call `lynx.render(diagram, "output.png", transparent=True)` to produce an image with a transparent background.

**Why this priority**: Transparent backgrounds are essential for professional presentations, web design, and document layouts with non-white backgrounds. This is a common export requirement.

**Independent Test**: Can be tested by exporting with `transparent=True` and placing the image over a colored background to verify the background shows through.

**Acceptance Scenarios**:

1. **Given** a diagram, **When** the user calls `lynx.render(diagram, "out.png", transparent=True)`, **Then** the output image has a transparent background (alpha channel).
2. **Given** a transparent PNG placed on a red background, **When** displayed, **Then** the red background is visible around and between diagram elements.
3. **Given** `transparent=False` (default), **When** the diagram is rendered, **Then** the image has a solid white background.
4. **Given** SVG output with `transparent=True`, **When** rendered, **Then** the SVG has no background rectangle element.

---

### User Story 5 - Auto-fit Diagram to Canvas (Priority: P3)

A user has a diagram where blocks are positioned with varying amounts of whitespace around them. When they render the diagram, it automatically fits the content bounds with consistent padding, regardless of where blocks were originally positioned on the infinite canvas.

**Why this priority**: Auto-fitting ensures consistent, professional output without requiring users to manually position their diagrams. This enhances usability but isn't strictly required for basic functionality.

**Independent Test**: Can be tested by creating diagrams with blocks at extreme positions and verifying the output image is cropped to content bounds with consistent margins.

**Acceptance Scenarios**:

1. **Given** a diagram with blocks scattered across a large canvas area, **When** rendered, **Then** the output image is cropped to fit the content bounds plus a small margin.
2. **Given** a diagram with blocks in the top-left corner only, **When** rendered, **Then** the output does not include unnecessary whitespace from the rest of the canvas.
3. **Given** a diagram with a single block, **When** rendered, **Then** the output shows the block centered with appropriate margins.

---

### Edge Cases

- What happens when rendering an empty diagram (no blocks)? (Raises a clear error: "Cannot render empty diagram: no blocks to display")
- What happens when rendering a very large diagram with many blocks? (Should handle gracefully, possibly with reduced quality warning)
- What happens if the specified dimensions are too small for the content? (Content should scale down to fit)
- What happens if the output path is not writable? (Should raise a clear error message)
- What happens if an unsupported file extension is specified? (Should raise a clear error listing supported formats)
- What happens during rendering if the widget is not displayed in a notebook? (Should work without requiring visible widget display)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `lynx.render(diagram, path, **kwargs)` function to export diagrams as static images.
- **FR-002**: System MUST support PNG output format when the path ends with `.png`.
- **FR-003**: System MUST support SVG output format when the path ends with `.svg`.
- **FR-004**: System MUST raise a clear error for unsupported file extensions.
- **FR-005**: System MUST render only diagram content (blocks, connections, labels) without UI elements (toolbar, block library, parameter panel, selection handles, resize handles).
- **FR-006**: System MUST correctly render all block types: Gain (triangle), Sum (circle/ellipse), TransferFunction (rectangle), StateSpace (rectangle), IOMarker (circle).
- **FR-007**: System MUST correctly render LaTeX content in blocks (parameter values, equations).
- **FR-008**: System MUST correctly render orthogonal connections with waypoints and arrowhead markers.
- **FR-009**: System MUST correctly render port markers on unconnected ports.
- **FR-010**: System MUST correctly render connection labels when visible.
- **FR-011**: System MUST accept optional `width` parameter to specify output width in pixels.
- **FR-012**: System MUST accept optional `height` parameter to specify output height in pixels.
- **FR-013**: System MUST maintain diagram aspect ratio when only one dimension is specified.
- **FR-014**: System MUST use sensible default dimensions when no dimensions are specified.
- **FR-015**: System MUST accept optional `transparent` parameter (boolean, default False) to control background transparency.
- **FR-016**: PNG output MUST support alpha channel for transparent backgrounds.
- **FR-017**: SVG output MUST omit background rectangle when transparent is True.
- **FR-018**: System MUST auto-fit diagram content to canvas bounds with consistent padding/margins.
- **FR-019**: System MUST work without requiring the widget to be visibly displayed in a notebook cell.
- **FR-020**: System MUST raise clear, actionable error messages for invalid inputs (unwritable path, etc.).
- **FR-021**: System MUST raise a clear error when attempting to render an empty diagram (no blocks), rather than producing a blank image.

### Key Entities

- **Render Output**: The exported image file (PNG or SVG) containing the static diagram visualization.
- **Content Bounds**: The bounding box encompassing all blocks and connections in the diagram, used for auto-fitting.
- **Output Dimensions**: The pixel width and height of the exported image, either specified by the user or calculated automatically.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can export any diagram to PNG or SVG format with a single function call.
- **SC-002**: Exported images contain all diagram elements (blocks, connections, labels, LaTeX content) with visual fidelity matching the interactive widget.
- **SC-003**: Exported images contain no UI chrome (toolbars, panels, selection handles).
- **SC-004**: Users can specify exact output dimensions and receive images at those dimensions.
- **SC-005**: Transparent background option produces images that composite correctly over other backgrounds.
- **SC-006**: Render operation completes in under 5 seconds for diagrams with up to 50 blocks.
- **SC-007**: Render function works in both Jupyter notebook and standalone Python script contexts.

## Assumptions

- The render function leverages the existing React frontend rendering by capturing from a hidden or headless widget instance.
- The frontend capture approach means visual fidelity is guaranteed to match the interactive display.
- SVG export captures the DOM-rendered SVG elements directly rather than re-generating them.
- PNG export uses canvas or DOM-to-image techniques to rasterize the SVG content.
- The widget JavaScript code will need to support a "capture mode" that hides UI elements and returns image data.
- Python-to-JavaScript communication uses the existing anywidget traitlet mechanism.
- Block labels (shown below blocks) are included in the rendered output.
- Port markers (triangular arrowheads on unconnected ports) are included in the rendered output.
