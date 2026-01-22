<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Technical Research: Switchable CSS Themes

**Branch**: `010-switchable-themes` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)

## Research Questions

This document addresses the following technical decisions required for implementing a CSS theme system:

1. CSS Custom Properties Strategy
2. WCAG 2.1 AAA Contrast Requirements
3. anywidget Traitlet Patterns
4. Theme Precedence Resolution
5. Backward Compatibility
6. React Theme Switching Performance

---

## 1. CSS Custom Properties Strategy

### Research Question

How should theme palettes be organized with Tailwind CSS v4? Should we use data attributes (`data-theme`) or CSS classes for theme switching?

### Decision

**Use `data-theme` attribute with CSS custom properties defined in `@theme` directive and overridden in `@layer base`.**

### Rationale

1. **Tailwind CSS v4 Native Support**: Tailwind v4 drastically simplifies theming by allowing you to define theme variables in `@theme` and override them using `@layer base` with selectors like `[data-theme='ocean']`. This is the officially recommended pattern.

2. **Semantic Clarity**: Data attributes provide semantic meaning that only one theme should be active per element, and they are more separated from layout/positioning classes. This separation improves code organization.

3. **Better Organization**: Using data attributes allows separation of the style guide from the class structure. Layout and positioning are handled by classes, while visual styling is handled by data attributes, avoiding collisions.

4. **Negligible Performance Difference**: While attribute selectors are marginally slower than class selectors in performance tests, the difference is negligible for most applications and is outweighed by semantic benefits. Attribute selectors have the same specificity as classes.

5. **Ecosystem Alignment**: Modern theming libraries (Material UI, Panda CSS) prefer `data-theme` attributes for theme switching as of 2025-2026.

### Implementation Pattern

```css
@theme {
  /* Default theme (light) */
  --color-primary-600: #465082;
  --color-slate-800: #1e293b;
  /* ... other variables */
}

@layer base {
  [data-theme="dark"] {
    --color-primary-600: #818cf8;
    --color-slate-800: #cbd5e1;
    /* ... override all semantic colors */
  }

  [data-theme="high-contrast"] {
    --color-primary-600: #000000;
    --color-slate-800: #ffffff;
    /* ... WCAG AAA compliant overrides */
  }
}
```

### Alternatives Considered

**Alternative 1: CSS Classes (e.g., `.theme-dark`)**
- **Pros**: Slightly faster selector performance, familiar pattern
- **Cons**: Less semantic meaning, potential class name collisions, not aligned with Tailwind v4 best practices
- **Rejected**: Data attributes provide better code organization and semantic clarity

**Alternative 2: CSS Variables on `:root` Only**
- **Pros**: Simple, no attribute switching needed
- **Cons**: Requires JavaScript to swap entire CSS variable sets, doesn't leverage CSS cascade, not extensible for multiple themes
- **Rejected**: Not scalable for 3+ themes, poor separation of concerns

**Alternative 3: Multiple CSS Files**
- **Pros**: Complete style isolation per theme
- **Cons**: Requires loading/unloading stylesheets, flash of unstyled content, larger bundle size
- **Rejected**: Poor performance, complex state management

### References

- [Tailwind CSS v4: Multi-Theme Strategy | simonswiss](https://simonswiss.com/posts/tailwind-v4-multi-theme)
- [Theming best practices in v4 · tailwindlabs/tailwindcss · Discussion #18471](https://github.com/tailwindlabs/tailwindcss/discussions/18471)
- [Using data attributes instead of CSS classes | by Matt Dawkins | Medium](https://medium.com/@matt.dawkins/using-data-attributes-instead-of-css-classes-78476535b111)
- [A (mostly complete) guide to theme switching in CSS and JS | by Alexander Cerutti | Medium](https://medium.com/@cerutti.alexander/a-mostly-complete-guide-to-theme-switching-in-css-and-js-c4992d5fd357)

---

## 2. WCAG 2.1 AAA Contrast Requirements

### Research Question

What are the exact contrast ratio requirements for WCAG 2.1 AAA, and what tools/methods should be used to verify contrast ratios programmatically?

### Decision

**Enforce 7:1 contrast ratio for normal text (under 18pt or 14pt bold) and 4.5:1 for large text (18pt+ or 14pt+ bold). Use WebAIM's Color Contrast Checker and Firefox Accessibility Inspector for verification.**

### Rationale

1. **Official Standards**: WCAG 2.1 Level AAA requires a contrast ratio of at least 7:1 for normal text and 4.5:1 for large text. Large text is defined as 14 point (typically 18.66px) and bold or larger, or 18 point (typically 24px) or larger.

2. **Accessibility Justification**: The contrast ratio of 7:1 was chosen for level AAA because it compensates for the loss in contrast sensitivity usually experienced by users with vision loss equivalent to approximately 20/80 vision.

3. **Text Size Thresholds**:
   - **Normal text**: Under 18pt (24px) or under 14pt bold (18.66px bold) → **7:1 minimum**
   - **Large text**: 18pt+ (24px+) or 14pt+ bold (18.66px+ bold) → **4.5:1 minimum**

4. **Tooling Availability**: Multiple free, reliable tools exist for automated verification during development and testing.

### Verification Tools

**Primary Tools (Manual Verification)**:
1. **WebAIM's Color Contrast Checker** - Browser-based tool for checking foreground/background color pairs
2. **Color Contrast Analyser (CCA)** - Desktop application for sampling colors and checking ratios
3. **Firefox Accessibility Inspector** - Built-in browser DevTools for on-the-fly contrast checking

**Automated Testing**:
- **axe-core** (via Vitest) - Programmatic accessibility testing for React components
- **Pa11y** - Command-line tool for automated WCAG compliance checking
- **Contrast calculation formula**: Can be implemented in Python/TypeScript for CI/CD validation

### Implementation Strategy

1. **Design Phase**: Use WebAIM Contrast Checker to validate all color pairs in high-contrast theme before implementation
2. **Development**: Use Firefox Accessibility Inspector for real-time verification during styling
3. **Testing**: Write automated tests using axe-core to enforce contrast ratios in CI/CD pipeline
4. **Documentation**: Document all color pairs with their measured contrast ratios in theme definitions

### Contrast Calculation Formula

For automated testing, implement the WCAG contrast ratio formula:

```
Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)

Where:
- L1 is the relative luminance of the lighter color
- L2 is the relative luminance of the darker color
- Relative luminance is calculated from sRGB values
```

### Alternatives Considered

**Alternative 1: WCAG 2.1 AA (4.5:1 normal, 3:1 large)**
- **Pros**: Easier to achieve, more color palette flexibility
- **Cons**: Lower accessibility standard, doesn't meet user requirement (AAA specified in spec)
- **Rejected**: Specification explicitly requires AAA standards

**Alternative 2: Manual Verification Only**
- **Pros**: Simple, no tooling setup
- **Cons**: Error-prone, not enforceable in CI/CD, regression risk
- **Rejected**: Not sustainable for long-term maintenance

**Alternative 3: Design System with Pre-validated Colors**
- **Pros**: No verification needed per-theme
- **Cons**: Limits design flexibility, may not work for all use cases
- **Rejected**: Too restrictive for future theme extensibility

### References

- [WCAG 2.1 Level AAA requires a contrast ratio of at least 7:1 for normal text and 4.5:1 for large text](https://www.makethingsaccessible.com/guides/contrast-requirements-for-wcag-2-2-level-aa/)
- [Understanding Success Criterion 1.4.3: Contrast (Minimum) | WAI | W3C](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [WebAIM: Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WebAIM: Contrast and Color Accessibility](https://webaim.org/articles/contrast/)
- [Color contrast - Accessibility | MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Understanding_WCAG/Perceivable/Color_contrast)

---

## 3. anywidget Traitlet Patterns

### Research Question

What are best practices for bidirectional state sync in anywidget? Should theme be a separate traitlet or part of the `diagram_state` dict?

### Decision

**Use a separate `theme` traitlet (not embedded in `diagram_state`). Follow anywidget's preferred pattern of dedicated traitlets with `sync=True` for bidirectional state.**

### Rationale

1. **Prefer Traitlets Over Custom Messages**: anywidget documentation explicitly recommends preferring traitlets over custom messages for state synchronization. Widget state can be fully recreated from traits without Python running, whereas custom messages require both an active Python kernel and special ordering of function calls.

2. **Separation of Concerns**: Theme is a diagram-level configuration property, not part of the diagram's structural state (blocks/connections). Separating it into its own traitlet makes the API clearer and prevents accidental coupling.

3. **Granular Change Detection**: A separate `theme` traitlet allows frontend to subscribe specifically to theme changes without re-processing the entire diagram state. This improves performance and reduces unnecessary re-renders.

4. **Consistency with Existing Patterns**: The codebase already uses separate traitlets for configuration-like properties:
   - `grid_snap_enabled` (boolean config)
   - `selected_block_id` (UI state)
   - `diagram_state` (structural data)

5. **Clean Bidirectional Sync**: The standard anywidget pattern for bidirectional communication is:
   ```python
   theme = traitlets.Unicode(default_value="light").tag(sync=True)
   ```
   ```javascript
   // Read
   let theme = model.get("theme");

   // Write (e.g., from UI)
   model.set("theme", "dark");
   model.save_changes();  // Syncs to Python

   // Listen
   model.on("change:theme", () => {
     applyTheme(model.get("theme"));
   });
   ```

### Implementation Pattern

**Python Backend (`widget.py`)**:
```python
class LynxWidget(anywidget.AnyWidget):
    # Theme traitlet (separate from diagram_state)
    theme = traitlets.Unicode(default_value="light").tag(sync=True)

    # Existing diagram structure
    diagram_state = traitlets.Dict(default_value={}).tag(sync=True)

    def __init__(self, diagram: Optional[Diagram] = None, **kwargs):
        super().__init__(**kwargs)
        self.diagram = diagram if diagram is not None else Diagram()

        # Initialize theme from diagram or defaults
        self.theme = self.diagram.theme or self._resolve_default_theme()

        # Observe theme changes from frontend
        self.observe(self._on_theme_change, names=["theme"])

    def _on_theme_change(self, change: Dict[str, Any]) -> None:
        """Handle theme changes from JavaScript UI."""
        new_theme = change["new"]
        # Update diagram's theme attribute
        self.diagram.theme = new_theme
```

**Frontend (`DiagramCanvas.tsx`)**:
```typescript
function render({ model, el }) {
  // Read initial theme
  const applyTheme = (theme: string) => {
    el.setAttribute("data-theme", theme);
  };

  applyTheme(model.get("theme"));

  // Listen for theme changes from Python
  model.on("change:theme", () => {
    applyTheme(model.get("theme"));
  });

  // Update theme from UI (Settings panel)
  const handleThemeChange = (newTheme: string) => {
    model.set("theme", newTheme);
    model.save_changes();  // Syncs to Python
  };
}
```

### Alternatives Considered

**Alternative 1: Embed Theme in `diagram_state` Dict**
- **Pros**: Single source of truth, simpler traitlet structure
- **Cons**: Requires re-parsing entire diagram state on theme change, couples theme with structural data, violates separation of concerns, poor change detection granularity
- **Rejected**: Performance penalty, conceptual coupling

**Alternative 2: Theme as Part of `_action` Traitlet**
- **Pros**: Reuses existing action infrastructure
- **Cons**: Theme is state, not an action; no automatic sync from Python to JavaScript; requires manual change propagation; doesn't match existing config patterns (`grid_snap_enabled`)
- **Rejected**: Semantic mismatch, inconsistent with existing patterns

**Alternative 3: Custom Message Passing**
- **Pros**: Complete control over message format
- **Cons**: anywidget docs discourage this; requires active Python kernel; complex ordering requirements; state not recoverable without Python running
- **Rejected**: Violates anywidget best practices

### Data Type Support

anywidget supports JSON-serializable types and binary data. For theme switching, a simple Unicode string (`traitlets.Unicode`) is sufficient and maps cleanly to JavaScript strings.

### References

- [Jupyter Widgets: The Good Parts | anywidget](https://anywidget.dev/en/jupyter-widgets-the-good-parts/)
- [Getting Started | anywidget](https://anywidget.dev/en/getting-started/)
- [How to get feedback from front-end? · manzt/anywidget · Discussion #656](https://github.com/manzt/anywidget/discussions/656)

---

## 4. Theme Precedence Resolution

### Research Question

What patterns should be used for configuration precedence (environment variable > session config > instance attribute)? How should fallback logic be implemented?

### Decision

**Implement precedence as: instance attribute (diagram.theme) > session config (set_default_theme()) > environment variable (LYNX_DEFAULT_THEME) > built-in default ("light"). Use a single resolution function with explicit fallback chain.**

### Rationale

1. **Standard Precedence Hierarchy**: The pattern of "explicit > session > environment > defaults" aligns with industry best practices. More explicit configuration sources override more implicit ones. This matches patterns used by tools like virtualenv, Ansible, and configglue.

2. **Fail-Safe Defaults**: Providing default values for Python environment variables is a best practice that makes applications more resilient. Using `os.getenv('KEY', 'default_value')` offers a safer way to access optional variables.

3. **Centralized Resolution Logic**: Centralizing theme resolution in a single function (`resolve_theme()`) ensures consistent behavior across all code paths and makes testing straightforward.

4. **No Side Effects**: The resolution function is pure - it doesn't modify global state, just reads from various sources and returns the resolved theme. This makes it testable and predictable.

### Implementation Pattern

**Backend (`utils/theme_config.py`)**:
```python
import os
from typing import Optional

# Session-level default (module-level variable)
_session_default_theme: Optional[str] = None

VALID_THEMES = {"light", "dark", "high-contrast"}
BUILTIN_DEFAULT = "light"

def set_default_theme(theme: str) -> None:
    """Set session-wide default theme.

    Args:
        theme: Theme name to use as default for new diagrams

    Raises:
        ValueError: If theme name is invalid
    """
    global _session_default_theme

    if theme not in VALID_THEMES:
        raise ValueError(
            f"Invalid theme '{theme}'. Must be one of: {', '.join(sorted(VALID_THEMES))}"
        )

    _session_default_theme = theme

def get_session_default_theme() -> Optional[str]:
    """Get session-wide default theme (if set)."""
    return _session_default_theme

def resolve_theme(diagram_theme: Optional[str] = None) -> str:
    """Resolve theme using precedence hierarchy.

    Precedence (highest to lowest):
    1. diagram_theme (instance attribute)
    2. Session default (from set_default_theme())
    3. Environment variable (LYNX_DEFAULT_THEME)
    4. Built-in default ("light")

    Args:
        diagram_theme: Diagram-specific theme (if set)

    Returns:
        Resolved theme name (guaranteed to be valid)
    """
    # 1. Check diagram-level theme (highest priority)
    if diagram_theme is not None:
        if diagram_theme in VALID_THEMES:
            return diagram_theme
        else:
            # Invalid diagram theme - log warning, fall through to next level
            import logging
            logging.warning(
                f"Invalid diagram theme '{diagram_theme}'. "
                f"Must be one of: {', '.join(sorted(VALID_THEMES))}. "
                f"Falling back to session/environment defaults."
            )

    # 2. Check session-level default
    session_theme = get_session_default_theme()
    if session_theme is not None:
        return session_theme  # Already validated in set_default_theme()

    # 3. Check environment variable
    env_theme = os.getenv("LYNX_DEFAULT_THEME")
    if env_theme is not None:
        if env_theme in VALID_THEMES:
            return env_theme
        else:
            # Invalid env theme - log warning, fall through to built-in default
            import logging
            logging.warning(
                f"Invalid LYNX_DEFAULT_THEME environment variable '{env_theme}'. "
                f"Must be one of: {', '.join(sorted(VALID_THEMES))}. "
                f"Using built-in default '{BUILTIN_DEFAULT}'."
            )

    # 4. Use built-in default (always valid)
    return BUILTIN_DEFAULT
```

**Usage in `Diagram` class**:
```python
class Diagram:
    def __init__(self, theme: Optional[str] = None, **kwargs):
        from lynx.utils.theme_config import resolve_theme

        # Resolve theme using precedence hierarchy
        self.theme = resolve_theme(theme)
        # ... rest of initialization
```

### Precedence Flow Diagram

```
┌─────────────────────────────┐
│ Diagram Instance Attribute  │ ← Highest Priority (Explicit)
│   diagram.theme = "dark"    │
└──────────┬──────────────────┘
           │ If None or invalid ↓
┌─────────────────────────────┐
│ Session Configuration       │
│   set_default_theme("dark") │
└──────────┬──────────────────┘
           │ If None ↓
┌─────────────────────────────┐
│ Environment Variable        │
│   LYNX_DEFAULT_THEME=dark   │
└──────────┬──────────────────┘
           │ If None or invalid ↓
┌─────────────────────────────┐
│ Built-in Default            │ ← Lowest Priority (Implicit)
│   "light"                   │
└─────────────────────────────┘
```

### Alternatives Considered

**Alternative 1: Reverse Precedence (Environment > Session > Instance)**
- **Pros**: Allows system admins to enforce themes
- **Cons**: Violates principle of explicit over implicit; users can't override global settings; poor user experience
- **Rejected**: Doesn't match user expectations for configuration hierarchy

**Alternative 2: Config File-Based Precedence**
- **Pros**: Persistent configuration across sessions
- **Cons**: Adds complexity (file I/O, parsing); not requested in spec; overkill for single setting
- **Rejected**: Scope creep, unnecessary complexity

**Alternative 3: No Session-Level Configuration**
- **Pros**: Simpler implementation, fewer code paths
- **Cons**: Users must set theme on every diagram or use environment variable; poor developer experience
- **Rejected**: Violates requirement for `set_default_theme()` function

### References

- [Leveraging Environment Variables in Python Programming - Configu](https://configu.com/blog/working-with-python-environment-variables-and-5-best-practices-you-should-know/)
- [Best Practices for Python Env Variables](https://dagster.io/blog/python-environment-variables)
- [Environment variable fallback patterns - Python Value Checking | StudyRaid](https://app.studyraid.com/en/read/15071/521741/environment-variable-fallback-patterns)
- [Environment variables — configglue 1.1.2 documentation](https://configglue.readthedocs.io/en/latest/topics/environment-variables.html)

---

## 5. Backward Compatibility

### Research Question

How should we handle loading old JSON diagrams that don't have a theme field? What are the Pydantic Optional field patterns?

### Decision

**Add `theme` as an Optional field with default `None` in the Pydantic schema. Use the resolution function to apply defaults when loading diagrams.**

### Rationale

1. **Pydantic V2 Semantics**: In Pydantic V2, `Optional[str] = None` means the field is not required and defaults to `None` if absent. This is the correct pattern for backward-compatible schema evolution.

2. **Graceful Degradation**: Existing diagrams without a theme field will load successfully with `theme=None`, then the resolution function will apply the appropriate default based on session/environment configuration.

3. **Forward Compatibility**: New diagrams will serialize with an explicit theme field, making future migrations easier.

4. **No Data Loss**: The `extra="forbid"` policy remains intact for all other fields, ensuring strict validation while allowing this specific field to be optional.

5. **Consistent with Existing Patterns**: The codebase already uses Optional fields for backward compatibility:
   - `width: Optional[float] = None` (added in feature 007)
   - `height: Optional[float] = None` (added in feature 007)
   - `custom_latex: Optional[str] = None` (added in feature 002)

### Implementation Pattern

**Pydantic Schema (`schema.py`)**:
```python
class DiagramModel(BaseModel):
    """Diagram schema - complete block diagram with version."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0.0"
    blocks: list[BlockModel] = Field(default_factory=list)
    connections: list[ConnectionModel] = Field(default_factory=list)
    theme: Optional[str] = None  # NEW: Optional for backward compatibility
    _version: Optional[float] = None  # Internal timestamp (not persisted)
```

**Diagram Loading (`diagram.py`)**:
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Diagram":
    """Deserialize diagram from dictionary.

    Args:
        data: Serialized diagram dictionary

    Returns:
        Diagram instance
    """
    from lynx.utils.theme_config import resolve_theme

    # Validate with Pydantic schema
    diagram_model = DiagramModel.model_validate(data)

    # Create diagram instance
    diagram = cls()

    # Resolve theme (handles None from old diagrams)
    diagram.theme = resolve_theme(diagram_model.theme)

    # Load blocks and connections
    # ... (existing deserialization logic)

    return diagram
```

### Migration Scenarios

**Scenario 1: Old Diagram without Theme Field**
```json
{
  "version": "1.0.0",
  "blocks": [...],
  "connections": [...]
}
```
- Pydantic parses `theme` as `None` (field is optional)
- `resolve_theme(None)` applies session/environment/built-in default
- Diagram loads successfully with resolved theme

**Scenario 2: New Diagram with Theme Field**
```json
{
  "version": "1.0.0",
  "blocks": [...],
  "connections": [...],
  "theme": "dark"
}
```
- Pydantic parses `theme` as `"dark"`
- `resolve_theme("dark")` validates and returns `"dark"`
- Diagram loads with explicit theme

**Scenario 3: Diagram with Invalid Theme**
```json
{
  "version": "1.0.0",
  "blocks": [...],
  "connections": [...],
  "theme": "purple"
}
```
- Pydantic parses `theme` as `"purple"` (string is valid type)
- `resolve_theme("purple")` logs warning, falls back to session/environment/built-in default
- Diagram loads successfully (graceful degradation)

### Pydantic V2 Optional Semantics

**Important Note**: In Pydantic V2, the semantics of `Optional` changed from V1:
- **V1**: `Optional[str]` implied a default of `None` (not required)
- **V2**: `Optional[str]` means the field is required but allows `None` values
- **V2 with default**: `Optional[str] = None` means the field is not required and defaults to `None`

Our pattern uses `Optional[str] = None`, making the field truly optional (backward compatible).

### Alternatives Considered

**Alternative 1: Required Theme Field with Migration Script**
- **Pros**: Clean schema, no Optional complexity
- **Cons**: Breaks existing diagrams, requires users to run migration script, poor user experience
- **Rejected**: Violates backward compatibility requirement

**Alternative 2: Use Field with `default_factory`**
- **Pros**: More explicit, could inject resolved theme at parse time
- **Cons**: Resolution logic would run during Pydantic validation (side effects), couples schema to business logic
- **Rejected**: Violates separation of concerns

**Alternative 3: Store Theme in Separate Metadata File**
- **Pros**: Complete backward compatibility (no schema change)
- **Cons**: Two files to manage, synchronization issues, complexity
- **Rejected**: Over-engineered solution for single optional field

### References

- [Fields - Pydantic Validation](https://docs.pydantic.dev/latest/concepts/fields/)
- [Migration Guide - Pydantic Validation](https://docs.pydantic.dev/latest/migration/)
- [What is best way to specify optional fields in pydantic? · pydantic/pydantic · Discussion #2462](https://github.com/pydantic/pydantic/discussions/2462)
- [Change of API in v2 to declare required and optional fields · pydantic/pydantic · Discussion #2353](https://github.com/pydantic/pydantic/discussions/2353)

---

## 6. React Theme Switching Performance

### Research Question

What's the most performant way to switch themes in React? Re-render with new CSS variables vs. pure CSS cascade?

### Decision

**Use pure CSS cascade with `data-theme` attribute changes. Avoid React re-renders for theme switching.**

### Rationale

1. **Performance Comparison**: CSS variables approach requires only layout + repaint by the browser, compared to the context approach which requires rerendering + layout + repaint. From a performance angle, CSS variables do significantly less work.

2. **Avoid Re-render Cascade**: When theme changes using ThemeProvider/Context, every styled component needs to be re-rendered to account for the theme change. When there are many components on the page, switching the theme takes a while with sometimes a noticeable delay, leading to poor user experience. Real-world examples show theme switching taking over 100ms of scripting alone with context-based approaches.

3. **Browser Optimization**: CSS custom properties leverage the browser's built-in optimizations, as CSS is typically faster to process and apply than JavaScript. The browser can optimize CSS variable updates more efficiently than JavaScript-triggered component re-renders.

4. **Minimal JavaScript**: With CSS Variables, only the component responsible for updating the `data-theme` attribute needs to re-render, while the browser handles style recalculation automatically. This is orders of magnitude faster than re-rendering dozens of components.

5. **Meets Performance Target**: The spec requires theme changes to apply within 100ms. Pure CSS cascade achieves this easily (typically <10ms), while context-based re-renders can exceed 100ms for complex diagrams.

### Implementation Pattern

**Apply Theme Without Re-rendering React Components**:

```typescript
// DiagramCanvas.tsx
function DiagramCanvas({ model }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Read initial theme
    const theme = model.get("theme") || "light";
    if (containerRef.current) {
      containerRef.current.setAttribute("data-theme", theme);
    }

    // Listen for theme changes from Python
    const handleThemeChange = () => {
      const newTheme = model.get("theme") || "light";
      if (containerRef.current) {
        // Pure DOM manipulation - no React re-render
        containerRef.current.setAttribute("data-theme", newTheme);
      }
    };

    model.on("change:theme", handleThemeChange);

    return () => {
      model.off("change:theme", handleThemeChange);
    };
  }, [model]);

  return (
    <div ref={containerRef} className="lynx-widget">
      {/* All child components inherit theme via CSS cascade */}
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

**Why This is Performant**:
1. `setAttribute()` is a synchronous DOM operation (typically <1ms)
2. Browser's CSS engine handles variable substitution (optimized C++ code)
3. Only affected styles are recalculated (not entire component tree)
4. No React reconciliation, no virtual DOM diffing
5. No component lifecycle hooks triggered
6. Minimal JavaScript execution time

### Performance Comparison

| Approach | Scripting Time | Layout/Paint | Total | Re-renders |
|----------|---------------|--------------|-------|------------|
| **CSS Variables (Chosen)** | <1ms | ~5-10ms | ~10ms | 0 |
| Context Re-render | 50-150ms | ~10-20ms | ~100ms+ | All styled components |
| CSS-in-JS Re-render | 100-200ms | ~10-20ms | ~150ms+ | All components |

### CSS Cascade Example

```css
/* styles.css */

/* Default theme variables */
@theme {
  --color-primary-600: #465082;
  --color-slate-800: #1e293b;
}

/* Dark theme overrides */
@layer base {
  [data-theme="dark"] {
    --color-primary-600: #818cf8;
    --color-slate-800: #cbd5e1;
  }
}

/* Component styles reference variables (no JS needed) */
.block {
  border: 2px solid var(--color-primary-600);
  background: var(--color-slate-800);
}
```

When `data-theme` changes from `"light"` to `"dark"`:
1. Browser detects attribute change
2. CSS engine re-evaluates matching selectors
3. Variable values update atomically
4. Browser repaints affected elements
5. Total time: ~5-10ms (no JavaScript involved)

### Alternatives Considered

**Alternative 1: React Context + ThemeProvider**
- **Pros**: Idiomatic React pattern, easy to access theme in components
- **Cons**: Forces re-render of entire component tree, 10-20x slower than CSS approach, can exceed 100ms performance budget
- **Rejected**: Performance penalty unacceptable for spec requirements

**Alternative 2: CSS-in-JS (styled-components, Emotion)**
- **Pros**: Scoped styles, dynamic styling
- **Cons**: Runtime style injection, even slower than Context approach, requires recomputing all styled components
- **Rejected**: Worst performance option, adds dependency

**Alternative 3: CSS Modules with Dynamic Imports**
- **Pros**: Type-safe, build-time optimization
- **Cons**: Requires loading/unloading CSS files, potential flash of unstyled content, doesn't work well with anywidget bundling
- **Rejected**: Complexity, FOUC risk

**Alternative 4: Inline Styles with React State**
- **Pros**: Direct control, no CSS cascade needed
- **Cons**: Requires passing theme state to every component, forces re-renders, loses browser optimization, poor maintainability
- **Rejected**: Anti-pattern, worst of both worlds

### References

- [Use CSS Variables instead of React Context | Epic React by Kent C. Dodds](https://www.epicreact.dev/css-variables)
- [CSS variables vs ThemeContext - DEV Community](https://dev.to/vtechguys/css-variables-vs-themecontext-o44)
- [Why We're Breaking Up with CSS-in-JS - DEV Community](https://dev.to/srmagura/why-were-breaking-up-wiht-css-in-js-4g9b)
- [How to use CSS variables with React • Josh W. Comeau](https://www.joshwcomeau.com/css/css-variables-for-react-devs/)

---

## Summary of Decisions

| Decision Area | Chosen Approach | Key Rationale |
|--------------|----------------|---------------|
| **CSS Strategy** | `data-theme` attribute + CSS variables in `@theme` | Tailwind v4 native support, semantic clarity, better organization |
| **WCAG Compliance** | 7:1 normal text, 4.5:1 large text + WebAIM Checker | Meets AAA standards, automated tooling available |
| **Traitlet Pattern** | Separate `theme` traitlet (not in `diagram_state`) | Granular change detection, clean separation, follows anywidget best practices |
| **Precedence Logic** | Instance > Session > Environment > Built-in Default | Standard precedence hierarchy, centralized resolution, fail-safe defaults |
| **Backward Compatibility** | `Optional[str] = None` in Pydantic schema | Graceful degradation, consistent with existing patterns, no data loss |
| **React Performance** | Pure CSS cascade (no re-renders) | 10x faster than context approach, meets 100ms requirement |

---

## Next Steps

1. **Phase 1 - Design**: Create `data-model.md`, `contracts/theme-sync.yaml`, and `quickstart.md` based on these decisions
2. **Phase 2 - Tasks**: Generate `tasks.md` using `/speckit.tasks` command to break implementation into actionable steps
3. **Phase 3 - Implementation**: Execute tasks following TDD principles (tests first, then implementation)

All technical decisions documented here are **APPROVED** and ready for implementation planning.
