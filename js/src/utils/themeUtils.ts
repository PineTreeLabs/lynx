// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Theme utilities for frontend theme management
 *
 * Provides validation and CSS class application helpers for theme switching.
 */

/** Valid theme names (must match Python VALID_THEMES) */
export const VALID_THEMES = [
  "light",
  "dark",
  "high-contrast",
  "archimedes-light",
  "archimedes-dark",
] as const;

export type ThemeName = (typeof VALID_THEMES)[number];

/**
 * Validate a theme name
 *
 * @param name - Theme name to validate
 * @returns The validated theme name, or "light" as fallback
 */
export function validateThemeName(name: string | null | undefined): ThemeName {
  if (name && VALID_THEMES.includes(name as ThemeName)) {
    return name as ThemeName;
  }
  console.warn(`Invalid theme name: ${name}. Using default "light".`);
  return "light";
}

/**
 * Apply theme to a DOM element via data-theme attribute
 *
 * @param element - DOM element to apply theme to
 * @param theme - Theme name to apply
 */
export function applyThemeToElement(element: HTMLElement, theme: ThemeName): void {
  element.setAttribute("data-theme", theme);
}

/**
 * Get current theme from a DOM element
 *
 * @param element - DOM element to read theme from
 * @returns Current theme name or "light" as default
 */
export function getThemeFromElement(element: HTMLElement): ThemeName {
  const theme = element.getAttribute("data-theme");
  return validateThemeName(theme);
}
