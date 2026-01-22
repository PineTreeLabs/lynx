<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Data Model: Switchable CSS Themes

**Feature**: 010-switchable-themes
**Created**: 2026-01-14
**Purpose**: Define entities, attributes, relationships, and state management for the theme system

---

## Entities

### 1. Theme

**Description**: A named collection of visual styling rules (color palette, contrast levels) that defines the appearance of all diagram components.

**Attributes**:

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | `str` | Yes | - | Unique theme identifier (e.g., "light", "dark", "high-contrast") |
| `display_name` | `str` | Yes | - | Human-readable name shown in UI (e.g., "Light", "Dark", "High Contrast") |
| `css_palette` | `dict[str, str]` | Yes | - | CSS variable mappings (e.g., `{"--color-primary-600": "#465082"}`) |

**Validation Rules**:
- `name` must be lowercase, alphanumeric with hyphens (e.g., "light", "high-contrast")
- `name` must be one of the valid theme names: `{"light", "dark", "high-contrast"}`
- `css_palette` must define all required CSS variables (see Constants below)

**Constants**:
```python
VALID_THEMES = {"light", "dark", "high-contrast"}
BUILT_IN_DEFAULT_THEME = "light"

REQUIRED_CSS_VARIABLES = {
    "--color-primary-600",     # Block strokes, port markers, resize handles
    "--color-primary-700",     # Darker primary (hover states)
    "--color-primary-500",     # Lighter primary (active states)
    "--color-slate-50",        # Canvas background
    "--color-slate-200",       # Block fills, grid dots
    "--color-slate-900",       # Text color
    "--color-slate-700",       # Borders, dividers
    "--color-slate-400",       # Edge default color
    "--color-error",           # Red for errors/invalid connections
    "--color-warning",         # Amber for warnings
    "--color-success",         # Green for valid connections
    "--color-shadow",          # Shadow color for overlays
    "--color-input-blue",      # Input port indicators
    "--color-output-red",      # Output port indicators
}
```

**Relationships**:
- Referenced by `Diagram` entities (many-to-one: many diagrams can use the same theme)
- Referenced by `ThemeConfiguration` entities for defaults

---

### 2. Diagram

**Description**: A block diagram instance with an associated theme preference.

**Modified Attributes** (existing attributes not listed):

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `theme` | `Optional[str]` | No | `None` | Diagram-specific theme name (takes precedence over all defaults) |

**Validation Rules**:
- If `theme` is not `None`, it must be a valid theme name from `VALID_THEMES`
- If `theme` is `None`, theme is resolved via precedence chain (see ThemeConfiguration)
- Invalid theme names are logged as warnings and fallback to resolved default

**Persistence**:
- `theme` field is serialized to JSON via Pydantic `DiagramModel` schema
- Field is `Optional[str] = None` in schema (backward compatible with existing diagrams)
- Old diagrams without `theme` field load correctly (defaults to `None`)

**State Transitions**:
```
State: None (no theme set)
  ↓
Action: diagram.theme = "dark" (Python API)
  ↓
State: "dark"
  ↓
Action: User selects "light" via UI
  ↓
State: "light" (UI change propagates to diagram.theme)
  ↓
Action: diagram.save("file.json")
  ↓
Persisted: {"theme": "light", ...other fields...}
  ↓
Action: diagram = lynx.Diagram.load("file.json")
  ↓
State: "light" (restored from JSON)
```

**Relationships**:
- References one `Theme` by name (foreign key relationship)
- Owned by one `LynxWidget` instance (one-to-one composition)

---

### 3. ThemeConfiguration

**Description**: Global and session-level theme settings that provide fallback theme names when diagrams don't specify one.

**Attributes**:

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `environment_default` | `Optional[str]` | No | `None` | Theme name from `LYNX_DEFAULT_THEME` environment variable |
| `session_default` | `Optional[str]` | No | `None` | Theme name from `lynx.set_default_theme()` call |

**Validation Rules**:
- Both fields must be valid theme names from `VALID_THEMES` or `None`
- Invalid values are logged as warnings and replaced with `None`

**Implementation**:
- Singleton pattern (module-level variable in `src/lynx/utils/theme_config.py`)
- Environment variable is read once at module import time
- Session default is mutable via `set_default_theme()` function

**Precedence Logic**:
```python
def resolve_theme(diagram_theme: Optional[str]) -> str:
    """
    Resolve the effective theme for a diagram.

    Precedence order (highest to lowest):
    1. diagram.theme (diagram-level attribute)
    2. session_default (set via set_default_theme())
    3. environment_default (LYNX_DEFAULT_THEME env var)
    4. BUILT_IN_DEFAULT_THEME ("light")

    Returns:
        Valid theme name (never None)
    """
    if diagram_theme is not None:
        return diagram_theme
    if session_default is not None:
        return session_default
    if environment_default is not None:
        return environment_default
    return BUILT_IN_DEFAULT_THEME
```

**Relationships**:
- Provides defaults for all `Diagram` entities
- No persistent storage (ephemeral session state)

---

### 4. LynxWidget

**Description**: anywidget wrapper for Lynx diagrams, manages Python-JavaScript synchronization.

**Modified Attributes** (existing traitlets not listed):

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `theme` | `traitlets.Unicode` | Yes | `"light"` | Currently resolved theme name, synced to JavaScript |

**Synchronization**:
- Traitlet is tagged with `.tag(sync=True)` for bidirectional Python-JS sync
- JavaScript reads initial value from `model.get("theme")`
- JavaScript listens to changes via `model.on("change:theme", callback)`
- JavaScript sends updates via `model.set("theme", "dark"); model.save_changes()`

**Initialization**:
```python
# When widget is created:
self.theme = resolve_theme(self.diagram.theme)
```

**Action Handlers**:
- `_on_theme_change()`: Observer that updates `diagram.theme` when traitlet changes
- `_on_action()`: Handles `updateTheme` actions from JavaScript UI

**Relationships**:
- Owns one `Diagram` instance (composition)
- Bridges to JavaScript frontend via traitlets

---

## Relationships Diagram

```
┌─────────────────────────┐
│   ThemeConfiguration    │  (module-level singleton)
│  ┌──────────────────┐   │
│  │ environment_default│  │  ← Read from os.environ["LYNX_DEFAULT_THEME"]
│  │ session_default    │  │  ← Set via set_default_theme()
│  └──────────────────┘   │
└───────────┬─────────────┘
            │ provides defaults
            ↓
      ┌──────────┐
      │  Diagram │  (has optional theme attribute)
      │ ┌──────┐ │
      │ │ theme│ │  ← Optional[str] = None
      │ └──────┘ │
      └─────┬────┘
            │ owned by
            ↓
      ┌────────────┐
      │ LynxWidget │  (anywidget instance)
      │ ┌────────┐ │
      │ │ theme  │ │  ← traitlets.Unicode (synced to JS)
      │ └────────┘ │
      └─────┬──────┘
            │ syncs to
            ↓
    ┌──────────────┐
    │  JavaScript  │  (React frontend)
    │ ┌──────────┐ │
    │ │data-theme│ │  ← HTML attribute on container
    │ └──────────┘ │
    └──────────────┘
            │ selects
            ↓
      ┌──────────┐
      │   Theme  │  (CSS custom properties)
      │ ┌──────┐ │
      │ │ name │ │  ← "light" | "dark" | "high-contrast"
      │ └──────┘ │
      └──────────┘
```

---

## State Management

### Python Backend State

**Location**: `src/lynx/utils/theme_config.py`

**Global Variables**:
```python
# Module-level singleton
_environment_default: Optional[str] = None  # Read from LYNX_DEFAULT_THEME
_session_default: Optional[str] = None      # Set via set_default_theme()

# Initialized at module import
_environment_default = os.environ.get("LYNX_DEFAULT_THEME")
if _environment_default and _environment_default not in VALID_THEMES:
    logging.warning(f"Invalid LYNX_DEFAULT_THEME: {_environment_default}")
    _environment_default = None
```

**Public API**:
```python
def set_default_theme(theme_name: str) -> None:
    """Set session-wide default theme."""
    global _session_default
    if theme_name not in VALID_THEMES:
        logging.warning(f"Invalid theme name: {theme_name}")
        return
    _session_default = theme_name

def get_session_default() -> Optional[str]:
    """Get current session default theme."""
    return _session_default

def get_environment_default() -> Optional[str]:
    """Get environment variable default theme."""
    return _environment_default

def resolve_theme(diagram_theme: Optional[str]) -> str:
    """Resolve effective theme using precedence rules."""
    # Implementation shown above
```

**Thread Safety**: Not required (Python single-threaded execution in Jupyter)

---

### JavaScript Frontend State

**Location**: `js/src/DiagramCanvas.tsx`

**React State**:
```typescript
const [currentTheme, setCurrentTheme] = useState<string>("light");

// Sync from Python on mount and changes
useEffect(() => {
  const theme = model.get("theme") as string;
  setCurrentTheme(theme);

  const onChange = () => {
    const newTheme = model.get("theme") as string;
    setCurrentTheme(newTheme);
  };

  model.on("change:theme", onChange);
  return () => model.off("change:theme", onChange);
}, [model]);
```

**DOM Application**:
```typescript
<div className="lynx-widget" data-theme={currentTheme}>
  {/* All components inherit theme via CSS cascade */}
</div>
```

**User-Triggered Updates**:
```typescript
const handleThemeChange = (newTheme: string) => {
  // Optimistic update (immediate visual feedback)
  setCurrentTheme(newTheme);

  // Sync to Python (propagates to diagram.theme)
  sendAction(model, "updateTheme", { theme: newTheme });
};
```

---

## Persistence Schema

**Pydantic Model** (in `src/lynx/schema.py`):

```python
class DiagramModel(BaseModel):
    """Schema for JSON serialization of diagrams."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    version: str
    blocks: list[BlockModel]
    connections: list[ConnectionModel]
    theme: Optional[str] = None  # NEW FIELD
    _version: Optional[float] = None  # Timestamp
```

**JSON Example** (saved diagram):
```json
{
  "version": "1.0.0",
  "theme": "dark",
  "blocks": [...],
  "connections": [...],
  "_version": 1736899200.0
}
```

**Backward Compatibility**:
- Old diagrams without `theme` field: `{"version": "1.0.0", "blocks": [...], "connections": [...]}`
- Pydantic loads with `theme=None` (uses precedence chain to resolve)
- No migration required

---

## Validation Rules Summary

### Theme Name Validation

**Function**: `validate_theme_name(name: Optional[str]) -> Optional[str]`

**Rules**:
1. If `name` is `None`, return `None` (valid)
2. If `name` in `VALID_THEMES`, return `name` (valid)
3. Otherwise, log warning and return `None` (invalid)

**Locations**:
- `Diagram.__init__()` and `Diagram.theme` setter
- `LynxWidget._on_action()` handler for `updateTheme` action
- `set_default_theme()` function
- `ThemeConfiguration` initialization (environment variable)

### Diagram Load Validation

**Process**:
1. Pydantic validates JSON schema (ensures `theme` is `str | None` if present)
2. `Diagram.from_dict()` calls `validate_theme_name(data.get("theme"))`
3. If invalid, warning is logged and `theme` is set to `None`
4. Widget resolves effective theme via `resolve_theme()` on display

---

## Edge Cases

### Case 1: Invalid Theme in Saved Diagram

**Scenario**: User saves diagram with `theme="purple"` (invalid name)

**Handling**:
1. `Diagram.save()` writes `{"theme": "purple", ...}` to JSON (no validation on save)
2. `Diagram.load()` reads JSON, Pydantic validates type (`str`)
3. `validate_theme_name("purple")` logs warning, returns `None`
4. `diagram.theme = None`, resolved via precedence chain

**Rationale**: Fail gracefully, don't crash on load

---

### Case 2: Environment Variable Changed During Session

**Scenario**: User sets `LYNX_DEFAULT_THEME=dark`, starts Python, then changes env var to `light`

**Handling**:
- `_environment_default` is read once at module import
- Changing env var during session has no effect
- Workaround: `importlib.reload(lynx.utils.theme_config)` (not recommended)

**Rationale**: Environment variables are typically set before process start

---

### Case 3: Multiple Diagrams in One Notebook

**Scenario**: User creates `diagram1` with `theme="dark"`, then creates `diagram2` without theme

**Handling**:
1. `diagram1.theme = "dark"` (explicit)
2. `diagram2.theme = None` (no explicit theme)
3. Both widgets resolve themes independently:
   - `widget1.theme = resolve_theme("dark")` → `"dark"`
   - `widget2.theme = resolve_theme(None)` → session/env/default
4. Changing `diagram2.theme` does not affect `diagram1`

**Rationale**: Diagrams are independent entities

---

### Case 4: UI Change vs. Programmatic Change

**Scenario**: User selects "dark" via UI, then runs `diagram.theme = "light"` in Python

**Handling**:
1. UI sends `updateTheme` action → Python sets `diagram.theme = "dark"`
2. Widget syncs `self.theme = "dark"` → JS updates `data-theme="dark"`
3. User runs `diagram.theme = "light"` in Python
4. Widget observer triggers, syncs `self.theme = "light"` → JS updates `data-theme="light"`

**Rationale**: Most recent explicit action wins (no conflict resolution needed)

---

## Performance Considerations

### Theme Switching Performance

**Target**: <100ms from user action to visual update

**Bottlenecks**:
1. **Python → JS sync**: anywidget traitlet change (~10ms)
2. **React re-render**: useState update + data-theme attribute change (~5ms)
3. **CSS variable cascade**: Browser repaints with new colors (~10-50ms depending on complexity)

**Total**: ~25-65ms (well within 100ms target)

**Optimization**: Use pure CSS cascade (no React Context), minimizes re-renders

---

### Memory Footprint

**Per-Diagram Overhead**:
- Python: `theme` attribute (8 bytes for `None`, 50-100 bytes for string)
- JavaScript: `currentTheme` state (50-100 bytes)
- CSS: No additional memory (CSS variables are global)

**Total per diagram**: ~150-200 bytes (negligible)

---

## Testing Considerations

### Unit Tests (pytest)

**Test Coverage**:
- `test_validate_theme_name()`: Valid, invalid, None cases
- `test_resolve_theme()`: All precedence combinations (16 cases: 2^4)
- `test_set_default_theme()`: Valid, invalid, overwrite cases
- `test_diagram_theme_persistence()`: Save/load with theme, backward compat

**Fixtures**:
```python
@pytest.fixture
def clean_theme_config():
    """Reset global theme config before each test."""
    import lynx.utils.theme_config as config
    config._session_default = None
    yield
    config._session_default = None
```

---

### Integration Tests (pytest)

**Test Coverage**:
- `test_ui_theme_change_propagates()`: Simulate UI action, verify diagram.theme
- `test_diagram_theme_syncs_to_widget()`: Set diagram.theme, verify widget.theme
- `test_environment_variable_precedence()`: Mock os.environ, verify resolution

---

### Frontend Tests (Vitest)

**Test Coverage**:
- `test_theme_selector_ui()`: Click dropdown, select theme, verify callback
- `test_theme_applies_to_dom()`: Verify `data-theme` attribute on container
- `test_theme_sync_from_model()`: Mock model change, verify React state update

---

## Summary

This data model defines three core entities (Theme, Diagram, ThemeConfiguration) and their relationships. Themes are immutable named palettes, Diagrams have optional theme preferences, and ThemeConfiguration provides global defaults. State flows from Python (business logic) to JavaScript (presentation) via anywidget traitlets, with theme changes applied instantly via CSS cascade. Validation ensures graceful fallback to defaults, and persistence uses Pydantic schemas for backward-compatible JSON serialization.

**Next Steps**: See `contracts/theme-sync.yaml` for Python-JS communication API and `quickstart.md` for usage examples.
