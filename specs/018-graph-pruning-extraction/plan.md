<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Implementation Plan: Graph-Based Subsystem Extraction

**Branch**: `018-graph-pruning-extraction` | **Date**: 2026-02-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/018-graph-pruning-extraction/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement graph-based pruning to fix subsystem extraction in complex diagrams with nested feedback loops. Currently, python-control's interconnect includes ALL blocks when extracting transfer functions, causing unwanted state coupling from unrelated downstream/upstream dynamics. The solution uses graph analysis to identify the minimal set of blocks on paths between source and destination signals, then builds the interconnect with only those blocks. This ensures extracted transfer functions contain only the relevant dynamics without extraneous coupling.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+ (existing Lynx requirement)
**Primary Dependencies**: python-control 0.10+ (existing), no new dependencies required
**Storage**: N/A (operates on in-memory Diagram objects)
**Testing**: pytest (existing test infrastructure)
**Target Platform**: Cross-platform (same as Lynx - Linux, macOS, Windows)
**Project Type**: Single Python package (library extension to existing lynx package)
**Performance Goals**: <500ms extraction time for 50-block diagrams, <1s for 100-block diagrams
**Constraints**: Must handle cycles (feedback loops) without infinite recursion, must be deterministic
**Scale/Scope**: Typical control diagrams (10-100 blocks), graceful degradation up to 500 blocks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity Over Features
✅ **PASS**: Feature directly addresses a core bug in subsystem extraction. Graph pruning is the minimal solution - simpler alternatives (direct block access) don't solve the general case of multi-block subsystem extraction. No feature bloat.

### Principle II: Python Ecosystem First
✅ **PASS**: Extends existing python-control integration. No vendor lock-in. Users continue using standard python-control API (`get_ss()`, `get_tf()`). Implementation uses native Python graph algorithms (no external graph libraries).

### Principle III: Test-Driven Development
✅ **PASS**: Specification explicitly requires "a clear failing test case (not the complex cascaded.json, but a minimal example that currently does not work) and resolve it using the graph analysis algorithm." TDD workflow enforced.

### Principle IV: Clean Separation of Concerns
✅ **PASS**: Graph analysis logic isolated in new module (`src/lynx/conversion/graph_pruning.py`). Diagram class and conversion logic remain UI-independent. No presentation layer coupling.

### Principle V: User Experience Standards
✅ **PASS**: Performance requirement (<500ms for 50 blocks) is explicit. Feature makes existing API work correctly for complex diagrams without changing user interface. Speed and correctness prioritized.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/lynx/conversion/
├── __init__.py
├── block_converters.py      # Existing
├── interconnect.py           # Existing
├── signal_extraction.py      # Modified - integrate pruning
└── graph_pruning.py          # NEW - graph analysis and pruning logic

tests/python/
├── unit/
│   └── test_graph_pruning.py          # NEW - unit tests for graph algorithms
└── integration/
    └── test_pruned_extraction.py      # NEW - integration tests with diagrams
```

**Structure Decision**: Single project structure (existing Lynx package). New module `graph_pruning.py` encapsulates all graph analysis logic. Existing `signal_extraction.py` modified to call pruning before building interconnect. Tests follow existing pattern (unit for algorithms, integration for end-to-end workflows).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution principles satisfied.

---

## Phase 0: Research & Decision Log

**Status**: ✅ Complete

### Key Decisions

#### 1. Graph Traversal Algorithm: DFS over BFS
**Decision**: Use Depth-First Search for path finding  
**Rationale**: 
- Lower memory overhead (O(depth) vs O(breadth))
- Simpler cycle handling with visited set
- Better cache locality for deep exploration
- Both are O(V+E), but DFS has lower constant factors for typical diagrams

**Alternatives Considered**:
- BFS: Higher memory usage, no significant benefit for path finding
- NetworkX library: Adds heavyweight dependency, overkill for simple graph operations

#### 2. Path Finding Strategy: Bidirectional Reachability
**Decision**: Use intersection of forward and backward reachable sets  
**Rationale**:
- 50-90% reduction in explored nodes vs single-direction search
- O(V+E) complexity vs exponential for full path enumeration
- Only need block set, not individual paths
- Automatically handles parallel paths and feedback loops

**Alternatives Considered**:
- All-paths enumeration: Exponentially many paths in graphs with cycles
- Single-direction DFS: Explores more nodes than necessary

#### 3. Cycle Handling: Automatic via Visited Sets
**Decision**: No explicit cycle detection, rely on DFS visited tracking  
**Rationale**:
- Internal feedback loops automatically preserved (reachable in both directions)
- External feedback loops automatically excluded (fail reachability test)
- Simpler implementation, no special-case logic

**Alternatives Considered**:
- Explicit cycle detection: Unnecessary complexity, already handled by DFS

#### 4. Integration Point: Modify `_prepare_for_extraction()`
**Decision**: Insert pruning step after signal resolution, before injection  
**Rationale**:
- Minimal changes to existing code
- Clear separation of concerns (pruning is self-contained)
- Maintains backward compatibility
- Works with all signal reference patterns

**Alternatives Considered**:
- New top-level API: Requires users to change their code
- Modify interconnect builder: More invasive, harder to test

### Research Documentation

See [research.md](research.md) for detailed analysis including:
- Algorithm complexity analysis
- Python pseudo-code examples
- Performance benchmarks
- Edge case handling strategies

---

## Phase 1: Design Artifacts

**Status**: ✅ Complete

### Generated Artifacts

1. **[data-model.md](data-model.md)**: Entity definitions
   - ConnectionGraph: Adjacency lists for forward/backward traversal
   - ReachabilityResult: Container for bidirectional DFS output
   - PrunedDiagram: Cloned diagram with only path-relevant blocks

2. **[quickstart.md](quickstart.md)**: Test scenarios
   - Scenario 1: Single block extraction (US1-P1)
   - Scenario 2: Internal feedback preservation (US2-P2)
   - Scenario 3: Parallel paths (US3-P3)
   - Edge cases and performance benchmarks

3. **Agent Context**: Updated [CLAUDE.md](../../CLAUDE.md)
   - Added technology: Python 3.11+, python-control 0.10+
   - No new dependencies required

### Architecture Summary

```
Signal Resolution
       ↓
Build ConnectionGraph (adjacency lists)
       ↓
Forward DFS from source  ─┐
                          ├─→ Intersection = minimal block set
Backward DFS from dest  ──┘
       ↓
Clone & Prune Diagram (remove unrelated blocks)
       ↓
Existing Injection & Interconnect Building
       ↓
Extract Transfer Function
```

**Key Files**:
- **New**: `src/lynx/conversion/graph_pruning.py` (all graph analysis logic)
- **Modified**: `src/lynx/conversion/signal_extraction.py` (call pruning before interconnect)
- **Tests**: Unit (`test_graph_pruning.py`), Integration (`test_pruned_extraction.py`)

---

## Phase 2: Ready for Task Generation

**Next Command**: `/speckit.tasks`

The plan is complete. Ready to generate implementation tasks following TDD workflow.

**Expected Task Structure**:
- Phase 1 (Setup): Test infrastructure
- Phase 2 (US1-P1): Single block extraction with minimal test case
- Phase 3 (US2-P2): Internal feedback preservation
- Phase 4 (US3-P3): Parallel paths handling
- Phase 5 (Polish): Edge cases, performance validation, documentation

Each phase will follow RED-GREEN-REFACTOR cycle per Constitution Principle III.
