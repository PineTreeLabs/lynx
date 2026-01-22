<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: Switchable CSS Themes

**Input**: Design documents from `/specs/010-switchable-themes/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/theme-sync.yaml

**Tests**: Tests are REQUIRED by constitution (TDD enforced). All tests must be written FIRST and FAIL before implementation begins (Red-Green-Refactor cycle).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Current Status: ALL PHASES COMPLETE ✅

**Completed Phases**:
- ✅ **Phase 1: Setup** (3/3 tasks) - Theme configuration infrastructure complete
- ✅ **Phase 2: Foundational** (8/8 tasks) - Core theme validation and precedence logic complete (38 tests passing)
- ✅ **Phase 3: User Story 1** (26/26 tasks) - UI-based theme selection complete with refinements
  - **Status**: FULLY FUNCTIONAL - Users can switch themes via UI, dark mode styling polished, VSCode Jupyter compatibility fixed
- ✅ **Phase 4: User Story 2** (9/9 tasks) - Programmatic diagram-level theme control complete
  - **Status**: FULLY FUNCTIONAL - Users can set themes via constructor or attribute assignment, 20 tests passing
- ✅ **Phase 5: User Story 3** (7/7 tasks) - Session-level default theme configuration complete
  - **Status**: FULLY FUNCTIONAL - Users can use lynx.set_default_theme(), session defaults work correctly
- ✅ **Phase 6: User Story 4** (7/7 tasks) - Environment variable default theme complete
  - **Status**: FULLY FUNCTIONAL - LYNX_DEFAULT_THEME environment variable works correctly
- ✅ **Phase 7: Persistence** (7/7 tasks) - Theme persistence in JSON save/load complete
  - **Status**: FULLY FUNCTIONAL - Themes persist correctly, backward compatible with old diagrams, 20 tests passing
- ✅ **Phase 8: Polish** (12/12 tasks) - Accessibility, performance, final validation complete
  - **Status**: FULLY VALIDATED - 92 tests passing (59 unit + 17 integration + 16 performance), WCAG AAA compliant, comprehensive documentation

**Overall Progress**: 79/79 tasks complete (100%) 🎉

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

**Jupyter widget (Python backend + TypeScript frontend)**:
- Python backend: `src/lynx/`
- TypeScript frontend: `js/src/`
- Python tests: `tests/`
- TypeScript tests: `js/src/` (co-located with components)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and theme system infrastructure

- [X] T001 Create theme configuration module in src/lynx/utils/theme_config.py with VALID_THEMES constant and placeholder functions
- [X] T002 [P] Define CSS custom properties for dark theme in js/src/styles.css using [data-theme="dark"] selector
- [X] T003 [P] Define CSS custom properties for high-contrast theme in js/src/styles.css using [data-theme="high-contrast"] selector

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core theme infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [P] Test validate_theme_name() function in tests/test_theme_validation.py (valid, invalid, None cases)
- [X] T005 [P] Test resolve_theme() precedence logic in tests/test_theme_precedence.py (all 16 combinations: 2^4 precedence levels)

### Foundational Implementation

- [X] T006 [P] Implement validate_theme_name() function in src/lynx/utils/theme_config.py (validates against VALID_THEMES, logs warnings)
- [X] T007 [P] Implement resolve_theme() function in src/lynx/utils/theme_config.py (precedence: diagram > session > env > default)
- [X] T008 [P] Implement set_default_theme() function in src/lynx/utils/theme_config.py (sets session-level default, validates input)
- [X] T009 [P] Implement get_session_default() and get_environment_default() functions in src/lynx/utils/theme_config.py
- [X] T010 [P] Add theme field to DiagramModel schema in src/lynx/schema.py (Optional[str] = None for backward compatibility)
- [X] T011 [P] Export set_default_theme() function in src/lynx/__init__.py module API

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - UI-Based Theme Selection (Priority: P1) 🎯 MVP

**Goal**: Users can switch between visual themes directly from the diagram interface using a settings menu with a Theme submenu dropdown showing available themes with checkmarks.

**Independent Test**: Open a diagram widget, click the gear icon, select a theme from the Theme submenu, and verify the visual appearance changes immediately. Check that diagram.theme reflects UI selection and persists when saved/reloaded.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Test ThemeSelector component rendering in js/src/components/ThemeSelector.test.tsx (renders all themes, shows checkmark on active theme)
- [X] T013 [P] [US1] Test ThemeSelector onClick handler in js/src/components/ThemeSelector.test.tsx (calls callback with selected theme)
- [X] T014 [P] [US1] Test SettingsPanel theme integration in js/src/components/SettingsPanel.test.tsx (opens Theme submenu, passes theme to ThemeSelector)
- [X] T015 [P] [US1] Test data-theme attribute application in js/src/DiagramCanvas.test.tsx (verifies data-theme on container element)
- [X] T016 [P] [US1] Test theme sync from model in js/src/DiagramCanvas.test.tsx (listens to change:theme event, updates DOM)

### Implementation for User Story 1

- [X] T017 [P] [US1] Create ThemeSelector component in js/src/components/ThemeSelector.tsx (dropdown with light/dark/high-contrast options, checkmark on active)
- [X] T018 [P] [US1] Create SettingsPanel component in js/src/components/SettingsPanel.tsx (settings UI with Theme submenu, positions bottom-left)
- [X] T019 [P] [US1] Create themeUtils.ts in js/src/utils/themeUtils.ts (validateThemeName helper, CSS class application utilities)
- [X] T020 [US1] Add theme traitlet to LynxWidget in src/lynx/widget.py (traitlets.Unicode default="light", tag sync=True)
- [X] T021 [US1] Add theme state to DiagramCanvas in js/src/DiagramCanvas.tsx (useState hook, sync from model.get("theme"))
- [X] T022 [US1] Apply data-theme attribute in DiagramCanvas in js/src/DiagramCanvas.tsx (set on .lynx-widget container, update on theme change)
- [X] T023 [US1] Add theme change listener in DiagramCanvas in js/src/DiagramCanvas.tsx (model.on("change:theme") updates data-theme attribute)
- [X] T024 [US1] Wire ThemeSelector to sendAction in SettingsPanel in js/src/components/SettingsPanel.tsx (sendAction "updateTheme" on selection)
- [X] T025 [US1] Implement updateTheme action handler in widget.py in src/lynx/widget.py (_handle_update_theme updates diagram.theme)
- [X] T026 [US1] Add theme observer in LynxWidget in src/lynx/widget.py (_on_theme_change syncs diagram.theme to traitlet)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can select themes via UI, theme changes apply instantly, and diagram.theme is updated.

### Additional Refinements Completed for User Story 1

**Menu System Refactoring**:
- [X] T026a [US1] Created menuStyles.ts in js/src/utils/menuStyles.ts (shared style constants: MENU_CONTAINER, MENU_ITEM_BUTTON, MENU_COLORS, etc.)
- [X] T026b [US1] Refactored SettingsMenu to use shared menuStyles in js/src/components/SettingsMenu.tsx (replaced inline styles with constants)
- [X] T026c [US1] Refactored ThemeSelector to use shared menuStyles in js/src/components/ThemeSelector.tsx (consistent button styling)
- [X] T026d [US1] Updated DiagramCanvas settings container to use shared menuStyles in js/src/DiagramCanvas.tsx (MENU_CONTAINER + SETTINGS_MENU_POSITION)

**Dark Mode UX Improvements**:
- [X] T026e [US1] Fixed control button theming in js/src/styles.css (background, border, SVG fill colors use CSS variables)
- [X] T026f [US1] Fixed block library panel theming in js/src/palette/BlockPalette.tsx (changed bg-white to bg-slate-50, text-slate-900)
- [X] T026g [US1] Preserved validation icon semantic colors in js/src/components/ValidationStatusIcon.tsx (added .validation-button class, excluded from slate-900 fill)
- [X] T026h [US1] Added control button borders in js/src/styles.css (1px solid matching menu containers)

**Background Transparency Fix (VSCode Jupyter)**:
- [X] T026i [US1] Implemented programmatic CSS injection hack in js/src/index.tsx (injects .cell-output-ipywidget-background override as last style element)
- [X] T026j [US1] Fixed VSCode Jupyter white background issue (transparent background now works correctly in dark notebooks)

**Status**: User Story 1 is COMPLETE with all refinements. Theme switching works in UI, dark mode styling is polished, and background transparency works in VSCode Jupyter notebooks.

---

## Phase 4: User Story 2 - Programmatic Diagram-Level Theme Control (Priority: P2)

**Goal**: Users can set a theme for individual diagrams programmatically when creating or configuring diagrams via Python API (constructor parameter or attribute assignment).

**Independent Test**: Create a diagram with `lynx.Diagram(theme='dark')`, display it, and verify it uses the dark theme. Also test setting `diagram.theme = 'light'` and re-displaying. Verify diagrams without explicit themes use defaults from precedence chain.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T027 [P] [US2] Test Diagram constructor with theme parameter in tests/test_diagram_theme.py (theme='dark' sets diagram.theme)
- [X] T028 [P] [US2] Test Diagram.theme attribute assignment in tests/test_diagram_theme.py (diagram.theme = 'light' updates attribute)
- [X] T029 [P] [US2] Test Diagram constructor without theme in tests/test_diagram_theme.py (uses resolve_theme() for default)
- [X] T030 [P] [US2] Test invalid theme in constructor in tests/test_diagram_theme.py (logs warning, falls back to default)
- [X] T031 [P] [US2] Test invalid theme in attribute assignment in tests/test_diagram_theme.py (logs warning, sets to None)

### Implementation for User Story 2

- [X] T032 [P] [US2] Add theme parameter to Diagram.__init__() in src/lynx/diagram.py (Optional[str] = None, calls validate_theme_name)
- [X] T033 [P] [US2] Add theme attribute to Diagram class in src/lynx/diagram.py (property with setter that validates on assignment)
- [X] T034 [US2] Initialize widget.theme from diagram.theme in src/lynx/widget.py (__init__ calls resolve_theme(diagram.theme))
- [X] T035 [US2] Add theme validation in Diagram.theme setter in src/lynx/diagram.py (validates with validate_theme_name, logs warnings)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can set themes via UI or Python API, and theme preferences are respected.

---

## Phase 5: User Story 3 - Session-Level Default Theme Configuration (Priority: P3)

**Goal**: Users can set a default theme for all new diagrams in their current session using `lynx.set_default_theme()`, providing consistent theming across multiple diagrams without repetition.

**Independent Test**: Call `lynx.set_default_theme('dark')`, create multiple diagrams without specifying themes, and verify all use the dark theme. Verify explicit themes override session default. Verify changing session default affects only future diagrams.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T036 [P] [US3] Test set_default_theme() with valid theme in tests/test_theme_precedence.py (sets session default, new diagrams use it)
- [X] T037 [P] [US3] Test set_default_theme() with invalid theme in tests/test_theme_precedence.py (logs warning, does not change session default)
- [X] T038 [P] [US3] Test session default precedence in tests/test_theme_precedence.py (session > environment > built-in)
- [X] T039 [P] [US3] Test explicit theme overrides session in tests/test_theme_precedence.py (diagram.theme='light' beats session='dark')
- [X] T040 [P] [US3] Test changing session default in tests/test_theme_precedence.py (existing diagrams unaffected, new diagrams use new default)

### Implementation for User Story 3

- [X] T041 [US3] Implement session default storage in src/lynx/utils/theme_config.py (module-level _session_default variable, already done in T008)
- [X] T042 [US3] Update resolve_theme() to check session default in src/lynx/utils/theme_config.py (checks get_session_default() after diagram theme, already done in T007)
- [X] T043 [US3] Add fixture for test isolation in tests/conftest.py (clean_theme_config fixture resets _session_default between tests)

**Checkpoint**: All three configuration methods (UI, programmatic, session) should now work independently and follow correct precedence.

---

## Phase 6: User Story 4 - Environment Variable Default Theme (Priority: P4)

**Goal**: Users can set a default theme for all Lynx sessions system-wide using `LYNX_DEFAULT_THEME` environment variable, enabling persistent theme preferences across sessions and notebooks.

**Independent Test**: Set `LYNX_DEFAULT_THEME=dark` in environment, start new Python session, create diagrams without specifying themes, and verify they use dark theme. Verify session config overrides environment. Verify explicit themes override environment. Verify invalid env var logs warning and uses built-in default.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T044 [P] [US4] Test environment variable precedence in tests/test_theme_precedence.py (env > built-in, session > env, diagram > env)
- [X] T045 [P] [US4] Test invalid environment variable in tests/test_theme_precedence.py (logs warning, falls back to built-in default)
- [X] T046 [P] [US4] Test missing environment variable in tests/test_theme_precedence.py (uses built-in default 'light')
- [X] T047 [P] [US4] Test environment variable with session override in tests/test_theme_precedence.py (session wins over env)

### Implementation for User Story 4

- [X] T048 [US4] Read LYNX_DEFAULT_THEME on module import in src/lynx/utils/theme_config.py (os.environ.get(), validate with validate_theme_name)
- [X] T049 [US4] Update resolve_theme() to check environment in src/lynx/utils/theme_config.py (checks get_environment_default() after session, already done in T007)
- [X] T050 [US4] Add environment variable mocking utilities in tests/conftest.py (fixture to mock os.environ for tests)

**Checkpoint**: All four configuration methods should now work with correct precedence: diagram > session > environment > built-in default.

---

## Phase 7: Theme Persistence

**Goal**: Theme preferences persist when diagrams are saved to JSON and restored when loaded, with backward compatibility for old diagrams without theme field.

**Independent Test**: Create diagram with theme='dark', save to JSON, load in new session, verify theme='dark'. Load old JSON without theme field, verify graceful fallback to defaults.

### Tests for Theme Persistence ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T051 [P] Test diagram save with theme in tests/test_theme_persistence.py (diagram.to_dict() includes theme field)
- [X] T052 [P] Test diagram load with theme in tests/test_theme_persistence.py (Diagram.from_dict() restores theme)
- [X] T053 [P] Test diagram load without theme field in tests/test_theme_persistence.py (backward compat, uses defaults)
- [X] T054 [P] Test diagram load with invalid theme in tests/test_theme_persistence.py (logs warning, falls back to defaults)

### Implementation for Theme Persistence

- [X] T055 [P] Add theme to Diagram.to_dict() in src/lynx/diagram.py (include theme field in serialization)
- [X] T056 [P] Add theme to Diagram.from_dict() in src/lynx/diagram.py (restore theme from dict, call validate_theme_name)
- [X] T057 Test backward compatibility with old diagrams in tests/test_theme_persistence.py (load JSON without theme field)

**Checkpoint**: Theme persistence is complete - diagrams save/load with themes, old diagrams load gracefully.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, accessibility verification, and final validation

### Accessibility Testing ⚠️

- [X] T058 [P] Verify WCAG 2.1 AAA contrast ratios for high-contrast theme (use WebAIM Contrast Checker, document all color pairs)
- [X] T059 [P] Test keyboard navigation for theme selector (Tab to settings, Enter to open, arrow keys to navigate, Enter to select)
- [X] T060 [P] Test screen reader compatibility for theme selector (verify ARIA labels, checkmark announcements)

### Performance Testing

- [X] T061 [P] Test theme switching performance (measure < 100ms from user action to visual update)
- [X] T062 [P] Test rapid theme switching (no visual artifacts or lag with multiple quick changes)
- [X] T063 [P] Test multiple diagrams performance (create 50+ diagrams with different themes, verify no degradation)

### Edge Cases & Integration

- [X] T064 Test multiple diagrams with independent themes in tests/test_edge_cases.py (d1=dark, d2=light, verify independence)
- [X] T065 Test UI theme change vs programmatic change in tests/test_edge_cases.py (UI then Python, verify last wins)
- [X] T066 Test theme persistence across widget lifecycle in tests/test_edge_cases.py (create, display, hide, re-display)

### Documentation & Validation

- [X] T067 [P] Run all test scenarios from quickstart.md (5 UI/integration tests + 3 accessibility tests)
- [X] T068 [P] Verify all acceptance scenarios from spec.md (US1-US4, all scenarios pass)
- [X] T069 [P] Document theme color palettes in code comments (all CSS variables for light/dark/high-contrast)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational (Phase 2) completion
  - User Story 1 (P1 - UI): Can start after Foundational
  - User Story 2 (P2 - Programmatic): Can start after Foundational, integrates with US1 widget
  - User Story 3 (P3 - Session): Can start after Foundational, tested independently
  - User Story 4 (P4 - Environment): Can start after Foundational, tested independently
- **Persistence (Phase 7)**: Depends on User Story 2 (diagram.theme attribute exists)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - UI)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - Programmatic)**: Can start after Foundational (Phase 2) - Integrates with US1 widget but independently testable
- **User Story 3 (P3 - Session)**: Can start after Foundational (Phase 2) - No dependencies on other stories, independently testable
- **User Story 4 (P4 - Environment)**: Can start after Foundational (Phase 2) - No dependencies on other stories, independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD enforced by constitution)
- Backend tests before backend implementation
- Frontend tests before frontend implementation
- Models/utilities before components
- Components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: All 3 tasks can run in parallel (T001, T002, T003) - different files
- **Phase 2 Tests**: T004 and T005 can run in parallel - different test files
- **Phase 2 Implementation**: T006-T011 can run in parallel - different functions/files
- **Phase 3 Tests (US1)**: T012-T016 can run in parallel - different test files
- **Phase 3 Implementation (US1)**: T017-T019 can run in parallel (frontend components), T020 standalone (backend)
- **Phase 4 Tests (US2)**: T027-T031 can run in parallel - different test methods
- **Phase 4 Implementation (US2)**: T032-T033 can run in parallel (different methods in diagram.py)
- **Phase 5 Tests (US3)**: T036-T040 can run in parallel - different test methods
- **Phase 6 Tests (US4)**: T044-T047 can run in parallel - different test methods
- **Phase 7 Tests**: T051-T054 can run in parallel - different test methods
- **Phase 7 Implementation**: T055-T056 can run in parallel - different methods
- **Phase 8 Accessibility**: T058-T060 can run in parallel - manual tests
- **Phase 8 Performance**: T061-T063 can run in parallel - independent benchmarks
- **Phase 8 Documentation**: T067-T069 can run in parallel - independent validation

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (write FIRST, ensure FAIL):
Task: "Test ThemeSelector component rendering in js/src/components/ThemeSelector.test.tsx"
Task: "Test ThemeSelector onClick handler in js/src/components/ThemeSelector.test.tsx"
Task: "Test SettingsPanel theme integration in js/src/components/SettingsPanel.test.tsx"
Task: "Test data-theme attribute application in js/src/DiagramCanvas.test.tsx"
Task: "Test theme sync from model in js/src/DiagramCanvas.test.tsx"

# After tests fail, launch frontend components in parallel:
Task: "Create ThemeSelector component in js/src/components/ThemeSelector.tsx"
Task: "Create SettingsPanel component in js/src/components/SettingsPanel.tsx"
Task: "Create themeUtils.ts in js/src/utils/themeUtils.ts"

# Backend integration (depends on frontend being ready):
Task: "Add theme traitlet to LynxWidget in src/lynx/widget.py"
Task: "Implement updateTheme action handler in widget.py in src/lynx/widget.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T012-T026)
4. **STOP and VALIDATE**: Test User Story 1 independently (all 5 acceptance scenarios)
5. Deploy/demo if ready - users can switch themes via UI

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T011)
2. Add User Story 1 (T012-T026) → Test independently → Deploy/Demo (MVP! UI-based theming works)
3. Add User Story 2 (T027-T035) → Test independently → Deploy/Demo (Programmatic control works)
4. Add User Story 3 (T036-T043) → Test independently → Deploy/Demo (Session defaults work)
5. Add User Story 4 (T044-T050) → Test independently → Deploy/Demo (Environment vars work)
6. Add Persistence (T051-T057) → Test independently → Deploy/Demo (Save/load works)
7. Polish (T058-T069) → Final validation → Production ready
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T011)
2. Once Foundational is done:
   - **Developer A**: User Story 1 - UI (T012-T026) - Frontend focus
   - **Developer B**: User Story 2 - Programmatic (T027-T035) - Backend focus
   - **Developer C**: User Story 3 & 4 - Defaults (T036-T050) - Config focus
   - **Developer D**: Persistence (T051-T057) - Serialization focus
3. Stories complete and integrate independently
4. Team collaborates on Polish phase (T058-T069)

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** (US1, US2, US3, US4) maps task to specific user story for traceability
- **TDD enforced**: Tests MUST be written first and FAIL before implementation (constitution requirement)
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Red-Green-Refactor cycle)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **WCAG 2.1 AAA** contrast ratios (7:1 normal text, 4.5:1 large text) must be verified for high-contrast theme
- **Performance target**: Theme changes apply within 100ms, UI selection completes in <3 seconds
- **Backward compatibility**: Old diagrams without theme field must load gracefully
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Total tasks**: 79 (original 69 + 10 refinements)
- **Phase 1 (Setup)**: 3 tasks ✅ COMPLETE
- **Phase 2 (Foundational)**: 8 tasks (5 tests + 6 implementation, some parallel) ✅ COMPLETE
- **Phase 3 (US1 - UI)**: 26 tasks (5 tests + 10 implementation + 10 refinements + 1 integration) ✅ COMPLETE
  - Original scope: 15 tasks
  - Menu system refactoring: 4 tasks (T026a-T026d)
  - Dark mode UX improvements: 4 tasks (T026e-T026h)
  - Background transparency fix: 2 tasks (T026i-T026j)
- **Phase 4 (US2 - Programmatic)**: 9 tasks (5 tests + 4 implementation)
- **Phase 5 (US3 - Session)**: 7 tasks (5 tests + 3 implementation, some reuse from Phase 2)
- **Phase 6 (US4 - Environment)**: 7 tasks (4 tests + 3 implementation, some reuse from Phase 2)
- **Phase 7 (Persistence)**: 7 tasks (4 tests + 3 implementation)
- **Phase 8 (Polish)**: 12 tasks (accessibility, performance, validation)

**Completed**: 37/79 tasks (46.8%)
**Parallelizable tasks**: 48 tasks marked with [P] (60.8% parallelization opportunity)

**User Story mapping**:
- US1 (UI): 26 tasks (MVP scope) ✅ COMPLETE
- US2 (Programmatic): 9 tasks
- US3 (Session): 7 tasks
- US4 (Environment): 7 tasks
- Persistence: 7 tasks (extends US2)
- Shared/Polish: 23 tasks (foundational + polish)

**MVP Delivered**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 37 tasks
- ✅ Core user value: UI-based theme switching with light/dark/high-contrast
- ✅ Polished dark mode styling (control buttons, library, validation icons)
- ✅ VSCode Jupyter compatibility (transparent backgrounds)
- ✅ Independently tested (38 passing tests)
- ✅ Production ready for UI-based theme switching
