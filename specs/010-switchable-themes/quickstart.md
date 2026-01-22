<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart Guide: Switchable CSS Themes

**Feature**: 010-switchable-themes
**Created**: 2026-01-14
**Audience**: End users and developers testing theme functionality

---

## Overview

Lynx now supports three built-in visual themes:
- **Light** (default): High brightness, suitable for well-lit environments
- **Dark**: Reduced brightness, easier on eyes in low-light conditions
- **High Contrast**: WCAG 2.1 AAA compliant, optimized for accessibility

Themes can be set in three ways (in order of precedence):
1. **Per-diagram**: Via constructor, attribute, or UI (highest priority)
2. **Session-wide**: Via `lynx.set_default_theme()` function
3. **System-wide**: Via `LYNX_DEFAULT_THEME` environment variable

---

## Quick Examples

### Example 1: Using the UI (Most Common)

```python
import lynx

# Create a diagram (uses default light theme)
diagram = lynx.Diagram()

# Display the widget
diagram
```

**In Jupyter:**
1. Click the **⚙️ gear icon** (bottom-left of diagram)
2. Select **"Theme"** from the menu
3. Choose **"Dark"**, **"Light"**, or **"High Contrast"**
4. Theme changes instantly ✨

**Result**: Diagram updates immediately, theme preference is saved to diagram JSON.

---

### Example 2: Setting Theme Programmatically

```python
import lynx

# Create diagram with explicit theme
dark_diagram = lynx.Diagram(theme="dark")
dark_diagram

# Or change theme after creation
light_diagram = lynx.Diagram()
light_diagram.theme = "high-contrast"
light_diagram
```

**Result**: Each diagram uses its specified theme, overriding all defaults.

---

### Example 3: Session-Wide Default Theme

```python
import lynx

# Set default theme for this session
lynx.set_default_theme("dark")

# All new diagrams use dark theme
diagram1 = lynx.Diagram()  # Uses dark theme
diagram2 = lynx.Diagram()  # Uses dark theme

# Explicit theme still takes precedence
diagram3 = lynx.Diagram(theme="light")  # Uses light theme
```

**Result**: Reduces repetition when working with multiple diagrams.

---

### Example 4: System-Wide Default (Environment Variable)

**In terminal (before starting Python):**
```bash
export LYNX_DEFAULT_THEME=high-contrast
jupyter notebook
```

**In Python notebook:**
```python
import lynx

# Uses high-contrast theme from environment variable
diagram = lynx.Diagram()
diagram
```

**Result**: All Lynx sessions use high-contrast theme by default (useful for accessibility).

---

## Complete Usage Guide

### 1. Per-Diagram Themes

#### Via Constructor

```python
import lynx

# Specify theme when creating diagram
diagram = lynx.Diagram(theme="dark")
diagram
```

#### Via Attribute Assignment

```python
import lynx

# Change theme after creation
diagram = lynx.Diagram()
diagram.theme = "dark"
diagram  # Re-display to see changes
```

#### Via UI Settings

```python
import lynx

# Create and display diagram
diagram = lynx.Diagram()
diagram
```

**Steps:**
1. Click **⚙️ Settings** button (bottom-left)
2. Select **Theme** submenu
3. Click desired theme (**Light**, **Dark**, or **High Contrast**)
4. Checkmark (✓) indicates current theme

**Verification:**
```python
# Check current theme in Python
print(diagram.theme)  # Reflects UI selection
```

---

### 2. Session-Wide Default Theme

Set a default theme for all new diagrams in the current Python session:

```python
import lynx

# Set session default (affects future diagrams)
lynx.set_default_theme("dark")

# Verify it's set
diagram1 = lynx.Diagram()
print(diagram1.theme)  # "dark"

# Change session default mid-session
lynx.set_default_theme("light")

diagram2 = lynx.Diagram()
print(diagram2.theme)  # "light"

# Explicit themes still override
diagram3 = lynx.Diagram(theme="high-contrast")
print(diagram3.theme)  # "high-contrast"
```

**Notes:**
- Only affects **newly created** diagrams
- Does **not** change themes of existing diagrams
- Persists for entire Python session (until kernel restart)

---

### 3. Environment Variable Default

Set a system-wide default theme via environment variable (before starting Python):

**Linux/macOS:**
```bash
export LYNX_DEFAULT_THEME=dark
jupyter notebook
```

**Windows (PowerShell):**
```powershell
$env:LYNX_DEFAULT_THEME = "dark"
jupyter notebook
```

**Windows (Command Prompt):**
```cmd
set LYNX_DEFAULT_THEME=dark
jupyter notebook
```

**In Python:**
```python
import lynx

# Uses theme from environment variable
diagram = lynx.Diagram()
print(diagram.theme)  # "dark"

# Session default overrides environment
lynx.set_default_theme("light")
diagram2 = lynx.Diagram()
print(diagram2.theme)  # "light"

# Explicit theme overrides everything
diagram3 = lynx.Diagram(theme="high-contrast")
print(diagram3.theme)  # "high-contrast"
```

**Use Cases:**
- Accessibility: Users who always need high-contrast mode
- CI/CD: Automated testing with consistent theme
- Teams: Organization-wide default theme

---

## Theme Precedence Examples

### Precedence Rule

Themes are resolved in this order (highest to lowest priority):

1. **Diagram-level** (constructor, attribute, or UI)
2. **Session-level** (`set_default_theme()`)
3. **Environment-level** (`LYNX_DEFAULT_THEME`)
4. **Built-in default** (`"light"`)

### Example: All Defaults Set

```bash
# In terminal
export LYNX_DEFAULT_THEME=high-contrast
```

```python
import lynx

# Set session default
lynx.set_default_theme("dark")

# Create diagrams with different precedence levels
d1 = lynx.Diagram()                          # Uses session default: "dark"
d2 = lynx.Diagram(theme="light")             # Explicit theme: "light"
d3 = lynx.Diagram()
d3.theme = "high-contrast"                   # Attribute override: "high-contrast"

print(d1.theme)  # "dark" (session > environment)
print(d2.theme)  # "light" (explicit > session)
print(d3.theme)  # "high-contrast" (attribute > session)
```

### Example: No Defaults Set

```python
import lynx
# No environment variable, no set_default_theme() call

diagram = lynx.Diagram()
print(diagram.theme)  # "light" (built-in default)
```

---

## Theme Persistence

Themes **automatically persist** when saving diagrams:

```python
import lynx

# Create diagram with dark theme
diagram = lynx.Diagram(theme="dark")
diagram.add_gain_block(gain=5.0)

# Save diagram
diagram.save("my_diagram.json")

# Load diagram later (theme is preserved)
loaded = lynx.Diagram.load("my_diagram.json")
print(loaded.theme)  # "dark"
```

**JSON Format:**
```json
{
  "version": "1.0.0",
  "theme": "dark",
  "blocks": [...],
  "connections": [...]
}
```

**Backward Compatibility:**
Old diagrams saved without a theme field load correctly (default to precedence chain):

```python
# Old diagram JSON (no theme field):
# {"version": "1.0.0", "blocks": [...], "connections": [...]}

loaded_old = lynx.Diagram.load("old_diagram.json")
print(loaded_old.theme)  # None (resolved via precedence chain)
```

---

## Validation and Error Handling

### Invalid Theme Names

```python
import lynx

# Invalid theme name in constructor
diagram = lynx.Diagram(theme="purple")  # ⚠️ Warning logged
print(diagram.theme)  # None (falls back to precedence chain)

# Invalid theme name via attribute
diagram.theme = "rainbow"  # ⚠️ Warning logged
print(diagram.theme)  # None (falls back to precedence chain)

# Invalid session default
lynx.set_default_theme("neon")  # ⚠️ Warning logged
# Session default not changed
```

**Console Output:**
```
WARNING: Invalid theme name: purple. Using default.
WARNING: Invalid theme name: rainbow. Using default.
WARNING: Invalid theme name: neon. Valid themes: light, dark, high-contrast
```

**Valid Theme Names:**
- `"light"`
- `"dark"`
- `"high-contrast"`

*(Case-sensitive, lowercase only)*

---

## Testing Scenarios

### Test Scenario 1: UI Theme Selection

**Steps:**
1. Create and display diagram: `diagram = lynx.Diagram(); diagram`
2. Click ⚙️ settings button
3. Select "Theme" submenu
4. Choose "Dark"
5. Verify visual change (background darkens, colors invert)
6. Check Python attribute: `print(diagram.theme)`

**Expected:**
- ✅ Theme changes instantly (<3 seconds including menu navigation)
- ✅ `diagram.theme == "dark"`
- ✅ Checkmark appears next to "Dark" in menu

---

### Test Scenario 2: Theme Persistence

**Steps:**
1. Create diagram with theme: `d = lynx.Diagram(theme="high-contrast")`
2. Add blocks: `d.add_gain_block(gain=2.0)`
3. Save: `d.save("test.json")`
4. Restart Python kernel (simulate new session)
5. Load: `loaded = lynx.Diagram.load("test.json")`
6. Display: `loaded`

**Expected:**
- ✅ Loaded diagram uses high-contrast theme
- ✅ `loaded.theme == "high-contrast"`
- ✅ Visual appearance matches original

---

### Test Scenario 3: Precedence Rules

**Steps:**
1. Set environment variable: `export LYNX_DEFAULT_THEME=dark` (in terminal)
2. Start Python: `import lynx`
3. Set session default: `lynx.set_default_theme("light")`
4. Create diagram: `d = lynx.Diagram()`
5. Check theme: `print(d.theme)`

**Expected:**
- ✅ `d.theme == "light"` (session overrides environment)

**Continue:**
6. Create explicit diagram: `d2 = lynx.Diagram(theme="high-contrast")`
7. Check theme: `print(d2.theme)`

**Expected:**
- ✅ `d2.theme == "high-contrast"` (explicit overrides session)

---

### Test Scenario 4: Multiple Diagrams Independence

**Steps:**
1. Create diagram 1: `d1 = lynx.Diagram(theme="dark"); d1`
2. Create diagram 2: `d2 = lynx.Diagram(theme="light"); d2`
3. Change d1 theme via UI: Select "High Contrast" in d1's settings
4. Check both: `print(d1.theme, d2.theme)`

**Expected:**
- ✅ `d1.theme == "high-contrast"`
- ✅ `d2.theme == "light"` (unchanged)
- ✅ Each diagram maintains independent theme

---

### Test Scenario 5: Rapid Theme Switching (Performance)

**Steps:**
1. Create and display diagram: `d = lynx.Diagram(); d`
2. Rapidly switch themes in UI:
   - Click "Dark"
   - Immediately click "Light"
   - Immediately click "High Contrast"
3. Observe visual updates

**Expected:**
- ✅ Each theme change applies within 100ms (no lag)
- ✅ No visual artifacts or flickering
- ✅ Final theme is "high-contrast" (last selection wins)

---

## Accessibility Testing

### WCAG 2.1 AAA Contrast Verification

**High-Contrast Theme Requirements:**
- Normal text (<24px): 7:1 minimum contrast ratio
- Large text (≥24px): 4.5:1 minimum contrast ratio

**Manual Testing:**
1. Create diagram with high-contrast theme:
   ```python
   import lynx
   d = lynx.Diagram(theme="high-contrast")
   d.add_gain_block(gain=5.0)  # Block with text
   d
   ```

2. Use browser DevTools or contrast checker:
   - **Firefox**: Accessibility Inspector → Contrast ratio
   - **Chrome**: DevTools → Elements → Contrast ratio indicator
   - **WebAIM**: https://webaim.org/resources/contrastchecker/

3. Verify text contrast ratios:
   - Block labels (16px): Should show ≥7:1
   - Parameter values (14px): Should show ≥7:1
   - LaTeX math (varies): Should show ≥7:1 for <24px

**Expected:**
- ✅ All text meets WCAG 2.1 AAA standards
- ✅ No contrast warnings in browser DevTools

---

### Keyboard Navigation Testing

**Steps:**
1. Create and display diagram: `d = lynx.Diagram(); d`
2. Press `Tab` key repeatedly to navigate UI
3. When ⚙️ settings button has focus, press `Enter`
4. Use arrow keys to navigate Theme submenu
5. Press `Enter` to select theme

**Expected:**
- ✅ Settings button is keyboard-focusable
- ✅ Theme submenu is keyboard-navigable
- ✅ Theme selection works via keyboard
- ✅ Focus indicators visible in all themes

---

### Screen Reader Testing

**Steps:**
1. Enable screen reader (NVDA, JAWS, VoiceOver)
2. Create and display diagram: `d = lynx.Diagram(); d`
3. Navigate to settings button with screen reader
4. Activate settings menu
5. Navigate to Theme submenu
6. Listen to theme options and current selection

**Expected:**
- ✅ Settings button announces: "Settings, button"
- ✅ Theme submenu announces: "Theme, menu"
- ✅ Current theme announced: "Light, checked" (or current theme)
- ✅ Other themes announced: "Dark, not checked"

---

## Advanced Usage

### Working with 50+ Diagrams (Performance Test)

```python
import lynx

# Set session default to avoid repetition
lynx.set_default_theme("dark")

# Create many diagrams
diagrams = []
for i in range(50):
    d = lynx.Diagram()
    d.add_gain_block(gain=i * 0.1)
    diagrams.append(d)

# Display all (in separate cells)
for d in diagrams:
    display(d)

# Change session default (does NOT affect existing diagrams)
lynx.set_default_theme("light")

# New diagrams use new default
new_diagram = lynx.Diagram()
print(new_diagram.theme)  # "light"
print(diagrams[0].theme)  # "dark" (unchanged)
```

**Expected:**
- ✅ No performance degradation
- ✅ Each diagram maintains independent theme state
- ✅ Memory usage scales linearly (~200 bytes per diagram)

---

### Custom Workflows

#### Workflow 1: Batch Theme Update

```python
import lynx

# Create multiple diagrams
diagrams = [lynx.Diagram() for _ in range(10)]

# Batch update all themes
for d in diagrams:
    d.theme = "dark"

# Display all with consistent theme
for d in diagrams:
    display(d)
```

---

#### Workflow 2: Theme-Based Conditionals

```python
import lynx

diagram = lynx.Diagram()

# Customize behavior based on theme
if diagram.theme == "high-contrast":
    print("Accessibility mode enabled")
    # Add extra labels for screen readers, etc.
elif diagram.theme == "dark":
    print("Low-light mode enabled")
else:
    print("Standard mode")
```

---

#### Workflow 3: CI/CD Testing

```bash
#!/bin/bash
# test_themes.sh - Automated theme testing

export LYNX_DEFAULT_THEME=light
python test_light_theme.py

export LYNX_DEFAULT_THEME=dark
python test_dark_theme.py

export LYNX_DEFAULT_THEME=high-contrast
python test_accessibility.py
```

---

## Troubleshooting

### Theme Not Changing in UI

**Symptom:** Click theme in menu, but diagram appearance doesn't change.

**Solutions:**
1. Refresh browser page (clears CSS cache)
2. Check browser console for JavaScript errors
3. Verify `diagram.theme` in Python: `print(diagram.theme)`
4. Try programmatic change: `diagram.theme = "dark"; diagram`

---

### Theme Resets After Kernel Restart

**Symptom:** Diagram theme returns to "light" after restarting Python kernel.

**Cause:** Session default (`set_default_theme()`) is not persisted across sessions.

**Solutions:**
1. **Save diagrams**: Use `diagram.save()` to persist theme in JSON
2. **Set environment variable**: Add `export LYNX_DEFAULT_THEME=dark` to `.bashrc` or `.zshrc`
3. **Re-run setup cell**: Add `lynx.set_default_theme("dark")` to notebook setup

---

### Invalid Theme Warning

**Symptom:** See warning: `Invalid theme name: <name>. Using default.`

**Cause:** Typo or unsupported theme name.

**Solutions:**
1. Check spelling: Must be exactly `"light"`, `"dark"`, or `"high-contrast"` (lowercase)
2. Verify case-sensitivity: `"Light"` is invalid, use `"light"`
3. Check for spaces: `"high contrast"` is invalid, use `"high-contrast"`

**Valid Examples:**
```python
diagram.theme = "light"           # ✅ Valid
diagram.theme = "dark"            # ✅ Valid
diagram.theme = "high-contrast"   # ✅ Valid

diagram.theme = "Light"           # ❌ Invalid (capitalized)
diagram.theme = "high contrast"   # ❌ Invalid (space instead of hyphen)
diagram.theme = "purple"          # ❌ Invalid (not a built-in theme)
```

---

### Environment Variable Not Working

**Symptom:** Set `LYNX_DEFAULT_THEME` but diagrams still use light theme.

**Causes & Solutions:**

1. **Variable set after Python started:**
   - ✅ **Fix:** Restart Python kernel or Jupyter server

2. **Typo in variable name:**
   - ❌ `LYNX_THEME=dark` (wrong name)
   - ✅ `LYNX_DEFAULT_THEME=dark` (correct name)

3. **Session default overriding:**
   - If `set_default_theme()` was called, it overrides environment variable
   - ✅ **Fix:** Remove `set_default_theme()` call or restart kernel

4. **Verify environment variable:**
   ```python
   import os
   print(os.environ.get("LYNX_DEFAULT_THEME"))  # Should print "dark"
   ```

---

### Multiple Themes in Same Notebook

**Symptom:** Want different diagrams to have different themes in same notebook.

**Solution:** Use explicit per-diagram themes (highest precedence):

```python
import lynx

# Each diagram gets explicit theme
d1 = lynx.Diagram(theme="light")
d2 = lynx.Diagram(theme="dark")
d3 = lynx.Diagram(theme="high-contrast")

# Display side-by-side for comparison
d1, d2, d3
```

---

## FAQ

### Q: Can I create custom themes?

**A:** Not in v1.0. The feature is designed for extensibility, but custom themes are out of scope for this release. Future versions may support user-defined themes.

---

### Q: Do themes affect printed/exported diagrams?

**A:** Depends on export format. Themes are CSS-based, so:
- ✅ **Screenshot/PNG export**: Captures current theme appearance
- ✅ **Browser print**: Uses current theme (may want light theme for printing)
- ❌ **SVG export**: Depends on whether CSS variables are embedded

**Tip:** Switch to light theme before printing/exporting for best results.

---

### Q: Can I preview themes before selecting?

**A:** Not in v1.0. Theme preview is out of scope. You can quickly switch between themes to compare (changes are instant).

---

### Q: Does theme affect diagram functionality?

**A:** No. Themes are purely cosmetic. They don't change block behavior, connections, or simulation results. Changing themes is always safe.

---

### Q: Why does my theme reset when I reload a saved diagram?

**A:** If you changed the theme via UI but didn't save the diagram, the theme isn't persisted. Always use `diagram.save("file.json")` after changing themes to persist the preference.

---

### Q: Can I change the built-in theme colors?

**A:** Not via the Python API. Theme colors are defined in CSS (`styles.css`). Advanced users can modify the CSS directly, but this is not officially supported.

---

## Next Steps

- **Learn more**: See [data-model.md](./data-model.md) for technical details
- **API reference**: See [contracts/theme-sync.yaml](./contracts/theme-sync.yaml) for Python-JS communication
- **Contribute**: Report issues or suggest improvements on GitHub

---

**Happy theming! 🎨**
