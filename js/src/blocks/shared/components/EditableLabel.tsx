// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * EditableLabel - Double-click to edit text component
 */

import React, { useState, useCallback, useRef, useEffect } from "react";

interface EditableLabelProps {
  value: string;
  onSave: (newValue: string) => void;
  className?: string;
}

export default function EditableLabel({ value, onSave, className = "" }: EditableLabelProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when entering edit mode
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleDoubleClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      setEditValue(value);
      setIsEditing(true);
    },
    [value]
  );

  const handleBlur = useCallback(() => {
    setIsEditing(false);
    if (editValue.trim() && editValue !== value) {
      onSave(editValue.trim());
    } else {
      setEditValue(value);
    }
  }, [editValue, value, onSave]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        inputRef.current?.blur();
      } else if (e.key === "Escape") {
        setEditValue(value);
        setIsEditing(false);
      }
    },
    [value]
  );

  if (isEditing) {
    return (
      <input
        ref={inputRef}
        type="text"
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        className={`${className} bg-white border border-primary-600 rounded px-1 outline-none`}
        style={{ width: `${Math.max(editValue.length * 7, 80)}px` }}
      />
    );
  }

  return (
    <div
      onDoubleClick={handleDoubleClick}
      className={`${className} cursor-text hover:bg-slate-100 rounded px-1`}
      title="Double-click to edit"
    >
      {value}
    </div>
  );
}
