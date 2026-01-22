<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Research: Python-Control Export

**Feature**: 012-python-control-export
**Date**: 2026-01-15
**Status**: Complete

## Purpose

Document technical research and design decisions for converting Lynx diagrams to python-control `InterconnectedSystem` objects.

---

## Research Question 1: python-control `interconnect()` API Contract

**Question**: What are the exact parameter requirements and conventions for `control.interconnect()`?

**Decision**: Use python-control 0.10.2+ `interconnect()` function with these parameters:
- `systems`: List of subsystem objects (TransferFunction, StateSpace, or IOSystem)
- `connections`: List of `[source_signal, target_signal]` pairs where signals are `'block_name.port_name'`
- `inplist`: List of system input signals (from InputMarker blocks)
- `outlist`: List of system output signals (from OutputMarker blocks)

**Rationale**:
- python-control already in pyproject.toml at version 0.10.2
- Official documentation: https://python-control.readthedocs.io/en/latest/generated/control.interconnect.html
- Signal naming convention `'block.port'` matches Lynx's block_id.port_id structure perfectly
- `summing_junction()` available for Sum blocks (handles sign configuration)

**Alternatives Considered**:
1. **Use lower-level `series()`, `parallel()`, `feedback()` functions**
   - Rejected: Only handles simple topologies, doesn't support complex interconnections
   - `interconnect()` is the general-purpose solution for arbitrary block diagrams
2. **Build custom transfer function composition**
   - Rejected: Reinventing python-control's functionality, violates Constitution Principle II (Python Ecosystem First)
3. **Export to MATLAB format then import to python-control**
   - Rejected: Unnecessary indirection, python-control has direct API

**Implementation Notes**:
- Each Lynx block becomes a named subsystem via `name=block.id` parameter
- All blocks must specify `inputs=[...]` and `outputs=[...]` for signal routing
- Signal negation for Sum block subtraction uses `-` prefix: `'-block1.out'`

---

## Research Question 2: Sum Block Sign Mapping Algorithm

**Question**: How to correctly map Lynx Sum block port IDs (`in1`, `in2`, `in3`) to their corresponding signs (`["+", "-", "|"]`) accounting for skipped `"|"` entries?

**Decision**: Implement quadrant-to-port mapping algorithm:

```python
def get_sign_for_port(sum_block, port_id: str) -> str:
    """Map port ID to its sign, handling skipped '|' entries.

    Sum block signs array: [top, left, bottom] = signs[0], signs[1], signs[2]
    Port IDs are sequential: in1, in2, in3 (only for non-'|' signs)

    Example: signs = ["+", "|", "-"]
    - Creates ports: in1 (top, +), in2 (bottom, -)
    - Mapping: in1 → signs[0], in2 → signs[2]
    """
    signs = sum_block.get_parameter('signs')  # e.g., ["+", "|", "-"]
    port_num = int(port_id[2:])  # "in2" → 2

    # Count non-"|" signs until we reach port_num
    active_count = 0
    for quadrant_idx, sign in enumerate(signs):
        if sign != "|":
            active_count += 1
            if active_count == port_num:
                return sign

    # Should never reach here if port_id is valid
    raise ValueError(f"Invalid port {port_id} for signs {signs}")
```

**Rationale**:
- Lynx Sum blocks use `signs = [top, left, bottom]` with `"|"` meaning "no port"
- Ports are created sequentially (`in1`, `in2`, `in3`) skipping `"|"` positions
- Need reverse mapping: port ID → quadrant index → sign value
- Algorithm: count non-`"|"` signs until reaching port number

**Alternatives Considered**:
1. **Store sign alongside port during creation**
   - Rejected: Would require modifying Port dataclass and all existing serialization
   - Current approach keeps Port simple and derives sign when needed
2. **Pre-compute port-to-sign dictionary in SumBlock.__init__**
   - Rejected: Adds state to block for single use case, violates simplicity
   - On-demand calculation is fast enough (O(3) for 3 quadrants)
3. **Change port IDs to include quadrant info (e.g., `top_in`, `left_in`)**
   - Rejected: Breaking change to existing Sum block API, affects all connections

**Edge Cases**:
- `signs = ["|", "|", "|"]`: Already prevented by SumBlock validation (min 2 active inputs)
- `signs = ["+", "+", "+"]`: Creates `in1`, `in2`, `in3`, all positive
- `signs = ["+", "|", "-"]`: Creates `in1` (top, +), `in2` (bottom, -)

---

## Research Question 3: Validation Strategy for Diagram Completeness

**Question**: What validation checks are needed before export, and in what order should they run?

**Decision**: Implement layered validation with fail-fast behavior:

**Layer 1: System Boundary Validation** (fail-fast)
- FR-011: At least one InputMarker must exist
- FR-012: At least one OutputMarker must exist
- Rationale: No point checking connections if system I/O undefined

**Layer 2: Port Connection Validation** (per-block)
- FR-010: All non-InputMarker input ports must be connected
- Check: Iterate all blocks, for each input port, verify connection exists
- Exception message: "Block '{block_id}' port '{port_id}' is not connected"

**Layer 3: Graph Connectivity Validation** (optional for MVP, document as future enhancement)
- Check for disconnected subgraphs (clusters of blocks not connected to main system)
- Deferred: Spec mentions this (US3 scenario 4) but not marked as required
- Can be added post-MVP if users encounter issues

**Rationale**:
- Fail-fast saves computation time (don't check 50 blocks if no I/O markers)
- Per-block validation provides specific, actionable error messages (FR-013)
- python-control will also validate when building interconnect, but our validation gives better error messages

**Alternatives Considered**:
1. **Let python-control handle all validation**
   - Rejected: python-control errors are cryptic (e.g., "KeyError: 'block1.in'"), violates UX standard (FR-013)
2. **Comprehensive graph analysis before any conversion**
   - Rejected: Over-engineering for MVP, adds latency
   - Simple checks sufficient for 99% of user errors
3. **Warning-based validation (allow incomplete diagrams)**
   - Rejected: python-control will fail anyway, better to fail early with clear message

**Implementation Notes**:
- All validation in `_validate_for_export()` private method
- Raise custom `DiagramExportError` exception (subclass of ValueError)
- Exception message format: "{error_type}: {specific_issue} in block '{block_id}' port '{port_id}'"

---

## Research Question 4: Performance Optimization Strategy

**Question**: How to ensure <100ms export time for 50-block diagrams (SC-003)?

**Decision**: No optimization needed for MVP - linear algorithm is sufficient.

**Analysis**:
- Export algorithm complexity: O(blocks + connections)
  - Block conversion: O(n) where n = number of blocks
  - Connection mapping: O(m) where m = number of connections
  - Validation: O(n + m)
  - Total: O(n + m) ≈ O(n) for typical diagrams (connections ≈ blocks)
- For 50 blocks with ~60 connections (1.2x ratio typical in control systems):
  - Block conversion: 50 iterations × ~1ms = 50ms (mostly python-control object creation)
  - Connection mapping: 60 iterations × ~0.1ms = 6ms
  - Validation: 50 blocks + 60 connections × ~0.1ms = 11ms
  - Total estimated: ~70ms (within 100ms budget)

**Rationale**:
- Linear algorithm is fast enough for target scale
- python-control object creation is the bottleneck, not our code
- Premature optimization violates Constitution Principle I (Simplicity)

**Alternatives Considered**:
1. **Parallel block conversion**
   - Rejected: Added complexity, python-control objects likely not thread-safe
   - 50ms → 25ms gain not worth threading overhead
2. **Caching python-control subsystems per block**
   - Rejected: Lynx diagrams are mutable, cache invalidation complex
   - Export is one-shot operation, caching doesn't help
3. **Lazy validation (validate only on error)**
   - Rejected: Validation overhead ~11ms, not worth complexity

**Performance Monitoring**:
- Add integration test measuring export time for 50-block diagram
- If real-world usage exceeds 100ms, profile and optimize bottlenecks
- Document in risks: "Performance acceptable for MVP, monitor in production"

---

## Research Question 5: Exception Design for Validation Errors

**Question**: What exception types and message formats provide best user experience (FR-013)?

**Decision**: Custom exception hierarchy with structured error messages.

**Exception Types**:
```python
class DiagramExportError(Exception):
    """Base exception for diagram export failures."""
    pass

class ValidationError(DiagramExportError):
    """Raised when diagram validation fails before export."""
    def __init__(self, message: str, block_id: Optional[str] = None,
                 port_id: Optional[str] = None):
        self.block_id = block_id
        self.port_id = port_id
        super().__init__(message)
```

**Message Format**:
- **Unconnected input**: `"Validation failed: Block '{block_id}' input port '{port_id}' is not connected"`
- **Missing InputMarker**: `"Validation failed: Diagram has no InputMarker blocks. Add at least one system input."`
- **Missing OutputMarker**: `"Validation failed: Diagram has no OutputMarker blocks. Add at least one system output."`
- **python-control errors**: Wrap and re-raise with context: `"Export failed: {original_error}. Check block '{block_id}' parameters."`

**Rationale**:
- Structured exceptions allow programmatic error handling (tests can check block_id)
- Clear, actionable messages tell user exactly what to fix (FR-013)
- Consistent format aids debugging and user learning

**Alternatives Considered**:
1. **Generic ValueError with string messages**
   - Rejected: No structure, harder to test, can't extract error details programmatically
2. **Separate exception class per error type**
   - Rejected: Over-engineering, adds boilerplate
   - Single `ValidationError` with optional fields sufficient
3. **Return Result[T, Error] instead of exceptions**
   - Rejected: Not Pythonic, python-control uses exceptions
   - Exception handling is Python ecosystem standard (Principle II)

**Implementation Notes**:
- Define exceptions in `src/lynx/diagram.py` near `to_interconnect()` method
- Validation errors should be catchable for user-friendly error display in widget
- Document exception types in method docstring

---

## Summary of Research Outcomes

| Question | Decision | Impact |
|----------|----------|--------|
| python-control API | Use `interconnect()` with named signals | ✅ Clean, direct mapping |
| Sum block sign mapping | Quadrant-to-port algorithm | ✅ Correct negation handling |
| Validation strategy | Layered fail-fast validation | ✅ Clear error messages |
| Performance | Linear algorithm, no optimization | ✅ <100ms target achievable |
| Exception design | Custom `ValidationError` with structured messages | ✅ User-friendly errors |

**Research Complete**: All technical decisions resolved. Ready for Phase 1 (Design).
