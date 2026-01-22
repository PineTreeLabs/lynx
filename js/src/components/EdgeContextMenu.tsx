// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * EdgeContextMenu - Right-click context menu for connections
 *
 * Provides quick actions: Show/Hide Label, Reset routing to auto, Delete connection
 */

import React, { useEffect, useRef } from "react";

interface EdgeContextMenuProps {
  /** Mouse X position (viewport coordinates) */
  x: number;
  /** Mouse Y position (viewport coordinates) */
  y: number;
  /** ID of the connection */
  connectionId: string;
  /** Whether the connection has custom waypoints */
  hasCustomRouting: boolean;
  /** Whether the connection label is currently visible */
  labelVisible: boolean;
  /** Callback when Show/Hide Label is clicked */
  onToggleLabel: () => void;
  /** Callback when Reset Routing is clicked */
  onResetRouting: () => void;
  /** Callback when Delete is clicked */
  onDelete: () => void;
  /** Callback when menu should close */
  onClose: () => void;
}

/**
 * Context menu for connection actions
 *
 * Shows on right-click with options for:
 * - Show/Hide Label (toggles connection label visibility)
 * - Reset to Auto Routing (only when custom waypoints exist)
 * - Delete Connection
 */
export function EdgeContextMenu({
  x,
  y,
  hasCustomRouting,
  labelVisible,
  onToggleLabel,
  onResetRouting,
  onDelete,
  onClose,
}: EdgeContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    // Close on Escape key
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    // Add listeners with slight delay to avoid immediate closure
    setTimeout(() => {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleEscape);
    }, 100);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [onClose]);

  return (
    <div
      ref={menuRef}
      className="fixed bg-white border border-slate-300 rounded-lg shadow-lg py-1 z-50 min-w-40"
      style={{
        left: `${x}px`,
        top: `${y}px`,
      }}
    >
      {/* Show/Hide Label option (always available) */}
      <button
        onClick={() => {
          onToggleLabel();
          onClose();
        }}
        className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-100 flex items-center gap-2"
      >
        <span>{labelVisible ? "👁️‍🗨️" : "👁️"}</span>
        <span>{labelVisible ? "Hide Label" : "Show Label"}</span>
      </button>

      {/* Reset Routing option (only when custom routing exists) */}
      {hasCustomRouting && (
        <button
          onClick={() => {
            onResetRouting();
            onClose();
          }}
          className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-100 flex items-center gap-2"
        >
          <span>↺</span>
          <span>Reset to Auto Routing</span>
        </button>
      )}

      {/* Delete option (always available) */}
      <button
        onClick={() => {
          onDelete();
          onClose();
        }}
        className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
      >
        <span>🗑️</span>
        <span>Delete Connection</span>
      </button>
    </div>
  );
}
