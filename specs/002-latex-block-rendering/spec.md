<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Feature Specification: LaTeX Block Rendering

**Feature Branch**: `002-latex-block-rendering`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "Support LaTeX rendering for block contents. By default the StateSpace block should render the equations "\dot{x} = A x + B u" and "y = C x + D u", TransferFunction should render the polynomial form of the transfer function using appropriately formatted numerical coefficients, and Gain should render an appropriately formatted number. For each of these blocks, there should be a check-box in the parameter panel that says "Render custom block contents" - when enabled, the block should ONLY render the LaTeX provided (not the name of the block type like "Transfer Function" or "State Space")."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Default Mathematical Notation (Priority: P1)

Users can view control system blocks with mathematically formatted default representations that clearly show the underlying equations and parameters, making diagrams more readable and professional.

**Why this priority**: This is the core value proposition - users need to see mathematical notation for standard blocks to understand and communicate control system designs effectively. This must work before custom LaTeX is useful.

**Independent Test**: Can be fully tested by creating a StateSpace block with parameters A, B, C, D and verifying the rendered equations "\dot{x} = Ax + Bu" and "y = Cx + Du" appear with proper LaTeX formatting in symbolic notation. Delivers immediate value by making standard blocks more readable.

**Acceptance Scenarios**:

1. **Given** a StateSpace block exists with matrix parameters, **When** the user views the block on the canvas, **Then** the block displays the equations "\dot{x} = Ax + Bu" and "y = Cx + Du" rendered as formatted mathematical notation using symbolic notation (without expanding matrix values)
2. **Given** a TransferFunction block exists with numerator coefficients [1, 2.5, 0.00123] and denominator coefficients [1, 0.5, 1234], **When** the user views the block on the canvas, **Then** the block displays the transfer function as "$\frac{s^2 + 2.5s + 1.23 \times 10^{-3}}{s^2 + 0.5s + 1.23 \times 10^3}$" with numerical coefficients formatted to 3 significant figures and exponential notation for values outside [0.01, 1000)
3. **Given** a Gain block exists with a gain value of 0.00456, **When** the user views the block on the canvas, **Then** the block displays "$4.56 \times 10^{-3}$" formatted with 3 significant figures in exponential notation
4. **Given** a Gain block exists with a gain value of 123.456, **When** the user views the block on the canvas, **Then** the block displays "123" formatted with 3 significant figures

---

### User Story 2 - Customize Block Display with LaTeX (Priority: P2)

Users can override default block rendering with custom LaTeX expressions to display specialized notation, simplified forms, or domain-specific representations that better communicate their intent.

**Why this priority**: Extends the base functionality to support advanced users who need custom mathematical notation. Depends on P1 infrastructure but adds significant value for power users.

**Independent Test**: Can be fully tested by enabling the "Render custom block contents" checkbox for any block type, entering custom LaTeX (e.g., "K_p + \frac{K_i}{s}"), and verifying only the custom content appears (no block type label). Delivers value for users needing specialized notation.

**Acceptance Scenarios**:

1. **Given** a StateSpace block exists, **When** the user opens the parameter panel and enables the "Render custom block contents" checkbox, **Then** a text input field appears for entering custom LaTeX
2. **Given** the "Render custom block contents" checkbox is enabled and custom LaTeX is entered, **When** the user views the block on the canvas, **Then** only the custom LaTeX content is rendered (the default equations and block type name are not shown)
3. **Given** a TransferFunction block has custom LaTeX enabled, **When** the user disables the "Render custom block contents" checkbox, **Then** the block reverts to displaying the default polynomial form
4. **Given** a Gain block has custom LaTeX enabled, **When** the user enters invalid LaTeX syntax, **Then** the system shows an inline error message below the LaTeX input field and renders the block with a fallback placeholder (e.g., "Invalid LaTeX")
5. **Given** a block exists in a Python diagram, **When** the user sets `block.custom_latex = "K_p + \frac{K_i}{s}"` from Python, **Then** the block renders the custom LaTeX and the UI checkbox reflects the enabled state
6. **Given** a block has custom LaTeX enabled, **When** the user sets `block.custom_latex = None` from Python, **Then** the block reverts to default rendering and the UI checkbox reflects the disabled state

---

### Edge Cases

- When a block has empty or invalid parameters (e.g., non-numeric values in StateSpace matrices), the system shows placeholder text (e.g., "Invalid parameters") and allows custom LaTeX override
- When LaTeX expressions exceed the block's visual boundaries, the system auto-scales the text down to fit within the block
- What happens when custom LaTeX contains syntax errors or unsupported LaTeX commands? (Addressed in FR-011)
- Special characters and escape sequences in LaTeX input are passed through as-is to the LaTeX renderer without preprocessing
- When a block is resized, the LaTeX auto-scales to fit the new boundaries

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: StateSpace blocks MUST render the equations "\dot{x} = Ax + Bu" and "y = Cx + Du" as formatted LaTeX using symbolic notation (without expanding matrix values) by default
- **FR-002**: TransferFunction blocks MUST render the transfer function as a fraction with numerator and denominator polynomials in descending powers of s, using the coefficients as formatted LaTeX by default (e.g., $\frac{s^2 + 3s + 2}{s^3 + 4s^2 + 5s + 6}$)
- **FR-003**: Gain blocks MUST render the gain value as a properly formatted number using LaTeX by default
- **FR-004**: All block types (StateSpace, TransferFunction, Gain) MUST include a "Render custom block contents" checkbox in their parameter panel
- **FR-005**: When "Render custom block contents" is enabled, the block MUST display a text input field for entering custom LaTeX
- **FR-006**: When "Render custom block contents" is enabled and custom LaTeX is provided, the block MUST render ONLY the custom LaTeX content (not the block type name or default equations)
- **FR-007**: When "Render custom block contents" is disabled, the block MUST revert to rendering the default LaTeX representation for that block type
- **FR-008**: StateSpace blocks MUST use symbolic notation (A, B, C, D) rather than expanding numerical matrix values in the default rendering
- **FR-009**: Custom LaTeX content MUST persist when the diagram is saved and reloaded
- **FR-010**: The "Render custom block contents" checkbox state MUST persist when the diagram is saved and reloaded
- **FR-011**: When invalid LaTeX syntax is entered, the system MUST display an inline error message below the LaTeX input field and render the block with a fallback placeholder (e.g., "Invalid LaTeX")
- **FR-012**: When a block has empty or invalid parameters, the system MUST display placeholder text (e.g., "Invalid parameters") in the block and allow custom LaTeX override to function normally
- **FR-013**: The system MUST auto-scale LaTeX content to fit within block boundaries when the rendered content would otherwise overflow
- **FR-014**: The system MUST pass LaTeX input (including special characters and escape sequences) directly to the LaTeX renderer without preprocessing or modification
- **FR-015**: Blocks MUST provide a `custom_latex` property accessible from Python that, when set to a non-empty string, automatically enables custom LaTeX rendering
- **FR-016**: Setting `custom_latex` to `None` or an empty string from Python MUST disable custom rendering and revert the block to its default LaTeX representation
- **FR-017**: The `custom_latex` property MUST be readable, returning the current custom LaTeX string or `None` if custom rendering is disabled
- **FR-018**: Numerical values in TransferFunction and Gain blocks MUST be formatted to 3 significant figures by default
- **FR-019**: Numerical values with magnitude less than 0.01 or greater than or equal to 1000 MUST be displayed in exponential notation
- **FR-020**: The numerical formatting precision and exponential thresholds SHOULD be configurable if feasible, with 3 significant figures and thresholds of 0.01/1000 as defaults

### Key Entities

- **Block**: A visual element representing a control system component (StateSpace, TransferFunction, Gain) with parameters and visual rendering properties
- **Block Parameters**: Numerical or matrix values that define the block's mathematical behavior (A, B, C, D for StateSpace; numerator/denominator coefficients for TransferFunction; gain value for Gain)
- **Custom LaTeX Override**: Optional user-provided LaTeX string that replaces the default block rendering when enabled

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view default LaTeX-rendered content for all three block types (StateSpace, TransferFunction, Gain) without any configuration
- **SC-002**: Users can enable custom LaTeX rendering for any block in under 30 seconds (open panel, check checkbox, enter LaTeX)
- **SC-003**: Custom LaTeX overrides correctly replace default rendering in 100% of cases when enabled
- **SC-004**: Diagrams with LaTeX rendering (both default and custom) save and reload without loss of content or formatting
- **SC-005**: LaTeX rendering improves diagram readability such that users can understand block equations at a glance without opening parameter panels

## Clarifications

### Session 2026-01-04

- Q: What happens when a StateSpace block has empty or invalid matrix parameters (e.g., non-numeric values)? → A: Show placeholder text (e.g., "Invalid parameters") and allow custom LaTeX override
- Q: How does the system handle extremely long LaTeX expressions that exceed the block's visual boundaries? → A: Auto-scale text down to fit within block boundaries
- Q: How does the system handle special characters or escape sequences in LaTeX input? → A: Pass through as-is, LaTeX renderer handles escaping
- Q: Should StateSpace blocks show full matrix notation with numerical values or symbolic notation? → A: Symbolic only, show variable names without expanding matrices (e.g., $\dot{x} = Ax + Bu$)
- Q: What format should TransferFunction blocks use for polynomial display? → A: Standard fraction notation with descending powers (e.g., $\frac{s^2 + 3s + 2}{s^3 + 4s^2 + 5s + 6}$)
- Q: What Python API should be provided for setting custom LaTeX strings programmatically? → A: Block property with getter/setter and auto-enable (e.g., `block.custom_latex = "..."` automatically enables custom rendering, `block.custom_latex = None` reverts to default)
- Q: What precision and formatting should be used for numerical values in TransferFunction and Gain blocks? → A: 3 significant figures by default, exponential notation for |x| < 0.01 or |x| ≥ 1000. Ideally configurable as a parameter, but hardcoded default is acceptable if configurability is challenging

## Assumptions

- The system already has a LaTeX rendering library integrated (e.g., KaTeX, MathJax) or will integrate one as part of implementation
- Block parameter panels already exist and can be extended with new UI elements (checkbox and text input)
- The default LaTeX expressions for each block type follow standard control systems notation conventions
- Users have basic familiarity with LaTeX syntax when using custom rendering (no LaTeX tutorial/help is required in this feature)
- Block type names (e.g., "Transfer Function", "State Space") are currently displayed on blocks but can be conditionally hidden
