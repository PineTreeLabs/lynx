// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Shared styles for cascading menu system
 *
 * Provides consistent styling across Settings menu, submenus, and menu items
 */

import { CSSProperties } from "react";

/** Base container for dropdown menus */
export const MENU_CONTAINER: CSSProperties = {
  background: "var(--color-slate-100)",
  border: "1px solid var(--color-slate-300)",
  borderRadius: "4px",
  boxShadow: "var(--shadow-xl)",
  padding: "4px 0",
  minWidth: "80px",
  zIndex: 1000,
};

/** Button style for menu items */
export const MENU_ITEM_BUTTON: CSSProperties = {
  display: "flex",
  alignItems: "center",
  width: "100%",
  padding: "2px 8px",
  border: "none",
  background: "transparent",
  cursor: "pointer",
  fontSize: "14px",
  textAlign: "left",
};

/** Cascading submenu positioning (appears to the right of parent) */
export const SUBMENU_CASCADE: CSSProperties = {
  position: "absolute",
  left: "100%",
  bottom: "-5px",
  marginLeft: "0px",
};

/** Typography for menu item labels */
export const MENU_LABEL: CSSProperties = {
  fontSize: "12px",
  color: "var(--color-slate-600)",
  fontWeight: 500,
};

/** Layout for buttons with space between label and chevron */
export const MENU_ITEM_BUTTON_WITH_CHEVRON: CSSProperties = {
  ...MENU_ITEM_BUTTON,
  justifyContent: "space-between",
};

/** Layout for buttons with gap between icon and label */
export const MENU_ITEM_BUTTON_WITH_ICON: CSSProperties = {
  ...MENU_ITEM_BUTTON,
  ...MENU_LABEL,
  gap: "2px",
};

/** Colors for interactive states */
export const MENU_COLORS = {
  hoverBg: "var(--color-slate-200)",
  activeBg: "var(--color-slate-200)",
  transparent: "transparent",
};

/** Settings menu container positioning (relative to Controls) */
export const SETTINGS_MENU_POSITION: CSSProperties = {
  position: "absolute",
  left: "42px",
  bottom: "15px",
};
