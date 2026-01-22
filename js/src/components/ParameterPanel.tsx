// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * ParameterPanel - UI for editing block parameters
 *
 * Shows parameter editor when a block is selected.
 * Uses registry pattern to route to block-specific editors.
 */

import React, { useCallback } from "react";
import type { Block } from "../utils/traitletSync";
import { PARAMETER_EDITORS } from "../blocks";
import { LabelEditor } from "../blocks/shared/components";

interface ParameterPanelProps {
  block: Block | null;
  onUpdate: (blockId: string, parameterName: string, value: unknown) => void;
  onClose: () => void;
}

export default function ParameterPanel({ block, onUpdate, onClose }: ParameterPanelProps) {
  // Handle Enter key to close panel when no input is focused
  // IMPORTANT: Must be before any early returns to satisfy React Hooks rules
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        // Check if focus is on an input/textarea inside the panel
        const activeElement = document.activeElement;
        const isInputFocused =
          activeElement instanceof HTMLInputElement || activeElement instanceof HTMLTextAreaElement;

        if (!isInputFocused) {
          e.preventDefault();
          onClose();
        }
      }
    },
    [onClose]
  );

  if (!block) return null;

  // Sum blocks use quadrant-based configuration, not parameter panel
  if (block.type === "sum") return null;

  // Get the appropriate editor component for this block type
  const EditorComponent = PARAMETER_EDITORS[block.type];
  if (!EditorComponent) return null;

  return (
    <div
      tabIndex={0}
      onKeyDown={handleKeyDown}
      className="absolute top-2 right-2 z-10 bg-white rounded shadow-lg min-w-[250px] max-w-[350px] max-h-[280px] flex flex-col focus:outline-none"
    >
      {/* Header */}
      <div className="flex justify-between items-center px-3 py-2 border-b flex-shrink-0">
        <h3 className="text-sm font-semibold">Edit Block Parameters</h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 text-lg leading-none"
          title="Close"
        >
          ×
        </button>
      </div>

      {/* Scrollable content area */}
      <div className="overflow-y-auto flex-1 px-3 py-2">
        {/* Label editor */}
        <LabelEditor
          blockId={block.id}
          initialLabel={block.label || block.id}
          onUpdate={onUpdate}
        />

        {/* Block-specific parameter editor */}
        <EditorComponent block={block} onUpdate={onUpdate} />
      </div>
    </div>
  );
}
