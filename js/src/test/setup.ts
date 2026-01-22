// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { afterEach, vi } from "vitest";
import { cleanup, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import React from "react";

// Polyfill for React 19 act compatibility
// @ts-expect-error - React 19 has act but testing library expects old location
if (!React.act) {
  // @ts-expect-error - Adding polyfill for compatibility
  React.act = (callback) => {
    const result = callback();
    return Promise.resolve(result);
  };
}

/**
 * Global helper for React 19 async rendering
 * Use this after render() when you need to wait for components to mount
 * @example
 * render(<MyComponent />);
 * await flushUpdates();
 * // Now component is fully rendered
 */
export const flushUpdates = () => waitFor(() => {}, { timeout: 100 });

// Global cleanup after each test case
// This ensures test isolation and prevents pollution between tests
afterEach(() => {
  // Clean up React components
  cleanup();

  // Reset all timers to real timers (critical for CI stability)
  // Tests that use vi.useFakeTimers() can leave timers in fake mode,
  // breaking subsequent tests that expect real timers
  vi.useRealTimers();

  // Clear all mocks
  vi.clearAllMocks();

  // Restore all mocked functions
  vi.restoreAllMocks();
});
