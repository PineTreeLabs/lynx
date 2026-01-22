<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart Guide: Lynx Development

**Feature**: 001-lynx-jupyter-widget
**Date**: 2025-12-25
**Audience**: Developers implementing the Lynx block diagram widget

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- Git installed
- Basic familiarity with:
  - Python (dataclasses, traitlets)
  - TypeScript/React
  - Jupyter notebooks
  - Control theory concepts (transfer functions, state-space)

## Initial Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd lynx
```

### 2. Python Environment

**Using UV** (recommended - faster, modern dependency management):

```bash
# UV automatically manages virtual environment in .venv/
# Install package in development mode with dev dependencies
uv pip install -e ".[dev]"

# Or sync from uv.lock for exact reproducibility
uv sync
```

**Alternative - using pip**:

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install package in development mode
pip install -e ".[dev]"
```

**What this installs**:
- Core dependencies: anywidget, numpy, traitlets, python-control
- Development tools: pytest, black, ruff
- Type checking: mypy
- Jupyter: jupyter, jupyterlab, ipykernel

### 3. Frontend Setup

```bash
cd js
npm install
```

**What this installs**:
- React, TypeScript, React Flow
- Vite (build tool)
- Tailwind CSS
- Vitest (testing)
- Development dependencies

### 4. Verify Setup

```bash
# Test Python import
python -c "import lynx; print('Python OK')"

# Test frontend build
cd js
npm run build
echo "Frontend OK"
```

## Project Structure Quick Reference

```
lynx/
├── src/
│   └── lynx/                # Python package (UV src layout)
│       ├── __init__.py
│       ├── widget.py        # anywidget integration
│       ├── diagram.py       # Diagram class
│       ├── static/          # Bundled frontend assets (from Vite)
│       ├── blocks/          # Block implementations
│       ├── validation/      # Control theory validation
│       ├── persistence/     # JSON save/load
│       └── expression_eval.py # Safe eval() wrapper
├── js/                      # Frontend
│   ├── src/
│   │   ├── index.tsx        # Widget entry
│   │   ├── DiagramCanvas.tsx
│   │   └── ...
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── tests/
│   ├── python/              # Backend tests
│   └── js/                  # Frontend tests
├── specs/001-lynx-jupyter-widget/  # This feature's docs
│   ├── spec.md
│   ├── plan.md
│   ├── data-model.md
│   ├── research.md
│   └── contracts/
├── pyproject.toml           # UV-managed Python config
└── uv.lock                  # UV dependency lock file
```

## Development Workflow

### Running Tests (Test-Driven Development)

**Python tests**:
```bash
# Run all Python tests
pytest

# Run with coverage
pytest --cov=lynx --cov-report=html

# Run specific test file
pytest tests/python/unit/test_validation.py

# Run specific test
pytest tests/python/unit/test_validation.py::test_algebraic_loop_detection
```

**JavaScript tests**:
```bash
cd js

# Run all tests
npm run test

# Run in watch mode (for TDD)
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test -- blocks.test.tsx
```

### Development Server (Frontend)

```bash
cd js
npm run dev
```

This starts Vite dev server with hot module replacement. Changes to React components reload instantly.

### Jupyter Development

**Create test notebook**:
```python
# test_notebook.ipynb
import lynx
import numpy as np

# Create widget
diagram = lynx.Diagram()

# Display in notebook
diagram
```

**Reload widget after Python changes**:
```python
# In notebook cell
%load_ext autoreload
%autoreload 2

import lynx
diagram = lynx.Diagram()
diagram
```

### Code Style

**Python** (Black + Ruff):
```bash
# Format code
black lynx/ tests/

# Lint
ruff check lynx/ tests/

# Type check
mypy lynx/
```

**JavaScript** (Prettier):
```bash
cd js

# Format
npm run format

# Lint
npm run lint
```

## Test-Driven Development Workflow

**Mandatory**: Tests MUST be written first and FAIL before implementation.

### Example: Implementing Algebraic Loop Detection

**Step 1: Write failing test**
```python
# tests/python/unit/test_validation.py
def test_detects_algebraic_loop():
    """Algebraic loops (cycles without dynamics) must be detected."""
    diagram = Diagram()

    # Create cycle with only Gain blocks
    g1 = diagram.add_block('gain', K=1.0)
    g2 = diagram.add_block('gain', K=2.0)

    diagram.add_connection(g1.ports['out'], g2.ports['in'])
    diagram.add_connection(g2.ports['out'], g1.ports['in'])

    result = diagram.validate()

    assert not result.is_valid
    assert any(e.code == 'ALGEBRAIC_LOOP' for e in result.errors)
```

**Run test** (should FAIL):
```bash
pytest tests/python/unit/test_validation.py::test_detects_algebraic_loop -v
```

**Step 2: Implement minimal code to pass**
```python
# lynx/validation/algebraic_loop.py
def detect_algebraic_loops(diagram):
    """Detect feedback cycles without dynamic blocks."""
    cycles = find_cycles(diagram.connections)

    for cycle in cycles:
        has_dynamics = any(
            diagram.get_block(bid).type in ['transfer_function', 'state_space']
            for bid in cycle
        )
        if not has_dynamics:
            return ValidationError(code='ALGEBRAIC_LOOP', ...)

    return None
```

**Run test again** (should PASS):
```bash
pytest tests/python/unit/test_validation.py::test_detects_algebraic_loop -v
```

**Step 3: Refactor** (improve code quality while tests still pass)

## Common Tasks

### Adding a New Block Type

1. **Write tests** (`tests/python/unit/test_blocks.py`)
2. **Implement block class** (`lynx/blocks/new_block.py`)
3. **Add to block registry** (`lynx/blocks/__init__.py`)
4. **Create React component** (`js/src/blocks/NewBlock.tsx`)
5. **Add to block palette** (`js/src/palette/BlockPalette.tsx`)
6. **Update data model** (`specs/001-lynx-jupyter-widget/data-model.md`)

### Adding a New Validation Rule

1. **Write test** (`tests/python/unit/test_validation.py`)
2. **Implement validator** (`lynx/validation/new_rule.py`)
3. **Integrate into main validator** (`lynx/validation/graph_validator.py`)
4. **Add error display** (`js/src/validation/ValidationPanel.tsx`)

### Adding State-Modifying Operations (CRITICAL - Undo/Redo Support)

**⚠️ IMPORTANT**: Any operation that modifies diagram state MUST support undo/redo.

**Rule**: All mutations go through `Diagram` methods that call `_save_state()` before modification.

**Correct Pattern**:
```python
# In lynx/diagram.py
def update_something(self, block_id: str, new_value: Any) -> bool:
    """Update something (with undo support)."""
    block = self.get_block(block_id)
    if not block:
        return False

    # Save state before modification (for undo)
    self._save_state()

    # Perform mutation
    block.something = new_value
    return True
```

**Widget handlers should call Diagram methods**:
```python
# In lynx/widget.py
def _handle_update_something(self, payload: Dict[str, Any]) -> None:
    """Handle update action."""
    block_id = payload.get("blockId", "")
    new_value = payload.get("value")

    # Use diagram method (not direct mutation)
    if self.diagram.update_something(block_id, new_value):
        self._update_diagram_state()
```

**DO NOT**:
```python
# ❌ WRONG - bypasses undo/redo
block.something = new_value
```

**Checklist for New State Operations**:
1. ✅ Add method to `Diagram` class that calls `_save_state()` before mutation
2. ✅ Write undo/redo tests in `tests/python/unit/test_diagram.py::TestUndoRedo`
3. ✅ Update widget handler to call diagram method (not direct mutation)
4. ✅ Verify tests pass (RED → GREEN → REFACTOR)

**Existing State-Modifying Operations** (all support undo/redo):
- `add_block()` - Add block to diagram
- `remove_block()` - Remove block and connected edges
- `add_connection()` - Add connection between blocks
- `remove_connection()` - Remove connection
- `update_block_position()` - Move block on canvas
- `update_block_parameter()` - Change parameter value/expression
- `update_block_label()` - Rename block label

### Debugging Traitlet Sync

**Enable traitlet logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now create widget
diagram = lynx.Diagram()
# Watch console for traitlet sync messages
```

**JavaScript side** (browser console):
```javascript
// Access widget model in browser console
console.log(widget.model.get('diagram_state'));

// Watch for changes
widget.model.on('change:diagram_state', () => {
  console.log('Diagram state changed!', widget.model.get('diagram_state'));
});
```

## Building & Packaging

### Development Build

```bash
# Frontend only
cd js
npm run build

# This outputs to js/dist/, which anywidget will bundle
```

### Production Package

```bash
# Build frontend first
cd js
npm run build

# Build Python package
cd ..
python -m build

# Output: dist/lynx-0.1.0.tar.gz and dist/lynx-0.1.0-py3-none-any.whl
```

### Install Locally

```bash
pip install -e .
```

## Testing User Workflows

### Test Scenario: Create Simple Feedback Loop

```python
# In Jupyter notebook
import lynx
import numpy as np

# Create diagram
diagram = lynx.Diagram()
diagram

# Add blocks via UI:
# 1. Drag Input marker
# 2. Drag Sum junction
# 3. Drag Transfer Function (enter num=[1], den=[1, 1])
# 4. Drag Gain (K=-0.5)
# 5. Drag Output marker

# Connect: Input → Sum → TF → Output
#                    ↑     ↓
#                    └─ Gain

# Save
diagram.save('feedback_control.json')

# Load in new session
diagram2 = lynx.Diagram.load('feedback_control.json')
diagram2  # Should restore exactly
```

## Performance Profiling

### Python

```bash
# Profile validation performance
python -m cProfile -o validation.prof -m pytest tests/python/unit/test_validation.py

# View results
python -m pstats validation.prof
# In pstats shell: sort cumtime, stats 20
```

### JavaScript

```typescript
// In browser dev tools
console.time('render');
// Perform action
console.timeEnd('render');

// Or use React DevTools Profiler
```

## Troubleshooting

### Widget Not Displaying

1. Check Jupyter supports anywidget:
   ```bash
   jupyter labextension list
   ```

2. Restart Jupyter kernel after Python changes

3. Clear browser cache if JS changes not appearing

### Validation Not Working

1. Check diagram_state in Python:
   ```python
   print(widget.diagram_state)
   ```

2. Check validation_result:
   ```python
   print(widget.validation_result)
   ```

3. Enable debug logging

### Traitlet Sync Issues

1. Verify action is being sent from JS:
   ```typescript
   console.log('Sending action:', action);
   model.set('_action', action);
   ```

2. Verify Python receives it:
   ```python
   @observe('_action')
   def _on_action(self, change):
       print(f'Received action: {change["new"]}')
   ```

3. Check for timestamp conflicts (dedupe logic)

## Resources

- **anywidget docs**: https://anywidget.dev
- **React Flow docs**: https://reactflow.dev
- **Traitlets docs**: https://traitlets.readthedocs.io
- **python-control**: https://python-control.readthedocs.io

## Next Steps

After setup:
1. Review `specs/001-lynx-jupyter-widget/spec.md` for requirements
2. Review `data-model.md` for entity definitions
3. Review `contracts/traitlet-interface.md` for API contract
4. Start with Phase 1 tasks (see `tasks.md` when generated)
5. Follow TDD workflow: Red → Green → Refactor

## Getting Help

- **Constitution**: `.specify/memory/constitution.md` for principles
- **Tech Stack**: `.specify/memory/tech_stack.md` for technical decisions
- **Functional Spec**: `.specify/memory/functional_spec.md` for what/why

**Happy coding!** 🚀
