// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * SettingsMenu - Hierarchical settings menu with cascading submenus
 *
 * Displays a settings menu with sections like Theme that cascade to the right
 * to show their options. Uses click-to-open behavior for better UX.
 */

import React, { useState } from "react";
import ThemeSelector from "./ThemeSelector";
import {
  MENU_CONTAINER,
  MENU_LABEL,
  MENU_ITEM_BUTTON_WITH_CHEVRON,
  SUBMENU_CASCADE,
  MENU_COLORS,
} from "../utils/menuStyles";

export interface SettingsMenuProps {
  /** Currently active theme */
  activeTheme: string;
  /** Callback when theme is selected */
  onThemeChange: (theme: string) => void;
  /** Callback when menu should close */
  onClose: () => void;
}

export default function SettingsMenu({ activeTheme, onThemeChange, onClose }: SettingsMenuProps) {
  const [openSection, setOpenSection] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setOpenSection(openSection === section ? null : section);
  };

  return (
    <div
      style={{
        minWidth: "80px",
      }}
    >
      {/* Theme Section */}
      <div style={{ position: "relative" }}>
        {/* Theme Header - Click to open submenu */}
        <button
          onClick={() => toggleSection("theme")}
          style={{
            ...MENU_ITEM_BUTTON_WITH_CHEVRON,
            background: openSection === "theme" ? MENU_COLORS.activeBg : MENU_COLORS.transparent,
          }}
          onMouseEnter={(e) => {
            if (openSection !== "theme") {
              e.currentTarget.style.background = MENU_COLORS.hoverBg;
            }
          }}
          onMouseLeave={(e) => {
            if (openSection !== "theme") {
              e.currentTarget.style.background = MENU_COLORS.transparent;
            }
          }}
        >
          <span style={MENU_LABEL}>Theme</span>
          <span style={MENU_LABEL}>▶</span>
        </button>

        {/* Theme Submenu - Cascades to the right */}
        {openSection === "theme" && (
          <div
            style={{
              ...MENU_CONTAINER,
              ...SUBMENU_CASCADE,
              minWidth: "140px", // Override to fit "High Contrast" text
            }}
          >
            <ThemeSelector
              activeTheme={activeTheme}
              onThemeChange={(theme) => {
                onThemeChange(theme);
                onClose(); // Close menu after selection
              }}
            />
          </div>
        )}
      </div>

      {/* Future settings sections can be added here */}
      {/* Example:
      <div style={{ position: "relative" }}>
        <button onClick={() => toggleSection("grid")}>
          <span>Grid Settings</span>
          <span>▶</span>
        </button>
        {openSection === "grid" && (
          <div style={{ position: "absolute", left: "100%", bottom: "0" }}>
            Grid options here...
          </div>
        )}
      </div>
      */}
    </div>
  );
}
