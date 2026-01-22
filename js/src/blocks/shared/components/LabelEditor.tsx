// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * LabelEditor - Editable label field for Parameter Panel
 *
 * Feature 013: Editable Block Labels in Parameter Panel
 * Provides a text input for editing block labels with Enter/blur commit
 * and Escape cancel functionality.
 */

import React, { useState, useRef, useEffect, useLayoutEffect } from "react";

export interface LabelEditorProps {
  blockId: string;
  initialLabel: string;
  onUpdate: (blockId: string, parameterName: string, value: string) => void;
}

/**
 * LabelEditor component for Parameter Panel
 *
 * Displays an always-editable text input for block label editing.
 * Differs from EditableLabel (canvas) which requires double-click to edit.
 */
export function LabelEditor({ blockId, initialLabel, onUpdate }: LabelEditorProps) {
  const [labelValue, setLabelValue] = useState(initialLabel);
  const [originalLabel, setOriginalLabel] = useState(initialLabel);
  const inputRef = useRef<HTMLInputElement>(null);
  // Ref to store the latest value for synchronous access in event handlers
  const latestValueRef = useRef(initialLabel);

  // Sync ref with state (ensures ref always has latest value)
  useLayoutEffect(() => {
    latestValueRef.current = labelValue;
  }, [labelValue]);

  // Sync with external changes to initialLabel
  useEffect(() => {
    setLabelValue(initialLabel);
    setOriginalLabel(initialLabel);
  }, [initialLabel]);

  /**
   * Normalize label value (trim whitespace, replace newlines/tabs with spaces)
   * Per FR-005 (trim) and FR-011 (normalize whitespace)
   */
  const normalizeLabel = (value: string): string => {
    return value
      .replace(/[\n\t]/g, " ") // Replace newlines/tabs with spaces
      .trim(); // Trim leading/trailing whitespace
  };

  /**
   * Handle input change
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLabelValue(e.target.value);
  };

  /**
   * Save label changes (send to Python backend)
   */
  const handleSave = () => {
    // Read from ref to get the latest value (handles timing issues)
    const normalized = normalizeLabel(latestValueRef.current);
    onUpdate(blockId, "label", normalized);
    setOriginalLabel(normalized);
    setLabelValue(normalized);
  };

  /**
   * Handle Enter key (commit changes)
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSave();
      inputRef.current?.blur();
    } else if (e.key === "Escape") {
      // Cancel edit - revert to original
      setLabelValue(originalLabel);
      inputRef.current?.blur();
    }
  };

  /**
   * Handle input blur (commit changes)
   */
  const handleBlur = () => {
    handleSave();
  };

  return (
    <div className="mb-3 pb-3 border-b border-gray-200 flex items-center gap-2">
      <label
        htmlFor={`label-${blockId}`}
        className="text-xs font-medium text-gray-700 whitespace-nowrap"
      >
        Label:
      </label>
      <input
        ref={inputRef}
        id={`label-${blockId}`}
        type="text"
        value={labelValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder={blockId}
      />
    </div>
  );
}
