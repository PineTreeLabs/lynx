<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: GitHub Pages Documentation Website

**Feature Branch**: `016-github-pages-docs`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Create a GitHub pages documentation website based on the API reference and design doc in the dev/ directory"

## Clarifications

### Session 2026-01-21

- Q: When a Jupyter notebook fails to execute during the documentation build, what should happen? → A: Build fails immediately (CI deployment blocked until notebook is fixed)
- Q: How should broken internal links be detected and handled? → A: Build fails if broken internal links detected (Sphinx linkcheck fails build)
- Q: What security measures should be implemented for the documentation website? → A: GitHub Pages default security only (HTTPS automatic, no additional headers)
- Q: Should private methods (prefixed with `_`) be included in the auto-generated API documentation? → A: Exclude all private methods (underscore prefix) from docs
- Q: When GitHub Pages deployment fails in CI/CD, what should happen? → A: CI fails with notification; manual investigation required (no automatic retry)

## User Scenarios & Testing

### User Story 1 - New User Onboarding (Priority: P1)

A new user discovers Lynx through GitHub or PyPI, clicks the documentation link, and successfully installs Lynx and creates their first control system diagram within 10 minutes.

**Why this priority**: The primary goal of documentation is to convert interested users into successful users. Without clear onboarding, users abandon the tool within minutes.

**Independent Test**: Can be fully tested by having a new user (who has never used Lynx) follow the quickstart guide from a fresh Python environment to creating and saving their first feedback control diagram. Success means the user completes the task in under 10 minutes without external help.

**Acceptance Scenarios**:

1. **Given** a user visits the documentation landing page, **When** they scan the page for 30 seconds, **Then** they understand what Lynx does and see clear navigation to quickstart, examples, and API reference
2. **Given** a user follows the quickstart installation instructions, **When** they run the installation command, **Then** Lynx installs successfully in their environment
3. **Given** a user follows the first diagram tutorial, **When** they copy-paste the code examples, **Then** all code executes without errors and produces the expected interactive widget
4. **Given** a user completes the quickstart, **When** they want to explore further, **Then** they see clear next steps directing them to examples or API documentation

---

### User Story 2 - API Discovery and Reference (Priority: P1)

A developer building a control system needs to understand what methods are available on the Diagram class, what parameters each block type accepts, and how to export diagrams to python-control for analysis.

**Why this priority**: API documentation is the most frequently consulted resource after initial onboarding. Without comprehensive API docs, developers spend excessive time reading source code or guessing method signatures.

**Independent Test**: Can be fully tested by giving a developer a specific task (e.g., "Add a state-space block with custom matrices and export the closed-loop transfer function") and verifying they can complete it using only the API documentation without consulting source code or examples.

**Acceptance Scenarios**:

1. **Given** a user searches for "how to add a transfer function block", **When** they navigate to the API reference, **Then** they find the `add_block()` method with clear parameter documentation and code examples
2. **Given** a user wants to understand state-space block parameters, **When** they view the Blocks API page, **Then** they see a complete reference for the A, B, C, D matrices with example values and mathematical notation
3. **Given** a user needs to export a subsystem to python-control, **When** they consult the Export API documentation, **Then** they understand the signal reference system and see examples of using `get_ss()` and `get_tf()` methods
4. **Given** a developer encounters a ValidationError, **When** they search the API docs, **Then** they find exception documentation explaining the error attributes and how to handle it

---

### User Story 3 - Learning Through Examples (Priority: P2)

A control systems student or engineer wants to learn Lynx by studying working examples of feedback control systems, PID controllers, and state-space designs in interactive Jupyter notebooks.

**Why this priority**: Examples accelerate learning by showing complete workflows. They're essential for intermediate users but less critical than getting started (P1) since users need basic knowledge first.

**Independent Test**: Can be fully tested by having a user with basic control theory knowledge work through all example notebooks and successfully modify them (e.g., change PID gains, swap plant models) to solve a related problem without external guidance.

**Acceptance Scenarios**:

1. **Given** a user visits the examples gallery, **When** they scan the available notebooks, **Then** they see 3-5 examples covering fundamental control workflows (basic feedback, PID tuning, state feedback)
2. **Given** a user opens a feedback control example, **When** they read through the notebook, **Then** each code cell is explained with markdown text describing the control theory concepts and Lynx operations
3. **Given** a user wants to run an example locally, **When** they download the notebook file, **Then** it executes successfully in their Jupyter environment with all dependencies installed
4. **Given** a user views the rendered notebook on the website, **When** the page loads, **Then** all plots, outputs, and LaTeX equations render correctly without requiring notebook execution

---

### User Story 4 - Understanding Lynx Concepts (Priority: P2)

A user familiar with Simulink or LabVIEW needs to understand Lynx's conceptual model: what diagrams, blocks, connections, and ports represent, and how the programmatic API relates to the interactive widget.

**Why this priority**: Conceptual understanding enables users to transition from copy-pasting examples to designing their own systems. It's P2 because quickstart (P1) gets users working first, but concept mastery is needed for independent work.

**Independent Test**: Can be fully tested by interviewing users after reading the getting-started guide and asking them to explain (without looking at docs) the relationship between blocks, connections, ports, and how signal references work for python-control export.

**Acceptance Scenarios**:

1. **Given** a user reads the Core Concepts section, **When** they finish reading, **Then** they understand the difference between block IDs, block labels, and signal references
2. **Given** a user learns about the block library, **When** they review the block type summary table, **Then** they know which block type to use for gains, transfer functions, state-space models, and system boundaries
3. **Given** a user reads about signal references, **When** they see the 3-tier priority system, **Then** they understand why IOMarker labels are recommended over connection labels or block.port notation
4. **Given** a user learns about validation, **When** they read the examples, **Then** they know how to check for algebraic loops and port connectivity issues before exporting

---

### User Story 5 - Visual Design and Navigation (Priority: P3)

A user browsing the documentation on mobile, desktop, and dark mode expects a professional, readable experience with intuitive navigation, responsive layout, and consistent branding.

**Why this priority**: While important for professional polish, users can still access content even with imperfect design. This is P3 because functional content (P1/P2) delivers more value than aesthetics.

**Independent Test**: Can be fully tested by loading the documentation site on mobile (iOS Safari, Android Chrome), desktop (Chrome, Firefox, Safari), and toggling dark mode, then verifying all pages render correctly, logos switch appropriately, and navigation works without horizontal scrolling or broken layouts.

**Acceptance Scenarios**:

1. **Given** a user visits the site on a mobile device, **When** they navigate through pages, **Then** all content is readable without horizontal scrolling and the navigation menu is accessible via hamburger icon
2. **Given** a user toggles dark mode, **When** the theme switches, **Then** the logo changes to the dark-mode variant, code blocks remain readable, and no elements show jarring contrast issues
3. **Given** a user is reading API documentation, **When** they want to navigate to a different section, **Then** the sidebar shows their current location and provides quick access to all major sections
4. **Given** a user lands on any page, **When** they look at the page header, **Then** they see consistent Lynx branding and a clear visual hierarchy

---

### Edge Cases

- **Notebook execution failure**: When any example notebook fails to execute during the documentation build (e.g., missing dependency, API change), the CI/CD build MUST fail immediately, blocking deployment until the notebook is fixed. This ensures all published documentation has valid, executable examples.
- **Broken internal links**: When a page is renamed or moved, Sphinx linkcheck MUST detect broken internal cross-references and fail the build, preventing deployment until all links are updated. This ensures users never encounter 404 errors from documentation links.
- **Private method documentation**: Sphinx autodoc MUST be configured to exclude all private methods and attributes (prefixed with `_`) from the auto-generated API documentation. Only public API methods should appear in the documentation to avoid confusing users about internal implementation details.
- **GitHub Pages deployment failure**: When GitHub Pages deployment fails in CI/CD (e.g., permission issues, quota exceeded, Pages disabled), the CI/CD workflow MUST fail with notification via GitHub Actions standard mechanisms (PR status checks, email). No automatic retry is attempted; manual investigation of infrastructure/permission issues is required before re-running deployment.
- **Browser JavaScript support**: The Furo theme requires JavaScript for interactive features (search, navigation, theme toggle). Users with JavaScript disabled will see static content with degraded navigation but all text content remains readable. This is acceptable as <1% of modern browsers disable JavaScript by default.

## Requirements

### Functional Requirements

- **FR-001**: Documentation site MUST be generated using Sphinx with Furo theme and MyST Markdown parser
- **FR-002**: Site MUST include a landing page with project overview, feature highlights, and navigation cards to quickstart, examples, and API reference
- **FR-003**: Site MUST include a quickstart guide enabling users to install Lynx and create their first diagram in under 10 minutes
- **FR-004**: Site MUST include a comprehensive getting-started guide covering core concepts (diagrams, blocks, connections, ports, signal references)
- **FR-005**: Site MUST include an examples gallery with 3-5 executable Jupyter notebooks demonstrating feedback control, PID design, and state-space workflows
- **FR-006**: Site MUST auto-generate API documentation from Python docstrings using sphinx-autodoc for Diagram, Block, Connection, validation, and export modules
- **FR-006a**: Sphinx autodoc MUST be configured to exclude private methods and attributes (prefixed with `_`) from auto-generated API documentation, showing only the public API surface
- **FR-007**: Site MUST include curated API reference pages with examples and explanations for Diagram class, block types, validation functions, and python-control export methods
- **FR-008**: Site MUST render Jupyter notebooks with myst-nb, displaying code, outputs, plots, and LaTeX equations without requiring manual execution
- **FR-008a**: Documentation build MUST fail immediately if any example notebook fails to execute, preventing deployment of documentation with broken examples
- **FR-009**: Site MUST provide responsive layout supporting mobile, tablet, and desktop viewports without horizontal scrolling
- **FR-010**: Site MUST support light and dark themes with theme-appropriate logo variants
- **FR-011**: Site MUST deploy automatically to GitHub Pages via GitHub Actions workflow on push to main branch
- **FR-011a**: GitHub Pages deployment failures MUST cause CI/CD workflow to fail with notification via standard GitHub Actions mechanisms (no automatic retry); manual investigation required
- **FR-012**: Site MUST include navigation sidebar with hierarchical page structure and search functionality (provided by Furo)
- **FR-013**: API documentation MUST link to external documentation (NumPy, python-control, Python standard library) using Sphinx intersphinx
- **FR-014**: Site MUST include custom CSS for Lynx branding (colors, spacing, typography overrides)
- **FR-015**: All internal cross-references MUST resolve correctly (no broken links between pages)
- **FR-015a**: Documentation build MUST fail if Sphinx linkcheck detects any broken internal links, preventing deployment of documentation with invalid cross-references

### Key Entities

- **Documentation Page**: Represents a single page in the docs site (landing page, quickstart, API reference page, example notebook)
  - Attributes: Title, URL path, content format (Markdown/Jupyter), navigation position
  - Relationships: Belongs to a section (Getting Started, API, Examples), may reference other pages

- **API Reference Section**: Auto-generated or curated documentation for a Python module or class
  - Attributes: Module name, class name, method signatures, docstring content, code examples
  - Relationships: Links to related API sections, external library docs

- **Example Notebook**: Executable Jupyter notebook demonstrating a control system workflow
  - Attributes: Title, description, cells (code + markdown), outputs (plots, text)
  - Relationships: References API methods, may be linked from getting-started guide

- **Static Asset**: Logo, icon, CSS file, or image used in the documentation
  - Attributes: File path, format (PNG/SVG/CSS), purpose (logo, favicon, screenshot)
  - Relationships: Referenced by pages, may have theme variants (light/dark logos)

- **Build Configuration**: Sphinx settings controlling documentation generation
  - Attributes: Extensions enabled, theme options, autodoc settings, intersphinx mappings
  - Relationships: Defines how pages are generated, which notebooks are executed

## Success Criteria

### Measurable Outcomes

- **SC-001**: New users can install Lynx and create their first diagram following the quickstart guide in under 10 minutes (validated by user testing with 3+ first-time users)
- **SC-002**: All API methods, classes, and functions are documented with method signatures, parameter descriptions, return types, and at least one code example
- **SC-003**: Documentation site builds successfully in CI/CD without errors or warnings (zero Sphinx warnings on production builds)
- **SC-004**: All example notebooks execute successfully during documentation build without errors (build fails if any notebook execution fails), and render with correct outputs (plots, LaTeX, text) on the website
- **SC-005**: Site is publicly accessible at the GitHub Pages URL within 5 minutes of merging to main branch
- **SC-006**: Site achieves 95%+ mobile usability score (no horizontal scrolling, readable text, accessible navigation on viewport widths 320px to 768px)
- **SC-007**: All internal page links resolve correctly (zero broken links, enforced by Sphinx linkcheck failing build on any broken link)
- **SC-008**: Dark mode works correctly with appropriate logo switching and no readability issues (validated by manual testing on Chrome, Firefox, Safari)

## Assumptions

### Technical Assumptions

- **A-001**: The existing Python codebase has docstrings in Google-style format suitable for sphinx-autodoc (if not, docstrings will need to be added/updated as a prerequisite)
- **A-002**: Existing example notebooks in `examples/` directory are functional and execute without errors when dependencies are installed
- **A-003**: GitHub Pages is enabled for the repository with appropriate permissions for GitHub Actions deployment
- **A-004**: The repository has a `main` branch that serves as the deployment source for production documentation
- **A-005**: Logo assets exist or can be created in SVG/PNG format with light and dark theme variants
- **A-015**: Security relies on GitHub Pages default protections (automatic HTTPS enforcement, no custom security headers or user input handling required for static read-only site)

### Content Assumptions

- **A-006**: The API reference in `dev/api-reference.md` and design doc in `dev/docs-design.md` are up-to-date and accurately reflect the current codebase
- **A-007**: Target audience includes control systems engineers, students, and researchers with basic Python knowledge (Python 3.11+, pip/uv package management)
- **A-008**: Users have Jupyter installed or can install it as a dependency for running example notebooks locally
- **A-009**: Documentation will be versioned with the codebase (no separate versioned docs for MVP)
- **A-010**: The Furo theme's default search functionality (provided by Sphinx) is sufficient for MVP (no custom search implementation required)

### Workflow Assumptions

- **A-011**: Content will be written in MyST Markdown format (preferred over reStructuredText for easier authoring)
- **A-012**: Example notebooks will be executed during the documentation build process (myst-nb execution mode configured to fail build on any notebook execution error)
- **A-013**: Documentation updates will be part of the regular development workflow (docs updated in the same PR as code changes)
- **A-014**: The documentation site does not require a custom domain for MVP (GitHub Pages default URL is acceptable)

## Dependencies

### External Dependencies

- **D-001**: GitHub Pages must be enabled and configured for the repository
- **D-002**: Existing example Jupyter notebooks must be functional and execute without errors
- **D-003**: Python docstrings in the codebase must be complete enough for auto-generated API documentation
- **D-004**: Logo assets must be available (or created) in light and dark theme variants

### System Dependencies

- **D-005**: Documentation build requires Python 3.11+ environment with Sphinx and extensions installed
- **D-006**: CI/CD workflow requires GitHub Actions with appropriate permissions (contents: read, pages: write, id-token: write)
- **D-007**: Local documentation development requires `make` command (or `make.bat` on Windows)

## Scope Boundaries

### In Scope

- Landing page, quickstart guide, getting-started guide
- API reference (auto-generated and curated) for core modules (Diagram, blocks, validation, export)
- Examples gallery with 3-5 executable Jupyter notebooks
- GitHub Actions workflow for automated deployment to GitHub Pages
- Responsive design (mobile, tablet, desktop)
- Light and dark theme support with appropriate logo variants
- Custom CSS for Lynx branding

### Out of Scope (Future Enhancements)

- Multi-part tutorial series (PID tuning deep dive, advanced state-space design)
- Topic-specific guides (troubleshooting, keyboard shortcuts, theme customization)
- Blog section or release notes
- Video tutorials or animated GIFs of widget interactions
- JupyterLite embedding (try Lynx in browser without installation)
- React/TypeScript architecture documentation for contributors
- Versioned documentation (docs switcher for multiple versions)
- Custom domain configuration
- Google Analytics or usage tracking
- Custom search implementation beyond Furo's built-in search
- Download buttons for notebooks (Furo provides this by default)
