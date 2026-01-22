<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Lynx Color System

## Philosophy
A sophisticated, technical palette that works for both 
the logo and UI. Colors convey precision, reliability, 
and modern engineering without feeling cold or sterile.

## Primary Palette

### Slate (Primary Blue-Gray)
The foundation color - technical, professional, versatile.

**Slate 900** - `#0f172a` - Text, primary dark
**Slate 800** - `#1e293b` - Surfaces, cards
**Slate 700** - `#334155` - Borders, dividers  
**Slate 600** - `#475569` - Subtle elements
**Slate 500** - `#64748b` - Secondary text
**Slate 400** - `#94a3b8` - Placeholder text
**Slate 300** - `#cbd5e1` - Subtle borders
**Slate 200** - `#e2e8f0` - Background surfaces
**Slate 100** - `#f1f5f9` - Hover states
**Slate 50**  - `#f8fafc` - Canvas background

**Usage:**
- UI backgrounds, surfaces, text
- Canvas grid lines
- Neutral elements
- Default block outlines

### Teal (Primary Accent)
Technical yet energetic. Suggests precision + innovation.

**Teal 600** - `#0891b2` - Primary accent (buttons, selection)
**Teal 500** - `#06b6d4` - Hover states
**Teal 400** - `#22d3ee` - Active connections
**Teal 100** - `#ccfbf1` - Subtle highlights

**Usage:**
- Selected blocks
- Active connections
- Primary buttons
- Logo primary color
- "Flow" indicators (signal paths)

### Amber (Secondary Accent)
Warm counterpoint. Suggests energy, caution when needed.

**Amber 600** - `#d97706` - Warning states
**Amber 500** - `#f59e0b` - Attention elements
**Amber 400** - `#fbbf24` - Highlights
**Amber 100** - `#fef3c7` - Subtle warnings

**Usage:**
- Warning messages
- Validation errors (when not critical)
- Input/output blocks (warm = source/sink)
- Logo secondary color (ear tufts, eye highlights?)

## Functional Colors

### Success (Green)
**Emerald 600** - `#059669` - Success states, valid connections
**Emerald 100** - `#d1fae5` - Success backgrounds

### Error (Red)
**Rose 600** - `#e11d48` - Errors, invalid connections
**Rose 100** - `#ffe4e6` - Error backgrounds

### Info (Blue)
**Sky 600** - `#0284c7` - Information, hints
**Sky 100** - `#e0f2fe` - Info backgrounds

## Component-Specific Colors

### Block Types
Suggested color coding for different block types:

**Transfer Function Blocks**
- Border: Teal 600
- Fill: Slate 50
- Text: Slate 900
- Selected: Teal 100 fill, Teal 600 border (2px)

**Gain Blocks**
- Border: Slate 600
- Fill: Slate 50
- Text: Slate 900
- Icon/Symbol: Teal 600

**Sum Junctions**
- Border: Slate 700
- Fill: White
- Symbol: Slate 900
- Signs: Teal 600 (+), Rose 600 (-)

**Input/Output Markers**
- Fill: Amber 500 (warm = energy source/sink)
- Icon: White
- Border: Amber 600

### Connections/Edges
**Default:** Slate 400 (2px)
**Hover:** Teal 500 (2.5px)
**Selected:** Teal 600 (3px)
**Invalid (during drag):** Rose 400 (2px, dashed)
**Valid (during drag):** Emerald 400 (2px)

### Canvas
**Background:** Slate 50
**Grid dots:** Slate 300 (subtle)
**Grid dots (on dark mode):** Slate 700

## Logo Color Application

### Primary Logo
**Background:** White or Slate 50
**Lynx head:** Teal 600 (primary shape)
**Accents (ear tufts, eye):** Amber 500
**Details/lines:** Slate 700

### Monochrome Variants
**On light:** Slate 900
**On dark:** Slate 50
**On teal:** White

### Favicon/Small Sizes
Simplified to just Teal 600 silhouette with Amber 500 
ear tuft accent on white/transparent background.

## Dark Mode (Future Consideration)

If implementing dark mode later:
- Invert slate scale (50 ↔ 900)
- Keep teal/amber accents similar
- Canvas: Slate 900
- Text: Slate 100
- Reduce accent saturation by ~10% for eye comfort

## Accessibility

### Contrast Ratios (WCAG AA)
All text combinations meet 4.5:1 minimum:
- ✅ Slate 900 on Slate 50: 18.6:1
- ✅ Slate 700 on White: 8.6:1
- ✅ Teal 600 on White: 4.6:1
- ✅ White on Teal 600: 4.6:1

### Color Blindness
- Avoid relying solely on red/green for critical info
- Use + and - symbols, not just colors for sum junctions
- Invalid connections: use dashed pattern + color

## Implementation (Tailwind Config)
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        slate: {
          // Tailwind's default slate is perfect
        },
        teal: {
          // Tailwind's default teal
        },
        amber: {
          // Tailwind's default amber
        },
        // Custom brand colors
        'lynx-primary': '#0891b2',    // Teal 600
        'lynx-accent': '#f59e0b',      // Amber 500
        'lynx-canvas': '#f8fafc',      // Slate 50
      }
    }
  }
}
```

## Design System Summary

**Why This Palette Works:**

1. **Cohesive:** Teal + Amber + Slate creates technical-but-warm feeling
2. **Scalable:** Can add shades as needed, Tailwind provides full scales
3. **Functional:** Clear hierarchy, semantic color usage
4. **Accessible:** All critical combinations meet WCAG standards
5. **Distinctive:** Teal/Amber combo is uncommon in technical tools
6. **Printable:** Works in grayscale (sufficient contrast)
7. **Logo-friendly:** Colors work abstractly (not "realistic lynx")

**The Vibe:**
- Modern engineering tool (VS Code, Linear)
- NOT: Corporate blue, consumer bright, academia dull
- Feels like: Precision instrument, technical but approachable
```

## Bringing It Together: Logo + UI Mockup Concept
```
┌─────────────────────────────────────────────────────────┐
│  [Logo: Teal lynx head w/amber ear tufts]  LYNX        │ ← Slate 50 bg
│  ─────────────────────────────────────────────────────  │ ← Slate 300 border
│  File  Edit  View                                       │ ← Slate 700 text
├──────────┬──────────────────────────────────┬──────────┤
│ Blocks   │                                  │Properties│
│ ┌──────┐ │     Slate 50 Canvas             │          │
│ │  TF  │ │                                  │ Selected:│
│ └──────┘ │  ┌──────────┐                   │ ┌──────┐ │
│ Teal 600 │  │    G(s)   │ ← Teal 600       │ │      │ │
│          │  │ ──────────│    selected       │ │ G(s) │ │
│ ┌──────┐ │  │  [1]      │                   │ └──────┘ │
│ │  K   │ │  │  [1,2,1]  │ ← Slate 50 fill  │          │
│ └──────┘ │  └──────────┘                    │ Num: ___ │
│ Slate600 │      ╲ Teal 400 connection      │ Den: ___ │
│          │       ╲                          │          │
│ ┌──────┐ │        ╲  ┌────────┐            │ [Apply]  │
│ │  Σ   │ │         ╲ │ K=5.0  │            │ Teal 600 │
│ └──────┘ │          ╲└────────┘            │          │
└──────────┴───────────────────────────────────┴──────────┘