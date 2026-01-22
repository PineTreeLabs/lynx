<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart: LaTeX Block Rendering

**Feature**: 002-latex-block-rendering
**Audience**: Developers and testers
**Purpose**: Test scenarios and usage examples

## User Scenarios

### Scenario 1: View Default Mathematical Notation (P1)

**Objective**: Verify default LaTeX rendering for all block types without configuration

**Steps**:
1. Create a new diagram with StateSpace, TransferFunction, and Gain blocks
2. Observe block rendering on canvas
3. Verify mathematical notation displays correctly

**Python Code**:
```python
from lynx import Diagram
from lynx.blocks import StateSpaceBlock, TransferFunctionBlock, GainBlock

# Create diagram
diagram = Diagram()

# Add StateSpace block
ss = diagram.add_block(StateSpaceBlock(
    id="ss1",
    A=[[0, 1], [-2, -3]],
    B=[[0], [1]],
    C=[[1, 0]],
    D=[[0]]
))

# Add TransferFunction block
tf = diagram.add_block(TransferFunctionBlock(
    id="tf1",
    numerator=[1, 2.5, 0.00123],
    denominator=[1, 0.5, 1234]
))

# Add Gain block
gain = diagram.add_block(GainBlock(
    id="gain1",
    K=123.456
))

# Display widget (in Jupyter)
diagram
```

**Expected Results**:
- **StateSpaceBlock**: Shows "ẋ = Ax + Bu" and "y = Cx + Du" in formatted LaTeX
- **TransferFunctionBlock**: Shows fraction "$(s^2 + 2.5s + 1.23×10^{-3}) / (s^2 + 0.5s + 1.23×10^3)$"
- **GainBlock**: Shows "123" (3 sig figs)

**Test Criteria**:
- ✅ LaTeX renders without errors
- ✅ Equations are readable and properly formatted
- ✅ No configuration or user action required
- ✅ All three block types display mathematical notation

---

### Scenario 2: Customize Block Display with LaTeX (P2)

**Objective**: Enable custom LaTeX via UI and verify rendering

**Steps**:
1. Select a Gain block
2. Open parameter panel
3. Check "Render custom block contents" checkbox
4. Enter custom LaTeX: `K_p + \frac{K_i}{s}`
5. Observe block updates to show custom content

**Python Code (Alternative - Set via API)**:
```python
from lynx import Diagram
from lynx.blocks import GainBlock

diagram = Diagram()
gain = diagram.add_block(GainBlock(id="pid", K=10))

# Set custom LaTeX programmatically
gain.custom_latex = r"K_p + \frac{K_i}{s}"

diagram
```

**Expected Results**:
- **Before**: Block shows "10" (default gain value)
- **After**: Block shows "K_p + K_i/s" (custom LaTeX)
- Block type label ("Gain") not shown when custom LaTeX active
- Checkbox in parameter panel is checked

**Test Criteria**:
- ✅ Checkbox enables custom LaTeX input field
- ✅ Custom LaTeX replaces default rendering
- ✅ Block type name hidden when custom LaTeX active
- ✅ Changes persist when diagram saved/reloaded

---

### Scenario 3: Invalid LaTeX Error Handling

**Objective**: Verify graceful error handling for invalid LaTeX syntax

**Steps**:
1. Open parameter panel for any block
2. Enable custom LaTeX
3. Enter invalid syntax: `\frac{incomplete`
4. Observe error handling

**Python Code**:
```python
gain = diagram.add_block(GainBlock(id="test", K=5))
gain.custom_latex = r"\frac{incomplete"  # Missing closing brace
diagram
```

**Expected Results**:
- Block renders "Invalid LaTeX" placeholder
- Inline error message appears below LaTeX input in parameter panel
- Original input preserved in text field (user can edit)
- Error does not crash widget or prevent other blocks from rendering

**Test Criteria**:
- ✅ Invalid LaTeX does not crash application
- ✅ Clear error message shown to user
- ✅ User can correct error without losing input
- ✅ Other blocks on diagram unaffected

---

### Scenario 4: Auto-Scaling Long Expressions

**Objective**: Verify LaTeX content scales to fit block boundaries

**Steps**:
1. Create Gain block
2. Set custom LaTeX to very long expression:
   `\frac{s^{10} + 2s^9 + 3s^8 + 4s^7 + 5s^6 + 6s^5 + 7s^4 + 8s^3 + 9s^2 + 10s + 11}{s^{10} + s^9}`
3. Observe block rendering

**Python Code**:
```python
gain = diagram.add_block(GainBlock(id="long", K=1))
gain.custom_latex = r"\frac{s^{10} + 2s^9 + 3s^8 + 4s^7 + 5s^6 + 6s^5 + 7s^4 + 8s^3 + 9s^2 + 10s + 11}{s^{10} + s^9}"
diagram
```

**Expected Results**:
- LaTeX content automatically scales down to fit block width
- All terms remain readable (not truncated)
- Aspect ratio preserved
- No horizontal scrolling or overflow outside block boundaries

**Test Criteria**:
- ✅ Long expressions fit within block bounds
- ✅ Text scales down (smaller but readable)
- ✅ No visual overflow or clipping
- ✅ Future: Scales when block resized (if resize feature added)

---

### Scenario 5: Python API - Programmatic Custom LaTeX

**Objective**: Set and retrieve custom LaTeX via Python property

**Steps**:
1. Create block programmatically
2. Set `custom_latex` property
3. Verify getter returns value
4. Set to `None` to revert
5. Verify UI reflects changes

**Python Code**:
```python
from lynx import Diagram
from lynx.blocks import StateSpaceBlock

diagram = Diagram()
ss = diagram.add_block(StateSpaceBlock(
    id="ss1",
    A=[[0, 1], [-1, -2]],
    B=[[1], [0]],
    C=[[1, 0]],
    D=[[0]]
))

# Initially None (default rendering)
assert ss.custom_latex is None

# Set custom LaTeX
ss.custom_latex = r"\mathbf{G}(s) = \mathbf{C}(s\mathbf{I} - \mathbf{A})^{-1}\mathbf{B} + \mathbf{D}"
assert ss.custom_latex == r"\mathbf{G}(s) = \mathbf{C}(s\mathbf{I} - \mathbf{A})^{-1}\mathbf{B} + \mathbf{D}"

# Revert to default
ss.custom_latex = None
assert ss.custom_latex is None

diagram
```

**Expected Results**:
- Property getter/setter works correctly
- UI checkbox automatically updates when property set from Python
- Block rendering updates in real-time
- Empty string treated same as `None` (reverts to default)

**Test Criteria**:
- ✅ `custom_latex` property readable and writable
- ✅ Setting property updates UI immediately
- ✅ Setting to `None` reverts to default rendering
- ✅ UI checkbox state synchronized with property value

---

### Scenario 6: Numerical Formatting Precision

**Objective**: Verify consistent 3-significant-figure formatting and exponential notation

**Steps**:
1. Create TransferFunction and Gain blocks with various coefficient magnitudes
2. Verify formatting matches specification

**Python Code**:
```python
from lynx import Diagram
from lynx.blocks import TransferFunctionBlock, GainBlock

diagram = Diagram()

# Test exponential notation for small numbers
tf1 = diagram.add_block(TransferFunctionBlock(
    id="tf_small",
    numerator=[0.00456],
    denominator=[1, 0.0123]
))

# Test exponential notation for large numbers
tf2 = diagram.add_block(TransferFunctionBlock(
    id="tf_large",
    numerator=[1234, 5678],
    denominator=[1]
))

# Test normal notation for mid-range
gain = diagram.add_block(GainBlock(id="gain_mid", K=123.456))

diagram
```

**Expected Results**:
- **tf_small**: Shows "4.56×10⁻³ / (s + 1.23×10⁻²)"
- **tf_large**: Shows "(1.23×10³s + 5.68×10³) / 1"
- **gain_mid**: Shows "123" (3 sig figs)

**Formatting Rules Applied**:
- 3 significant figures for all numbers
- Exponential notation when |x| < 0.01 or |x| ≥ 1000
- Consistent between Python and JavaScript

**Test Criteria**:
- ✅ Small numbers (<0.01) use exponential notation
- ✅ Large numbers (≥1000) use exponential notation
- ✅ Mid-range numbers (0.01 to 999) use fixed notation
- ✅ All numbers formatted to 3 significant figures

---

### Scenario 7: Persistence and Reload

**Objective**: Verify custom LaTeX persists across save/load

**Steps**:
1. Create diagram with custom LaTeX
2. Save diagram to JSON file
3. Load diagram from JSON
4. Verify custom LaTeX restored

**Python Code**:
```python
from lynx import Diagram
from lynx.blocks import GainBlock

# Create and customize
diagram = Diagram()
gain = diagram.add_block(GainBlock(id="pid", K=10))
gain.custom_latex = r"K_p + \frac{K_i}{s} + K_d s"

# Save
diagram.save("test_diagram.json")

# Load in new session
diagram2 = Diagram.load("test_diagram.json")
loaded_gain = diagram2.get_block("pid")

assert loaded_gain.custom_latex == r"K_p + \frac{K_i}{s} + K_d s"

diagram2
```

**Expected Results**:
- Custom LaTeX property saved in JSON
- Reloaded diagram shows custom LaTeX (not default)
- Checkbox state restored correctly
- No data loss

**Test Criteria**:
- ✅ `custom_latex` included in JSON serialization
- ✅ Loaded blocks retain custom LaTeX
- ✅ UI state (checkbox) matches loaded data
- ✅ Backward compatible: diagrams without custom_latex load normally

---

## Testing Checklist

### Unit Tests (Python)

```python
# tests/python/unit/test_blocks.py
def test_custom_latex_property_default():
    """Test custom_latex defaults to None"""
    block = GainBlock(id="test", K=1)
    assert block.custom_latex is None

def test_custom_latex_property_setter():
    """Test setting custom_latex"""
    block = GainBlock(id="test", K=1)
    block.custom_latex = r"\alpha"
    assert block.custom_latex == r"\alpha"

def test_custom_latex_property_clear():
    """Test clearing custom_latex reverts to None"""
    block = GainBlock(id="test", K=1)
    block.custom_latex = r"\beta"
    block.custom_latex = None
    assert block.custom_latex is None

def test_custom_latex_empty_string_treated_as_none():
    """Test empty string equivalent to None"""
    block = GainBlock(id="test", K=1)
    block.custom_latex = ""
    assert block.custom_latex is None or block.custom_latex == ""
```

```python
# tests/python/unit/test_latex_formatting.py
from lynx.utils.latex_formatting import format_number

def test_format_number_small_exponential():
    """Test exponential notation for small numbers"""
    assert format_number(0.00456) == "4.56e-3"

def test_format_number_large_exponential():
    """Test exponential notation for large numbers"""
    assert format_number(1234) == "1.23e3"

def test_format_number_mid_range():
    """Test fixed notation for mid-range numbers"""
    assert format_number(123.456) == "123"

def test_format_number_zero():
    """Test zero formatting"""
    assert format_number(0) == "0"
```

### Unit Tests (TypeScript)

```typescript
// tests/js/unit/numberFormatting.test.ts
import { formatNumber } from '../../src/utils/numberFormatting';

describe('formatNumber', () => {
  test('formats small numbers with exponential notation', () => {
    expect(formatNumber(0.00456)).toBe('4.56e-3');
  });

  test('formats large numbers with exponential notation', () => {
    expect(formatNumber(1234)).toBe('1.23e+3');
  });

  test('formats mid-range numbers without exponential', () => {
    expect(formatNumber(123.456)).toBe('123');
  });

  test('handles zero', () => {
    expect(formatNumber(0)).toBe('0');
  });
});
```

```typescript
// tests/js/unit/LaTeXRenderer.test.tsx
import { render } from '@testing-library/react';
import { LaTeXRenderer } from '../../src/components/LaTeXRenderer';

describe('LaTeXRenderer', () => {
  test('renders valid LaTeX', () => {
    const { container } = render(<LaTeXRenderer latex="x^2 + y^2 = z^2" />);
    expect(container.querySelector('.katex')).toBeTruthy();
  });

  test('shows error for invalid LaTeX', () => {
    const { getByText } = render(<LaTeXRenderer latex="\\frac{incomplete" />);
    expect(getByText(/Invalid LaTeX/i)).toBeTruthy();
  });

  test('auto-scales when content overflows', () => {
    const longLatex = '\\frac{s^{10} + s^9 + s^8}{s^5}';
    const { container } = render(
      <LaTeXRenderer latex={longLatex} maxWidth={100} />
    );
    const katexEl = container.querySelector('.katex-scaled') as HTMLElement;
    expect(katexEl.style.transform).toContain('scale');
  });
});
```

### Integration Tests

```python
# tests/python/integration/test_latex_widget_integration.py
def test_custom_latex_syncs_to_frontend():
    """Test custom_latex property synchronizes to widget"""
    diagram = Diagram()
    gain = diagram.add_block(GainBlock(id="test", K=5))

    # Set via Python
    gain.custom_latex = r"\alpha"

    # Verify trait sync (check widget model)
    assert gain.get_parameter("custom_latex") == r"\alpha"
```

---

## Performance Benchmarks

### Render Time (Target: <50ms per block)

```python
import time
from lynx import Diagram
from lynx.blocks import StateSpaceBlock

diagram = Diagram()

# Add 50 blocks with LaTeX
start = time.time()
for i in range(50):
    diagram.add_block(StateSpaceBlock(
        id=f"ss{i}",
        A=[[0, 1], [-1, -2]],
        B=[[1], [0]],
        C=[[1, 0]],
        D=[[0]]
    ))
end = time.time()

# Verify performance
time_per_block = (end - start) / 50
assert time_per_block < 0.05, f"Render time {time_per_block}s exceeds 50ms target"
```

### Auto-Scaling Performance (Target: <16ms / 60fps)

```typescript
// Performance test (manual - use browser DevTools)
// 1. Create diagram with 20 blocks
// 2. Enable custom LaTeX with long expressions
// 3. Open DevTools Performance tab
// 4. Record while resizing browser window
// 5. Verify auto-scaling computations <16ms in flame graph
```

---

## Troubleshooting

### LaTeX Not Rendering
- **Check**: KaTeX dependency installed (`katex` in package.json)
- **Check**: No JavaScript errors in browser console
- **Fix**: Run `npm install` in `js/` directory

### Custom LaTeX Not Persisting
- **Check**: Diagram saved after setting `custom_latex`
- **Check**: JSON file contains `custom_latex` parameter
- **Fix**: Ensure traitlets sync working (check anywidget version)

### Auto-Scaling Not Working
- **Check**: Container has defined width/height
- **Check**: `useAutoScaledLatex` hook receiving ref correctly
- **Fix**: Verify CSS layout (flex/grid) provides size constraints

### Formatting Inconsistency Between Python/JS
- **Check**: Both use same `formatNumber` logic
- **Check**: Floating point edge cases (0.0095 vs 0.01 threshold)
- **Fix**: Align rounding behavior in both implementations
