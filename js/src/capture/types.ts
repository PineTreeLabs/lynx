// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Capture module types for static diagram export
 *
 * Defines interfaces for capture request/result communication between Python and JS
 */

/**
 * Capture request (Python -> JavaScript)
 * Sent via `_capture_request` traitlet to trigger image export
 */
export interface CaptureRequest {
  /** Output format */
  format: "png" | "svg";
  /** Target width in pixels, null for auto */
  width: number | null;
  /** Target height in pixels, null for auto */
  height: number | null;
  /** Whether background should be transparent */
  transparent: boolean;
  /** Unix timestamp for request deduplication */
  timestamp: number;
  /** Filename for download (deprecated - Python handles file saving now) */
  filename: string | null;
  /** Whether to display the image inline in Jupyter (false = just send result to Python) */
  displayInline: boolean;
}

/**
 * Capture result (JavaScript -> Python)
 * Sent via `_capture_result` traitlet with the captured image data
 */
export interface CaptureResult {
  /** Whether capture succeeded */
  success: boolean;
  /** Base64-encoded image data (PNG bytes or SVG string) */
  data: string;
  /** Format of the data */
  format: "png" | "svg";
  /** Actual output width in pixels */
  width: number;
  /** Actual output height in pixels */
  height: number;
  /** Error message if success is false */
  error?: string;
  /** Echo of request timestamp for correlation */
  timestamp: number;
}

/**
 * Content bounds for diagram
 * Calculated bounding box that contains all diagram elements
 */
export interface ContentBounds {
  /** Left edge (canvas coordinates) */
  x: number;
  /** Top edge (canvas coordinates) */
  y: number;
  /** Total width */
  width: number;
  /** Total height */
  height: number;
}
