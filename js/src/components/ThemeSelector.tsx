// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * ThemeSelector - Dropdown menu for selecting visual themes
 *
 * Displays available themes (light, dark, high-contrast, archimedes-light, archimedes-dark)
 * with a checkmark indicating the currently active theme.
 */

import React from "react";
import { MENU_ITEM_BUTTON_WITH_ICON, MENU_COLORS } from "../utils/menuStyles";

export interface ThemeSelectorProps {
  /** Currently active theme */
  activeTheme: string;
  /** Callback when theme is selected */
  onThemeChange: (theme: string) => void;
}

const THEME_OPTIONS = [
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
  { value: "high-contrast", label: "High Contrast" },
  { value: "archimedes-light", label: "Archimedes (Light)" },
  { value: "archimedes-dark", label: "Archimedes (Dark)" },
];

export default function ThemeSelector({ activeTheme, onThemeChange }: ThemeSelectorProps) {
  return (
    <div
      className="theme-selector"
      role="menu"
      aria-label="Theme selection"
      style={{ minWidth: "160px" }}
    >
      {THEME_OPTIONS.map((option) => (
        <button
          key={option.value}
          className="theme-option"
          role="menuitem"
          onClick={() => onThemeChange(option.value)}
          style={MENU_ITEM_BUTTON_WITH_ICON}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = MENU_COLORS.hoverBg;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = MENU_COLORS.transparent;
          }}
        >
          <span style={{ width: "16px", fontWeight: "bold" }}>
            {activeTheme === option.value ? "✓" : ""}
          </span>
          <span>{option.label}</span>
        </button>
      ))}
    </div>
  );
}
