<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Lynx Block Diagram Widget

**Feature Branch**: `001-lynx-jupyter-widget`
**Created**: 2025-12-25
**Status**: Draft
**Input**: User description: "Develop Lynx, a block diagram GUI for control systems, implemented as a Jupyter widget"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Block Diagram Creation (Priority: P1)

As a controls engineer working in a Jupyter notebook, I want to create and edit block diagrams interactively using drag-and-drop, so that I can quickly sketch control system architectures without leaving my notebook environment.

**Why this priority**: This is the core value proposition - enabling visual control system design within Jupyter. Without this, there's no reason to use the tool.

**Independent Test**: User can create a simple feedback control system (input → sum → controller → plant → output with feedback) by dragging blocks and connecting them, then save it to JSON. System validates connections in real-time and prevents invalid configurations.

**Acceptance Scenarios**:

1. **Given** an empty Jupyter notebook cell, **When** user creates a Diagram object and displays it, **Then** an interactive canvas appears with a block palette
2. **Given** the interactive canvas, **When** user drags a Transfer Function block onto canvas, **Then** block appears at cursor position and can be positioned
3. **Given** two blocks on canvas, **When** user connects output of one block to input of another, **Then** connection line appears and validation confirms it's valid
4. **Given** a completed diagram, **When** user calls `diagram.save("design.json")`, **Then** diagram is persisted to JSON file with all blocks and connections
5. **Given** a saved JSON file, **When** user calls `Diagram.load("design.json")`, **Then** diagram is restored exactly as it was saved

---

### User Story 2 - Block Parameter Configuration (Priority: P2)

As a controls engineer, I want to configure block parameters using Python expressions (like transfer function coefficients or state-space matrices), so that I can leverage my existing numpy variables and programmatically define system components.

**Why this priority**: Parameter entry is essential for creating meaningful diagrams, but doesn't need to be perfect in the first iteration. Text input is sufficient for MVP.

**Independent Test**: User can create a transfer function block, enter numerator `[5, 3]` and denominator `[1, 2, 1]`, and see the values stored correctly. For state-space blocks, user can enter `A` (referencing a numpy variable) and see both the expression and resolved matrix value displayed.

**Acceptance Scenarios**:

1. **Given** a Transfer Function block, **When** user enters `num=[5, 3]` and `den=[1, 2, 1]`, **Then** parameters are validated and stored
2. **Given** a State Space block and numpy variable `A = np.eye(2)`, **When** user enters "A" in matrix field, **Then** system evaluates expression, displays both "A" and `[[1,0],[0,1]]`, and stores both in JSON
3. **Given** a Gain block, **When** user enters `K=5.0`, **Then** gain value is stored and displayed on block
4. **Given** invalid input, **When** user enters malformed expression, **Then** clear error message appears explaining the issue

---

### User Story 3 - Control Theory Validation (Priority: P3)

As a controls engineer, I want the system to validate my block diagram against control theory rules (algebraic loops, connection constraints, system completeness), so that I don't create mathematically invalid systems that will fail when exported.

**Why this priority**: Validation prevents errors, but users can start creating valid diagrams before all validation is complete. Most important validation (connection constraints) should be in P1, advanced checks (algebraic loops) can follow.

**Independent Test**: User attempts to create a pure gain feedback loop (algebraic loop) and receives real-time error. User creates valid feedback loop with transfer function block and validation passes.

**Acceptance Scenarios**:

1. **Given** user creates a feedback loop with only Gain blocks, **When** connection is made closing the loop, **Then** validation error appears: "Algebraic loop detected - feedback loops must contain dynamic blocks"
2. **Given** user attempts to connect two wires to single input port, **When** second connection is attempted, **Then** error appears: "Input port can only have one connection"
3. **Given** a valid diagram with one input and one output block, **When** validation runs, **Then** system reports "Ready to export"
4. **Given** diagram with disconnected blocks, **When** validation runs, **Then** warning appears but diagram can still be saved

---

### User Story 4 - Diagram Persistence & Reproducibility (Priority: P4)

As a controls engineer, I want my diagrams to be saved in human-readable JSON format and fully reproducible when loaded, so that I can version control my designs with git and share them with colleagues.

**Why this priority**: Persistence is covered in P1 (save/load), but complete reproducibility details (handling missing variables, forward compatibility) are refinements.

**Independent Test**: User saves diagram with state-space block referencing variable `A`, commits JSON to git, opens in new session without defining `A`, and system loads using stored matrix values with warning message.

**Acceptance Scenarios**:

1. **Given** saved diagram JSON file, **When** user opens in text editor, **Then** structure is human-readable with clear block/connection hierarchy
2. **Given** diagram with matrix expression "A", **When** loaded in session without variable `A` defined, **Then** diagram loads using stored value and displays warning
3. **Given** diagram created with older JSON schema version, **When** loaded, **Then** system ignores unknown fields and provides sensible defaults for missing fields
4. **Given** notebook with `Diagram.load()` in first cell, **When** user runs "Restart & Run All", **Then** diagram loads identically every time

---

### User Story 5 - User Experience Essentials (Priority: P5)

As a controls engineer, I want keyboard shortcuts for common operations, undo/redo functionality, and optional grid snapping, so that I can work efficiently and experiment freely without fear of making mistakes.

**Why this priority**: These UX enhancements significantly improve workflow but aren't blocking for basic functionality. Can be added incrementally.

**Independent Test**: User creates diagram, uses Ctrl+Z to undo last action, uses keyboard shortcut to add new block, toggles grid snapping on/off.

**Acceptance Scenarios**:

1. **Given** user has made several edits, **When** user presses Ctrl+Z (or Cmd+Z), **Then** last action is undone and can be redone with Ctrl+Y
2. **Given** user wants to add block quickly, **When** user presses keyboard shortcut (e.g., "T" for transfer function), **Then** new block appears at center of viewport
3. **Given** grid snapping is enabled, **When** user drags block, **Then** block snaps to 20-pixel grid for neat alignment
4. **Given** grid snapping is disabled, **When** user drags block, **Then** block moves freely without snapping

---

### Edge Cases

- What happens when user tries to load JSON file that doesn't exist? → Clear error message: "File not found: design.json"
- What happens when user creates diagram with 100+ blocks? → Performance degrades gracefully; system warns if >50 blocks
- What happens when user enters Python expression that throws exception during eval()? → Error caught, clear message shown, stored value used if available
- What happens when user tries to connect incompatible port types? → Real-time validation prevents connection, shows error
- What happens when user closes notebook without saving? → Changes lost (expected Jupyter behavior), no auto-save in MVP
- What happens when JSON contains cycle that wasn't detected? → Load-time validation catches it, shows error with affected blocks
- What happens when user creates multiple input/output blocks? → Allowed - system exports treating them as separate boundary points

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide interactive canvas for drag-and-drop block diagram editing
- **FR-002**: System MUST support five block types: Transfer Function, State Space, Gain, Sum Junction, and Input/Output markers
- **FR-003**: System MUST allow users to create connections between block output ports and input ports via drag interaction
- **FR-004**: System MUST validate connections in real-time (<100ms feedback)
- **FR-005**: System MUST detect and prevent algebraic loops (feedback cycles without dynamic blocks)
- **FR-006**: System MUST enforce connection constraints (one connection per input port, unlimited fan-out from output ports)
- **FR-007**: System MUST validate system completeness (at least one input and one output block for export)
- **FR-008**: System MUST allow parameters to be entered as Python expressions evaluated in notebook namespace
- **FR-009**: System MUST save diagrams to JSON format via explicit `diagram.save(filename)` method
- **FR-010**: System MUST load diagrams from JSON format via `Diagram.load(filename)` classmethod
- **FR-011**: System MUST store both expression and resolved value for matrix parameters (hybrid approach)
- **FR-012**: System MUST display both expression and current evaluated value in UI for matrix parameters
- **FR-013**: System MUST provide undo/redo functionality for all operations (in-session only)
- **FR-014**: System MUST provide keyboard shortcuts for common operations (add block, delete, undo, redo)
- **FR-015**: System MUST provide optional grid snapping (20 pixel grid, toggleable)
- **FR-016**: System MUST handle diagrams with 50+ blocks without performance degradation
- **FR-017**: System MUST provide clear, actionable error messages for all validation failures
- **FR-018**: System MUST warn (but allow) disconnected blocks in diagram
- **FR-019**: System MUST support multiple input and output blocks per diagram
- **FR-020**: System MUST include JSON schema version for forward/backward compatibility

### Key Entities

- **Diagram**: Top-level container for block diagram; contains blocks and connections; provides save/load methods
- **Block**: Visual element representing control system component; has type (TF, SS, Gain, Sum, I/O), parameters, position, ports
- **Connection**: Directed link from one block's output port to another block's input port; represents signal flow
- **Port**: Input or output connection point on a block; enforces SISO constraints
- **Parameter**: Configurable value on block (e.g., transfer function coefficients, matrix); stores expression and resolved value
- **ValidationResult**: Outcome of diagram validation; includes errors, warnings, and system completeness status

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Controls engineers can recreate standard textbook feedback control examples in under 5 minutes
- **SC-002**: System provides validation feedback in under 100 milliseconds for all operations
- **SC-003**: Diagrams with 50 blocks render and respond to interactions smoothly (no perceptible lag)
- **SC-004**: Saved JSON files are human-readable and produce meaningful git diffs when modified
- **SC-005**: System experiences zero crashes during normal use scenarios (create, edit, save, load operations)
- **SC-006**: 90% of engineers can use core features (add blocks, connect, save) without consulting documentation
- **SC-007**: Diagrams created and saved can be loaded and run through "Restart & Run All" reproducibly

## Assumptions

- Users have basic familiarity with Jupyter notebooks and Python
- Users understand classical control theory (transfer functions, state-space, feedback loops)
- Users have python-control library installed (or will install it for export functionality)
- Users have numpy available for matrix operations
- Jupyter environment supports anywidget framework (JupyterLab, classic notebook, VSCode)
- Users are working with SISO control systems (not MIMO)
- Maximum diagram complexity is ~50-100 blocks (not industrial-scale thousands of blocks)
- Network latency is reasonable for loading widget assets

## Dependencies

- **python-control library**: Target for export functionality (future user story, not in MVP)
- **numpy**: Required for matrix operations in state-space blocks
- **anywidget**: Framework dependency for Jupyter widget integration
- **React Flow**: Frontend library for diagram rendering
- **Jupyter environment**: JupyterLab, classic notebook, or VSCode with Jupyter extension

## Out of Scope (Explicitly Excluded)

The following are explicitly excluded from this specification to maintain MVP focus:

- Export to python-control code (future feature, not in initial MVP)
- Simulation or analysis capabilities
- Visualization (Bode plots, root locus, step response)
- Block diagram algebra or automatic simplification
- LaTeX rendering of equations
- Nonlinear blocks
- MIMO system support
- Desktop application version (future consideration)
- Real-time collaborative editing
- Custom block type creation
- Programmatic diagram construction via Python API (future user story)
- Auto-layout or automatic block arrangement
- Block libraries or templates
