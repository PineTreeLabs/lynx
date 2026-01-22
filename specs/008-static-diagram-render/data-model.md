<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Static Diagram Render

**Feature**: 008-static-diagram-render
**Date**: 2026-01-13

## Overview

This feature does not introduce new persistent data entities. It adds transient communication structures between Python and JavaScript for the capture workflow.

## Traitlet Communication Structures

### CaptureRequest (Python → JavaScript)

Sent via `_capture_request` traitlet to trigger image export.

```typescript
interface CaptureRequest {
  format: "png" | "svg";     // Output format
  width: number | null;       // Target width (pixels), null for auto
  height: number | null;      // Target height (pixels), null for auto
  transparent: boolean;       // Whether background should be transparent
  timestamp: number;          // Unix timestamp for request deduplication
}
```

**Field Details**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| format | string | Yes | - | Output format: "png" or "svg" |
| width | number | null | No | null | Desired output width in pixels |
| height | number | null | No | null | Desired output height in pixels |
| transparent | boolean | Yes | false | If true, background is transparent |
| timestamp | number | Yes | - | Request timestamp for deduplication |

**Dimension Behavior**:

| width | height | Result |
|-------|--------|--------|
| null | null | Auto-fit to content bounds |
| number | null | Fixed width, height calculated from aspect ratio |
| null | number | Fixed height, width calculated from aspect ratio |
| number | number | Fixed dimensions, content scaled to fit |

### CaptureResult (JavaScript → Python)

Sent via `_capture_result` traitlet with the captured image data.

```typescript
interface CaptureResult {
  success: boolean;          // Whether capture succeeded
  data: string;              // Base64-encoded image data (PNG bytes or SVG string)
  format: "png" | "svg";     // Format of the data
  width: number;             // Actual output width
  height: number;            // Actual output height
  error?: string;            // Error message if success is false
  timestamp: number;         // Matches request timestamp
}
```

**Field Details**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | Yes | True if capture completed successfully |
| data | string | Yes | Base64-encoded PNG bytes, or base64-encoded SVG string |
| format | string | Yes | "png" or "svg" matching the request |
| width | number | Yes | Actual width of output in pixels |
| height | number | Yes | Actual height of output in pixels |
| error | string | No | Error message if success is false |
| timestamp | number | Yes | Echo of request timestamp for correlation |

### ContentBounds (Internal)

Calculated bounding box for diagram content.

```typescript
interface ContentBounds {
  x: number;      // Left edge (canvas coordinates)
  y: number;      // Top edge (canvas coordinates)
  width: number;  // Total width
  height: number; // Total height
}
```

## Existing Data Structures (Unchanged)

### Diagram State

The existing `diagram_state` traitlet structure is reused for capture:

```typescript
interface DiagramState {
  version: string;
  blocks: Block[];
  connections: Connection[];
  _version: number;  // Timestamp for change detection
}
```

### Block

Existing block structure - no changes required:

```typescript
interface Block {
  id: string;
  type: "gain" | "sum" | "transfer_function" | "state_space" | "io_marker";
  position: { x: number; y: number };
  parameters: Parameter[];
  ports: Port[];
  label: string;
  flipped: boolean;
  custom_latex?: string;
  label_visible: boolean;
  width?: number;
  height?: number;
}
```

### Connection

Existing connection structure - no changes required:

```typescript
interface Connection {
  id: string;
  source_block_id: string;
  source_port_id: string;
  target_block_id: string;
  target_port_id: string;
  waypoints: { x: number; y: number }[];
  label: string;
  label_visible: boolean;
}
```

## State Diagram

```
                    ┌─────────────────┐
                    │   Idle State    │
                    │ (no capture)    │
                    └────────┬────────┘
                             │
                    Python sends _capture_request
                             │
                             ▼
                    ┌─────────────────┐
                    │  Capturing...   │
                    │ (JS rendering)  │
                    └────────┬────────┘
                             │
               ┌─────────────┴─────────────┐
               │                           │
          Success                       Failure
               │                           │
               ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │  Result Ready   │         │  Error State    │
    │ (data in b64)   │         │ (error message) │
    └────────┬────────┘         └────────┬────────┘
             │                           │
     Python reads _capture_result        │
             │                           │
             ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │  File Written   │         │ Exception Raised│
    │ (path on disk)  │         │ (ValueError)    │
    └─────────────────┘         └─────────────────┘
```

## Validation Rules

### CaptureRequest Validation

1. **format**: Must be exactly "png" or "svg"
2. **width/height**: If provided, must be positive integers
3. **timestamp**: Must be a positive number (used for deduplication)

### Pre-capture Validation (Python)

1. **Empty Diagram**: `diagram.blocks` must not be empty
   - Error: `ValueError("Cannot render empty diagram: no blocks to display")`

2. **Invalid Extension**: Path must end with `.png` or `.svg`
   - Error: `ValueError("Unsupported file format. Use .png or .svg")`

3. **Unwritable Path**: Parent directory must exist and be writable
   - Error: `IOError("Cannot write to path: {path}")`

## File Output Formats

### PNG Output

- MIME type: `image/png`
- Color depth: 32-bit RGBA (supports transparency)
- Compression: Standard PNG compression
- Typical size: 50KB - 500KB for diagrams

### SVG Output

- MIME type: `image/svg+xml`
- Encoding: UTF-8
- Contains: foreignObject elements for HTML content (KaTeX, block labels)
- Typical size: 10KB - 100KB for diagrams
