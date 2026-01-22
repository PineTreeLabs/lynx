<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Switchable CSS Themes

**Feature Branch**: `010-switchable-themes`
**Created**: 2026-01-14
**Status**: Draft
**Input**: User description: "Add support for switchable CSS themes - at a minimum, dark, light (default), and high-contrast (accessible), but plan for more in the future.  The theme should be settable in three pre-empting ways.   First, a LYNX_DEFAULT_THEME environment variable; second, a lynx.set_default_theme() configuration function that sets a global variable for the current sessions; third, a per-Diagram attribute that can either be set manually (lynx.Diagram(theme=...)) or via the UI.  In the UI the theme should be settable via the gear-icon settings control button and a Theme submenu, which should propagate to the Diagram attribute (not the set_default_theme global function)."

## Clarifications

### Session 2026-01-14

- Q: High-contrast theme contrast ratios - WCAG 2.1 AA (4.5:1 normal text, 3:1 large text) or AAA (7:1 normal text, 4.5:1 large text)? → A: WCAG 2.1 AAA (7:1 normal text, 4.5:1 large text)
- Q: Theme submenu UI control type - radio buttons, dropdown with checkmark, dropdown with highlighting, or toggle buttons? → A: Dropdown menu with checkmark (checkmark icon next to currently selected theme)
- Q: Should successful theme changes be logged (info/debug level) or only errors/warnings? → A: No logging for successful theme changes (only log errors/warnings)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - UI-Based Theme Selection (Priority: P1)

Users can switch between visual themes directly from the diagram interface using a settings menu, allowing immediate customization of their workspace appearance without writing code.

**Why this priority**: This is the most common way users will interact with themes and delivers immediate visual feedback. It's the core user-facing functionality that can be demonstrated independently.

**Independent Test**: Can be fully tested by opening a diagram widget, clicking the gear icon, selecting a theme from the Theme submenu, and verifying the visual appearance changes. Delivers immediate value as a standalone feature.

**Acceptance Scenarios**:

1. **Given** a diagram is displayed, **When** the user clicks the gear icon settings button, **Then** a settings menu appears with a "Theme" submenu option
2. **Given** the settings menu is open, **When** the user hovers over or clicks the Theme submenu, **Then** a dropdown menu displays all available themes (light, dark, high-contrast) with a checkmark icon next to the currently active theme
3. **Given** the theme submenu is displayed, **When** the user selects a different theme, **Then** the diagram immediately updates to display using the selected theme
4. **Given** a theme is selected via the UI, **When** the user inspects the diagram object, **Then** the diagram's theme attribute reflects the selected theme
5. **Given** a diagram with a UI-selected theme is saved, **When** the diagram is reloaded, **Then** the selected theme persists and is applied automatically

---

### User Story 2 - Programmatic Diagram-Level Theme Control (Priority: P2)

Users can set a theme for individual diagrams programmatically when creating or configuring diagrams, enabling theme selection as part of their Python workflow.

**Why this priority**: This enables programmatic control for users building notebooks or scripts where they want explicit theme control. It's independently valuable for users who prefer code-based configuration and works without UI interaction.

**Independent Test**: Can be fully tested by creating a diagram with `lynx.Diagram(theme='dark')`, displaying it, and verifying it uses the dark theme. Also test setting the theme attribute after creation. Delivers value to programmatic users without requiring UI.

**Acceptance Scenarios**:

1. **Given** a user creates a diagram with `lynx.Diagram(theme='dark')`, **When** the diagram is displayed, **Then** it uses the dark theme
2. **Given** a user creates a diagram with `lynx.Diagram(theme='light')`, **When** the diagram is displayed, **Then** it uses the light theme
3. **Given** a user creates a diagram with `lynx.Diagram(theme='high-contrast')`, **When** the diagram is displayed, **Then** it uses the high-contrast theme
4. **Given** an existing diagram, **When** the user sets `diagram.theme = 'dark'` and re-displays, **Then** the diagram updates to the dark theme
5. **Given** a diagram created without specifying a theme, **When** the diagram is displayed, **Then** it uses the default theme from session or environment configuration

---

### User Story 3 - Session-Level Default Theme Configuration (Priority: P3)

Users can set a default theme for all new diagrams in their current session using a configuration function, providing consistent theming across multiple diagrams without repetition.

**Why this priority**: This convenience feature reduces repetition for users working with multiple diagrams in a single session. It's valuable for users who want consistency but don't want to specify the theme for every diagram. Can be tested independently without UI or environment variables.

**Independent Test**: Can be fully tested by calling `lynx.set_default_theme('dark')`, creating multiple diagrams without specifying themes, and verifying all use the dark theme. Delivers value by reducing code repetition.

**Acceptance Scenarios**:

1. **Given** a user calls `lynx.set_default_theme('dark')`, **When** a new diagram is created without specifying a theme, **Then** it uses the dark theme
2. **Given** a default theme is set via `set_default_theme()`, **When** a diagram is created with an explicit theme parameter, **Then** the explicit theme takes precedence
3. **Given** a default theme is set, **When** the user later calls `set_default_theme('light')`, **Then** all subsequently created diagrams use the light theme
4. **Given** a session starts without calling `set_default_theme()`, **When** diagrams are created, **Then** they fall back to the environment variable or built-in default

---

### User Story 4 - Environment Variable Default Theme (Priority: P4)

Users can set a default theme for all Lynx sessions system-wide using an environment variable, enabling persistent theme preferences across sessions and notebooks.

**Why this priority**: This is the lowest-priority convenience feature, primarily for users who want system-wide theme persistence. It's independently testable but provides the least direct user value since it requires environment configuration before Python execution.

**Independent Test**: Can be fully tested by setting `LYNX_DEFAULT_THEME=dark` in the environment, starting a new Python session, creating diagrams without specifying themes, and verifying they use the dark theme. Delivers value as a system-wide preference.

**Acceptance Scenarios**:

1. **Given** `LYNX_DEFAULT_THEME=dark` is set in the environment, **When** a user creates a diagram without specifying a theme, **Then** it uses the dark theme
2. **Given** `LYNX_DEFAULT_THEME=high-contrast` is set, **When** `set_default_theme('light')` is called, **Then** session configuration overrides the environment variable
3. **Given** `LYNX_DEFAULT_THEME` is set, **When** a diagram is created with an explicit theme parameter, **Then** the explicit theme takes precedence
4. **Given** `LYNX_DEFAULT_THEME` is not set, **When** diagrams are created without theme specifications, **Then** they use the built-in default theme (light)
5. **Given** `LYNX_DEFAULT_THEME` is set to an invalid value, **When** diagrams are created, **Then** the system logs a warning and falls back to the built-in default

---

### Edge Cases

- What happens when a user specifies an invalid theme name (e.g., `lynx.Diagram(theme='purple')`)?
  - System should log a warning and fall back to the default theme
- What happens when a diagram is created with a theme, then the UI changes the theme, and the user later sets `diagram.theme` programmatically?
  - Programmatic setting should take precedence (most recent explicit action wins)
- What happens when a theme is selected via UI, the diagram is saved to JSON, and loaded in an environment where that theme doesn't exist?
  - System should log a warning and fall back to the default theme
- What happens when multiple diagrams are displayed and the user calls `set_default_theme()`?
  - Only newly created diagrams use the new default; existing diagrams retain their current themes
- What happens when a user rapidly switches themes in the UI?
  - Each theme change should be applied immediately without lag or visual artifacts

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide at least three built-in themes: light (default), dark, and high-contrast
- **FR-002**: System MUST support extensibility to add additional themes in the future without breaking changes
- **FR-003**: Users MUST be able to set a system-wide default theme via the `LYNX_DEFAULT_THEME` environment variable
- **FR-004**: Users MUST be able to set a session-wide default theme via the `lynx.set_default_theme()` configuration function
- **FR-005**: Users MUST be able to set a diagram-specific theme via the `lynx.Diagram(theme=...)` constructor parameter
- **FR-006**: Users MUST be able to set a diagram-specific theme via direct attribute assignment (`diagram.theme = ...`)
- **FR-007**: Users MUST be able to set a diagram-specific theme via the UI settings gear icon and Theme submenu
- **FR-008**: System MUST apply themes in the following precedence order (highest to lowest):
  1. Diagram-level theme (set via constructor, attribute, or UI)
  2. Session-level default theme (set via `set_default_theme()`)
  3. Environment variable default theme (`LYNX_DEFAULT_THEME`)
  4. Built-in default theme (light)
- **FR-009**: Theme changes via UI MUST propagate to the diagram's theme attribute, NOT to the session-wide default
- **FR-010**: Theme changes MUST take effect immediately without requiring diagram reload or widget restart
- **FR-011**: Diagram theme preferences MUST persist when diagrams are saved and reloaded
- **FR-012**: System MUST validate theme names and fall back to default for invalid values
- **FR-013**: System MUST log warnings when invalid theme names are provided (successful theme changes are not logged)
- **FR-014**: Settings gear icon MUST display a Theme submenu option that lists all available themes
- **FR-015**: Theme submenu MUST indicate which theme is currently active via a checkmark icon displayed next to the selected theme name
- **FR-016**: High-contrast theme MUST maintain minimum contrast ratios of 7:1 for normal text (under 24px) and 4.5:1 for large text (24px and above) to meet WCAG 2.1 AAA standards

### Key Entities

- **Theme**: A named collection of visual styling rules (colors, contrast levels, typography) that defines the appearance of diagram components
  - Attributes: name (string), visual properties (colors, contrast, font styling)
  - Relationships: Applied to Diagram instances
- **Diagram**: A block diagram instance with an associated theme
  - Attributes: theme (string name), other existing diagram properties
  - Relationships: References one Theme by name
- **Theme Configuration**: Global and session-level theme settings
  - Attributes: environment default (from `LYNX_DEFAULT_THEME`), session default (from `set_default_theme()`)
  - Relationships: Provides fallback theme names when Diagram doesn't specify one

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can switch between light, dark, and high-contrast themes via the UI in under 3 seconds (including menu navigation)
- **SC-002**: Theme changes apply visually within 100 milliseconds of user selection
- **SC-003**: 100% of diagram saves preserve the selected theme correctly when reloaded
- **SC-004**: Theme precedence rules work correctly in 100% of test cases (environment < session < diagram-level)
- **SC-005**: Invalid theme names gracefully fall back to default in 100% of cases without crashing
- **SC-006**: The theme selection UI is accessible via keyboard navigation and screen readers (meets WCAG 2.1 AA for accessibility)
- **SC-008**: High-contrast theme maintains minimum contrast ratios of 7:1 for normal text and 4.5:1 for large text (WCAG 2.1 AAA)
- **SC-007**: Users can programmatically set themes for at least 50 diagrams in a single session without performance degradation

## Assumptions

- Users expect immediate visual feedback when changing themes (no reload required)
- The high-contrast theme will meet WCAG 2.1 AAA accessibility standards with minimum contrast ratios of 7:1 for normal text and 4.5:1 for large text
- Theme changes are cosmetic only and do not affect diagram functionality or data
- Themes apply to all diagram components uniformly (blocks, edges, backgrounds, text, UI controls)
- The settings gear icon already exists in the UI and supports submenus
- Diagram JSON schema can accommodate a new theme field without breaking existing saved diagrams
- Most users will interact with themes via UI (P1), followed by programmatic diagram-level control (P2)
- Environment variable configuration is the least common use case but important for system administrators and CI/CD environments

## Dependencies

- Existing settings gear icon UI component must support submenu functionality
- Diagram serialization/deserialization must support optional theme field
- CSS styling system must support dynamic theme switching (CSS variables or similar)

## Out of Scope

- Custom user-created themes (future enhancement)
- Per-block or per-edge theming (only diagram-wide themes)
- Animated theme transitions
- Theme preview before selection
- Theme editor or theme customization UI
- Synchronization of themes across multiple diagram instances in the same notebook cell
- System-level theme detection (e.g., respecting OS dark mode preference automatically)
