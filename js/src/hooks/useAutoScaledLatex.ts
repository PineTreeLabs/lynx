// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * useAutoScaledLatex hook - Auto-scale LaTeX content to fit container.
 *
 * Measures rendered LaTeX content and calculates appropriate CSS transform scale
 * to fit within container bounds while maintaining aspect ratio.
 *
 * Uses CSS transform for GPU-accelerated scaling without re-rendering.
 */

import { useEffect, useState, RefObject } from "react";

interface UseAutoScaledLatexOptions {
  /** Content selector (default: '.katex') */
  contentSelector?: string;
  /** Enable scaling (default: true) */
  enabled?: boolean;
  /** Allow scaling up (default: false, only scale down) */
  allowScaleUp?: boolean;
}

/**
 * Auto-scale LaTeX content to fit container bounds.
 *
 * @param containerRef - Ref to container element
 * @param options - Scaling options
 * @returns Scale factor (0-1 or >1 if allowScaleUp enabled)
 *
 * @example
 * const containerRef = useRef<HTMLDivElement>(null);
 * const scale = useAutoScaledLatex(containerRef);
 *
 * return (
 *   <div ref={containerRef}>
 *     <div style={{ transform: `scale(${scale})` }}>
 *       {/* LaTeX content *\/}
 *     </div>
 *   </div>
 * );
 */
export function useAutoScaledLatex(
  containerRef: RefObject<HTMLElement>,
  options: UseAutoScaledLatexOptions = {}
): number {
  const { contentSelector = ".katex", enabled = true, allowScaleUp = false } = options;

  const [scale, setScale] = useState(1);

  useEffect(() => {
    if (!enabled || !containerRef.current) {
      setScale(1);
      return;
    }

    const container = containerRef.current;
    const content = container.querySelector(contentSelector) as HTMLElement;

    if (!content) {
      setScale(1);
      return;
    }

    // Measure dimensions
    const containerRect = container.getBoundingClientRect();
    const contentRect = content.getBoundingClientRect();

    // Avoid division by zero
    if (contentRect.width === 0 || contentRect.height === 0) {
      setScale(1);
      return;
    }

    // Calculate scale factors for both dimensions
    const scaleX = containerRect.width / contentRect.width;
    const scaleY = containerRect.height / contentRect.height;

    // Use minimum scale to ensure content fits in both dimensions
    let newScale = Math.min(scaleX, scaleY);

    // Restrict scaling up unless explicitly allowed
    if (!allowScaleUp) {
      newScale = Math.min(1, newScale);
    }

    setScale(newScale);
  }, [containerRef, contentSelector, enabled, allowScaleUp]);

  return scale;
}
