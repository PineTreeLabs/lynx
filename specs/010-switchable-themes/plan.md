<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Switchable CSS Themes

**Branch**: `010-switchable-themes` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-switchable-themes/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a theme system that allows users to switch between light (default), dark, and high-contrast visual themes. Themes can be set via environment variable (`LYNX_DEFAULT_THEME`), session configuration (`lynx.set_default_theme()`), or per-diagram (constructor parameter, attribute assignment, or UI settings). The UI provides a Theme submenu in the settings gear icon with a dropdown showing available themes and a checkmark indicating the current selection. Theme preferences persist in saved diagrams and follow precedence: diagram-level > session-level > environment > built-in default (light).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.9 (frontend)
**Primary Dependencies**: React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Tailwind CSS v4, Pydantic (schema validation)
**Storage**: JSON diagram files (existing persistence layer via Pydantic schemas)
**Testing**: Vitest 2.1.8 + React Testing Library 16.1.0 (frontend), pytest (backend - TDD enforced by constitution)
**Target Platform**: Jupyter Notebook (JupyterLab 3+, Jupyter Notebook 7+), web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Jupyter widget (hybrid Python backend + TypeScript frontend)
**Performance Goals**: Theme changes apply within 100ms, UI selection completes in <3 seconds including navigation
**Constraints**: WCAG 2.1 AAA contrast ratios (7:1 normal text, 4.5:1 large text) for high-contrast theme, backward compatible with existing saved diagrams
**Scale/Scope**: 3 built-in themes (light, dark, high-contrast), extensible for future themes, applies to all blocks/edges/UI components (~10 React components)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Simplicity Over Features**
- ✅ **PASS**: Three built-in themes satisfy core accessibility and user preference needs. Future extensibility is planned but not implemented (no premature abstractions).
- ✅ **PASS**: Theme precedence (diagram > session > environment > default) is minimal viable ordering without complex override logic.
- ✅ **PASS**: UI is a simple dropdown menu in existing settings panel, no new chrome.

**II. Python Ecosystem First**
- ✅ **PASS**: Theme configuration uses standard Python patterns: environment variables (`os.environ`), module-level function (`set_default_theme()`), and object attributes (`diagram.theme`).
- ✅ **PASS**: Themes persist in open JSON format (no vendor lock-in), backward compatible with existing diagrams.
- ✅ **PASS**: Works seamlessly in Jupyter notebooks without special configuration.

**III. Test-Driven Development (NON-NEGOTIABLE)**
- ✅ **PASS**: Backend tests will verify theme precedence logic, validation, and persistence using pytest (TDD enforced).
- ✅ **PASS**: Frontend tests will verify theme rendering, UI interaction, and accessibility using Vitest + React Testing Library (existing test infrastructure).
- ✅ **PASS**: WCAG 2.1 AAA contrast ratios are measurable and testable via automated tools.

**IV. Clean Separation of Concerns**
- ✅ **PASS**: Theme selection logic lives in Python (Diagram class), presentation logic lives in TypeScript (React components).
- ✅ **PASS**: Theme definitions are CSS (presentation), theme state is Python (business logic), communication via anywidget traitlets (clean interface).
- ✅ **PASS**: No UI logic in Python backend, no business logic in frontend components.

**V. User Experience Standards**
- ✅ **PASS**: Theme changes apply within 100ms (CSS variable swaps, no reflow required).
- ✅ **PASS**: UI is immediately accessible via existing settings gear icon, <3 second interaction time.
- ✅ **PASS**: High-contrast theme meets WCAG 2.1 AAA standards (7:1 normal text, 4.5:1 large text) - testable and measurable.

**GATE RESULT: ✅ APPROVED** - All principles satisfied. No complexity violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/010-switchable-themes/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output: Theme system patterns, CSS variable strategies, accessibility
├── data-model.md        # Phase 1 output: Theme entity definitions and state management
├── quickstart.md        # Phase 1 output: Theme usage examples and test scenarios
├── contracts/           # Phase 1 output: Python-JS theme communication contracts
│   └── theme-sync.yaml  # anywidget traitlet schema and action payloads
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure: Jupyter widget (Python backend + TypeScript frontend)**

```text
src/lynx/
├── diagram.py           # [MODIFY] Add theme attribute, validation, precedence logic
├── widget.py            # [MODIFY] Add theme traitlet, action handler for UI theme changes
├── schema.py            # [MODIFY] Add theme field to DiagramModel (Optional[str])
├── __init__.py          # [MODIFY] Export set_default_theme() function
└── utils/
    └── theme_config.py  # [NEW] Theme validation, precedence resolution, env var handling

js/src/
├── styles.css           # [MODIFY] Add [data-theme="dark"] and [data-theme="high-contrast"] palettes
├── DiagramCanvas.tsx    # [MODIFY] Add theme prop, apply data-theme to container, read from diagram_state
├── components/
│   ├── SettingsPanel.tsx      # [NEW] Settings UI with Theme submenu dropdown
│   └── ThemeSelector.tsx      # [NEW] Dropdown menu with checkmark for active theme
└── utils/
    └── themeUtils.ts    # [NEW] Theme validation, CSS class application helpers

tests/
├── test_theme_precedence.py   # [NEW] Test env > session > diagram precedence
├── test_theme_persistence.py  # [NEW] Test theme survives save/load
├── test_theme_validation.py   # [NEW] Test invalid theme fallback
└── js/src/components/
    ├── SettingsPanel.test.tsx  # [NEW] Test settings UI interaction
    └── ThemeSelector.test.tsx  # [NEW] Test theme dropdown behavior
```

**Structure Decision**: This feature touches both Python backend (theme configuration, validation, persistence) and TypeScript frontend (CSS variables, UI controls, rendering). The existing Jupyter widget architecture (anywidget with traitlet syncing) provides clean communication between layers. All color styling already uses CSS variables, making theme switching via `data-theme` attribute straightforward. Tests use existing infrastructure: pytest for Python, Vitest for TypeScript.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Constitution check passed without requiring justification.

---

## Post-Design Constitution Re-Evaluation

*Re-check after Phase 1 design artifacts (research.md, data-model.md, contracts, quickstart.md) are complete.*

**I. Simplicity Over Features**
- ✅ **PASS**: Design maintains three built-in themes only, no premature extensibility abstractions.
- ✅ **PASS**: Theme resolution logic is centralized in a single function (`resolve_theme()`), no complex state machines.
- ✅ **PASS**: UI is a single dropdown component (ThemeSelector), reuses existing SettingsPanel infrastructure.
- ✅ **PASS**: No feature creep: theme preview, animated transitions, and custom themes are explicitly out of scope.

**II. Python Ecosystem First**
- ✅ **PASS**: Theme configuration uses idiomatic Python patterns (os.environ, module-level function, instance attributes).
- ✅ **PASS**: Persistence uses standard Pydantic models with Optional fields (backward compatible with existing JSON files).
- ✅ **PASS**: anywidget traitlets provide standard Jupyter widget integration, no vendor-specific APIs.
- ✅ **PASS**: Zero external dependencies added (uses existing Tailwind CSS v4, Pydantic, anywidget).

**III. Test-Driven Development (NON-NEGOTIABLE)**
- ✅ **PASS**: Test cases defined in quickstart.md for all user stories (UI selection, programmatic control, precedence, persistence).
- ✅ **PASS**: Contract tests specified in theme-sync.yaml (valid/invalid theme names, round-trip sync, error handling).
- ✅ **PASS**: Accessibility tests defined (WCAG AAA contrast ratios, keyboard navigation, screen reader support).
- ✅ **PASS**: Performance tests specified (theme switching <100ms, no degradation with 50+ diagrams).
- ⚠️ **NOTE**: Tests must be written BEFORE implementation (Red-Green-Refactor cycle enforced during `/speckit.implement`).

**IV. Clean Separation of Concerns**
- ✅ **PASS**: Business logic (theme validation, precedence resolution) isolated in `src/lynx/utils/theme_config.py`.
- ✅ **PASS**: Presentation logic (CSS variables, DOM attributes) isolated in TypeScript components and styles.css.
- ✅ **PASS**: Communication layer (traitlets) is declarative and type-safe (anywidget handles serialization).
- ✅ **PASS**: Data model (Theme, Diagram, ThemeConfiguration entities) is independent of UI and persistence layers.

**V. User Experience Standards**
- ✅ **PASS**: Performance target <100ms theme switching is achievable (research.md validates pure CSS cascade approach).
- ✅ **PASS**: Accessibility target WCAG 2.1 AAA is verifiable (research.md documents contrast checking tools).
- ✅ **PASS**: UI interaction target <3 seconds is testable (quickstart.md defines test scenario).
- ✅ **PASS**: Backward compatibility ensures zero breaking changes for existing users (Optional field, graceful fallback).

**FINAL GATE RESULT: ✅ APPROVED** - All principles remain satisfied after design phase. Implementation may proceed to Phase 2 (task generation via `/speckit.tasks` command).

---

## Design Artifacts Summary

All Phase 1 deliverables are complete:

1. **research.md** (767 lines):
   - 6 technical decisions documented with rationale and alternatives
   - CSS variable strategy: data-theme attribute with Tailwind v4
   - WCAG AAA contrast requirements: 7:1 normal text, 4.5:1 large text
   - anywidget pattern: separate theme traitlet (not embedded in diagram_state)
   - Precedence resolution: instance > session > environment > default
   - Backward compatibility: Pydantic Optional field
   - Performance: Pure CSS cascade (no React re-renders)

2. **data-model.md** (428 lines):
   - 4 entities: Theme, Diagram, ThemeConfiguration, LynxWidget
   - Validation rules for theme names and precedence logic
   - State management patterns (Python backend, JavaScript frontend)
   - Persistence schema (Pydantic DiagramModel with Optional theme field)
   - Edge cases documented (invalid themes, multiple diagrams, UI vs. programmatic changes)
   - Performance analysis (theme switching 25-65ms, 150-200 bytes per diagram)
   - Testing considerations (16 precedence test cases, fixtures, integration tests)

3. **contracts/theme-sync.yaml** (492 lines):
   - anywidget traitlet specification: `theme` (bidirectional sync)
   - Action specification: `updateTheme` (JavaScript to Python)
   - 4 state sync patterns (initial load, UI change, Python change, session default)
   - Error handling (4 error cases with detection and response)
   - Performance requirements (4 metrics with targets)
   - Security considerations (validation, no injection risks)
   - 4 test contracts with setup, action, and assertions

4. **quickstart.md** (612 lines):
   - 4 quick examples (UI, programmatic, session default, environment variable)
   - Complete usage guide for all three configuration methods
   - Theme precedence examples with multiple scenarios
   - Theme persistence and backward compatibility examples
   - Validation and error handling examples
   - 5 test scenarios (UI selection, persistence, precedence, independence, performance)
   - 3 accessibility tests (contrast verification, keyboard navigation, screen reader)
   - Troubleshooting guide (5 common issues with solutions)
   - FAQ (6 questions with detailed answers)

**Total Documentation**: ~2,299 lines across 4 files

**Next Command**: `/speckit.tasks` - Generate actionable task list with TDD workflow
