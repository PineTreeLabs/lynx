<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasks: GitHub Pages Documentation Website

**Input**: Design documents from `/specs/016-github-pages-docs/`
**Prerequisites**: plan.md (complete), spec.md (complete), quickstart.md (manual test procedure)

**Tests**: Tests are NOT required for documentation (TDD exception justified in plan.md - quality assured through build-time validation, notebook execution, and user testing)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Sphinx documentation project structure and configuration

- [X] T001 Create docs/source/ directory structure with subdirectories: _static/, _templates/, api/, examples/, getting-started/
- [X] T002 Create docs/_build/ placeholder in .gitignore (build artifacts excluded from version control)
- [X] T003 [P] Create docs/source/requirements.txt with pinned Sphinx dependencies (Sphinx >=7.0, Furo >=2024.0, myst-parser >=3.0, myst-nb >=1.0, sphinx-design >=0.5, sphinx-copybutton >=0.5, ipykernel >=6.0, jupyter >=1.0, numpy >=1.24, scipy >=1.10, matplotlib >=3.7, python-control >=0.9.4, anywidget >=0.9.0)
- [X] T004 [P] Create docs/source/conf.py with complete Sphinx configuration (extensions: autodoc, autosummary, napoleon, intersphinx, viewcode, myst_nb, sphinx_design, sphinx_copybutton; MyST-NB cache mode with fail-on-error; autodoc exclude private members; Furo theme with light/dark logo; intersphinx mappings for python, numpy, scipy, matplotlib, control)
- [X] T005 [P] Create docs/Makefile with targets: help, clean, html, linkcheck, serve (using sphinx-build with -W flag for warnings-as-errors)
- [X] T006 [P] Create docs/make.bat for Windows build support (equivalent to Makefile targets)
- [X] T007 [P] Create .github/workflows/docs.yml with GitHub Actions workflow (build job: checkout, setup Python 3.11, install UV, install dependencies, cache Sphinx doctrees, cache Jupyter execution, build HTML with -W flag, run linkcheck; deploy job: deploy to GitHub Pages using actions/deploy-pages@v4 on main branch only)
- [X] T008 [P] Add docs build artifacts to .gitignore (docs/_build/, docs/source/api/generated/, docs/source/.jupyter_cache/, docs/source/**/.ipynb_checkpoints/, *.doctree)
- [X] T009 [P] Add [project.optional-dependencies.docs] section to pyproject.toml with same dependencies as requirements.txt
- [X] T010 [P] Create placeholder logo assets in docs/source/_static/ (logo-light.png, logo-dark.png, favicon.svg) - use temporary placeholders if final logos not ready
- [X] T011 Validate local build: run `cd docs && make html` - should generate empty site without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration and empty pages that all user stories will populate

**⚠️ CRITICAL**: No user story content work can begin until this phase is complete

- [X] T012 Create empty docs/source/index.md with landing page placeholder (title, project tagline, navigation placeholders for quickstart/examples/API)
- [X] T013 [P] Create empty docs/source/getting-started/index.md with getting-started section placeholder
- [X] T014 [P] Create empty docs/source/api/index.md with API reference section placeholder
- [X] T015 [P] Create empty docs/source/examples/index.md with examples gallery section placeholder
- [X] T016 [P] Create docs/source/_static/custom.css with minimal Lynx branding CSS overrides (primary color variables, if known)
- [X] T017 Validate foundational structure: run `cd docs && make html` - should build successfully with empty placeholder pages

**Checkpoint**: Foundation ready - user story content can now be written in parallel

---

## Phase 3: User Story 1 - New User Onboarding (Priority: P1) 🎯 MVP

**Goal**: New users can install Lynx and create their first diagram in under 10 minutes by following quickstart guide

**Independent Test**: 3+ first-time users follow docs/source/getting-started/quickstart.md and complete first diagram creation in <10 minutes (validated using specs/016-github-pages-docs/quickstart.md test procedure)

**Success Criteria**: SC-001 (user completes onboarding in <10 min)

### Implementation for User Story 1

- [X] T018 [P] [US1] Write docs/source/index.md landing page with project overview, feature highlights (block-based control system design, interactive Jupyter widget, python-control export), and navigation grid cards to Quickstart, Examples, API Reference
- [X] T019 [P] [US1] Write docs/source/getting-started/installation.md with pip installation instructions (`pip install lynx`), verification command (`python -c "import lynx; print(lynx.__version__)"`), troubleshooting section for common issues
- [X] T020 [US1] Write docs/source/getting-started/quickstart.md with "First Diagram in 5 Minutes" tutorial (import lynx, create diagram, add blocks: IOMarker input, Gain controller, TransferFunction plant, IOMarker output; add connections for feedback loop; save diagram; launch widget in Jupyter; expected: working feedback control diagram with visual output)
- [X] T021 [US1] Add "Next Steps" section to quickstart.md with links to examples gallery and API reference for further learning
- [X] T022 [US1] Update docs/source/index.md with direct link to getting-started/quickstart.md as primary call-to-action
- [X] T023 [US1] Validate quickstart: follow steps in clean Python environment, verify <5 minutes execution time for programmatic workflow

**Checkpoint**: User Story 1 complete - new users can successfully onboard using quickstart guide

---

## Phase 4: User Story 2 - API Discovery and Reference (Priority: P1)

**Goal**: Developers can find any Lynx API method with complete parameter documentation and code examples without reading source code

**Independent Test**: Give developer task "Add a state-space block with custom matrices and export the closed-loop transfer function" - they complete using only API docs (no source code consultation)

**Success Criteria**: SC-002 (all API methods documented with examples)

### Implementation for User Story 2

- [X] T024 [P] [US2] Write docs/source/api/index.md as API landing page with overview sections: Diagram Management (create, save, load), Block Library (5 block types), Connections (add, remove), Validation (check errors), Python-Control Export (get_ss, get_tf); include quick reference table mapping common tasks to API methods
- [X] T025 [P] [US2] Write docs/source/api/diagram.md as curated Diagram class reference with narrative introduction, autosummary table of methods, detailed examples for: creating diagrams, adding blocks with parameters, adding connections, saving/loading JSON files, validation workflow; include `.. autosummary:: lynx.Diagram` directive with `:toctree: generated/` for auto-generated method details
- [X] T026 [P] [US2] Write docs/source/api/blocks.md as curated block types reference with block comparison table (when to use Gain vs TransferFunction vs StateSpace vs Sum vs IOMarker), parameter reference for each block type with mathematical notation, autosummary directives for each block class: `.. autosummary:: lynx.blocks.GainBlock`, `.. autosummary:: lynx.blocks.TransferFunctionBlock`, `.. autosummary:: lynx.blocks.StateSpaceBlock`, `.. autosummary:: lynx.blocks.SumBlock`, `.. autosummary:: lynx.blocks.IOMarker`; include examples: gain with scalar K, transfer function with numerator/denominator arrays, state-space with A/B/C/D matrices, sum block with signs configuration, IOMarker with input/output types
- [X] T027 [P] [US2] Write docs/source/api/validation.md as validation API reference with overview of validation layer (algebraic loops, port connectivity, label uniqueness), autosummary for validation functions, examples: catching ValidationError with block_id context, interpreting error messages, pre-export validation workflow
- [X] T028 [US2] Write docs/source/api/export.md as python-control export guide with signal reference system explanation (3-tier priority: IOMarker labels → connection labels → block_label.output_port), subsystem extraction using `diagram.get_ss(from_signal, to_signal)` and `diagram.get_tf(from_signal, to_signal)`, complete workflow examples: basic closed-loop transfer function, feedback system with subsystem extraction, Sum block sign handling in feedback loops; include code examples with numpy arrays and python-control objects
- [X] T029 [US2] Validate API reference completeness: verify all public methods in lynx.Diagram, lynx.blocks.*, lynx.conversion.* appear in autosummary tables or curated documentation (excluding private methods with underscore prefix per autodoc config)
- [X] T030 [US2] Build docs and verify autodoc generation: run `cd docs && make html`, confirm docs/source/api/generated/ directory contains auto-generated method pages with docstring content, verify intersphinx links to numpy/scipy/matplotlib/control resolve correctly

**Checkpoint**: User Story 2 complete - developers can discover and use any Lynx API method through comprehensive documentation

---

## Phase 5: User Story 3 - Learning Through Examples (Priority: P2)

**Goal**: Users learn Lynx through 3-5 working Jupyter notebook examples covering fundamental control workflows

**Independent Test**: User with basic control theory knowledge works through all example notebooks, successfully modifies example (e.g., change PID gains, swap plant model) to solve related problem without external guidance

**Success Criteria**: SC-004 (all notebooks execute successfully and render correctly)

### Implementation for User Story 3

- [X] T031 [P] [US3] Create docs/source/examples/basic-feedback.ipynb as simple feedback control example (markdown cells: introduction to feedback control, block diagram description; code cells: import lynx, create diagram with IOMarker input, Gain controller K=5, TransferFunction plant [2.0]/[1.0, 3.0], IOMarker output, add forward path connections, add feedback connection; visualize with lynx.edit(); analyze with diagram.get_tf('r', 'y'); plot step response with python-control; markdown conclusion: interpretation of results)
- [X] T032 [P] [US3] Create docs/source/examples/pid-controller.ipynb as PI tuning example (simplified from PID due to improper transfer function issues; markdown cells: PI control theory overview, tuning goals; code cells: create plant model, implement PI controller as TransferFunction block with numerator [Kp, Ki] and denominator [1.0, 0.0], closed-loop diagram assembly; tune gains; plot step response; markdown conclusion: integral action eliminates steady-state error)
- [X] T033 [P] [US3] Create docs/source/examples/state-feedback.ipynb as state-space design example (markdown cells: state-space control introduction, pole placement concepts; code cells: define plant as StateSpace block with A/B/C/D matrices; design state feedback gain K using python-control.place(); create closed-loop diagram with state feedback; export and verify closed-loop poles; simulate step response; markdown conclusion: advantages of state-space design)
- [X] T034 [US3] Write docs/source/examples/index.md as examples gallery landing page with grid cards (sphinx-design `.. grid::` directive) for each notebook: card with title, thumbnail placeholder/first plot, brief description (1-2 sentences), link to notebook page; include "Prerequisites" section listing required Python packages and control theory background; include "Running Examples Locally" section with download instructions
- [X] T035 [US3] Configure myst-nb execution in conf.py for examples: verify `nb_execution_mode = "cache"`, `nb_execution_raise_on_error = True`, `nb_execution_timeout = 60`, `nb_execution_cache_path = "_build/.jupyter_cache"` are set
- [X] T036 [US3] Validate notebook execution: run `cd docs && rm -rf _build/.jupyter_cache && make html` - should execute all 3 notebooks without errors, generate HTML pages with rendered outputs (plots, LaTeX equations, text), verify first build takes ~2-10 minutes depending on notebook complexity
- [X] T037 [US3] Validate incremental builds with caching: modify one notebook cell, run `cd docs && make html` - should re-execute only changed notebook in <30 seconds, reuse cached outputs for unchanged notebooks
- [X] T037.5 [US3] [OPTION B] Convert notebooks to MyST markdown format: convert basic-feedback.ipynb, pid-controller.ipynb, state-feedback.ipynb to .md files with jupytext frontmatter (format_name: myst, kernelspec: python3); delete .ipynb files; update examples/index.md toctree to reference .md files; validate build with `make html` - MyST-NB should execute .md notebooks successfully

**Checkpoint**: User Story 3 complete - users can learn Lynx through executable, well-documented example notebooks

---

## Phase 6: User Story 4 - Understanding Lynx Concepts (Priority: P2)

**Goal**: Users understand Lynx's conceptual model (diagrams, blocks, connections, ports, signal references) to design their own systems independently

**Independent Test**: Interview users after reading getting-started/concepts.md - they explain (without looking at docs) the relationship between blocks, connections, ports, and how signal references work for python-control export

**Success Criteria**: Implicit in SC-001 (users can create diagrams independently after conceptual understanding)

### Implementation for User Story 4

- [X] T038 [P] [US4] Write docs/source/getting-started/concepts.md section "Core Concepts" with definitions and diagrams-as-code examples: Diagram (container for blocks and connections, JSON serialization), Block (computational unit with inputs/outputs: Gain, TransferFunction, StateSpace, Sum, IOMarker), Connection (directed edge from output port to input port with optional waypoints for routing), Port (typed connection point: input vs output, identified by port_id)
- [X] T039 [P] [US4] Write docs/source/getting-started/concepts.md section "Block Types Overview" with comparison table showing when to use each block type: Gain (scalar multiplication, controller gains), TransferFunction (LTI systems in s-domain, plant models), StateSpace (MIMO systems, state feedback, A/B/C/D matrices), Sum (adding/subtracting signals, error calculation, +/- sign configuration), IOMarker (system boundaries, input/output labels for export)
- [X] T040 [US4] Write docs/source/getting-started/concepts.md section "Signal References for Export" explaining 3-tier priority system: (1) IOMarker labels (highest priority, recommended for subsystem boundaries), (2) Connection labels (mid-priority for internal signals), (3) block_label.output_port notation (lowest priority, explicit reference); include examples showing each reference type in diagram.get_ss() and diagram.get_tf() calls
- [X] T041 [US4] Write docs/source/getting-started/concepts.md section "Validation" explaining pre-export checks: algebraic loops detection (feedback without dynamics), port connectivity (all non-IOMarker inputs must be connected), label uniqueness (warnings for duplicate block/connection labels); include example ValidationError with block_id and port_id context, show how to interpret and fix common validation errors
- [X] T042 [US4] Write docs/source/getting-started/concepts.md section "Interactive Widget" explaining relationship between programmatic API and Jupyter widget: diagram created in Python code, lynx.edit(diagram) launches interactive widget, bidirectional sync (UI changes reflected in Python object), use cases (visual verification, manual layout adjustments, exploratory design)
- [X] T043 [US4] Update docs/source/getting-started/index.md with navigation structure: Installation → Quickstart → Core Concepts → API Reference (next steps), add brief section introductions
- [X] T044 [US4] Add cross-references throughout getting-started/ and api/ sections using MyST syntax: `:doc:` links for page references (e.g., `{doc}../api/diagram`), `:ref:` links for section anchors, verify all internal links resolve during build

**Checkpoint**: User Story 4 complete - users understand Lynx conceptual model and can design systems independently

---

## Phase 7: User Story 5 - Visual Design and Navigation (Priority: P3)

**Goal**: Professional, readable documentation experience across devices (mobile, tablet, desktop) with intuitive navigation and consistent branding

**Independent Test**: Load documentation site on mobile (iOS Safari, Android Chrome), desktop (Chrome, Firefox, Safari), toggle dark mode - verify all pages render correctly, logos switch appropriately, navigation works without horizontal scrolling or broken layouts

**Success Criteria**: SC-006 (95%+ mobile usability), SC-008 (dark mode works correctly)

### Implementation for User Story 5

- [X] T045 [P] [US5] Replace placeholder logo assets in docs/source/_static/ with final Lynx logos: logo-light.png (light theme variant, 93KB), logo-dark.png (dark theme variant, 93KB), favicon.svg (site icon); logos are optimized for web (<100KB each)
- [X] T045.5 [P] [US5] [OPTION B] Add comprehensive light/dark CSS variables to conf.py: Lynx brand colors (#6366f1 indigo primary, #1f2937 slate) with complete light_css_variables and dark_css_variables dictionaries covering brand, background, foreground, links, sidebar, admonitions
- [X] T046 [P] [US5] [OPTION B] Update docs/source/_static/custom.css with enhanced dark mode styling: Google Fonts import (Roboto family), dark mode fixes for backgrounds/code blocks/tables, notebook cell styling with Lynx brand colors, theme-aware image handling (.only-light/.only-dark classes), comprehensive syntax highlighting, scrollbar styling
- [X] T047 [US5] Verify Furo theme configuration in conf.py for responsive behavior: `html_theme_options` includes `light_logo`, `dark_logo`, `sidebar_hide_name: False`, `navigation_with_keys: True`, `source_repository`, `source_branch`, `source_directory` - ALL VERIFIED
- [ ] T048 [US5] Test mobile responsiveness using browser DevTools device emulation: iPhone SE (375px width), iPad Mini (768px width), desktop (1920px width); verify hamburger menu appears and functions on narrow screens, no horizontal scrolling at any viewport size, text remains readable (minimum 16px font size), touch targets ≥44px for mobile
- [ ] T049 [US5] Test dark mode on desktop browsers: Chrome, Firefox, Safari; verify logo switches from light to dark variant automatically, code blocks remain readable (syntax highlighting visible), no contrast issues (light text on light backgrounds or dark on dark), LaTeX equations render correctly in both themes
- [ ] T050 [US5] Test navigation usability: verify sidebar shows hierarchical page structure (Getting Started → Installation, Quickstart, Concepts; API Reference → Diagram, Blocks, Validation, Export; Examples → Basic Feedback, PID, State Feedback), verify search functionality (Furo built-in search) returns relevant results for common queries ("add block", "export", "validation"), verify keyboard navigation works (Tab, Enter, arrow keys)
- [ ] T051 [US5] Manual testing on physical devices (if available): iOS Safari on iPhone, Android Chrome on Android phone; validate SC-006 criteria (95%+ mobile usability: no horizontal scroll, readable text, accessible menu)

**Checkpoint**: User Story 5 complete - documentation has professional visual design and works correctly across devices and themes

---

## Phase 8: Deployment & Validation

**Purpose**: Deploy documentation to GitHub Pages and validate all success criteria

- [ ] T052 Configure GitHub Pages in repository settings: Settings → Pages → Source: "GitHub Actions", verify permissions (Settings → Actions → General → Workflow permissions: "Read and write permissions") - **DEFERRED**: Repository private, deployment disabled until ready
- [X] T053 Create feature branch merge-ready commit: ensure all documentation content is complete, run `cd docs && make clean && make html` locally to verify zero warnings, run `cd docs && make linkcheck` to verify zero broken internal links, commit all changes with deployment prep; DEPLOYMENT DISABLED via `if: false` in workflow; docs/DEPLOYMENT.md created with activation instructions
- [ ] T054 Push feature branch and create pull request: push `016-github-pages-docs` branch to origin, create PR to main branch, verify GitHub Actions workflow runs successfully in PR (build job passes, linkcheck passes, HTML artifact uploaded) - **READY**: Awaiting user decision to push
- [ ] T055 Merge to main branch: after PR approval, merge to main, verify GitHub Actions deploy job runs automatically, verify deployment completes within 5 minutes (SC-005)
- [ ] T056 Validate deployed site accessibility: visit GitHub Pages URL (typically https://[username].github.io/lynx/), verify landing page loads correctly, test navigation to all major sections (Getting Started, API Reference, Examples), verify no 404 errors on any internal links
- [ ] T057 Run SC-001 user testing: recruit 3+ first-time users who have never used Lynx, provide only GitHub Pages URL (no additional guidance), time each user following specs/016-github-pages-docs/quickstart.md test procedure, record completion times and pain points, validate all users complete quickstart in <10 minutes, document feedback in test log template (quickstart.md Appendix)
- [ ] T058 Validate SC-002 API documentation completeness: audit all public methods in lynx.Diagram, lynx.blocks.*, lynx.conversion.* against API reference pages, verify each method has: method signature with type hints, parameter descriptions with types and defaults, return type description, at least one code example, verify zero missing public methods
- [ ] T059 Validate SC-003 build quality: run `cd docs && make html` locally with `-W` flag (warnings as errors), verify exit code 0 (zero warnings), check CI build logs for any Sphinx warnings, confirm clean build
- [ ] T060 Validate SC-004 notebook execution: verify all 3 example notebooks executed during build (check build logs for myst-nb execution output), verify rendered notebook pages show correct outputs (plots visible, LaTeX equations rendered, text output present), test notebook downloads work (click download button on each example page, verify .ipynb file downloads correctly)
- [ ] T061 Validate SC-007 link integrity: run `cd docs && make linkcheck`, verify zero broken internal links (exit code 0), review linkcheck output for external link issues (warnings acceptable per plan.md, failures investigated but don't block release)
- [ ] T062 Update repository README.md with documentation link: add "Documentation" section with link to GitHub Pages URL, add badge (optional): `[![Docs](https://img.shields.io/badge/docs-live-brightgreen)](https://[username].github.io/lynx/)`

**Checkpoint**: Documentation deployed and all 8 success criteria validated - feature complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational (Phase 2) completion
  - User stories can proceed in parallel (if team capacity allows)
  - Or sequentially in priority order: US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → US5 (P3)
  - US1 and US2 are both P1 priority (MVP must include both onboarding AND API docs)
- **Deployment (Phase 8)**: Depends on desired user stories being complete (minimum: US1 + US2 for MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (API docs independent of quickstart)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May reference US1 quickstart and US2 API docs in notebook markdown, but notebooks are independently functional
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - References US1 quickstart and US2 API docs via cross-links, but concepts.md can be written independently
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Visual polish applies to all existing pages, so benefits from having US1-US4 content already written, but CSS/logo work is independent

### Within Each User Story

- **US1**: T018-T019 can run in parallel (landing page, installation guide independent), T020 depends on T019 (quickstart references installation), T021-T023 sequential (build on quickstart content)
- **US2**: T024-T028 can run in parallel (all API reference pages are independent Markdown files), T029-T030 sequential (validation requires all pages written first)
- **US3**: T031-T033 can run in parallel (all notebooks are independent), T034 depends on T031-T033 (gallery page links to notebooks), T035-T037 sequential (configuration, then validation)
- **US4**: T038-T042 can run in parallel (all sections of concepts.md can be drafted independently), T043-T044 sequential (navigation and cross-references require all content written)
- **US5**: T045-T047 can run in parallel (logos, CSS, theme config are independent files), T048-T051 sequential (testing requires all prior work complete)

### Parallel Opportunities

- **Phase 1 (Setup)**: T003-T010 all marked [P] - can run in parallel (8 tasks: requirements.txt, conf.py, Makefile, make.bat, docs.yml, .gitignore, pyproject.toml, placeholder logos)
- **Phase 2 (Foundational)**: T013-T016 all marked [P] - can run in parallel (4 tasks: getting-started/index.md, api/index.md, examples/index.md, custom.css)
- **Phase 3 (US1)**: T018-T019 marked [P] - can run in parallel (2 tasks: landing page, installation guide)
- **Phase 4 (US2)**: T024-T028 all marked [P] - can run in parallel (5 tasks: all API reference pages)
- **Phase 5 (US3)**: T031-T033 all marked [P] - can run in parallel (3 tasks: all example notebooks)
- **Phase 6 (US4)**: T038-T042 all marked [P] - can run in parallel (5 tasks: all concepts.md sections)
- **Phase 7 (US5)**: T045-T047 all marked [P] - can run in parallel (3 tasks: logos, CSS, theme config)
- **User Story Parallelization**: After Phase 2, US1-US5 can be worked on in parallel by different team members (each story is in separate files/directories)

---

## Parallel Example: User Story 2 (API Reference)

```bash
# Launch all API reference pages together (after Phase 2 complete):
Task T024: "Write docs/source/api/index.md as API landing page"
Task T025: "Write docs/source/api/diagram.md as curated Diagram class reference"
Task T026: "Write docs/source/api/blocks.md as curated block types reference"
Task T027: "Write docs/source/api/validation.md as validation API reference"
Task T028: "Write docs/source/api/export.md as python-control export guide"

# Then validate sequentially:
Task T029: "Validate API reference completeness"
Task T030: "Build docs and verify autodoc generation"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

**Rationale**: Both US1 (New User Onboarding) and US2 (API Reference) are P1 priority. Documentation is not useful without both quickstart AND comprehensive API docs.

1. Complete Phase 1: Setup (T001-T011) - ~2 hours
2. Complete Phase 2: Foundational (T012-T017) - ~1 hour
3. Complete Phase 3: User Story 1 (T018-T023) - ~4 hours
4. Complete Phase 4: User Story 2 (T024-T030) - ~6 hours
5. **STOP and VALIDATE**: Run local build, test quickstart with 1 internal user
6. Complete Phase 8: Deployment (T052-T056) - ~2 hours
7. **MVP DEPLOYED**: Validate SC-001 (user testing), SC-002 (API completeness), SC-005 (deployment)
8. **Total MVP effort**: ~15 hours for US1+US2+deployment

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + empty pages → ~3 hours
2. **MVP** (Phase 3-4): US1+US2 → Test → Deploy → ~10 hours (cumulative 13 hours)
3. **Examples** (Phase 5): US3 → Test → Deploy → +6 hours (cumulative 19 hours)
4. **Concepts** (Phase 6): US4 → Test → Deploy → +4 hours (cumulative 23 hours)
5. **Polish** (Phase 7): US5 → Test → Deploy → +4 hours (cumulative 27 hours)
6. Each increment adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers working simultaneously:

1. **Day 1**: Team completes Phase 1+2 together (Setup + Foundational) → ~3 hours
2. **Days 2-3**: Once Foundational done:
   - **Developer A**: User Story 1 (Onboarding) → T018-T023 (6 tasks)
   - **Developer B**: User Story 2 (API Reference) → T024-T030 (7 tasks)
   - **Developer C**: User Story 3 (Examples) → T031-T037 (7 tasks)
3. **Day 4**: Developer A finishes US4 (Concepts), Developer B finishes US5 (Visual Polish)
4. **Day 5**: Team validates together (Phase 8 Deployment) → T052-T062 (11 tasks)
5. **Total calendar time**: ~5 days with 2-3 developers (vs ~4 weeks solo)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can be worked on simultaneously
- **[Story] labels**: Map tasks to user stories for traceability and independent story completion
- **No test tasks**: Tests omitted per constitution check (TDD exception) - quality assured through Sphinx build validation, linkcheck, notebook execution, and user testing
- **File paths are exact**: All tasks include absolute paths from repository root for clarity
- **Checkpoints**: Each phase ends with validation checkpoint - stop here to verify story works independently
- **Sphinx warnings as errors**: `-W` flag in Makefile and GitHub Actions treats warnings as build failures (enforces quality)
- **Notebook execution**: MyST-NB cache mode means first build ~10min, incremental <5s - expect long first build time
- **Commit strategy**: Commit after each task or logical group (e.g., all API reference pages together)
- **Success criteria mapping**:
  - SC-001: Validated in T057 (user testing)
  - SC-002: Validated in T058 (API completeness audit)
  - SC-003: Validated in T059 (zero Sphinx warnings)
  - SC-004: Validated in T060 (notebook execution)
  - SC-005: Validated in T055 (deployment within 5 min)
  - SC-006: Validated in T048, T051 (mobile usability)
  - SC-007: Validated in T061 (linkcheck)
  - SC-008: Validated in T049 (dark mode testing)
