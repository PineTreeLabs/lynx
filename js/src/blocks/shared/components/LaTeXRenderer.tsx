// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * LaTeXRenderer component - KaTeX wrapper with error handling and auto-scaling.
 *
 * Renders LaTeX mathematical expressions using KaTeX with:
 * - Automatic error handling for invalid LaTeX syntax
 * - CSS transform-based auto-scaling to fit container
 * - Fallback placeholder for rendering errors
 */

import React, { useRef, useEffect, useState } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

interface LaTeXRendererProps {
  /** LaTeX string to render */
  latex: string;
  /** Optional CSS class for styling */
  className?: string;
  /** Enable auto-scaling to fit container (default: true) */
  autoScale?: boolean;
  /** Optional error callback */
  onError?: (error: string) => void;
  /** Horizontal alignment (default: 'center') */
  align?: "left" | "center" | "right";
  /** KaTeX display mode - true for display-style (larger fractions), false for inline (default: false) */
  displayMode?: boolean;
}

/**
 * LaTeXRenderer component - Renders LaTeX with KaTeX and auto-scaling.
 *
 * @example
 * <LaTeXRenderer latex="x^2 + y^2 = z^2" />
 * <LaTeXRenderer latex="\frac{s^2 + 1}{s + 2}" autoScale={true} />
 */
export const LaTeXRenderer: React.FC<LaTeXRendererProps> = ({
  latex,
  className = "",
  autoScale = true,
  onError,
  align = "center",
  displayMode = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLSpanElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [scale, setScale] = useState(1);

  // Render LaTeX with KaTeX
  useEffect(() => {
    if (!contentRef.current) return;

    try {
      // Clear previous error
      setError(null);

      // Render LaTeX using KaTeX
      katex.render(latex, contentRef.current, {
        throwOnError: true,
        displayMode,
        output: "html",
      });
    } catch (err) {
      // Catch KaTeX rendering errors
      const errorMessage = err instanceof Error ? err.message : "Invalid LaTeX syntax";
      setError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    }
  }, [latex, onError, displayMode]);

  // Auto-scaling effect
  useEffect(() => {
    if (!autoScale || !containerRef.current || !contentRef.current || error) {
      setScale(1);
      return;
    }

    // Measure rendered content and container
    const container = containerRef.current;
    const content = contentRef.current;

    const containerRect = container.getBoundingClientRect();
    const contentRect = content.getBoundingClientRect();

    if (contentRect.width === 0 || contentRect.height === 0) {
      setScale(1);
      return;
    }

    // Calculate scale factor (never scale up, only down)
    const scaleX = containerRect.width / contentRect.width;
    const scaleY = containerRect.height / contentRect.height;
    const newScale = Math.min(1, scaleX, scaleY);

    setScale(newScale);
  }, [latex, autoScale, error]);

  // Error fallback UI
  if (error) {
    return (
      <div
        ref={containerRef}
        className={`latex-renderer latex-renderer-error ${className}`}
        style={{ color: "red", fontSize: "0.8em" }}
      >
        <span>Invalid LaTeX</span>
      </div>
    );
  }

  // Map align prop to flex justifyContent value
  const justifyContent =
    align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";

  return (
    <div
      ref={containerRef}
      className={`latex-renderer ${className}`}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent,
        overflow: "hidden",
        width: "100%",
        height: "100%",
      }}
    >
      <span
        ref={contentRef}
        className="katex-content"
        style={{
          transform: `scale(${scale})`,
          transformOrigin: "center",
          transition: "transform 0.1s ease-out",
        }}
      />
    </div>
  );
};
