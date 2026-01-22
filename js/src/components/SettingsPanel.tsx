// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * SettingsPanel - Settings menu with gear icon trigger
 *
 * Displays a settings button (gear icon) that opens a dropdown menu
 * containing theme selection and other settings.
 */

import React, { useState, useRef, useEffect } from "react";
import ThemeSelector from "./ThemeSelector";

export interface SettingsPanelProps {
  /** Currently active theme */
  activeTheme: string;
  /** Callback when theme is selected */
  onThemeChange: (theme: string) => void;
}

export default function SettingsPanel({ activeTheme, onThemeChange }: SettingsPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  const handleThemeChange = (theme: string) => {
    onThemeChange(theme);
    setIsOpen(false); // Close menu after selection
  };

  return (
    <div
      ref={panelRef}
      style={{
        position: "absolute",
        bottom: "16px",
        left: "16px",
        zIndex: 1000,
      }}
    >
      {/* Settings button (gear icon) */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Settings"
        aria-expanded={isOpen}
        style={{
          width: "32px",
          height: "32px",
          borderRadius: "4px",
          border: "1px solid var(--color-slate-300)",
          background: "var(--color-slate-50)",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "16px",
          boxShadow: "0 2px 4px var(--color-shadow)",
        }}
      >
        ⚙️
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div
          style={{
            position: "absolute",
            bottom: "40px",
            left: "0",
            minWidth: "180px",
            background: "var(--color-slate-50)",
            border: "1px solid var(--color-slate-300)",
            borderRadius: "4px",
            boxShadow: "0 4px 8px var(--color-shadow)",
            overflow: "hidden",
          }}
        >
          {/* Theme submenu */}
          <div style={{ padding: "8px 0" }}>
            <div
              style={{
                padding: "4px 12px",
                fontSize: "12px",
                fontWeight: "bold",
                color: "var(--color-slate-500)",
                textTransform: "uppercase",
              }}
            >
              Theme
            </div>
            <ThemeSelector activeTheme={activeTheme} onThemeChange={handleThemeChange} />
          </div>
        </div>
      )}
    </div>
  );
}
