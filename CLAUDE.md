<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Lynx** is a lightweight block diagram GUI for control systems. The repository includes **SpecKit**, a feature specification and planning workflow toolkit implemented as Claude Code skills.

### Environment Details

The project uses a UV virtual environment for Python, so activate this using the `.venv` directory and run tests with `uv run pytest`, etc.

For frontend testing, use `npm test -- --run` in the `js/` directory.

### Project Status

**Test Suite**:
- Python: 407 tests
- Frontend: 310 tests (180 test() + 130 it())
- Total: 717 tests

**Test Coverage**:
- Python: 22% overall (key modules: diagram.py 93%, conversion 72-95%, blocks 80-100%)
- Frontend: Comprehensive coverage across all block types and components

**Features Implemented**:
- 15 features fully implemented (001-015)
- 1 feature partially implemented (016 - documentation infrastructure complete, testing/deployment pending)

## SpecKit Workflow

SpecKit provides a structured approach to feature development through a series of commands that guide you from initial concept to implementation:

### Workflow Sequence

1. **`/speckit.specify`** - Create feature specification
   - Generates a numbered feature branch (e.g., `1-feature-name`, `2-another-feature`)
   - Creates `specs/###-feature-name/spec.md` with user stories and requirements
   - Validates spec quality and resolves clarifications
   - Branch numbering is automatic - checks remote branches, local branches, and specs directories

2. **`/speckit.clarify`** - Refine specification requirements
   - Identifies underspecified areas in the spec
   - Asks up to 5 targeted clarification questions
   - Updates spec with answers

3. **`/speckit.plan`** - Generate technical implementation plan
   - Creates `plan.md` with tech stack, architecture, and design decisions
   - Generates `data-model.md`, API contracts in `contracts/`, and `quickstart.md`
   - Runs research phase to resolve technical unknowns
   - Updates agent context files

4. **`/speckit.tasks`** - Break plan into actionable tasks
   - Generates `tasks.md` organized by user story priority
   - Tasks follow strict checklist format: `- [ ] [T###] [P] [US#] Description with file path`
   - Includes dependency graph and parallel execution opportunities
   - Each user story is independently testable

5. **`/speckit.implement`** - Execute implementation plan
   - Processes all tasks from `tasks.md` in phases
   - Follows dependency order
   - Completes one phase at a time

6. **`/speckit.analyze`** - Cross-artifact consistency analysis
   - Validates consistency across spec.md, plan.md, and tasks.md
   - Non-destructive quality check

7. **`/speckit.taskstoissues`** - Convert tasks to GitHub issues
   - Creates GitHub issues from tasks.md
   - Preserves dependency ordering

8. **`/speckit.checklist`** - Generate custom checklists
   - Creates domain-specific validation checklists

9. **`/speckit.constitution`** - Manage project principles
   - Creates/updates project constitution from principle inputs
   - Ensures dependent templates stay in sync

## Key File Locations

### Feature Workspace Structure

```
specs/
  ###-feature-name/           # Feature number + short name
    spec.md                   # Feature specification (WHAT + WHY)
    plan.md                   # Technical plan (HOW)
    tasks.md                  # Actionable task list
    data-model.md             # Entity definitions (optional)
    research.md               # Technical decisions (optional)
    quickstart.md             # Test scenarios (optional)
    contracts/                # API contracts (optional)
      *.yaml                  # OpenAPI/GraphQL schemas
    checklists/               # Quality validation checklists
      requirements.md         # Spec quality checklist
```

### Infrastructure Files

```
.specify/
  memory/
    constitution.md           # Project principles and standards
  templates/
    spec-template.md          # Feature spec template
    plan-template.md          # Implementation plan template
    tasks-template.md         # Task list template
    checklist-template.md     # Checklist template
    agent-file-template.md    # Agent context template
  scripts/bash/
    create-new-feature.sh     # Initialize new feature branch/spec
    setup-plan.sh             # Setup planning environment
    check-prerequisites.sh    # Validate prerequisites for tasks
    update-agent-context.sh   # Update AI agent context
    common.sh                 # Shared utilities

.claude/commands/             # Claude Code skill definitions
  speckit.*.md                # Individual skill prompts
```

## Important Conventions

### Specification Principles

**Specs focus on WHAT and WHY, never HOW:**
- Written for business stakeholders, not developers
- No technology stack, frameworks, APIs, or code structure
- User stories must be independently testable and prioritized (P1, P2, P3...)
- Success criteria must be measurable and technology-agnostic
- Maximum 3 `[NEEDS CLARIFICATION]` markers per spec

### Task Format Rules

All tasks in `tasks.md` MUST follow this strict format:

```
- [ ] [T###] [P] [US#] Description with file path
```

Components:
- `- [ ]` - Markdown checkbox (required)
- `[T###]` - Sequential task ID (required)
- `[P]` - Parallelizable marker (optional, only if no dependencies)
- `[US#]` - User story label (required for story tasks, e.g., [US1], [US2])
- Description with exact file path (required)

### Phase Organization

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites)
- **Phase 3+**: User Stories in priority order (one phase per story)
- **Final Phase**: Polish & cross-cutting concerns

### Branch Naming

Feature branches follow pattern: `###-feature-name`
- Number is auto-incremented by checking existing branches and specs
- Short name is 2-4 words, action-noun format when possible

## Workflow Tips

### Starting a New Feature

1. Run `/speckit.specify <feature description>`
2. Answer any clarification questions (max 3)
3. Spec is validated automatically - proceed when ready
4. Run `/speckit.plan` to create technical design
5. Run `/speckit.tasks` to generate actionable task list
6. Run `/speckit.implement` to execute tasks

### Working with Constitution

The constitution file (`.specify/memory/constitution.md`) defines project-wide principles. Check it during planning to ensure compliance. Use `/speckit.constitution` to update it.

### Agent Context Updates

After planning, agent context files are updated automatically via `update-agent-context.sh`. This preserves manual additions between markers while adding new technology from the plan.

### Prerequisites Scripts

All setup scripts (`create-new-feature.sh`, `setup-plan.sh`, `check-prerequisites.sh`) support `--json` flag for structured output. Always use absolute paths.

### Handling Single Quotes in Arguments

For arguments with single quotes (e.g., "I'm ready"), use escape syntax: `'I'\''m ready'` or prefer double quotes: `"I'm ready"`.

## Testing Philosophy

Tests are OPTIONAL by default. Only generate test tasks if:
- Explicitly requested in the feature specification
- User requests TDD approach
- Constitution requires tests for the domain

When tests are included, they follow the same user story organization.

## Active Technologies
- Python 3.11+ (001-lynx-jupyter-widget)
- File system (JSON diagrams saved via explicit save/load) (001-lynx-jupyter-widget)
- Python 3.11+ (backend), TypeScript 5.x (frontend) (002-latex-block-rendering)
- JSON diagram files (existing persistence layer) (002-latex-block-rendering)
- KaTeX (LaTeX rendering library) (002-latex-block-rendering)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Tailwind CSS v4 (003-simulink-port-markers)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget, Tailwind CSS v4 (004-editable-orthogonal-routing)
- JSON diagram files (existing persistence layer via Pydantic) (004-editable-orthogonal-routing)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget, Pydantic (005-hideable-block-labels)
- JSON diagram files (existing persistence layer via Pydantic schemas) (005-hideable-block-labels)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget, Pydantic, KaTeX (007-block-resizing)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget, html-to-image (new), KaTeX 0.16.27 (008-static-diagram-render)
- File system (PNG/SVG output files) (008-static-diagram-render)
- TypeScript 5.9 (frontend) + React 19.2.3, Tailwind CSS v4 (009-collapsible-block-library)
- N/A (UI-only feature, no persistence) (009-collapsible-block-library)
- Python 3.11+ (backend), TypeScript 5.9 (frontend) + React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Tailwind CSS v4, Pydantic (schema validation) (010-switchable-themes)
- JSON diagram files (existing persistence via Pydantic) (011-sum-quadrant-config)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), KaTeX 0.16.27, Tailwind CSS v4 (011-sum-quadrant-config)
- JSON diagram files (existing persistence via Pydantic schemas) (011-sum-quadrant-config)
- Python 3.11+ (existing Lynx requirement) (012-python-control-export)
- N/A (operates on in-memory Diagram objects) (012-python-control-export)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Pydantic (schema validation) (013-editable-block-labels)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget, KaTeX 0.16.27, Pydantic (014-iomarker-latex-rendering)
- JSON diagram files (existing persistence via Pydantic schemas) (014-iomarker-latex-rendering)
- TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Pydantic (schema validation) (015-block-drag-detection)

## Key Components

### LaTeX Rendering (002-latex-block-rendering)

**Frontend Components**:
- `js/src/blocks/shared/components/LaTeXRenderer.tsx` - Core KaTeX rendering component with auto-scaling and error handling
- `js/src/utils/numberFormatting.ts` - 3-significant-figure formatting with exponential notation
- `js/src/blocks/shared/utils/latexGeneration.ts` - Default LaTeX generation for Gain, TransferFunction, StateSpace blocks

**Python Utilities**:
- `src/lynx/utils/latex_formatting.py` - Number formatting (matches TypeScript behavior)
- `src/lynx/blocks/base.py` - Block base class with `custom_latex` attribute

**Custom LaTeX Override**:
- Blocks support `custom_latex` property for custom rendering
- Available on Gain, TransferFunction, and StateSpace blocks
- Set via Python API (`block.custom_latex = r"\alpha"`) or UI parameter panel
- Persists in diagram JSON for save/load
- `custom_latex` is a top-level block attribute (NOT a parameter)

**Architecture Notes**:
- Number formatting: Use exponential notation when |x| < 0.01 or |x| ≥ 1000
- Auto-scaling: LaTeX content scales to fit block bounds (implemented in LaTeXRenderer)
- Error handling: Invalid LaTeX shows "Invalid LaTeX" placeholder without crashing
- Performance: LaTeX rendering <50ms per block for 50-block diagrams

### Port Markers (003-simulink-port-markers)

**Frontend Components**:
- `js/src/blocks/shared/components/PortMarker.tsx` - Triangular arrowhead marker component (Simulink-style, two lines only)
- `js/src/blocks/shared/utils/portMarkerGeometry.ts` - Isosceles triangle geometry calculations (60% height-to-width ratio)
- `js/src/blocks/shared/hooks/usePortMarkerVisibility.ts` - Connection state detection hook using React Flow edges

**Marker Behavior**:
- **Visibility**: Markers appear on unconnected ports only, hide when port is connected
- **Orientation**:
  - Input ports: Tip at border, base extends outward
  - Output ports: Base at border, tip extends outward
  - Bottom inputs (Sum block): Point upward
- **Styling**: 2px stroke width (matches blocks/edges), primary-600 color, 3px clearance from blocks
- **Flipping**: When blocks flip horizontally, ports swap positions AND arrow directions reverse

**Block Integration**:
- All 5 block types integrated: Gain, TransferFunction, StateSpace, Sum, IOMarker
- Sum block has special port regeneration logic when `signs` parameter changes
- Connection cleanup automatically removes orphaned connections when ports are deleted

**Testing Infrastructure**:
- Vitest 2.1.9 configured with jsdom environment for React component testing
- React Testing Library 16.1.0 for component testing utilities
- @testing-library/user-event for realistic user interaction testing
- 310+ frontend tests covering all block types and parameter editors
- Test setup handles React 19 compatibility with Testing Library
- Configuration in `js/vite.config.ts` (test section) and `js/src/test/setup.ts`

**Backend Port Management** (Python):
- `src/lynx/diagram.py::update_block_parameter()` - Special handling for Sum block port regeneration
- When Sum block `signs` parameter changes, input ports are regenerated dynamically
- Automatic connection cleanup removes edges to deleted ports

**Architecture Notes**:
- Isosceles triangles (not equilateral): height = 60% of width for better visual proportion
- Two-line arrowheads (no base line) match Simulink style
- Port markers inherit block transforms (flip, position) via CSS
- `portType` prop determines arrow orientation (input vs output)
- Drag-and-drop hover behavior intentionally NOT implemented (current behavior is acceptable)

### Block Resizing (007-block-resizing)

**Frontend Components**:
- `js/src/blocks/shared/hooks/useBlockResize.ts` - Hook for managing resize operations with Python sync
- `js/src/blocks/shared/utils/blockDefaults.ts` - Default/minimum dimensions per block type

**Block Dimensions**:
- All blocks support custom width/height via `data.width` and `data.height` props
- Default dimensions defined in `BLOCK_DEFAULTS`: Gain (120x80), Sum (56x56), TransferFunction (100x50), StateSpace (100x60), IOMarker (60x48)
- Minimum dimensions enforce usability: typically 60x40 or 40x40

**Resize Behavior**:
- **Handles**: 4 corner handles visible when block is selected (React Flow NodeResizer)
- **Anchor Corner**: Opposite corner stays fixed during resize
- **Connection Re-routing**: Waypoints cleared automatically when block is resized

**Python Backend**:
- `src/lynx/blocks/base.py` - Block class has `width` and `height` attributes (Optional[float], default None)
- `src/lynx/diagram.py::update_block_dimensions()` - Updates dimensions and clears connection waypoints
- `src/lynx/widget.py` - Handles `resizeBlock` action from frontend

**SVG Scaling**:
- GainBlock: Triangle polygon points scale with dimensions
- SumBlock: Circle becomes ellipse for non-square dimensions, X lines scale proportionally
- Text/LaTeX content maintains fixed font size (does not scale with block)

**Architecture Notes**:
- Python is source of truth for dimensions (persisted in JSON diagrams)
- Frontend uses optimistic updates during drag, syncs to Python on resize end
- `useUpdateNodeInternals()` called after resize to update handle positions
- Dimensions omitted from JSON when None (backward compatible)

### Sum Block Quadrant Configuration (011-sum-quadrant-config)

**Frontend Components**:
- `js/src/blocks/sum/SumBlock.tsx` - Interactive quadrant-based sign configuration
- `js/src/blocks/sum/ellipseQuadrantPaths.ts` - SVG path generation for quadrant regions

**Interactive Configuration**:
- Users click quadrants (top, left, bottom) to cycle port signs: "+" → "-" → "|" → "+"
- Properties panel removed for Sum blocks - all configuration via direct clicks
- Single-click interaction with drag detection (>5px movement = drag, <5px = click)

**Quadrant Mapping**:
- Top quadrant (0): `signs[0]` - configured port at top of ellipse
- Left quadrant (1): `signs[1]` - configured port at left of ellipse
- Bottom quadrant (2): `signs[2]` - configured port at bottom of ellipse
- Right quadrant (3): Output port (not configurable, clicks ignored)

**Visual Feedback**:
- CSS `:hover` pseudo-class for performance (no React state)
- Transparent quadrant overlays with `sum-quadrant` class
- Hover highlights with `var(--color-primary-200)` fill at 0.5 opacity
- Pointer cursor on clickable quadrants

**Click Detection**:
- Uses browser's native SVG hit detection via `data-quadrant` attributes
- Works correctly at any zoom level, canvas position, or block size
- Eliminates need for manual coordinate transformations

**Sign Cycling**:
- "+" (addition): Port visible with marker
- "-" (subtraction): Port visible with marker
- "|" (no port): Port hidden, connections removed

**Backend Integration**:
- Uses existing `updateBlockParameter` action pattern
- Python backend in `src/lynx/blocks/sum.py` regenerates ports when signs change
- Connection cleanup automatic when port removed (sign → "|")

**Performance**:
- Click-to-update latency: <50ms (optimistic UI updates)
- Hover response: <5ms (CSS-based, no re-renders)
- Quadrant detection: O(1) via browser SVG hit testing

**Architecture Notes**:
- Simplified from original plan: browser SVG hit detection instead of manual coordinate math
- CSS hover instead of React state for better performance
- Architectural simplification resulted in ~70 fewer lines of code and elimination of complex geometric calculations
- 27 tests for quadrant interaction, all passing
- Works correctly with resized blocks (wide, tall, or square Sum blocks)

### Python-Control Export (012-python-control-export)

**Core Functionality**:
Convert Lynx diagrams to python-control system objects for analysis, simulation, and control design. Supports subsystem extraction between arbitrary signals using flexible signal reference patterns.

**Python API** (`src/lynx/diagram.py`):
```python
# Primary API - extract subsystems between any two signals
sys_ss = diagram.get_ss('from_signal', 'to_signal')  # Returns StateSpace
sys_tf = diagram.get_tf('from_signal', 'to_signal')  # Returns TransferFunction

# Advanced API - full system export (internal/advanced use)
from lynx.conversion import to_interconnect
sys_full = to_interconnect(diagram)  # Returns LinearICSystem
```

**Signal Reference Patterns (3-tier priority system)**:
1. **IOMarker labels** (highest priority): Use the 'label' parameter from InputMarker/OutputMarker blocks
   - Example: `diagram.get_ss('r', 'y')` where 'r' and 'y' are IOMarker labels
2. **Connection labels**: Reference labeled connections between blocks
   - Example: `diagram.get_ss('r', 'error')` where 'error' is a connection label
3. **block_label.{output_port_id}**: Explicit block label and output port using dot notation
   - Example: `diagram.get_ss('controller.out', 'plant.out')`
   - Note: Must use block **label** (not ID) and **output** ports only
   - Bare block labels no longer supported - use explicit `.out` suffix
   - Input port references not allowed - signals are outputs, not inputs

**Conversion Module Structure** (`src/lynx/conversion/`):
```
conversion/
  __init__.py              # Public API exports (get_ss, get_tf)
  block_converters.py      # Block → python-control subsystem conversion
  interconnect.py          # Full diagram → LinearICSystem (advanced)
  signal_extraction.py     # Subsystem extraction logic (break-and-inject)
```

**Block Converters** (`src/lynx/conversion/block_converters.py`):
- **GainBlock** → `ct.ss([], [], [], [[K]])` - Pure gain, no dynamics
- **TransferFunction** → `ct.tf(numerator, denominator)` - Standard TF form
- **StateSpace** → `ct.ss(A, B, C, D)` - Full state-space
- **SumBlock** → `ct.summing_junction()` with sign handling (+, -, |)
- **IOMarker** → `ct.ss([], [], [], [[1.0]])` - Unity pass-through

**Sum Block Sign Handling**:
- Signs parameter: `["+", "-", "|"]` for [top, left, bottom] quadrants
- "+" adds signal, "-" subtracts (prepends "-" to source signal name)
- "|" means no port (skipped in quadrant-to-port mapping)
- Helper function `SumBlock.get_port_sign(port_id)` maps port IDs to signs

**Break-and-Inject Architecture** (`signal_extraction.py::prepare_for_extraction()`):
1. Clone diagram for safe modification (doesn't affect original)
2. Resolve from_signal and to_signal to block.port references
3. Inject InputMarker at from_signal point if needed
4. Build full interconnect with ALL signals exported as outputs
5. Return indexed subsystem using python-control's MIMO indexing: `sys[to_name, from_name]`

**Validation** (`interconnect.py::validate_for_export()`):
Three-layer validation:
- **Layer 1**: System boundary checks (at least one InputMarker and OutputMarker)
- **Layer 2**: Label uniqueness check (warnings for duplicates, non-blocking)
- **Layer 3**: Port connectivity (all non-InputMarker input ports must be connected)
- Raises `ValidationError` with block_id and port_id context on failure
- Issues `UserWarning` for duplicate block or connection labels

**Exception Hierarchy** (`src/lynx/diagram.py`):
```python
DiagramExportError (base exception for export failures)
├── ValidationError (diagram validation failures, includes block_id and port_id)
└── SignalNotFoundError (signal not found, includes signal_name and searched_locations)
```

**Usage Example**:
```python
import lynx
import control as ct
import numpy as np

# Create feedback control loop
diagram = lynx.Diagram()
diagram.add_block('io_marker', 'ref', marker_type='input', label='r')
diagram.add_block('sum', 'error_sum', signs=['+', '-', '|'])
diagram.add_block('gain', 'controller', K=5.0)
diagram.add_block('transfer_function', 'plant',
                 numerator=[2.0], denominator=[1.0, 3.0])
diagram.add_block('io_marker', 'output', marker_type='output', label='y')

diagram.add_connection('c1', 'ref', 'out', 'error_sum', 'in1')
diagram.add_connection('c2', 'error_sum', 'out', 'controller', 'in')
diagram.add_connection('c3', 'controller', 'out', 'plant', 'in')
diagram.add_connection('c4', 'plant', 'out', 'output', 'in')
diagram.add_connection('c5', 'plant', 'out', 'error_sum', 'in2')  # Negative feedback

# Extract closed-loop transfer function
sys = diagram.get_tf('r', 'y')

# Simulate step response
t = np.linspace(0, 5, 500)
t_out, y_out = ct.step_response(sys, t)
print(f"DC gain: {y_out[-1]:.3f}")
```

**Testing**:
- 24 conversion-specific tests (17 unit + 7 integration)
- Test coverage: 22% overall (key modules: diagram.py 93%, conversion 72-95%)
- TDD approach (RED-GREEN-REFACTOR) used throughout
- Integration tests verify end-to-end workflows from quickstart.md scenarios

**Performance**:
- Export <100ms for 50-block diagrams
- Validation <10ms (set-based port connectivity checks)
- Break-and-inject overhead <20ms for subsystem extraction

**Architecture Notes**:
- Subsystem extraction preserves diagram immutability (clones before modification)
- Signal resolution uses 4-tier priority to minimize ambiguity
- python-control's native MIMO indexing eliminates need for manual subsystem extraction
- Connection negation (for sum block minus signs) uses simple string prepending: `"-signal.name"`

### Parameter Panel Registry Pattern

**Architecture**:
The parameter panel uses a registry pattern for extensibility, making it easy to add new block types without modifying the core panel code.

**Frontend Components**:
- `js/src/components/ParameterPanel.tsx` - Main parameter panel (78 lines, down from 324 lines - 76% reduction)
- `js/src/blocks/gain/GainParameterEditor.tsx` - K parameter + custom LaTeX editing
- `js/src/blocks/io_marker/IOMarkerParameterEditor.tsx` - Label + marker type editing
- `js/src/blocks/transfer_function/TransferFunctionParameterEditor.tsx` - Numerator/denominator + custom LaTeX editing
- `js/src/blocks/state_space/StateSpaceParameterEditor.tsx` - Matrix display + custom LaTeX editing
- `js/src/blocks/shared/hooks/useCustomLatex.ts` - Shared custom LaTeX state management hook
- `js/src/blocks/index.ts` - Parameter editor registry (PARAMETER_EDITORS map)

**Registry Pattern**:
```typescript
// Adding a new block type requires only:
// 1. Create parameter editor component
// 2. Add one line to registry:
export const PARAMETER_EDITORS = {
  gain: GainParameterEditor,
  transfer_function: TransferFunctionParameterEditor,
  state_space: StateSpaceParameterEditor,
  io_marker: IOMarkerParameterEditor,
  // sum blocks use direct interaction, no panel
};
```

**Shared Hooks**:
- `useCustomLatex()` - Manages custom LaTeX state, validation, toggle, and apply logic
  - Used by Gain, TransferFunction, and StateSpace blocks
  - Centralizes LaTeX validation and error handling
  - Consistent Enter key handling (non-Shift Enter applies and blurs)

**Testing**:
- 717 total tests (407 Python + 310 frontend), all passing
- Each parameter editor has comprehensive unit tests
- GainParameterEditor uses `@testing-library/user-event` for realistic interaction testing
- Tests verify controlled input behavior with `useRef` + `useLayoutEffect` pattern for state capture

**Architecture Benefits**:
1. **Scalability**: Adding new block types is O(1) - create editor, add to registry
2. **Maintainability**: Each editor is self-contained and independently testable
3. **Code reduction**: 76% reduction in ParameterPanel core (324 → 78 lines)
4. **Type safety**: TypeScript enforces `ParameterEditorProps` interface

### Frontend Directory Structure

**Block Organization** (`js/src/blocks/`):
Each block type has its own directory with co-located components:
```
blocks/
  gain/
    GainBlock.tsx                    # Block visualization
    GainParameterEditor.tsx          # Parameter editor
    GainParameterEditor.test.tsx     # Tests
    index.ts                         # Exports
  transfer_function/
    TransferFunctionBlock.tsx
    TransferFunctionParameterEditor.tsx
    TransferFunctionParameterEditor.test.tsx
    index.ts
  state_space/
    StateSpaceBlock.tsx
    StateSpaceParameterEditor.tsx
    StateSpaceParameterEditor.test.tsx
    MatrixDisplay.tsx                # Matrix editing component
    index.ts
  sum/
    SumBlock.tsx
    ellipseQuadrantPaths.ts          # Quadrant SVG utilities
    ellipseQuadrantPaths.test.ts
    index.ts
  io_marker/
    IOMarkerBlock.tsx
    IOMarkerParameterEditor.tsx
    IOMarkerParameterEditor.test.tsx
    index.ts
  shared/
    components/
      LaTeXRenderer.tsx              # Shared LaTeX rendering
      PortMarker.tsx                 # Shared port markers
      EditableLabel.tsx              # Shared editable labels
      index.ts
    hooks/
      useBlockResize.ts              # Resize management
      useBlockLabel.ts               # Label editing
      useFlippableBlock.ts           # Horizontal flip
      useCustomLatex.ts              # Custom LaTeX state
      usePortMarkerVisibility.ts     # Port connection detection
      index.ts
    utils/
      blockDefaults.ts               # Default dimensions
      latexGeneration.ts             # Default LaTeX generation
      portMarkerGeometry.ts          # Marker geometry
      index.ts
    index.ts
  index.ts                           # Block registry + parameter editor registry
```

**Other Key Directories**:
- `js/src/` - Root level: `index.tsx` (app entry), `DiagramCanvas.tsx` (main canvas)
- `js/src/components/` - App-level components (ParameterPanel, SettingsPanel, context menus)
- `js/src/utils/` - Shared utilities (numberFormatting, orthogonalRouting, traitletSync)
- `js/src/connections/` - Edge components (OrthogonalEditableEdge)
- `js/src/hooks/` - App-level hooks (useSegmentDrag, useAutoScaledLatex)
- `js/src/palette/` - Block palette component (BlockPalette)
- `js/src/capture/` - Diagram capture utilities (CaptureCanvas, captureUtils)
- `js/src/context/` - React context (AnyWidgetModel)
- `js/src/test/` - Test configuration and setup files

## Recent Changes
- **015-block-drag-detection**: Intelligent drag detection with 5-pixel movement threshold
  - Click-to-select (< 5px movement) vs drag-to-move (≥ 5px movement) behavior
  - Uses React Flow 11.11.4's `nodeDragThreshold={5}` prop for automatic click/drag separation
  - Distance calculation in `onNodesChange` filter using squared distance (no sqrt overhead)
  - Exclusive selection on click (< 5px), clear selection on drag (≥ 5px)
  - NodeResizer handles hidden during drag via `isVisible={selected}` pattern
  - `dragStartPos` ref tracks initial positions for distance calculation
  - All 5 block types (Gain, Sum, TransferFunction, StateSpace, IOMarker) consistent behavior
  - Performance: < 5ms overhead per drag operation, maintains 60 FPS
  - 717 total tests passing (407 Python + 310 frontend)
  - Frontend-only feature (no Python backend changes required)
- **014-iomarker-latex-rendering**: Complete IOMarker LaTeX rendering with automatic indexing and Simulink-style renumbering
  - Automatic index display (0, 1, 2...) via LaTeX for InputMarker and OutputMarker blocks
  - Custom LaTeX override using existing useCustomLatex hook (checkbox + textarea UI)
  - Removed "Input/Output" text and "Type" dropdown from parameter panel for cleaner UX
  - Simulink-style automatic index renumbering (downward shift, upward shift, cascade on delete)
  - Index validation and clamping (negative/out-of-range values clamped to [0, N-1])
  - Independent index sequences for InputMarker and OutputMarker (both can have index 0, 1, 2...)
  - Backward compatibility: legacy diagrams auto-assign indices by block ID alphabetical order
  - Performance: 2.26ms per block LaTeX rendering (22x faster than <50ms requirement), <20ms renumbering for 100 markers
  - 14 backend tests (5 auto-indexing + 6 renumbering + 3 integration), 13 frontend tests (6 parameter editor + 7 block including performance)
  - 95% coverage for io_marker.py, renumbering methods fully covered in diagram.py
  - TDD approach (RED-GREEN-REFACTOR) throughout implementation with strict test-first discipline
- 013-editable-block-labels: Added TypeScript 5.9 (frontend), Python 3.11+ (backend) + React 19.2.3, React Flow 11.11.4, anywidget (Jupyter widget framework), Pydantic (schema validation)
  - Added `diagram.get_ss(from_signal, to_signal)` and `diagram.get_tf(from_signal, to_signal)` API
  - 3-tier signal reference system (IOMarker labels → connection labels → block_label.output_port)
  - Break-and-inject architecture for subsystem extraction preserving diagram immutability
  - Sum block sign handling with proper negation for feedback loops ("+", "-", "|")
  - Validation runs before extraction (validates I/O markers, port connectivity, warns on duplicate labels)
  - Three-layer validation (system boundaries + label uniqueness warnings + port connectivity)
  - Exception hierarchy: DiagramExportError → ValidationError, SignalNotFoundError
  - Future-proofed block converters query actual port IDs (prepares for MIMO/multi-output blocks)
  - Modular conversion package structure (block_converters, interconnect, signal_extraction)
  - 24 conversion tests (17 unit + 7 integration), part of 407 total Python tests
  - Performance: <100ms for 50-block diagrams, <20ms break-and-inject overhead
  - TDD approach (RED-GREEN-REFACTOR) throughout implementation
  - All three user stories complete: US1 (Basic Export), US2 (Sign Handling), US3 (Validation)

  - Reduced ParameterPanel from 324 lines to 78 lines (76% reduction)
  - Created dedicated parameter editors for each block type
  - Extracted `useCustomLatex` hook for shared LaTeX state management
  - Added `@testing-library/user-event` for realistic interaction testing
  - All parameter editors fully tested (part of 310+ frontend tests)
  - Fixed TransferFunction scalar rendering bug (scalars now normalize to arrays)

  - Click quadrants (top, left, bottom) to cycle port signs: "+" → "-" → "|" → "+"
  - Removed properties panel for Sum blocks (all config via direct clicks)
  - CSS hover highlights for visual feedback (no React state for performance)
  - Browser's native SVG hit detection via `data-quadrant` attributes
  - Single-click with drag detection (>5px = drag, <5px = click)
  - Works correctly with resized blocks (wide, tall, or square)
  - 27 quadrant interaction tests
  - Architectural simplification: eliminated ~70 lines of complex coordinate math
  - All 5 block types (Gain, Sum, TransferFunction, StateSpace, IOMarker) support resizing
  - Dimensions persist to Python and JSON diagram files
  - SVG shapes scale proportionally (Gain triangle, Sum circle/ellipse)
  - Connection waypoints auto-cleared when blocks are resized
  - Comprehensive test coverage across all block types and resizing behavior
  - Added Simulink-style triangular port markers (two-line arrowheads) to all blocks
  - Implemented connection-aware visibility (hide when connected, show when unconnected)
  - Added horizontal flip support with proper port position swapping
  - Configured Vitest 2.1.9 testing infrastructure with 310+ frontend tests
  - Added backend port regeneration for Sum blocks with connection cleanup
  - Drag-and-drop hover behavior intentionally skipped (complexity not justified)
