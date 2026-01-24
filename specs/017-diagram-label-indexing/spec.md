<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: Diagram Label Indexing

**Feature Branch**: `017-diagram-label-indexing`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "Add support for indexing into a diagram by block label, for instance plant = diagram["plant"]. This should raise an error if the label is not unique."

## Clarifications

### Session 2026-01-24

- Q: Should LabelNotUniqueError message include just the count OR the full list of block IDs? → A: Both count and block IDs (e.g., "Label 'plant' appears on 3 blocks: ['block_123', 'block_456', ...]")
- Q: How should the system handle non-string index keys (e.g., `diagram[123]`, `diagram[block_obj]`)? → A: Raise TypeError immediately for non-string keys (e.g., "Label must be a string, got int")

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Block by Label (Priority: P1)

Engineers working with control system diagrams need a quick, readable way to retrieve blocks by their meaningful labels (e.g., "plant", "controller", "sensor") rather than by cryptic block IDs. This makes code more self-documenting and easier to understand.

**Why this priority**: This is the core functionality. Without it, engineers must track block IDs manually or iterate through all blocks to find the one they need, making the API cumbersome and error-prone.

**Independent Test**: Can be fully tested by creating a diagram with uniquely labeled blocks, indexing by label (e.g., `plant = diagram["plant"]`), and verifying the correct block is returned. Delivers immediate value by simplifying block access.

**Acceptance Scenarios**:

1. **Given** a diagram with a block labeled "plant", **When** an engineer accesses `diagram["plant"]`, **Then** the block with label "plant" is returned
2. **Given** a diagram with blocks labeled "controller", "plant", and "sensor", **When** an engineer accesses `diagram["controller"]`, **Then** the block with label "controller" is returned
3. **Given** an empty diagram, **When** an engineer accesses `diagram["nonexistent"]`, **Then** a KeyError is raised with a helpful error message indicating the label was not found

---

### User Story 2 - Prevent Ambiguous Access (Priority: P2)

When multiple blocks share the same label (either by accident or design), engineers need immediate feedback to avoid accessing the wrong block. The system must detect duplicate labels and fail explicitly (via ValidationError) rather than silently returning an arbitrary block.

**Why this priority**: This prevents subtle bugs where an engineer thinks they're accessing one block but actually get another. However, it's lower priority than basic access because diagrams with unique labels are the common case.

**Independent Test**: Can be fully tested by creating a diagram with duplicate labels, attempting to index by the duplicated label, and verifying an appropriate error is raised. Delivers value by preventing ambiguous access scenarios.

**Acceptance Scenarios**:

1. **Given** a diagram with two blocks labeled "plant", **When** an engineer accesses `diagram["plant"]`, **Then** a ValidationError is raised indicating the label appears on multiple blocks
2. **Given** a diagram with three blocks all labeled "sensor", **When** an engineer accesses `diagram["sensor"]`, **Then** a ValidationError is raised with a count of how many blocks share the label
3. **Given** a diagram with blocks labeled "A", "B", and two blocks labeled "C", **When** an engineer accesses `diagram["A"]`, **Then** block "A" is returned successfully (no error, since "A" is unique)

---

### User Story 3 - Update Parameters via Block Objects (Priority: P3)

Engineers who retrieve blocks via label indexing should be able to update parameters naturally using methods on the block object, without accessing internal block IDs. This reduces boilerplate and prevents confusion about direct attribute assignment (which doesn't sync to widgets).

**Why this priority**: This completes the ergonomic API story started by label indexing. While label indexing (P1) is functional alone, parameter updates remain awkward without this enhancement. Lower priority than duplicate detection (P2) because users can still update parameters using IDs.

**Independent Test**: Can be fully tested by retrieving a block via label, calling `block.set_parameter()`, and verifying the parameter updated in both the block and the diagram's widget state. Delivers value by making parameter updates feel natural and object-oriented.

**Acceptance Scenarios**:

1. **Given** a diagram with a block labeled "plant", **When** an engineer calls `diagram["plant"].set_parameter("K", 10.0)`, **Then** the parameter is updated in the block and synced to the widget
2. **Given** a block retrieved from a diagram, **When** an engineer calls `diagram.update_block_parameter(block, "K", 10.0)`, **Then** the parameter is updated (accepting Block objects, not just IDs)
3. **Given** a block not yet added to a diagram, **When** an engineer calls `block.set_parameter("K", 5.0)`, **Then** a RuntimeError is raised indicating the block is not attached
4. **Given** a block from a deleted diagram, **When** an engineer calls `block.set_parameter("K", 5.0)`, **Then** a RuntimeError is raised indicating the parent diagram no longer exists

---

### Edge Cases

- What happens when a block has no label (label is None or empty string)?
  - Index access should skip blocks without labels, treat as non-matching
  - Attempting `diagram[""]` (empty string) should raise KeyError
- What happens when indexing with non-string keys?
  - Attempting `diagram[None]`, `diagram[123]`, or any non-string should raise TypeError with a message indicating the expected and actual types
- What happens when the diagram is empty?
  - Any index access should raise KeyError with appropriate message
- What happens if label contains special characters (spaces, quotes, brackets)?
  - Should work correctly since labels are stored as strings
  - No special escaping needed for the indexing syntax
- What happens when accessing a label that exists but the block was recently deleted?
  - KeyError should be raised (diagram reflects current state)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support indexing into a Diagram object using bracket notation with a string label (e.g., `diagram["label"]`)
- **FR-002**: System MUST raise a TypeError when the index key is not a string, with a message indicating the expected type and the actual type received
- **FR-003**: System MUST return the Block object whose label attribute matches the provided string exactly (case-sensitive match)
- **FR-004**: System MUST raise a KeyError when the provided label does not match any block in the diagram
- **FR-005**: System MUST raise a ValidationError when the provided label matches multiple blocks in the diagram
- **FR-006**: System MUST skip blocks with None or empty string labels when searching for matches
- **FR-007**: KeyError messages MUST include the requested label to aid debugging
- **FR-008**: ValidationError messages for duplicate labels MUST include the label, the count of matching blocks, and the list of block IDs with that label
- **FR-009**: Block objects MUST provide a `set_parameter(param_name, value)` method that updates parameters and syncs to parent diagram
- **FR-010**: `set_parameter()` MUST raise RuntimeError if the block is not attached to a diagram
- **FR-011**: `update_block_parameter()` MUST accept Block objects in addition to string IDs (backward compatible enhancement)
- **FR-012**: Block objects MUST maintain a reference to their parent diagram using weak references to avoid circular reference issues

### Key Entities

- **Diagram**: Container for blocks and connections. Supports label-based indexing via `__getitem__` method and accepts Block objects in `update_block_parameter()`.
- **Block**: Individual diagram element with optional label attribute. Maintains weak reference to parent diagram and provides `set_parameter()` method for ergonomic parameter updates.
- **ValidationError**: Existing exception (from diagram.py) reused to indicate duplicate labels during index access.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Engineers can access any uniquely labeled block in a diagram using bracket notation in under 5 lines of code (typically 1 line: `block = diagram["label"]`)
- **SC-002**: All attempts to access duplicate labels result in an explicit error with actionable information (label name and count/list of duplicates)
- **SC-003**: 100% of KeyError exceptions for missing labels include the requested label in the error message
- **SC-004**: Label-based indexing completes in constant time O(1) for diagrams with up to 1000 blocks (assuming internal dictionary-based lookup)
- **SC-005**: Engineers can update block parameters via block objects in a single natural statement (e.g., `diagram["plant"].set_parameter("K", 5.0)`)
- **SC-006**: Parameter updates via `set_parameter()` sync correctly to diagram widget state 100% of the time
- **SC-007**: Attempting to update parameters on orphaned blocks (not in diagram) fails with clear RuntimeError message 100% of the time
