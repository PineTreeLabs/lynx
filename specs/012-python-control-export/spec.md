<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Python-Control Export

**Feature Branch**: `012-python-control-export`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "Create a feature specification for conversion from lynx.Diagram to python-control (don't worry about the other direction)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Export Basic Linear Diagram (Priority: P1)

A controls engineer creates a simple feedback control system diagram in Lynx (using Gain, Transfer Function, State Space, and Sum blocks with connections) and exports it to a python-control `InterconnectedSystem` object for simulation and analysis.

**Why this priority**: This is the core value proposition - enabling users to visually design control systems in Lynx and then analyze them computationally with python-control. Without this, Lynx remains a documentation tool with no computational capability.

**Independent Test**: Can be fully tested by creating a standard PID feedback loop diagram in Lynx (controller, plant, sum junction), exporting to python-control, running a step response simulation, and verifying the output matches expected behavior for the given parameters.

**Acceptance Scenarios**:

1. **Given** a Lynx diagram with Gain, TransferFunction, and Sum blocks connected in a valid topology, **When** user calls `diagram.to_interconnect()`, **Then** a python-control `InterconnectedSystem` is returned with all blocks converted to subsystems and connections preserved
2. **Given** a Lynx diagram with InputMarker and OutputMarker blocks defining system boundaries, **When** exported to python-control, **Then** the `inplist` and `outlist` parameters correctly identify system inputs and outputs
3. **Given** a valid python-control system from export, **When** user runs `ct.step_response(sys)`, **Then** simulation completes successfully and produces expected control behavior
4. **Given** a Lynx diagram with StateSpace blocks, **When** exported to python-control, **Then** state-space matrices (A, B, C, D) are correctly passed to `ct.ss()` constructor

---

### User Story 2 - Handle Sum Block Sign Configuration (Priority: P2)

A controls engineer creates a feedback system with sum junctions that include negative feedback (subtraction). When exported, the python-control system correctly applies signal negation according to the sum block's quadrant signs.

**Why this priority**: Negative feedback is fundamental to control systems (e.g., error = reference - output). Without correct sign handling, exported systems will have incorrect dynamics and produce wrong simulation results.

**Independent Test**: Can be fully tested by creating a Lynx diagram with a Sum block configured with `signs = ["+", "-", "|"]`, connecting signals to the positive and negative inputs, exporting to python-control, and verifying that the negative input is prefixed with `-` in the connections list.

**Acceptance Scenarios**:

1. **Given** a Sum block with `signs = ["+", "-", "|"]` and connections to `in1` (top, positive) and `in2` (left, negative), **When** exported to python-control, **Then** the connection to `in2` includes a `-` prefix (e.g., `['-block1.out', 'sum1.in2']`)
2. **Given** a Sum block with all positive signs `["+", "+", "+"]`, **When** exported, **Then** no signal negation is applied to any connection
3. **Given** a closed-loop feedback system with negative feedback (subtraction at error sum junction), **When** exported and simulated, **Then** step response shows stable feedback behavior (not runaway positive feedback)

---

### User Story 3 - Validate Diagram Before Export (Priority: P3)

A controls engineer attempts to export an incomplete or invalid Lynx diagram (e.g., unconnected inputs, missing system boundaries). The export operation detects the issues and provides clear error messages explaining what needs to be fixed.

**Why this priority**: While validation is important for good UX, the core functionality (exporting valid diagrams) doesn't depend on it. Users can manually verify their diagrams are complete before export. This is polish that improves usability but isn't blocking for MVP.

**Independent Test**: Can be fully tested by creating invalid diagrams (unconnected input port, no InputMarkers, no OutputMarkers) and verifying that `to_interconnect()` raises exceptions with helpful error messages identifying the specific problems.

**Acceptance Scenarios**:

1. **Given** a Lynx diagram with an unconnected input port on a block, **When** user calls `to_interconnect()`, **Then** a validation error is raised identifying the specific block and port that is unconnected
2. **Given** a Lynx diagram with no InputMarker blocks, **When** exported, **Then** a validation error explains that at least one system input must be defined
3. **Given** a Lynx diagram with no OutputMarker blocks, **When** exported, **Then** a validation error explains that at least one system output must be defined
4. **Given** a Lynx diagram with disconnected subgraphs (two separate unconnected clusters of blocks), **When** exported, **Then** a validation error identifies the disconnected components

---

### Edge Cases

- What happens when a Sum block has only "|" signs (no active inputs)?
  - Validation should reject this during diagram construction (already enforced by `SumBlock.__init__`)
- What happens when a Gain block has `K=0`?
  - Valid configuration - python-control should handle zero gain correctly
- What happens when a TransferFunction has unstable poles?
  - Valid configuration - python-control will create the system and simulations may diverge (expected behavior)
- What happens when a StateSpace block has non-square A matrix or mismatched dimensions?
  - Validation should reject this during diagram construction (Lynx parameter panel already validates SISO dimensions)
- What happens when a diagram has only blocks but no connections?
  - Validation error - all non-InputMarker blocks must have connected inputs
- What happens when multiple outputs connect to the same input (fan-in)?
  - Already prevented by Lynx's connection validation (one source per input port)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a method `Diagram.to_interconnect()` that returns a python-control `InterconnectedSystem` object
- **FR-002**: Gain blocks MUST be converted to python-control transfer functions using `ct.tf(K, 1, name=block.id, inputs=['in'], outputs=['out'])`
- **FR-003**: TransferFunction blocks MUST be converted using `ct.tf(numerator, denominator, name=block.id, inputs=['in'], outputs=['out'])`
- **FR-004**: StateSpace blocks MUST be converted using `ct.ss(A, B, C, D, name=block.id, inputs=['in'], outputs=['out'])`
- **FR-005**: Sum blocks MUST be converted to `ct.summing_junction(inputs=[...], output='out', name=block.id)`
- **FR-006**: Connections MUST be converted to python-control's signal naming format: `['source_block.source_port', 'target_block.target_port']`
- **FR-007**: Sum block connections with negative signs MUST apply signal negation using `-` prefix (e.g., `['-block1.out', 'sum1.in2']`)
- **FR-008**: InputMarker blocks MUST be extracted to the `inplist` parameter (not created as subsystems)
- **FR-009**: OutputMarker blocks MUST be extracted to the `outlist` parameter (not created as subsystems)
- **FR-010**: System MUST validate that all non-InputMarker input ports are connected before export
- **FR-011**: System MUST validate that at least one InputMarker exists (system must have inputs)
- **FR-012**: System MUST validate that at least one OutputMarker exists (system must have outputs)
- **FR-013**: System MUST raise descriptive exceptions when validation fails, identifying the specific problem and affected blocks/ports
- **FR-014**: The method signature MUST be `to_interconnect() -> control.InterconnectedSystem` (no parameters required for MVP)
- **FR-015**: Sum block port ID to sign mapping MUST correctly handle skipped "|" signs (e.g., `signs=["+", "|", "-"]` creates `in1` (top, +) and `in2` (bottom, -) only)

### Key Entities *(include if feature involves data)*

- **InterconnectedSystem (python-control)**: The output object representing the complete control system with all subsystems and connections. Contains subsystems list, connection map, input list, and output list.
- **Block Mapping**: The correspondence between Lynx block types/parameters and python-control system constructors (tf, ss, summing_junction).
- **Connection Mapping**: The correspondence between Lynx Connection objects (source_block_id, source_port_id, target_block_id, target_port_id) and python-control connection format (`['source.signal', 'target.signal']`).
- **Signal Name**: Fully qualified signal identifier in python-control's format (`block_id.port_id`), with optional negation prefix for sum block inputs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can export any valid Lynx diagram (with connected blocks and I/O markers) to python-control and run simulations without manual code modifications
- **SC-002**: Exported systems produce identical step response behavior when simulated in python-control as equivalent hand-coded interconnect systems
- **SC-003**: Export operation completes in under 100ms for diagrams with up to 50 blocks (typical complexity for control systems)
- **SC-004**: Validation errors identify the specific problem (block ID, port ID, issue description) allowing users to fix diagrams in under 1 minute per error
- **SC-005**: 100% of Lynx's supported block types (Gain, TransferFunction, StateSpace, Sum, InputMarker, OutputMarker) successfully convert to python-control equivalents
- **SC-006**: Sum blocks with negative feedback correctly produce stable closed-loop behavior when appropriate (sign handling is correct)

## Assumptions *(mandatory)*

- Users have python-control installed (`pip install control`)
- Lynx diagrams are already validated at construction time (no invalid block parameters)
- All Lynx blocks remain SISO (single input, single output) for MVP - MIMO support deferred
- Nonlinear systems are out of scope (python-control's `nlsys()` not supported)
- Hierarchical subsystems are out of scope (flat diagrams only)
- Connection waypoints and labels are visual-only and not exported (python-control doesn't support routing metadata)
- Block positions, flipped state, custom LaTeX, and visual properties are not exported (python-control has no visual representation)

## Out of Scope *(mandatory)*

- **Reverse conversion (python-control → Lynx)**: Not included in this feature. Would require parsing python-control system objects and inferring visual layout.
- **MIMO block support**: Multi-input, multi-output blocks require different port naming conventions (`in[0]`, `in[1]`, `out[0]`, `out[1]`)
- **Nonlinear systems**: python-control's `nlsys()` blocks not supported
- **Frequency Response Data (FRD) systems**: Not supported by Lynx
- **Hierarchical/nested subsystems**: Lynx diagrams are flat; python-control nested systems not supported
- **Custom simulation parameters**: Users must configure simulation settings (time span, initial conditions) in python-control after export
- **Automatic system analysis**: No automatic Bode plots, root locus, or stability analysis - users run these manually in python-control
- **Export to other control libraries**: Only python-control supported (not MATLAB Control Toolbox, Slycot, etc.)
- **Round-trip editing**: No ability to re-import modified python-control systems back into Lynx

## Dependencies *(mandatory)*

- **python-control library**: Must be installed in user environment (`control` package version 0.9.0 or later)
- **NumPy**: Required by python-control for array operations (already a Lynx dependency)
- **Existing Lynx validation logic**: Leverages existing connection validation (output→input, no duplicate connections)
- **Port naming conventions**: Relies on consistent port ID format (e.g., `in1`, `in2`, `out`) established in earlier features

## Risks *(include if applicable)*

- **python-control API changes**: If python-control changes the `interconnect()` signature or behavior, export code may break. Mitigation: Pin to specific python-control version range in requirements.
- **Sum block sign indexing bugs**: Mapping port IDs to signs with skipped "|" entries is error-prone. Mitigation: Comprehensive unit tests with all sign combinations.
- **Validation false positives/negatives**: Over-strict validation may reject valid diagrams; under-strict may allow diagrams that crash python-control. Mitigation: Test against known-valid and known-invalid control system examples.
- **Performance on large diagrams**: Complex diagrams (>100 blocks) may have slow export due to validation overhead. Mitigation: Profile and optimize validation if needed (acceptable for MVP with 50-block target).
