<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: GitHub Pages Documentation Website

**Branch**: `016-github-pages-docs` | **Date**: 2026-01-21 | **Spec**: [spec.md](spec.md)

## Summary

Create a production-ready documentation website for Lynx using Sphinx with Furo theme, deployed automatically to GitHub Pages. The site will include a landing page, quickstart guide, getting-started guide, API reference (curated + auto-generated), and 3-5 executable Jupyter notebook examples. Documentation builds will enforce quality through automated checks: notebooks must execute without errors, internal links must resolve correctly, and Sphinx must produce zero warnings. The architecture leverages MyST-NB for notebook integration with caching for fast incremental builds, sphinx-autodoc for API documentation (excluding private members), and GitHub Actions for CI/CD deployment.

## Technical Context

**Language/Version**: Python 3.11+ (documentation build environment)
**Primary Dependencies**: Sphinx >=7.0, Furo >=2024.0, MyST-NB >=1.0, sphinx-design >=0.5, sphinx-autodoc, sphinx-intersphinx
**Storage**: Static HTML files deployed to GitHub Pages (git repository)
**Testing**: Sphinx build validation (zero warnings), linkcheck (no broken links), notebook execution (must succeed)
**Target Platform**: GitHub Pages (static site hosting), compatible with modern browsers (Chrome, Firefox, Safari, mobile)
**Project Type**: Documentation site (static site generation from Markdown/Jupyter sources)
**Performance Goals**: Page load <2s on 3G, search results <500ms, notebook execution cache enabled for <5s incremental builds
**Constraints**: Zero Sphinx warnings on production builds, all notebooks must execute successfully, all internal links must resolve, mobile-responsive (viewport 320px-2560px), GitHub Pages 1GB size limit
**Scale/Scope**: 15-20 documentation pages, 3-5 example notebooks, full API reference for 50+ Python classes/functions, 5-10 static assets (logos, CSS)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity Over Features ✅

**Compliance**: MVP focuses exclusively on essential documentation capabilities:
- Landing page, quickstart, getting-started guide (core onboarding)
- API reference (essential for developers)
- 3-5 example notebooks (minimum viable examples)
- Automated deployment (essential for maintenance)

**Out of scope** (deferred to future): Multi-part tutorials, topic guides, blog, video tutorials, JupyterLite, versioned docs, custom search, analytics.

**Justification**: Documentation website is inherently a "feature" but serves the core product (Lynx). The MVP scope is minimal viable documentation - enough to enable users to successfully use Lynx without creating a comprehensive documentation portal.

### Principle II: Python Ecosystem First ✅

**Compliance**:
- Uses standard Sphinx toolchain (de facto standard for Python projects)
- MyST Markdown format (modern, accessible alternative to reStructuredText)
- sphinx-autodoc with Google-style docstrings (NumPy/SciPy convention)
- Intersphinx links to NumPy, python-control, Python stdlib (ecosystem integration)
- Furo theme (modern Python project standard: pip, attrs, pytest)
- Content stored in Markdown/Jupyter (.md, .ipynb) - open, portable formats
- No vendor lock-in: docs can be migrated to ReadTheDocs, self-hosted, etc.

### Principle III: Test-Driven Development ⚠️ EXCEPTION REQUIRED

**Compliance Challenge**: Documentation sites don't follow traditional TDD (no unit tests for content).

**Alternative Quality Assurance**:
- **Build-time validation**: Sphinx warnings treated as errors (`-W` flag)
- **Link validation**: `sphinx-build -b linkcheck` fails on broken links
- **Notebook execution**: myst-nb configured with `nb_execution_raise_on_error=True` - notebooks are "tests" that must pass
- **CI enforcement**: All validation runs in GitHub Actions before deployment
- **User testing**: SC-001 requires validation with 3+ first-time users (<10 min onboarding)

**Justification**: Documentation quality is validated through automated checks (link validation, notebook execution, build warnings) and user testing rather than unit tests. Content correctness comes from review and user feedback, not test-first development.

### Principle IV: Clean Separation of Concerns ✅

**Compliance**:
- **Content layer** (Markdown/Jupyter) separate from **presentation layer** (Sphinx/Furo theme)
- **Business logic** (Lynx Python code) separate from **documentation** (docs/ directory)
- **Build configuration** (conf.py) separate from **content** (source files)
- **Static assets** (_static/) separate from **generated content** (_build/)

Clean separation enables:
- Theme changes without content rewrites
- Content updates without build system changes
- API docs auto-generated from source (DRY principle)

### Principle V: User Experience Standards ✅

**Compliance**:
- **Performance targets**: Page load <2s (SC-006: 95%+ mobile usability), search <500ms (Furo built-in), build <5s incremental (MyST-NB caching)
- **Accessibility**: Furo theme WCAG 2.1 AA compliant, mobile-responsive (320px-2560px viewports), keyboard navigation enabled
- **Usability**: <10 minute quickstart (SC-001), zero broken links (SC-007), executable examples (SC-004)
- **Speed priority**: Notebook caching reduces build times from 10+ min to <5s on incremental changes

**Measurement**: User testing with 3+ first-time users (SC-001), mobile usability testing on iOS/Android (SC-006), manual accessibility validation (dark mode, keyboard navigation).

### ✅ Gates Passed

- All principles compliant or justified exceptions documented
- TDD exception: Quality assured through automated validation and user testing instead of unit tests
- Ready for Phase 0 research

---

## Project Structure

### Documentation (this feature)

```text
specs/016-github-pages-docs/
├── plan.md              # This file
├── research.md          # Sphinx/Furo best practices (Phase 0 output)
├── quickstart.md        # Manual test procedure (Phase 1 output)
└── checklists/
    └── requirements.md  # Specification quality checklist (from /speckit.specify)
```

### Source Code (repository root)

```text
docs/
├── source/                          # Sphinx source files
│   ├── _static/                     # Static assets
│   │   ├── logo-light.png           # Light theme logo
│   │   ├── logo-dark.png            # Dark theme logo
│   │   ├── favicon.svg              # Site favicon
│   │   └── custom.css               # Lynx branding CSS overrides
│   ├── _templates/                  # Custom Jinja2 templates (optional)
│   ├── api/                         # API reference documentation
│   │   ├── index.md                 # API landing page (curated overview)
│   │   ├── diagram.md               # Diagram class reference (curated + autodoc)
│   │   ├── blocks.md                # Block types reference (curated + autodoc)
│   │   ├── validation.md            # Validation API reference
│   │   ├── export.md                # Python-control export reference
│   │   └── generated/               # Autodoc-generated files (gitignored)
│   ├── examples/                    # Example notebooks
│   │   ├── index.md                 # Examples gallery (grid cards)
│   │   ├── basic-feedback.ipynb     # Simple feedback control (P1)
│   │   ├── pid-controller.ipynb     # PID tuning example (P1)
│   │   └── state-feedback.ipynb     # State-space design (P2)
│   ├── getting-started/             # Tutorial content
│   │   ├── index.md                 # Getting-started landing
│   │   ├── installation.md          # Installation guide
│   │   └── concepts.md              # Core concepts (diagrams, blocks, connections)
│   ├── conf.py                      # Sphinx configuration
│   ├── index.md                     # Documentation landing page
│   └── requirements.txt             # Doc build dependencies
├── _build/                          # Build output (gitignored)
│   ├── html/                        # HTML output for GitHub Pages
│   ├── linkcheck/                   # Linkcheck output
│   └── .jupyter_cache/              # MyST-NB execution cache (gitignored)
├── Makefile                         # Build automation (Unix)
└── make.bat                         # Build automation (Windows)

.github/workflows/
└── docs.yml                         # GitHub Actions workflow (build + deploy)

pyproject.toml                       # Add [project.optional-dependencies.docs]
.gitignore                           # Add docs build artifacts
```

**Structure Decision**: Single documentation project using standard Sphinx layout recommended by `sphinx-quickstart`. The `docs/source/` directory contains all Markdown/Jupyter source files organized by section (api/, examples/, getting-started/). Static assets in `_static/` and configuration in `conf.py` follow Sphinx conventions used by NumPy, SciPy, and python-control projects. This structure enables:
- Clean separation of source (`source/`) from build artifacts (`_build/`)
- Intuitive content organization matching site navigation
- Standard tools (`make html`, `sphinx-autobuild`) work out of the box
- Easy migration to ReadTheDocs or self-hosting if needed

---

## Complexity Tracking

> **No violations to justify** - Constitution gates passed

---

## Architecture Decisions

### 1. Static Site Generator: Sphinx + Furo Theme

**Decision**: Use Sphinx with Furo theme for static site generation.

**Rationale**:
- **Sphinx**: De facto standard for Python documentation (used by Python itself, NumPy, SciPy, pytest, etc.). Mature ecosystem, excellent Python integration.
- **Furo**: Modern, clean theme with excellent mobile support, automatic dark mode, built-in search. Used by pip, attrs, and many recent Python projects. Much more polished than default Sphinx themes.
- **Alternative considered**: MkDocs + Material theme - Rejected because Sphinx has better Python autodoc integration and deeper Jupyter notebook support via MyST-NB.

**Trade-offs**:
- **Pro**: Best-in-class Python ecosystem integration, mature tooling, excellent community support
- **Pro**: Furo provides professional design out-of-the-box without custom theming
- **Con**: Sphinx has steeper learning curve than MkDocs (but team already familiar with Python tooling)
- **Con**: reStructuredText legacy (mitigated by using MyST Markdown)

**References**: Sphinx is used by 90%+ of major Python projects. Furo theme adopted by pip (2021), attrs (2022), showing industry trend toward modern themes.

### 2. Content Format: MyST Markdown + Jupyter Notebooks

**Decision**: Write documentation in MyST Markdown (.md files) and integrate Jupyter notebooks directly (.ipynb files) using myst-nb extension.

**Rationale**:
- **MyST Markdown**: Modern, accessible alternative to reStructuredText. Supports all Sphinx features (cross-references, directives, roles) with cleaner syntax.
- **Direct notebook integration**: myst-nb renders Jupyter notebooks directly without conversion. Notebooks are executed during doc builds, ensuring examples stay current with code.
- **Alternative considered**: Convert notebooks to Markdown/rst - Rejected because conversion loses fidelity and creates maintenance burden (two sources of truth).

**Trade-offs**:
- **Pro**: Authors can write docs in familiar Markdown syntax
- **Pro**: Notebooks are executable documentation - they must work or build fails
- **Pro**: Notebook outputs (plots, LaTeX) render correctly without manual intervention
- **Con**: MyST adds dependency (but provides significant value for Markdown support)
- **Con**: Notebook execution adds ~2-10min to build time (mitigated with caching - see below)

**Configuration**:
```python
# conf.py
extensions = ['myst_nb', 'myst_parser']
myst_enable_extensions = ['colon_fence', 'deflist', 'dollarmath', 'amsmath']
```

### 3. Notebook Execution: Cache Mode with Fail-on-Error

**Decision**: Configure myst-nb with `nb_execution_mode = "cache"` and `nb_execution_raise_on_error = True`.

**Rationale**:
- **Cache mode**: Re-executes notebooks only when content changes. First build ~10min (execute all), incremental builds <5s (use cached outputs). Critical for development velocity.
- **Fail-on-error**: Any notebook cell failure fails the entire build. Ensures published docs have valid, working examples. Without this, errors produce warnings that can be missed.
- **Alternative considered**: `nb_execution_mode = "off"` (use committed outputs) - Rejected because notebooks can become stale (code changes but outputs don't update). Cache mode provides best balance of speed and correctness.

**Trade-offs**:
- **Pro**: Fast incremental builds (<5s typical)
- **Pro**: Guarantees all published examples work (notebooks are integration tests)
- **Pro**: Automatic output updates when code changes (no manual notebook re-runs)
- **Con**: First build is slow (~10min for 20 notebooks) - acceptable since CI caches results
- **Con**: Notebooks must be reproducible (no external data dependencies) - this is a feature (enforces best practices)

**Configuration**:
```python
# conf.py
nb_execution_mode = "cache"
nb_execution_allow_errors = False
nb_execution_raise_on_error = True
nb_execution_timeout = 60
nb_execution_cache_path = "_build/.jupyter_cache"
```

### 4. API Documentation: Curated Overview + Auto-generated Details

**Decision**: Hybrid approach - hand-written overview pages (api/index.md, api/diagram.md, etc.) that use sphinx-autosummary to generate detailed reference pages in api/generated/.

**Rationale**:
- **Curated structure**: Explicit control over what appears in docs and how it's organized. Better than pure autodoc which dumps everything alphabetically.
- **Auto-generated details**: Detailed per-class/function pages generated from docstrings. Keeps docs in sync with code (DRY principle).
- **Alternative considered**: Pure autodoc (fully automated) - Rejected because it produces alphabetical dumps without narrative structure. Users need guided discovery.

**Trade-offs**:
- **Pro**: Best of both worlds - narrative structure + detailed reference
- **Pro**: Docs stay in sync with code automatically
- **Pro**: Reduces maintenance burden (docstrings are single source of truth for API)
- **Con**: Requires writing overview pages manually (but these are high-value navigation)

**Configuration**:
```python
# conf.py
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.napoleon']
autodoc_default_options = {
    'members': True,
    'private-members': False,  # Exclude _private methods
    'special-members': '__init__',
    'show-inheritance': True,
}
autosummary_generate = True
```

### 5. Link Validation: Fail Build on Broken Links

**Decision**: Run `sphinx-build -b linkcheck` in CI and fail the build on broken internal links. External link failures only warn (don't block deployment).

**Rationale**:
- **Internal links**: Broken internal cross-references (e.g., `:doc:`, `:ref:`) are bugs that confuse users. Must be caught before deployment.
- **External links**: Third-party sites can be temporarily down or change URLs. Failing builds on external issues creates false positives. Warn instead.
- **Alternative considered**: Manual link checking - Rejected because it's error-prone and doesn't scale. Automated checking is standard practice.

**Trade-offs**:
- **Pro**: Zero broken internal links guaranteed (SC-007)
- **Pro**: External link issues logged for manual review without blocking releases
- **Con**: Adds ~30-60s to build time (acceptable for quality assurance)

**Configuration**:
```yaml
# .github/workflows/docs.yml
- name: Run linkcheck
  continue-on-error: ${{ github.event_name == 'pull_request' }}  # Warn on PRs, fail on main
  run: sphinx-build -b linkcheck source _build/linkcheck
```

### 6. Private Method Exclusion: autodoc `private-members: False`

**Decision**: Configure sphinx-autodoc to exclude all methods/attributes prefixed with `_` from generated documentation.

**Rationale**:
- **Python convention**: Leading underscore signals private/internal API not intended for users.
- **Clean API surface**: Public docs should only show stable, supported API. Private methods clutter docs and confuse users about what they should use.
- **Alternative considered**: Include all methods with "Internal API" warnings - Rejected because it creates noise. If something shouldn't be used, don't document it publicly.

**Trade-offs**:
- **Pro**: Clean, focused documentation showing only public API
- **Pro**: Reduces doc page size and cognitive load
- **Con**: Power users who need internals must read source code (acceptable - they're advanced)

**Configuration**:
```python
# conf.py
autodoc_default_options = {
    'private-members': False,  # Exclude _private
}
```

### 7. Deployment: GitHub Actions + GitHub Pages

**Decision**: Use GitHub Actions workflow to build docs on push to main, then deploy to GitHub Pages using official `actions/deploy-pages@v4`.

**Rationale**:
- **GitHub Pages**: Free, fast, HTTPS automatic, custom domain support. Perfect for open-source project docs.
- **GitHub Actions**: Integrated with repo, excellent caching, official deployment action. No third-party service needed.
- **Alternative considered**: ReadTheDocs - Rejected for MVP because GitHub Pages is simpler (one less account/service) and sufficient for static docs. Can migrate later if needed.

**Trade-offs**:
- **Pro**: Zero-cost hosting, automatic HTTPS, excellent performance (CDN)
- **Pro**: Deployment fully automated (push to main = live docs in <5min)
- **Pro**: Preview builds on PRs verify docs before merge
- **Con**: GitHub Pages has 1GB site size limit (not an issue for docs)
- **Con**: No versioned docs (acceptable for MVP - deferred to future)

**Configuration**:
```yaml
# .github/workflows/docs.yml
permissions:
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4  # Fast dependency management
      - run: uv pip install -r docs/source/requirements.txt
      - run: sphinx-build -W --keep-going -b html source _build/html

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
```

### 8. Dependency Management: UV for Fast Builds

**Decision**: Use UV (Astral's Rust-based package installer) instead of pip for installing doc dependencies in CI.

**Rationale**:
- **Speed**: UV is 10-100x faster than pip for dependency resolution and installation. Critical for CI performance.
- **Reproducibility**: Better lockfile support and caching integration with GitHub Actions.
- **Official support**: `astral-sh/setup-uv` is officially maintained action with great docs.
- **Alternative considered**: pip - Rejected because UV provides significant speed improvement with zero downside (drop-in replacement).

**Trade-offs**:
- **Pro**: 10-100x faster CI builds (typical: 30s vs 5min for fresh install)
- **Pro**: Better caching, more reliable dependency resolution
- **Con**: Adds UV as dependency (but it's becoming standard in Python ecosystem)

**Configuration**:
```yaml
# .github/workflows/docs.yml
- uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
- run: uv pip install --system -r docs/source/requirements.txt
```

### 9. Theme Customization: Minimal CSS Overrides

**Decision**: Use Furo theme with minimal CSS customization (only branding colors in `custom.css`). Accept Furo's design decisions.

**Rationale**:
- **Furo provides**: Responsive layout, dark mode, excellent typography, mobile menu, search. No need to reinvent.
- **Minimal override**: Only customize Lynx brand colors (primary color, accent). ~20 lines CSS.
- **Alternative considered**: Heavy customization or custom theme - Rejected because Furo is already excellent. Time better spent on content than design.

**Trade-offs**:
- **Pro**: Professional design out-of-the-box, maintained by Furo team
- **Pro**: Future Furo improvements (accessibility, features) benefit Lynx automatically
- **Pro**: Less maintenance burden (theme code is external)
- **Con**: Lynx docs look similar to other Furo sites (but with distinct branding via logos/colors)

**Customization**:
```css
/* docs/source/_static/custom.css */
:root {
  --color-brand-primary: #yourcolor;
  --color-brand-content: #yourcolor;
}
```

### 10. Mobile Responsiveness: Furo's Built-in Support

**Decision**: Rely on Furo theme's responsive design without custom media queries. Test on iOS Safari, Android Chrome, and Firefox mobile.

**Rationale**:
- **Furo handles**: Hamburger menu on narrow screens, responsive images, readable text at all viewport sizes (320px-2560px).
- **Validation**: Manual testing (SC-006) ensures 95%+ mobile usability without custom work.
- **Alternative considered**: Custom responsive CSS - Rejected because Furo already solves this. No need to duplicate effort.

**Testing Strategy**:
- **Development**: Use browser DevTools device emulation
- **Pre-release**: Manual testing on physical iOS/Android devices
- **Success criteria**: No horizontal scrolling, readable text, accessible navigation (SC-006)

---

## Testing Strategy

### Build-Time Validation (Automated)

**1. Sphinx Warnings as Errors**

```bash
sphinx-build -W --keep-going -b html source _build/html
```

- **Purpose**: Catch all Sphinx issues (missing references, invalid syntax, broken directives)
- **Configuration**: `-W` treats warnings as errors, `--keep-going` shows all issues (not just first)
- **Enforcement**: CI fails if any warnings detected
- **Success Criteria**: SC-003 (zero Sphinx warnings on production builds)

**2. Linkcheck Validation**

```bash
sphinx-build -b linkcheck source _build/linkcheck
```

- **Purpose**: Detect broken internal cross-references and validate external links
- **Configuration**: Fail on broken internal links, warn on external link issues
- **Enforcement**: CI runs linkcheck on every build
- **Success Criteria**: SC-007 (all internal links resolve correctly)

**3. Notebook Execution Validation**

```python
# conf.py
nb_execution_raise_on_error = True
```

- **Purpose**: Ensure all example notebooks execute without errors
- **Configuration**: myst-nb configured to fail build on any cell error
- **Enforcement**: Notebooks executed during every build (with caching)
- **Success Criteria**: SC-004 (all notebooks execute successfully)

### Manual Validation (Pre-Release)

**1. User Testing (SC-001)**

- **Procedure**: 3+ first-time users follow quickstart guide from fresh environment
- **Success Criteria**: Users install Lynx and create first diagram in <10 minutes
- **Validation**: Time each user, collect feedback on confusing steps
- **Frequency**: Before major releases, after quickstart changes

**2. Mobile Usability Testing (SC-006)**

- **Procedure**: Test on iOS Safari, Android Chrome across viewport widths (320px-768px)
- **Success Criteria**: No horizontal scrolling, readable text, accessible hamburger menu
- **Validation**: Manual testing on physical devices + browser DevTools
- **Frequency**: After theme changes, before major releases

**3. Dark Mode Validation (SC-008)**

- **Procedure**: Toggle dark mode on Chrome, Firefox, Safari and verify:
  - Logo switches correctly (light/dark variants)
  - Code blocks remain readable
  - No contrast issues (text visible on backgrounds)
- **Success Criteria**: All content readable and appropriately styled in both modes
- **Frequency**: After CSS changes, before major releases

### Continuous Integration Gates

```yaml
# .github/workflows/docs.yml

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # Gate 1: Sphinx build with warnings-as-errors
      - run: sphinx-build -W --keep-going -b html source _build/html

      # Gate 2: Linkcheck (fail on internal, warn on external)
      - run: sphinx-build -b linkcheck source _build/linkcheck

      # Gate 3: Notebook execution (automatic via nb_execution_raise_on_error)
      # (Runs during Sphinx build above)

      # Upload artifacts for manual review
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _build/html

  deploy:
    # Only deploy if all gates pass
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
```

**Gate Policy**:
- **PR builds**: All gates must pass before merge approval
- **Main branch**: Any gate failure blocks deployment
- **External links**: Allowed to warn (not fail) to prevent false positives from temporary external site issues

---

## Performance Optimization

### Build Performance

**Target**: Incremental builds <5 seconds (SC-003 implicit), first build <10 minutes

**Strategy 1: MyST-NB Execution Caching**

```python
# conf.py
nb_execution_mode = "cache"
nb_execution_cache_path = "_build/.jupyter_cache"
```

**Impact**:
- First build: ~10min (execute all notebooks)
- Incremental (no changes): ~3s (reuse all cached outputs)
- Incremental (1 notebook changed): ~15s (re-execute 1, reuse rest)

**Strategy 2: Sphinx Doctree Caching**

```bash
# Incremental build preserves doctrees
sphinx-build -b html source _build/html  # Uses existing _build/.doctrees
```

**Impact**: 30-50% speedup on unchanged pages (parser results cached)

**Strategy 3: CI Caching**

```yaml
# .github/workflows/docs.yml
- uses: actions/cache@v4
  with:
    path: docs/_build/.doctrees
    key: sphinx-doctrees-${{ github.sha }}

- uses: actions/cache@v4
  with:
    path: docs/_build/.jupyter_cache
    key: jupyter-cache-${{ hashFiles('docs/source/examples/**/*.ipynb') }}
```

**Impact**: CI builds from 8-12min (cold) to 1-2min (warm cache)

### Runtime Performance

**Target**: Page load <2s on 3G, search <500ms (SC-006 implicit)

**Strategy 1: Static Site (No Server)**

- **Benefit**: Instant page loads (HTML files served directly by CDN)
- **Implementation**: Sphinx generates static HTML/CSS/JS, no backend
- **Result**: Typical page load <500ms on broadband, <2s on 3G

**Strategy 2: Furo Theme Optimization**

- **Benefit**: Furo is optimized for performance (minimal JS, efficient CSS)
- **Metrics**:
  - Bundle size: ~50KB JS + ~30KB CSS (gzipped)
  - Search index: ~100KB for 50-page site
  - Time to Interactive: <1s on desktop, <2s on mobile

**Strategy 3: GitHub Pages CDN**

- **Benefit**: Global CDN with edge caching, automatic HTTPS
- **Result**: Consistent fast loads worldwide (<200ms TTFB typical)

---

## Security Considerations

### Threat Model

**Documentation site characteristics**:
- Read-only static content (no user input)
- No forms, no comments, no user-generated content
- No server-side code execution
- No sensitive data storage

**Conclusion**: Low attack surface - primary concerns are availability and integrity (not confidentiality).

### Security Controls

**1. HTTPS Enforcement (A-015)**

- **Control**: GitHub Pages automatically enforces HTTPS
- **Benefit**: Prevents man-in-the-middle attacks, ensures content integrity
- **Configuration**: Automatic (no action needed)

**2. Content Security Policy**

- **Control**: GitHub Pages applies default CSP headers
- **Current policy**: Allows inline scripts (needed for Furo search), blocks external resources
- **Decision**: Accept GitHub Pages defaults (no custom CSP needed for MVP)

**3. Dependency Security**

- **Control**: Pin Sphinx extension versions in requirements.txt
- **Monitoring**: Dependabot alerts for vulnerable dependencies
- **Update policy**: Update dependencies quarterly, immediately for security issues

**4. Build Security**

- **Control**: CI runs in isolated GitHub Actions environment
- **Benefit**: No access to production systems, repository secrets, or user data
- **Risk**: Malicious commit could inject content (mitigated by PR review + branch protection)

### Security Validation

**Pre-deployment checklist**:
- ✅ HTTPS enabled (automatic via GitHub Pages)
- ✅ No user input vectors (static site)
- ✅ Dependencies pinned (requirements.txt with version constraints)
- ✅ CI environment isolated (GitHub Actions sandbox)
- ✅ Branch protection enabled (require PR review for main)

**Ongoing monitoring**:
- Dependabot security alerts (automatic)
- Quarterly dependency updates
- Manual review of Sphinx/Furo security advisories

---

## Maintenance Plan

### Content Updates

**Frequency**: Continuous (docs updated in same PR as code changes per A-013)

**Workflow**:
1. Developer modifies Python code
2. Developer updates corresponding docstrings (if API changed)
3. Developer updates example notebooks (if behavior changed)
4. Developer updates getting-started guide (if new features added)
5. CI validates: notebooks execute, links resolve, autodoc builds
6. PR merged → docs automatically deployed

**Responsibility**: Feature developers own documentation updates for their changes

### Infrastructure Maintenance

**Frequency**: Quarterly

**Tasks**:
- Update Sphinx and extensions (`pip list --outdated`, update requirements.txt)
- Review Furo theme updates (new features, bug fixes)
- Update GitHub Actions dependencies (checkout, setup-python, deploy-pages)
- Review GitHub Pages configuration (custom domain, CNAME)

**Responsibility**: Documentation maintainer or DevOps team

### Quality Monitoring

**Metrics to track**:
- Build times (incremental, CI cold start) - alert if >2x expected
- Link check failures - investigate external link issues quarterly
- User testing feedback (SC-001) - conduct after major documentation changes
- Mobile usability issues - review quarterly

**Tools**:
- GitHub Actions build logs (build times, linkcheck results)
- Google Analytics (optional, out of scope for MVP) - page views, bounce rate, time on page
- User feedback issues (GitHub issues labeled "documentation")

### Contingency Planning

**Scenario 1: GitHub Pages outage**

- **Fallback**: Docs still accessible in repository (docs/source/)
- **Communication**: Post notice on README linking to source docs
- **Recovery time**: Automatic when GitHub Pages restored

**Scenario 2: Build failures blocking deployment**

- **Diagnosis**: Check CI logs for Sphinx warnings, linkcheck failures, notebook errors
- **Resolution**: Fix underlying issue (update notebook, fix broken link, update docstring)
- **Workaround**: Temporarily disable offending notebook/page if critical production issue

**Scenario 3: Dependency security vulnerability**

- **Detection**: Dependabot alert
- **Assessment**: Review CVE severity, check if vulnerability affects Sphinx build (not runtime)
- **Remediation**: Update vulnerable dependency, test build, deploy
- **Timeline**: <24 hours for critical vulnerabilities

---

## Rollout Plan

### Phase 0: Setup Infrastructure (Week 1, Days 1-2)

**Tasks**:
- Create `docs/` directory structure (source/, _static/, _templates/)
- Initialize `conf.py` with Sphinx configuration
- Create `Makefile` and `make.bat` for local builds
- Add `requirements.txt` with pinned Sphinx/Furo/MyST-NB versions
- Create `.github/workflows/docs.yml` workflow
- Configure GitHub Pages in repository settings (Source: GitHub Actions)
- Add docs build artifacts to `.gitignore`

**Validation**:
- Run `make html` locally - should generate empty site
- Push to branch - CI should build and upload artifact
- Merge to main - should deploy to GitHub Pages URL

### Phase 1: Create Core Content (Week 1-2, Days 3-10)

**Priority 1 (P1): Essential Onboarding (US1)**

**Tasks**:
- Write `source/index.md` (landing page with grid cards)
- Write `source/getting-started/installation.md` (pip install, verify)
- Write `source/getting-started/quickstart.md` (first diagram in 5 code blocks)
- Copy logo assets to `_static/` (logo-light.png, logo-dark.png, favicon.svg)
- Create `_static/custom.css` with Lynx brand colors

**Acceptance**:
- User can navigate from landing → quickstart → first working diagram
- SC-001 validation: 3 users complete quickstart in <10 minutes

**Priority 1 (P1): API Reference (US2)**

**Tasks**:
- Write `source/api/index.md` (API overview with quick reference table)
- Write `source/api/diagram.md` (curated Diagram class examples + autosummary)
- Write `source/api/blocks.md` (curated block types table + autosummary)
- Write `source/api/validation.md` (validation functions reference)
- Write `source/api/export.md` (python-control export guide + examples)
- Configure autodoc in `conf.py` (exclude private members, enable napoleon)

**Acceptance**:
- Developer can find `add_block()` method with parameters and example
- Developer can understand `get_ss()` / `get_tf()` signal reference system
- SC-002 validation: All API methods documented with examples

### Phase 2: Add Examples (Week 2, Days 8-10)

**Priority 2 (P2): Example Notebooks (US3)**

**Tasks**:
- Copy `examples/01_simple_feedback.ipynb` → `source/examples/basic-feedback.ipynb`
- Copy `examples/02_pid_controller.ipynb` → `source/examples/pid-controller.ipynb`
- Copy `examples/03_state_feedback.ipynb` → `source/examples/state-feedback.ipynb`
- Write `source/examples/index.md` (examples gallery with grid cards)
- Configure myst-nb in `conf.py` (cache mode, fail-on-error)
- Test notebook execution: `make html` should run all notebooks

**Acceptance**:
- All 3 notebooks execute without errors (SC-004)
- User can view rendered notebooks with plots and LaTeX on website
- User can download .ipynb files and run locally

### Phase 3: Polish & Testing (Week 3, Days 11-15)

**Priority 2 (P2): Conceptual Documentation (US4)**

**Tasks**:
- Write `source/getting-started/concepts.md` (diagrams, blocks, connections, ports)
- Add signal reference system explanation
- Add block type summary table (when to use Gain vs TransferFunction)
- Add validation concepts (algebraic loops, port connectivity)

**Acceptance**:
- User can explain relationship between blocks, connections, ports after reading

**Priority 3 (P3): Visual Polish (US5)**

**Tasks**:
- Test dark mode logo switching (manual: toggle theme in browser)
- Test mobile responsiveness (manual: DevTools + physical devices)
- Validate navigation (manual: test hamburger menu, sidebar, search)
- Add custom CSS for Lynx branding (primary color, accent)

**Acceptance**:
- SC-006: 95%+ mobile usability (no horizontal scroll, readable text, accessible menu)
- SC-008: Dark mode works correctly (logo switches, code readable, no contrast issues)

### Phase 4: Deployment & Validation (Week 3, Days 13-15)

**Tasks**:
- Merge to main branch → trigger deployment
- Validate GitHub Pages URL is accessible (SC-005: within 5 minutes)
- Run full validation suite:
  - Link check: `make linkcheck` (SC-007: zero broken links)
  - Build validation: `make html` with `-W` (SC-003: zero warnings)
  - User testing: 3 first-time users (SC-001: <10 min quickstart)
  - Mobile testing: iOS Safari, Android Chrome (SC-006: 95%+ usability)
  - Dark mode testing: Chrome, Firefox, Safari (SC-008: logo switches, readable)
- Document deployment URL in README.md

**Acceptance**:
- All 8 success criteria validated (SC-001 through SC-008)
- Site is live and accessible to public

### Phase 5: Handoff & Documentation (Week 3, Day 15)

**Tasks**:
- Update main README.md with link to documentation site
- Document maintenance procedures (content updates, dependency updates)
- Create GitHub issue template for documentation bugs
- Train team on documentation workflow (PR updates, CI validation)

**Deliverables**:
- Live documentation site at GitHub Pages URL
- README.md linking to docs
- Maintenance documentation in `docs/README.md`
- Team trained on doc workflow

---

## Known Limitations & Future Work

### Current Limitations

1. **No versioned documentation** (A-009): Documentation is tied to main branch. Users cannot access docs for older Lynx versions.
   - **Impact**: Users on older Lynx versions may see docs for newer features
   - **Workaround**: Maintain stability in public API, document version requirements per feature
   - **Future**: Implement versioned docs using sphinx-multiversion or ReadTheDocs

2. **No search analytics** (Out of scope): Cannot track what users search for or which pages they visit.
   - **Impact**: Less data for improving documentation
   - **Workaround**: Rely on user feedback via GitHub issues
   - **Future**: Add Google Analytics or Plausible (privacy-friendly alternative)

3. **External link validation** (Edge case): External links can break without detection between releases.
   - **Impact**: Users may encounter 404s on external references
   - **Workaround**: Quarterly manual review of linkcheck output
   - **Future**: Scheduled CI job to run linkcheck weekly and notify maintainers

4. **No video tutorials** (Out of scope): Visual learners may prefer video walkthroughs.
   - **Impact**: Slower onboarding for some user personas
   - **Workaround**: Clear screenshots, step-by-step written guides
   - **Future**: Record screencasts for YouTube, embed in docs

5. **Limited customization** (Design decision): Docs look similar to other Furo sites.
   - **Impact**: Less distinctive branding compared to fully custom theme
   - **Workaround**: Minimal CSS overrides for Lynx brand colors, distinctive logos
   - **Future**: Consider custom Furo theme variant if branding becomes priority

### Future Enhancements

**High Priority** (Next 6 months):
- **Versioned docs**: Use sphinx-multiversion for per-release documentation
- **Contributor guide**: Document React/TypeScript architecture for contributors
- **Advanced tutorials**: Multi-part series on PID tuning, state-space design

**Medium Priority** (6-12 months):
- **Search analytics**: Add privacy-friendly analytics (Plausible, not Google Analytics)
- **Video tutorials**: Screen recordings for key workflows (quickstart, first diagram)
- **Interactive demos**: JupyterLite integration for try-before-install experience

**Low Priority** (12+ months):
- **Blog section**: Release notes, case studies, guest posts
- **Custom domain**: docs.lynx-project.org (requires domain purchase + DNS setup)
- **Internationalization**: Translate docs to other languages (requires i18n infrastructure)

---

## Success Metrics

### Deployment Success (Day 1)

- ✅ Site accessible at GitHub Pages URL within 5 minutes of merge (SC-005)
- ✅ Zero Sphinx warnings on production build (SC-003)
- ✅ Zero broken internal links (SC-007)
- ✅ All example notebooks execute successfully (SC-004)

### Content Quality (Week 1 post-launch)

- ✅ 3+ first-time users complete quickstart in <10 minutes (SC-001)
- ✅ All API methods documented with examples (SC-002)
- ✅ 95%+ mobile usability score on iOS/Android (SC-006)
- ✅ Dark mode validated on Chrome/Firefox/Safari (SC-008)

### Ongoing Health (Monthly)

- Build times: <5s incremental, <10min first build
- Link check: <5 broken external links per check
- User feedback: <10 open documentation issues at any time
- API coverage: 100% of public methods documented

### Long-term Impact (6 months post-launch)

- User onboarding time: <10 minutes (SC-001 sustained)
- Documentation issues: <5 per month (indicates good docs)
- API documentation completeness: Maintained at 100% (SC-002)
- Site performance: <2s page load on 3G (SC-006 sustained)

---

## Appendix: Configuration Files

### docs/source/requirements.txt

```txt
# Sphinx core
sphinx>=7.0,<8.0
sphinx-autobuild>=2024.0

# Theme
furo>=2024.0

# Markdown and notebook support
myst-parser>=3.0
myst-nb>=1.0

# Sphinx extensions
sphinx-design>=0.5
sphinx-copybutton>=0.5

# Jupyter kernel (for notebook execution)
ipykernel>=6.0
jupyter>=1.0

# Lynx dependencies (for autodoc and notebook execution)
# (These should match main pyproject.toml dependencies)
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
python-control>=0.9.4
anywidget>=0.9.0
```

### docs/source/conf.py (complete)

```python
# Configuration file for the Sphinx documentation builder.

import os
import sys

# Path setup
sys.path.insert(0, os.path.abspath('../../src'))  # Adjust to find lynx package

# Project information
project = 'Lynx'
copyright = '2026, Lynx Contributors'
author = 'Lynx Contributors'
release = '0.1.0'  # TODO: Auto-detect from package version

# General configuration
extensions = [
    'sphinx.ext.autodoc',           # Auto-generate API docs
    'sphinx.ext.autosummary',       # API index generation
    'sphinx.ext.napoleon',          # Google-style docstrings
    'sphinx.ext.intersphinx',       # Link to external docs
    'sphinx.ext.viewcode',          # Source code links
    'myst_nb',                      # Jupyter notebook support
    'sphinx_design',                # Grid cards, tabs, dropdowns
    'sphinx_copybutton',            # Copy code block button
]

# MyST configuration
myst_enable_extensions = [
    'colon_fence',      # ::: directive syntax
    'deflist',          # Definition lists
    'dollarmath',       # $...$ for inline math
    'amsmath',          # Advanced math
]

# MyST-NB configuration (Jupyter notebook execution)
nb_execution_mode = 'cache'              # Cache execution results
nb_execution_allow_errors = False        # Don't allow cell errors
nb_execution_raise_on_error = True       # Fail build on notebook errors
nb_execution_timeout = 60                # Max execution time per cell (seconds)
nb_execution_show_tb = True              # Show tracebacks on errors
nb_execution_cache_path = '_build/.jupyter_cache'
nb_kernel_rgx_aliases = {'python3': 'python'}
nb_merge_streams = True                  # Merge stdout/stderr

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': False,
    'private-members': False,            # Exclude _private members
    'special-members': '__init__',
    'inherited-members': False,
    'show-inheritance': True,
}
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Autosummary configuration
autosummary_generate = True              # Generate stub pages
autosummary_imported_members = False

# Intersphinx mapping (link to external docs)
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'control': ('https://python-control.readthedocs.io/en/latest', None),
}
intersphinx_timeout = 10

# Linkcheck configuration
linkcheck_ignore = [
    r'http://localhost.*',
    r'https://github.com/.*/issues/new',
]
linkcheck_retries = 2
linkcheck_timeout = 15
linkcheck_workers = 5

# HTML output configuration
html_theme = 'furo'
html_title = 'Lynx Documentation'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_favicon = '_static/favicon.svg'

# Furo theme options
html_theme_options = {
    'light_logo': 'logo-light.png',
    'dark_logo': 'logo-dark.png',
    'sidebar_hide_name': False,
    'navigation_with_keys': True,
    'source_repository': 'https://github.com/jcallaham/lynx',
    'source_branch': 'main',
    'source_directory': 'docs/source/',
}

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
    '.ipynb': 'myst-nb',
}

# Exclude patterns
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    '**.ipynb_checkpoints',
    'api/generated',  # Gitignored autodoc output
]

# Master document (landing page)
master_doc = 'index'

# Table of contents depth
toctree_depth = 2
```

### docs/Makefile

```makefile
# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

.PHONY: help clean html linkcheck serve

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(BUILDDIR)
	rm -rf $(SOURCEDIR)/api/generated
	rm -rf $(SOURCEDIR)/.jupyter_cache

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

serve:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" --open-browser
```

### .github/workflows/docs.yml (complete)

```yaml
name: Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: "docs/source/requirements.txt"

      - name: Install dependencies
        run: |
          uv venv
          uv pip install --system -r docs/source/requirements.txt
          uv pip install --system -e .

      - name: Cache Sphinx doctrees
        uses: actions/cache@v4
        with:
          path: docs/_build/.doctrees
          key: sphinx-doctrees-${{ github.sha }}
          restore-keys: sphinx-doctrees-

      - name: Cache Jupyter execution
        uses: actions/cache@v4
        with:
          path: docs/_build/.jupyter_cache
          key: jupyter-cache-${{ hashFiles('docs/source/examples/**/*.ipynb') }}
          restore-keys: jupyter-cache-

      - name: Build documentation
        run: |
          cd docs
          sphinx-build -W --keep-going -b html source _build/html

      - name: Run linkcheck
        continue-on-error: ${{ github.event_name == 'pull_request' }}
        run: |
          cd docs
          sphinx-build -b linkcheck source _build/linkcheck

      - name: Upload linkcheck results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: linkcheck-results
          path: docs/_build/linkcheck/output.txt

      - name: Upload HTML artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/_build/html

  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest

    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}

    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### .gitignore additions

```gitignore
# Sphinx build artifacts
docs/_build/
docs/source/api/generated/
docs/source/.jupyter_cache/
docs/source/**/.ipynb_checkpoints/

# Sphinx caches
*.doctree
```

### pyproject.toml additions

```toml
[project.optional-dependencies]
docs = [
    "sphinx>=7.0,<8.0",
    "furo>=2024.0",
    "myst-parser>=3.0",
    "myst-nb>=1.0",
    "sphinx-design>=0.5",
    "sphinx-copybutton>=0.5",
    "sphinx-autobuild>=2024.0",
    "ipykernel>=6.0",
    "jupyter>=1.0",
]
```

---

## Phase 0 Complete

This plan provides a comprehensive implementation strategy for the GitHub Pages documentation website. All technical unknowns have been researched and resolved. The architecture decisions are documented with rationales, trade-offs, and alternatives considered. Configuration files are provided in full for immediate implementation.

**Next Steps**:
1. Execute Phase 1 (Setup Infrastructure) - create directory structure, initialize Sphinx config
2. Execute Phase 2 (Create Core Content) - write landing page, quickstart, API reference
3. Execute Phase 3 (Add Examples) - integrate Jupyter notebooks with myst-nb
4. Execute Phase 4 (Polish & Testing) - validate all success criteria
5. Execute Phase 5 (Deployment & Validation) - merge to main, deploy to GitHub Pages

All prerequisites are satisfied. Ready to proceed to implementation.
