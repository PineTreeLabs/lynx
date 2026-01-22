<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Traitlet Interface Contract

**Feature**: 001-lynx-jupyter-widget
**Date**: 2025-12-25
**Purpose**: Define the contract between Python backend and JavaScript frontend via anywidget traitlets

## Overview

The Lynx widget uses anywidget's traitlet system for bidirectional Python ↔ JavaScript communication. This document defines the interface contract that both sides must adhere to.

## Traitlet Definitions (Python Side)

### State Traitlets (Python → JavaScript)

```python
from traitlets import Unicode, Dict, List, Bool
from anywidget import AnyWidget

class LynxWidget(AnyWidget):
    # Diagram state (serialized as JSON)
    diagram_state = Dict({}).tag(sync=True)

    # Validation results
    validation_result = Dict({}).tag(sync=True)

    # Current selection
    selected_block_id = Unicode(None, allow_none=True).tag(sync=True)

    # UI state
    grid_snap_enabled = Bool(True).tag(sync=True)
```

### Command Traitlets (JavaScript → Python)

```python
    # User actions (JavaScript triggers, Python handles)
    _action = Dict({}).tag(sync=True)

    # File operations
    _save_request = Unicode('').tag(sync=True)
    _load_request = Unicode('').tag(sync=True)
```

## Data Structures

### diagram_state (Dict)

**Python → JavaScript** (Read-only in frontend)

Represents the complete diagram state synchronized from Python to JavaScript.

```typescript
interface DiagramState {
  version: string;
  blocks: Block[];
  connections: Connection[];
  metadata?: {
    name?: string;
    created?: string;
    [key: string]: any;
  };
}

interface Block {
  id: string;
  type: 'transfer_function' | 'state_space' | 'gain' | 'sum' | 'io_marker';
  position: { x: number; y: number };
  parameters: Parameter[];
  ports: Port[];
  label?: string;
}

interface Parameter {
  name: string;
  value: any;  // number, number[], number[][]
  expression?: string;  // For matrix parameters with hybrid storage
}

interface Port {
  id: string;
  type: 'input' | 'output';
  label?: string;
}

interface Connection {
  id: string;
  sourceBlockId: string;
  sourcePortId: string;
  targetBlockId: string;
  targetPortId: string;
}
```

**Update Pattern**:
- Python updates `diagram_state` whenever diagram changes
- JavaScript React components re-render automatically via traitlet sync
- JavaScript MUST NOT modify this traitlet directly

---

### validation_result (Dict)

**Python → JavaScript** (Read-only in frontend)

Contains validation errors and warnings computed by Python validator.

```typescript
interface ValidationResult {
  isValid: boolean;
  isExportReady: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

interface ValidationError {
  code: string;  // e.g., 'ALGEBRAIC_LOOP', 'DUPLICATE_INPUT_CONNECTION'
  message: string;
  affectedBlocks?: string[];
  affectedConnections?: string[];
}

interface ValidationWarning {
  code: string;  // e.g., 'DISCONNECTED_BLOCK', 'MISSING_IO'
  message: string;
  affectedBlocks?: string[];
}
```

**Update Pattern**:
- Python recomputes validation whenever diagram changes
- JavaScript displays errors/warnings in UI
- Validation runs in Python (control theory logic), not JavaScript

---

### _action (Dict)

**JavaScript → Python** (Command channel)

User actions from JavaScript that Python must handle.

```typescript
interface Action {
  type: string;  // Action type identifier
  payload: any;  // Action-specific data
  timestamp: number;  // For deduplication
}
```

**Supported Actions**:

#### addBlock
```typescript
{
  type: 'addBlock',
  payload: {
    blockType: 'transfer_function' | 'state_space' | 'gain' | 'sum' | 'io_marker',
    position: { x: number, y: number }
  },
  timestamp: Date.now()
}
```
**Python Response**: Adds block to diagram, updates `diagram_state`, runs validation

#### deleteBlock
```typescript
{
  type: 'deleteBlock',
  payload: {
    blockId: string
  },
  timestamp: Date.now()
}
```
**Python Response**: Removes block and connected edges, updates `diagram_state`, runs validation

#### moveBlock
```typescript
{
  type: 'moveBlock',
  payload: {
    blockId: string,
    position: { x: number, y: number }
  },
  timestamp: Date.now()
}
```
**Python Response**: Updates block position in `diagram_state`

#### addConnection
```typescript
{
  type: 'addConnection',
  payload: {
    sourceBlockId: string,
    sourcePortId: string,
    targetBlockId: string,
    targetPortId: string
  },
  timestamp: Date.now()
}
```
**Python Response**: Validates connection, adds if valid, updates `diagram_state`, runs validation

#### deleteConnection
```typescript
{
  type: 'deleteConnection',
  payload: {
    connectionId: string
  },
  timestamp: Date.now()
}
```
**Python Response**: Removes connection, updates `diagram_state`, runs validation

#### updateParameter
```typescript
{
  type: 'updateParameter',
  payload: {
    blockId: string,
    parameterName: string,
    expression: string  // Raw user input (e.g., "[1, 2, 3]" or "np.eye(2)")
  },
  timestamp: Date.now()
}
```
**Python Response**: Evaluates expression in notebook namespace, updates parameter with both expression and value, updates `diagram_state`, runs validation

#### undo
```typescript
{
  type: 'undo',
  payload: {},
  timestamp: Date.now()
}
```
**Python Response**: Reverts to previous diagram state, updates `diagram_state`

#### redo
```typescript
{
  type: 'redo',
  payload: {},
  timestamp: Date.now()
}
```
**Python Response**: Reapplies undone action, updates `diagram_state`

---

### _save_request (Unicode)

**JavaScript → Python** (File operation)

Triggers save operation.

```typescript
// JavaScript sends filename
widget.model.set('_save_request', 'my_diagram.json');
widget.model.save_changes();
```

**Python Handler**:
```python
@observe('_save_request')
def _on_save_request(self, change):
    filename = change['new']
    if filename:
        self.diagram.save(filename)
        # Optionally set feedback traitlet
```

---

### _load_request (Unicode)

**JavaScript → Python** (File operation)

Triggers load operation.

```typescript
// JavaScript sends filename
widget.model.set('_load_request', 'my_diagram.json');
widget.model.save_changes();
```

**Python Handler**:
```python
@observe('_load_request')
def _on_load_request(self, change):
    filename = change['new']
    if filename:
        self.diagram = Diagram.load(filename)
        self.diagram_state = self.diagram.to_dict()
        self._run_validation()
```

---

## Contract Tests

**Purpose**: Ensure Python and JavaScript sides agree on the traitlet interface.

### Test: diagram_state Synchronization

```python
# Python test
def test_diagram_state_sync():
    widget = LynxWidget()
    widget.diagram.add_block('gain', position={'x': 100, 'y': 200})

    state = widget.diagram_state
    assert len(state['blocks']) == 1
    assert state['blocks'][0]['type'] == 'gain'
```

```typescript
// JavaScript test
test('receives diagram_state updates', () => {
  const model = createMockModel({
    diagram_state: {
      blocks: [{ id: '1', type: 'gain', position: {x: 100, y: 200}, ...}],
      connections: []
    }
  });

  const { getByTestId } = render(<DiagramCanvas model={model} />);
  expect(getByTestId('block-1')).toBeInTheDocument();
});
```

### Test: Action Handling

```typescript
// JavaScript test
test('sends addBlock action', () => {
  const model = createMockModel();
  const { getByText } = render(<BlockPalette model={model} />);

  fireEvent.click(getByText('Gain Block'));

  const action = model.get('_action');
  expect(action.type).toBe('addBlock');
  expect(action.payload.blockType).toBe('gain');
});
```

```python
# Python test
def test_add_block_action():
    widget = LynxWidget()

    widget._action = {
        'type': 'addBlock',
        'payload': {'blockType': 'gain', 'position': {'x': 100, 'y': 200}},
        'timestamp': time.time()
    }

    assert len(widget.diagram.blocks) == 1
```

### Test: Validation Results

```python
# Python test
def test_validation_result_sync():
    widget = LynxWidget()
    # Create algebraic loop
    widget.diagram.add_block('gain', id='g1', ...)
    widget.diagram.add_block('gain', id='g2', ...)
    widget.diagram.add_connection('g1', 'out', 'g2', 'in')
    widget.diagram.add_connection('g2', 'out', 'g1', 'in')

    widget._run_validation()

    assert widget.validation_result['isValid'] == False
    assert any(e['code'] == 'ALGEBRAIC_LOOP' for e in widget.validation_result['errors'])
```

```typescript
// JavaScript test
test('displays validation errors', () => {
  const model = createMockModel({
    validation_result: {
      isValid: false,
      errors: [{
        code: 'ALGEBRAIC_LOOP',
        message: 'Feedback loops must contain dynamic blocks',
        affectedBlocks: ['g1', 'g2']
      }]
    }
  });

  const { getByText } = render(<ValidationPanel model={model} />);
  expect(getByText(/Feedback loops must contain dynamic blocks/)).toBeInTheDocument();
});
```

---

## Performance Considerations

### Debouncing

**Problem**: Rapid diagram edits (e.g., dragging blocks) could trigger excessive validation.

**Solution**: Debounce validation in Python:
```python
from threading import Timer

def _schedule_validation(self):
    if hasattr(self, '_validation_timer'):
        self._validation_timer.cancel()
    self._validation_timer = Timer(0.1, self._run_validation)  # 100ms debounce
    self._validation_timer.start()
```

### Batch Updates

**Problem**: Multiple simultaneous actions could cause race conditions.

**Solution**: Use timestamps in actions to deduplicate:
```python
@observe('_action')
def _on_action(self, change):
    action = change['new']
    if action.get('timestamp', 0) <= self._last_action_timestamp:
        return  # Ignore duplicate/old action
    self._last_action_timestamp = action['timestamp']
    self._handle_action(action)
```

---

## Error Handling

### Python Errors

When Python encounters errors (e.g., expression evaluation fails), update `validation_result`:

```python
try:
    value = eval(expression, notebook_namespace)
except Exception as e:
    self.validation_result = {
        'isValid': False,
        'errors': [{
            'code': 'EXPRESSION_ERROR',
            'message': f'Failed to evaluate expression: {str(e)}',
            'affectedBlocks': [block_id]
        }]
    }
```

### JavaScript Errors

JavaScript should catch errors and display user-friendly messages (not crash widget):

```typescript
try {
  model.set('_action', action);
  model.save_changes();
} catch (error) {
  console.error('Failed to send action:', error);
  toast.error('An error occurred. Please try again.');
}
```

---

## Versioning

**Current Version**: 1.0.0

**Future Changes**:
- Adding new action types: MINOR version bump
- Changing diagram_state structure: MAJOR version bump
- Adding optional fields: PATCH version bump

Include version in traitlet metadata:
```python
_interface_version = Unicode('1.0.0').tag(sync=True)
```
