<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: IOMarker LaTeX Rendering

**Feature Branch**: `014-iomarker-latex-rendering`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "Modify the IOMarker design to follow the LaTeX-rendering content style of the other blocks. First, remove the displayed Input/Output content in the block (this is obvious from the visual context). Then remove the Type: dialog from the parameter panel. Then, support a "render custom block contents" checkbox + LaTeX entry field in the parameter panel, just as in the other blocks. By default the block should display a number corresponding to the index of the input (starting at 0), though as for the other blocks, this should be overridden with the rendered LaTeX if the panel box is checked. To support the input/output indexing, we'll also have to add a new parameter to IOMarker that tracks the index of the input or output, along with logic to the diagram that returns a ValidationError if there are duplicate port indices for the same type (e.g. two inputs identified as 0) or if the indices aren't the integers up to the number of ports (e.g. two inputs identified as 0 and 3). An alternative design for the indexing would be to follow Simulink, which automatically renumbers indices, so if there are inputs 0, 1, 2, and input 2 is re-indexed to 0 via the parameter panel, then 0->1 and 1->2, with out-of-range indices automatically numbered to the last available index. I'm open to either design and will defer to your recommendation based on UX best practices and implementation complexity."

## Clarifications

### Session 2026-01-17

- Q: When loading an existing diagram with IOMarkers that have no `index` parameter (created before this feature), how should indices be assigned? → A: Block ID alphabetical order (e.g., "input1" < "input2" < "ref")
- Q: When the "Render custom block contents" checkbox is enabled but the LaTeX expression field is left empty, what should the block display? → A: Display the index (same as unchecked)
- Q: When markers are added/deleted rapidly in sequence, how should the system handle renumbering updates? → A: Immediate renumbering after each operation (real-time updates)
- Q: Should there be a maximum character length or complexity limit for custom LaTeX expressions? → A: No explicit limit - follow existing block pattern (rely on LaTeXRenderer auto-scaling and error handling)
- Q: Should the `label` parameter (for python-control export) and `index` parameter (for visual ordering) have any relationship? → A: Completely independent (label for export, index for visual ordering)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Index Display (Priority: P1)

Users can see the port index number (0, 1, 2, ...) displayed inside IOMarker blocks by default, providing clear visual identification of input/output signal ordering without needing to open a parameter panel.

**Why this priority**: This is the foundational visual change that makes IOMarkers consistent with other blocks and provides immediate value. Without this, the feature cannot function.

**Independent Test**: Can be fully tested by creating a diagram with multiple input and output markers, verifying that each displays its correct index (0-based) by default, and delivers immediate visual clarity about signal ordering.

**Acceptance Scenarios**:

1. **Given** a diagram with 3 InputMarkers, **When** the markers are created, **Then** they display indices 0, 1, 2 inside the blocks
2. **Given** a diagram with 2 OutputMarkers, **When** the markers are created, **Then** they display indices 0, 1 inside the blocks
3. **Given** a diagram with mixed InputMarkers and OutputMarkers, **When** viewing the diagram, **Then** inputs are numbered independently from outputs (input 0, input 1, output 0, output 2)
4. **Given** an existing IOMarker, **When** another marker of the same type is added, **Then** the new marker gets the next available index automatically
5. **Given** IOMarkers created before this feature, **When** the diagram is loaded, **Then** indices are automatically assigned based on block ID alphabetical order (deterministic and reproducible)

---

### User Story 2 - Custom LaTeX Override (Priority: P2)

Users can override the default index display with custom LaTeX expressions (e.g., "r", "θ", "ẋ") through a parameter panel checkbox and text field, matching the pattern used in Gain, TransferFunction, and StateSpace blocks.

**Why this priority**: Enables semantic labeling but depends on P1's index display infrastructure. Users can productively use P1 alone, but P2 adds professional polish.

**Independent Test**: Can be tested by selecting an IOMarker, enabling "Render custom block contents" checkbox, entering LaTeX expressions, and verifying the block displays the custom LaTeX instead of the index.

**Acceptance Scenarios**:

1. **Given** an IOMarker displaying index "0", **When** user checks "Render custom block contents" and enters `r`, **Then** the block displays "r" instead of "0"
2. **Given** custom LaTeX enabled with value `\theta`, **When** user unchecks the checkbox, **Then** the block reverts to displaying the index
3. **Given** invalid LaTeX expression entered, **When** user applies the change, **Then** the block displays "Invalid LaTeX" placeholder without crashing
4. **Given** custom LaTeX enabled, **When** user changes the expression, **Then** the block updates in real-time to show the new LaTeX rendering
5. **Given** a diagram saved with custom LaTeX on IOMarkers, **When** the diagram is reloaded, **Then** the custom LaTeX persists and renders correctly
6. **Given** custom LaTeX checkbox enabled with empty LaTeX field, **When** viewing the block, **Then** the block displays the index (graceful degradation)

---

### User Story 3 - Manual Index Control with Automatic Renumbering (Priority: P3)

Users can manually set the index of an IOMarker through the parameter panel, and the system automatically renumbers other markers to maintain a valid sequence (0, 1, 2, ..., N-1) without showing errors, following Simulink's approach.

**Why this priority**: Provides advanced control for specific use cases but most users will rely on automatic indexing from P1. Automatic renumbering eliminates frustrating validation errors and ensures system always maintains valid state.

**Independent Test**: Can be tested by manually setting marker indices through the parameter panel and verifying other markers automatically renumber to avoid conflicts and gaps.

**Acceptance Scenarios**:

1. **Given** 3 InputMarkers with indices 0, 1, 2, **When** user changes index 2 to 0, **Then** old index 0 shifts to 1, old index 1 shifts to 2, and the changed marker takes index 0
2. **Given** 3 InputMarkers with indices 0, 1, 2, **When** user changes index 0 to 2, **Then** old index 1 shifts to 0, old index 2 shifts to 1, and the changed marker takes index 2
3. **Given** an InputMarker with index 2 and an OutputMarker with index 2, **When** viewing the diagram, **Then** both keep index 2 (different marker types are independent sequences)
4. **Given** multiple markers with indices 0, 1, 2, **When** user deletes marker with index 1, **Then** the system automatically renumbers index 2 to index 1 (cascade down)
5. **Given** markers with indices 0, 1, 2, **When** user adds a new marker, **Then** it automatically gets index 3

---

### Edge Cases

- What happens when a diagram with 5 InputMarkers is loaded and one marker has index 10 (gap in sequence)? → Automatically fixed on load per FR-014
- How does the system handle IOMarkers created before this feature (no index parameter exists)? → Assigned via block ID alphabetical order per FR-013
- What happens when custom LaTeX is enabled but the field is left empty? → Displays index (graceful degradation) per FR-008
- How does automatic renumbering behave when markers are added/deleted rapidly in sequence? → Immediate renumbering after each operation (real-time updates)
- What happens if the user manually edits the JSON diagram file to create duplicate indices? → Automatically fixed on load per FR-014
- What happens when user manually sets index to a negative number or non-integer value? → Clamped/treated as 0 per FR-020, FR-021
- How does the system handle renumbering when there are 10+ markers (ensuring no collisions during cascade updates)? → Sequential renumbering algorithm ensures no collisions

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display the marker's index (0-based integer) inside the IOMarker block by default
- **FR-002**: System MUST render index numbers using the same LaTeX rendering component used by other blocks (LaTeXRenderer)
- **FR-003**: System MUST remove the "Input/Output" text currently displayed inside IOMarker blocks
- **FR-004**: System MUST remove the "Type" dropdown from the IOMarker parameter panel (marker type is visually obvious from port orientation)
- **FR-005**: System MUST add a "Render custom block contents" checkbox to the IOMarker parameter panel
- **FR-006**: System MUST add a LaTeX expression text field to the parameter panel (visible only when checkbox is enabled, no character limit to match existing block behavior)
- **FR-007**: System MUST display custom LaTeX content when the checkbox is enabled and LaTeX field is non-empty, overriding the default index display
- **FR-008**: System MUST display the index when custom LaTeX checkbox is enabled but LaTeX field is empty (graceful degradation)
- **FR-009**: System MUST revert to displaying the index when the custom LaTeX checkbox is disabled
- **FR-010**: System MUST persist the custom LaTeX setting and value in diagram JSON files
- **FR-011**: System MUST add an `index` parameter to IOMarker blocks in the Python backend
- **FR-012**: System MUST maintain InputMarker and OutputMarker indices as independent sequences (both can have index 0, 1, 2, etc.)
- **FR-013**: System MUST automatically assign indices to IOMarkers that don't have an index parameter using block ID alphabetical order (backward compatibility)
- **FR-014**: System MUST automatically fix invalid index configurations on diagram load (duplicates, gaps, out-of-range values)
- **FR-015**: System MUST display "Invalid LaTeX" placeholder when LaTeX syntax is invalid
- **FR-016**: System MUST add a manual "Index" field to the parameter panel for users to set the index explicitly
- **FR-017**: System MUST auto-scale LaTeX content to fit within block boundaries using the existing LaTeXRenderer component
- **FR-018**: System MUST automatically renumber markers when a marker is deleted (cascade indices higher than deleted index down by 1)
- **FR-019**: System MUST automatically renumber markers when a marker's index is manually changed (shift conflicting markers to maintain valid sequence 0...N-1)
- **FR-020**: System MUST clamp out-of-range manual index values to valid range [0, N-1] where N is the number of markers of that type
- **FR-021**: System MUST treat non-integer index values as 0 and trigger automatic renumbering
- **FR-022**: System MUST ensure indices always form a complete sequence from 0 to N-1 after any add/delete/change operation
- **FR-023**: System MUST perform renumbering immediately after each add/delete/change operation (real-time updates, no debouncing or batching)
- **FR-024**: System MUST maintain `label` and `index` parameters as completely independent (label for python-control export, index for visual ordering)

### Key Entities

- **IOMarker Block**: Represents input/output boundary markers with attributes:
  - `index`: 0-based integer indicating position in the input/output sequence (new, automatically managed, used for visual display ordering)
  - `custom_latex`: Optional LaTeX string for custom display content (new)
  - `marker_type`: "input" or "output" (existing)
  - `label`: Signal name used for python-control export (existing, completely independent from `index`)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify input/output signal ordering by glancing at IOMarker blocks without opening parameter panels
- **SC-002**: IOMarker blocks visually match the design consistency of Gain, TransferFunction, and StateSpace blocks (LaTeX rendering, auto-scaling)
- **SC-003**: Parameter panel complexity is reduced by 1 field (Type dropdown removed)
- **SC-004**: Users can create custom-labeled IOMarkers (e.g., "r", "θ") in under 10 seconds using the checkbox and text field
- **SC-005**: Users can manually reorder markers without encountering validation errors (automatic renumbering maintains valid state)
- **SC-006**: Existing diagrams without index parameters load successfully with automatically assigned indices
- **SC-007**: Diagrams with invalid index configurations (duplicates, gaps) automatically fix themselves on load
- **SC-008**: Custom LaTeX rendering matches the quality and performance of other blocks (<50ms per block for 50-block diagrams)

## Assumptions

- **A-001**: The existing LaTeXRenderer component can handle LaTeX expressions of any length (no explicit character limit, matching existing Gain/TransferFunction/StateSpace block behavior)
- **A-002**: IOMarker blocks are less frequently used than other blocks, so automatic index assignment and renumbering performance is not critical
- **A-003**: Users understand 0-based indexing from programming/engineering contexts
- **A-004**: Users are familiar with Simulink-style automatic renumbering behavior where index changes cascade to other markers
- **A-005**: For backward compatibility with existing diagrams, indices will be assigned based on block ID alphabetical order (deterministic and reproducible across loads)
- **A-006**: Automatic renumbering during rapid editing (multiple adds/deletes) will not cause noticeable performance issues for diagrams with <100 markers

## Dependencies

- **D-001**: Existing LaTeXRenderer component (js/src/blocks/shared/components/LaTeXRenderer.tsx)
- **D-002**: Existing useCustomLatex hook (js/src/blocks/shared/hooks/useCustomLatex.ts)
- **D-003**: Pydantic schemas for block serialization/deserialization
- **D-004**: Diagram add_block/delete_block/update_block_parameter methods for triggering automatic renumbering

## Design Decisions

### Automatic Renumbering (Simulink-Style)

**Decision**: Use automatic renumbering for all index changes instead of validation errors.

**Rationale**: Following Simulink's approach, the system automatically maintains valid index sequences (0, 1, 2, ..., N-1) by renumbering markers when needed. This eliminates validation errors and provides a frictionless UX.

**Behavior**:
- **Deletion**: When a marker is deleted (e.g., delete index 1 from [0, 1, 2]), higher indices cascade down (2→1)
- **Manual change down**: When user changes index to a lower value (e.g., change 2→0), existing markers shift up (0→1, 1→2)
- **Manual change up**: When user changes index to a higher value (e.g., change 0→2), middle markers shift down (1→0, 2→1)
- **Addition**: New markers automatically get the next available index (e.g., with [0, 1, 2], new marker gets 3)
- **Load invalid diagram**: Markers with duplicates/gaps are automatically renumbered on load

**Advantages**:
- No validation errors to frustrate users
- System always maintains valid state automatically
- Matches familiar Simulink behavior
- Simpler implementation (no validation infrastructure needed)
