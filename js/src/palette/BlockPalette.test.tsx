// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * BlockPalette Tests - Collapsible Block Library
 *
 * Tests for the hover-expandable block palette feature.
 * Following TDD: These tests were written FIRST before implementation.
 */

import React, { act } from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { AnyWidgetModelContext } from "../context/AnyWidgetModel";
import BlockPalette from "./BlockPalette";
import { flushUpdates } from "../test/setup";

// Helper to render with context provider
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const renderWithContext = async (model: any = null) => {
  const result = render(
    <AnyWidgetModelContext.Provider value={model}>
      <BlockPalette />
    </AnyWidgetModelContext.Provider>
  );
  await flushUpdates();
  return result;
};

describe("BlockPalette - Collapsible Block Library", () => {
  // ============================================
  // User Story 1: View Collapsed Library Icon
  // ============================================

  describe("US1: Collapsed Default State", () => {
    it("T006: panel renders collapsed by default (buttons hidden)", async () => {
      await renderWithContext();

      // The button panel should be collapsed (not visible)
      const buttonPanel = screen.getByTestId("button-panel");
      expect(buttonPanel).toHaveClass("max-h-0");
      expect(buttonPanel).toHaveClass("opacity-0");
    });

    it("T007: collapsed header shows 'Library' text", async () => {
      await renderWithContext();

      // The header should show "Library" text
      expect(screen.getByText("Library")).toBeInTheDocument();
    });

    it("T008: collapsed header has consistent styling (border, shadow)", async () => {
      await renderWithContext();

      // The container should have the expected styling classes
      const container = screen.getByTestId("block-palette");
      expect(container).toHaveClass("border-2");
      expect(container).toHaveClass("border-slate-300");
      expect(container).toHaveClass("rounded-lg");
      expect(container).toHaveClass("shadow-lg");
    });
  });

  // ============================================
  // User Story 2: Expand Library on Hover
  // ============================================

  describe("US2: Expand on Hover", () => {
    it("T013: panel expands on mouseEnter event", async () => {
      await renderWithContext();

      const container = screen.getByTestId("block-palette");
      const buttonPanel = screen.getByTestId("button-panel");

      // Initially collapsed
      expect(buttonPanel).toHaveClass("max-h-0");

      // Hover to expand
      fireEvent.mouseEnter(container);

      // Wait for React to re-render after state change
      await waitFor(() => {
        expect(buttonPanel).toHaveClass("max-h-96");
      });
      expect(buttonPanel).toHaveClass("opacity-100");
    });

    it("T014: all 6 buttons visible when expanded", async () => {
      await renderWithContext();

      const container = screen.getByTestId("block-palette");

      // Hover to expand
      fireEvent.mouseEnter(container);

      // Wait for expansion
      await waitFor(() => {
        expect(screen.getByText("Gain")).toBeInTheDocument();
      });

      // All 6 buttons should be present
      expect(screen.getByText("Gain")).toBeInTheDocument();
      expect(screen.getByText("Input")).toBeInTheDocument();
      expect(screen.getByText("Output")).toBeInTheDocument();
      expect(screen.getByText("Sum")).toBeInTheDocument();
      expect(screen.getByText("TF")).toBeInTheDocument();
      expect(screen.getByText("SS")).toBeInTheDocument();
    });

    it("T015: expansion uses CSS transitions for smooth animation", async () => {
      await renderWithContext();

      const buttonPanel = screen.getByTestId("button-panel");

      // Button panel should have transition classes
      expect(buttonPanel).toHaveClass("transition-all");
      expect(buttonPanel).toHaveClass("duration-150");
    });
  });

  // ============================================
  // User Story 3: Collapse Library on Mouse Leave
  // ============================================

  describe("US3: Collapse on Mouse Leave", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("T019: panel collapses on mouseLeave after delay", async () => {
      // Render with real timers first
      vi.useRealTimers();
      await renderWithContext();

      const container = screen.getByTestId("block-palette");
      const buttonPanel = screen.getByTestId("button-panel");

      // Expand first
      fireEvent.mouseEnter(container);
      await waitFor(() => {
        expect(buttonPanel).toHaveClass("max-h-96");
      });

      // Mouse leave - starts a setTimeout
      fireEvent.mouseLeave(container);

      // Should still be expanded immediately (delay not yet elapsed)
      expect(buttonPanel).toHaveClass("max-h-96");

      // Wait for the collapse delay (200ms) plus some buffer
      await waitFor(
        () => {
          expect(buttonPanel).toHaveClass("max-h-0");
        },
        { timeout: 500 }
      );
    });

    it("T020: rapid enter/leave does not cause flickering", async () => {
      // Render with real timers first
      vi.useRealTimers();
      await renderWithContext();

      const container = screen.getByTestId("block-palette");
      const buttonPanel = screen.getByTestId("button-panel");

      // Expand first
      fireEvent.mouseEnter(container);
      await waitFor(() => {
        expect(buttonPanel).toHaveClass("max-h-96");
      });

      // Now switch to fake timers
      vi.useFakeTimers();

      // Leave (starts collapse timeout)
      fireEvent.mouseLeave(container);

      // Re-enter before collapse delay elapses
      act(() => {
        vi.advanceTimersByTime(100); // Only 100ms, delay is 200ms
      });
      fireEvent.mouseEnter(container);

      // Should still be expanded (collapse was cancelled)
      expect(buttonPanel).toHaveClass("max-h-96");

      // Even after waiting longer, should stay expanded
      act(() => {
        vi.advanceTimersByTime(300);
      });
      expect(buttonPanel).toHaveClass("max-h-96");
    });

    it("T021: re-entering panel cancels collapse timeout", async () => {
      // Render with real timers first
      vi.useRealTimers();
      await renderWithContext();

      const container = screen.getByTestId("block-palette");
      const buttonPanel = screen.getByTestId("button-panel");

      // Expand first
      fireEvent.mouseEnter(container);
      await waitFor(() => {
        expect(buttonPanel).toHaveClass("max-h-96");
      });

      // Now switch to fake timers
      vi.useFakeTimers();

      // Leave (starts collapse timeout)
      fireEvent.mouseLeave(container);

      // Wait partial time
      act(() => {
        vi.advanceTimersByTime(150);
      });

      // Re-enter (should cancel timeout)
      fireEvent.mouseEnter(container);

      // Wait past original timeout
      act(() => {
        vi.advanceTimersByTime(200);
      });

      // Should still be expanded (timeout was cancelled)
      expect(buttonPanel).toHaveClass("max-h-96");
    });
  });

  // ============================================
  // User Story 4: Add Block While Panel is Expanded
  // ============================================

  describe("US4: Block Adding While Expanded", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("T025: clicking button does not collapse panel", async () => {
      // Render with real timers first
      vi.useRealTimers();
      await renderWithContext();

      const container = screen.getByTestId("block-palette");
      const buttonPanel = screen.getByTestId("button-panel");

      // Expand first
      fireEvent.mouseEnter(container);
      await waitFor(() => {
        expect(buttonPanel).toHaveClass("max-h-96");
      });

      // Now switch to fake timers
      vi.useFakeTimers();

      // Click a button
      const gainButton = screen.getByText("Gain");
      fireEvent.click(gainButton);

      // Panel should still be expanded
      expect(buttonPanel).toHaveClass("max-h-96");

      // Even after waiting
      act(() => {
        vi.advanceTimersByTime(300);
      });

      // Still expanded (mouse is still inside)
      expect(buttonPanel).toHaveClass("max-h-96");
    });

    it("T026: moving between buttons keeps panel expanded", async () => {
      // Render with real timers
      vi.useRealTimers();
      await renderWithContext();

      const container = screen.getByTestId("block-palette");
      const buttonPanel = screen.getByTestId("button-panel");

      // Expand first
      fireEvent.mouseEnter(container);
      await waitFor(() => {
        expect(buttonPanel).toHaveClass("max-h-96");
      });

      // Simulate moving between buttons (mouse events on buttons)
      const gainButton = screen.getByText("Gain");
      const sumButton = screen.getByText("Sum");

      fireEvent.mouseEnter(gainButton);
      fireEvent.mouseLeave(gainButton);
      fireEvent.mouseEnter(sumButton);

      // Panel should remain expanded throughout
      expect(buttonPanel).toHaveClass("max-h-96");

      // Wait a bit with real timers to ensure no collapse happens
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Verify still expanded
      expect(buttonPanel).toHaveClass("max-h-96");
    });
  });
});
