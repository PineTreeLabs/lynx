<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: LaTeX Block Rendering

**Feature**: 002-latex-block-rendering
**Date**: 2026-01-04

## Key Technical Decisions

### 1. LaTeX Rendering Library: KaTeX (Recommended)

**Decision**: Use KaTeX 0.16+ for client-side LaTeX rendering

**Rationale**:

| Factor | KaTeX | MathJax 3 |
|--------|-------|-----------|
| **Bundle Size** | ~120KB minified | ~500KB+ (modern output) |
| **Render Speed** | Synchronous, <10ms per equation | Asynchronous, ~50-100ms per equation |
| **React Integration** | react-katex, or direct API | react-mathjax, requires configuration |
| **LaTeX Coverage** | ~95% of common commands | ~99% of LaTeX packages |
| **Typography Quality** | Excellent for STEM | Slightly better edge cases |
| **Initial Load** | Instant, no font loading | May require web font downloads |

**For Lynx**: KaTeX is superior because:
1. **Performance at Scale**: Diagrams may have 10-50+ blocks. KaTeX's synchronous rendering means no cumulative delays
2. **Bundle Size**: Jupyter widgets should be lightweight. 120KB vs 500KB matters
3. **Sufficient Coverage**: Control systems use standard notation (fractions, subscripts, Greek letters, matrices) - all well-supported by KaTeX
4. **User Experience**: Instant rendering when adding/modifying blocks, no loading spinners

**Alternatives Considered**:
- **MathJax**: Rejected due to bundle size and async rendering overhead
- **Server-side LaTeX** (via system installation): Rejected because Jupyter widgets run in browser; would require backend rendering + image generation, adding latency and complexity

**Implementation**: Use KaTeX directly via npm, not react-katex wrapper (for better control over error handling and auto-scaling)

---

### 2. Numerical Formatting Strategy

**Decision**: Implement custom formatting utilities with 3 significant figures and exponential notation thresholds

**Python Implementation**:
```python
def format_number(value: float, sig_figs: int = 3) -> str:
    """Format number to N significant figures with exponential notation for extremes.

    Args:
        value: Number to format
        sig_figs: Number of significant figures (default: 3)

    Returns:
        Formatted string (e.g., "1.23", "4.56e-3", "1.23e3")

    Exponential notation used when |value| < 0.01 or |value| >= 1000
    """
    if value == 0:
        return "0"

    abs_value = abs(value)

    # Use exponential notation for very small or large numbers
    if abs_value < 0.01 or abs_value >= 1000:
        # Format in scientific notation with sig_figs-1 decimal places
        return f"{value:.{sig_figs-1}e}"
    else:
        # Calculate decimal places needed for sig_figs
        import math
        magnitude = math.floor(math.log10(abs_value))
        decimal_places = max(0, sig_figs - magnitude - 1)
        return f"{value:.{decimal_places}f}".rstrip('0').rstrip('.')
```

**TypeScript Implementation** (mirror of Python):
```typescript
export function formatNumber(value: number, sigFigs: number = 3): string {
  if (value === 0) return "0";

  const absValue = Math.abs(value);

  // Use exponential notation for very small or large numbers
  if (absValue < 0.01 || absValue >= 1000) {
    return value.toExponential(sigFigs - 1);
  } else {
    // Calculate decimal places needed for sigFigs
    const magnitude = Math.floor(Math.log10(absValue));
    const decimalPlaces = Math.max(0, sigFigs - magnitude - 1);
    return value.toFixed(decimalPlaces).replace(/\.?0+$/, '');
  }
}
```

**Rationale**:
- **Consistency**: Identical logic in Python and TypeScript ensures numbers look the same whether generated server-side or client-side
- **No External Dependencies**: Simple enough to implement without libraries (avoiding bundle bloat)
- **Configuration Ready**: Parameter-based design allows future configurability (FR-020)
- **Engineering Standard**: 3 sig figs with exp notation at 0.01/1000 matches MATLAB, Simulink, and Python control library conventions

**Alternatives Considered**:
- **sigfig library (Python)**: Adds dependency for trivial functionality
- **JavaScript libraries** (precision, bignumber.js): Overkill for simple formatting, large bundles
- **Fixed decimal places**: Rejected because doesn't adapt to value magnitude (0.001 vs 100 need different precision)

---

### 3. Auto-Scaling Approach

**Decision**: CSS transform-based scaling with dynamic measurement

**Implementation Strategy**:
1. Render LaTeX at natural size within a container
2. Measure rendered dimensions using `getBoundingClientRect()`
3. Calculate scale factor: `min(containerWidth / contentWidth, containerHeight / contentHeight)`
4. Apply CSS `transform: scale(factor)` with `transform-origin: center`

**React Hook Pattern**:
```typescript
function useAutoScaledLatex(containerRef: RefObject<HTMLDivElement>) {
  const [scale, setScale] = useState(1);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const content = container.querySelector('.katex'); // KaTeX rendered element

    if (!content) return;

    const containerRect = container.getBoundingClientRect();
    const contentRect = content.getBoundingClientRect();

    const scaleX = containerRect.width / contentRect.width;
    const scaleY = containerRect.height / contentRect.height;
    const newScale = Math.min(1, scaleX, scaleY); // Never scale up, only down

    setScale(newScale);
  }, [containerRef, /* LaTeX content dependency */]);

  return scale;
}
```

**Rationale**:
- **Maintains Quality**: Vector-based scaling (CSS transform) preserves LaTeX sharpness at any size
- **Performance**: Transform is GPU-accelerated, cheaper than re-rendering at different sizes
- **Simplicity**: No need to calculate font sizes or re-invoke KaTeX with different settings
- **Future-Compatible**: Works seamlessly with resizable blocks (planned feature per clarification session)

**Alternatives Considered**:
- **Font-size adjustment**: Rejected because requires re-rendering KaTeX, harder to calculate correct size
- **Viewport units** (vw/vh): Rejected because doesn't account for actual content size
- **Truncation with ellipsis**: Rejected in clarification (Option B), user chose auto-scaling (Option A)

---

### 4. State Management: Python as Source of Truth

**Decision**: Store `custom_latex` in Python Block objects, synchronized to frontend via traitlets

**Architecture**:
```
Python Block.custom_latex (traitlets.Unicode)
    ↓ (anywidget trait sync)
TypeScript BlockData.parameters.custom_latex
    ↓ (React props)
Block Component renders KaTeX
```

**Rationale**:
- **Consistency with Existing Architecture**: Lynx already uses this pattern for all block parameters
- **Persistence**: Python Diagram serialization handles save/load automatically
- **Single Source of Truth**: Avoids frontend/backend desync issues
- **Testability**: Can test Python API independently of UI

**Implementation Notes**:
- Add `custom_latex = traitlets.Unicode(default_value=None, allow_none=True)` to `Block` base class
- Frontend reads from `data.parameters.custom_latex` (existing parameter sync mechanism)
- UI checkbox updates via existing traitlet sync (no new infrastructure needed)

**Alternatives Considered**:
- **Frontend-only state**: Rejected because wouldn't persist across saves
- **Separate API/method**: Rejected in favor of simple property (Option A from clarification)

---

## Open Questions Resolved

1. **Invalid LaTeX handling**: Show inline error, render "Invalid LaTeX" placeholder (Clarification Q1)
2. **Overflow handling**: Auto-scale to fit (Clarification Q2)
3. **Special characters**: Pass through to KaTeX as-is (Clarification Q3)
4. **StateSpace format**: Symbolic notation (Ax + Bu), not expanded matrices (Clarification Q4)
5. **TransferFunction format**: Standard fraction with descending powers (Clarification Q5)
6. **Python API**: Property-based with auto-enable (Clarification Q6)
7. **Numerical precision**: 3 sig figs, exp at 0.01/1000, configurable if feasible (Clarification Q7)

All technical unknowns from feature specification have been resolved.
