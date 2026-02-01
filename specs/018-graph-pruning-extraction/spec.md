<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Graph-Based Subsystem Extraction

**Feature Branch**: `018-graph-pruning-extraction`
**Created**: 2026-02-01
**Status**: Draft
**Input**: User description: "Implement graph analysis to correct the coupling issue with naive application of interconnect. The expectation of subsystem extraction is that the extracted subsystem maps from the input signal to the output signal *without the influence of any feedback loops downstream of the output signal or upstream of the input signal, but accounting for internal feedback loops between those points*. The modified diagram used to generate the interconnect system should therefore be pruned to remove unrelated blocks and extraneous feedback loops. As part of the implementation, include a clear failing test case (not the complex cascaded.json, but a minimal example that currently does not work) and resolve it using the graph analysis algorithm."

## User Scenarios & Testing

### User Story 1 - Extract Single Block Transfer Function (Priority: P1)

A user has a complex cascaded control system diagram with multiple nested feedback loops. They want to extract the transfer function of a single controller block by specifying signals at its input and output, expecting to receive only that block's dynamics without influence from unrelated parts of the system.

**Why this priority**: This is the core value proposition - users need to isolate and analyze individual components within complex systems. This is the fundamental capability that enables controller design, system analysis, and verification workflows.

**Independent Test**: Can be fully tested by creating a minimal diagram with a feedforward path plus unrelated feedback, extracting a single block's TF, and verifying it matches the block's isolated dynamics.

**Acceptance Scenarios**:

1. **Given** a diagram with blocks A → B → C where B is a 2nd-order transfer function, and C has downstream feedback to an unrelated block D, **When** user extracts transfer function from signal at B's input to signal at B's output, **Then** the extracted TF is 2nd-order matching block B's parameters exactly
2. **Given** a cascaded system with three controllers in series (position, attitude, rate), each with local feedback, **When** user extracts TF from rate error signal to rate command signal (spanning just the rate controller), **Then** the result contains only the rate controller's dynamics without coupling from upstream position/attitude controllers
3. **Given** a diagram with a sum block feeding a controller, and the controller output connected to downstream plant dynamics with feedback, **When** user extracts from sum output (labeled signal) to controller output (labeled signal), **Then** the extraction includes only the controller block, not the downstream plant or feedback path

---

### User Story 2 - Preserve Internal Feedback Loops (Priority: P2)

A user wants to extract a subsystem that includes multiple blocks with feedback connections between them, while excluding external feedback loops that couple the subsystem to other parts of the diagram.

**Why this priority**: After single-block extraction works, users need to analyze multi-block subsystems with their internal couplings intact. This enables analysis of cascaded loops, inner-outer loop structures, and other common control architectures.

**Independent Test**: Can be tested by creating a diagram with two blocks in feedback (forming an inner loop), connected to a third block with external feedback. Extracting the inner loop subsystem should include both blocks and their mutual feedback, excluding the external loop.

**Acceptance Scenarios**:

1. **Given** a diagram with inner loop (controller + plant with feedback) and outer loop (cascaded controller feeding the inner loop), **When** user extracts from inner loop input to inner loop output, **Then** the result includes both inner loop blocks and their feedback connection, but excludes the outer cascade controller
2. **Given** a multi-rate control system with fast inner loop and slow outer loop, **When** user extracts the fast inner loop subsystem, **Then** the extraction includes all blocks and feedbacks within the fast loop boundary, treating outer loop signals as external inputs/outputs

---

### User Story 3 - Handle Complex Path Topologies (Priority: P3)

A user has a diagram where multiple parallel paths exist between the source and destination signals (e.g., feedforward + feedback paths), and wants the extraction to include all relevant paths while excluding unrelated branches.

**Why this priority**: Real control systems often have multiple signal paths (feedforward compensation, multiple feedback sensors, etc.). The algorithm must correctly identify and preserve all paths that contribute to the input-output relationship.

**Independent Test**: Can be tested with a diagram having parallel feedforward and feedback paths between two points, plus an unrelated side branch. Extraction should include both paths but exclude the side branch.

**Acceptance Scenarios**:

1. **Given** a diagram with feedforward path (A → B) and feedback path (B → C → A) forming a loop, plus unrelated branch D, **When** user extracts from external input to B's output, **Then** result includes A, B, C and their connections, excluding D
2. **Given** a MIMO system with cross-coupling (multiple inputs affecting multiple outputs through different paths), **When** user extracts from one input to one output, **Then** all blocks on any path between that input-output pair are included

---

### Edge Cases

- What happens when source and destination signals refer to the same block (e.g., extracting from a block's input to its output)?
- How does the system handle algebraic loops within the pruned subsystem?
- What if there are multiple disconnected paths between source and destination?
- How does extraction behave when source or destination is in the middle of a feedback loop?
- What happens if pruning removes all blocks (no path exists between source and destination)?
- How are blocks with multiple outputs handled when only one output is on the extraction path?

## Requirements

### Functional Requirements

- **FR-001**: System MUST analyze the diagram's connection topology to identify all blocks on any path between source signal and destination signal
- **FR-002**: System MUST remove blocks that are exclusively downstream of the destination signal (not affecting the source-to-destination transfer function)
- **FR-003**: System MUST remove blocks that are exclusively upstream of the source signal (not affecting the source-to-destination transfer function)
- **FR-004**: System MUST preserve all feedback connections between blocks on the source-to-destination path(s)
- **FR-005**: System MUST remove feedback connections that involve blocks outside the source-to-destination path(s)
- **FR-006**: System MUST handle cycles in the connection graph (feedback loops) without infinite recursion
- **FR-007**: System MUST validate that at least one valid path exists between source and destination signals before attempting extraction
- **FR-008**: System MUST work correctly when source and destination signals reference the same block
- **FR-009**: System MUST include all blocks on parallel paths when multiple routes exist between source and destination
- **FR-010**: Extracted transfer functions MUST match the isolated dynamics of the blocks on the path, without coupling from pruned blocks
- **FR-011**: System MUST provide clear error messages when no path exists between source and destination
- **FR-012**: Extraction behavior MUST be deterministic and independent of block creation order or diagram layout

### Key Entities

- **Connection Graph**: Directed graph representation of diagram blocks (nodes) and connections (edges), used for path analysis
- **Path**: Sequence of blocks and connections from source signal to destination signal through the diagram
- **Pruned Diagram**: Modified copy of original diagram with unrelated blocks removed, used for building the interconnect system
- **Source Signal**: Input boundary for extraction, specified by connection label, IOMarker label, or block.port notation
- **Destination Signal**: Output boundary for extraction, specified using same notation as source signal

## Success Criteria

### Measurable Outcomes

- **SC-001**: For a single-block extraction with unrelated downstream feedback, extracted TF order matches the isolated block's order (e.g., 2nd-order controller yields 2nd-order TF, not higher)
- **SC-002**: Extraction from connection label to OutputMarker label completes in under 500ms for diagrams with up to 50 blocks
- **SC-003**: Graph pruning correctly identifies minimal block set such that number of states in extracted system equals sum of states in blocks on the path (no extraneous coupling)
- **SC-004**: All existing extraction test cases continue to pass (backward compatibility maintained)
- **SC-005**: New minimal failing test case (included in implementation) passes after graph pruning is implemented
- **SC-006**: For diagrams with parallel paths, extraction includes all paths such that DC gain matches manual calculation accounting for all routes

## Scope

### In Scope

- Graph-based analysis to find all paths between source and destination signals
- Pruning algorithm to create minimal diagram containing only relevant blocks
- Preservation of internal feedback loops within the extraction boundary
- Removal of external feedback loops that couple to pruned blocks
- Validation that path exists before extraction
- Comprehensive test case demonstrating the problem and solution
- Integration with existing `get_ss()` and `get_tf()` API

### Out of Scope

- Changing the existing signal resolution priority (IOMarker labels → connection labels → block.port)
- Modifying the interconnect building logic (using python-control's existing API)
- Adding new signal reference formats beyond existing patterns
- Performance optimization for extremely large diagrams (>1000 blocks)
- Graphical visualization of pruned diagram or path highlighting

## Assumptions

- Users understand the concept of signal flow and input-output relationships in block diagrams
- Diagrams are acyclic at the top level or have well-defined feedback loops (no algebraic loops that make the system invalid)
- The existing validation logic correctly identifies invalid diagrams before extraction
- Python-control's `interconnect()` function correctly handles the pruned diagram structure
- Path finding terminates in reasonable time for typical control system diagrams (depth < 100 blocks)

## Dependencies

- Existing `get_ss()` and `get_tf()` extraction methods in `src/lynx/diagram.py`
- `_prepare_for_extraction()` function in `src/lynx/conversion/signal_extraction.py`
- Diagram validation logic in `src/lynx/validation/`
- Python-control library's `interconnect()` and indexing functionality
- Existing test infrastructure for integration and unit tests

## Constraints

- Must maintain backward compatibility with existing extraction behavior for simple diagrams
- Cannot modify python-control library internals
- Pruning algorithm must complete in reasonable time (sub-second for typical diagrams)
- Must work with all existing signal reference patterns (IOMarker labels, connection labels, block.port notation)
- Graph analysis must handle cycles without infinite loops or stack overflow
