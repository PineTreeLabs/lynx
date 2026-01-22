// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * BlockContextMenu - Right-click context menu for blocks
 *
 * Provides quick actions: Delete and Flip (for Gain and TransferFunction blocks)
 */

import React, { useEffect, useRef } from "react";

interface BlockContextMenuProps {
  /** Mouse X position (viewport coordinates) */
  x: number;
  /** Mouse Y position (viewport coordinates) */
  y: number;
  /** ID of the block */
  blockId: string;
  /** Type of the block */
  blockType: string;
  /** Whether the block's label is currently visible */
  labelVisible?: boolean;
  /** Callback when Delete is clicked */
  onDelete: () => void;
  /** Callback when Flip is clicked (optional - only for flippable blocks) */
  onFlip?: () => void;
  /** Callback when Show/Hide Label is clicked */
  onToggleLabel?: () => void;
  /** Callback when menu should close */
  onClose: () => void;
}

/**
 * Context menu for block actions
 *
 * Shows on right-click with options for:
 * - Delete (all blocks)
 * - Flip (Gain and TransferFunction only)
 */
export function BlockContextMenu({
  x,
  y,
  labelVisible,
  onDelete,
  onFlip,
  onToggleLabel,
  onClose,
}: BlockContextMenuProps) {
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
      className="fixed bg-white border border-slate-300 rounded-lg shadow-lg py-1 z-50 min-w-32"
      style={{
        left: `${x}px`,
        top: `${y}px`,
      }}
    >
      {/* Show/Hide Label option (always available) */}
      {onToggleLabel && (
        <button
          onClick={() => {
            onToggleLabel();
            onClose();
          }}
          className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-100 flex items-center gap-2"
        >
          <span>{labelVisible ? "🏷️" : "🏷️"}</span>
          <span>{labelVisible ? "Hide Label" : "Show Label"}</span>
        </button>
      )}

      {/* Flip option (all blocks) */}
      {onFlip && (
        <button
          onClick={() => {
            onFlip();
            onClose();
          }}
          className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-100 flex items-center gap-2"
        >
          <span>↔️</span>
          <span>Flip Horizontal</span>
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
        <span>Delete</span>
      </button>
    </div>
  );
}
