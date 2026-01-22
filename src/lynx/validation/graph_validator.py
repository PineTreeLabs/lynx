# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Graph-based validation algorithms.

Implements:
- Cycle detection (DFS-based)
- Disconnected block detection
- System completeness checking
"""

from typing import Dict, List, Set

from lynx.diagram import Diagram


def find_cycles(diagram: Diagram) -> List[List[str]]:
    """Find all cycles in the diagram using DFS.

    Args:
        diagram: Diagram to analyze

    Returns:
        List of cycles, where each cycle is a list of block IDs
    """
    # Build adjacency list
    adj: Dict[str, List[str]] = {block.id: [] for block in diagram.blocks}

    for conn in diagram.connections:
        adj[conn.source_block_id].append(conn.target_block_id)

    # DFS to find cycles
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    cycles: List[List[str]] = []
    current_path: List[str] = []

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.add(node)
        current_path.append(node)

        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                # Found a cycle - extract it from current path
                cycle_start = current_path.index(neighbor)
                cycle = current_path[cycle_start:]
                cycles.append(cycle)

        current_path.pop()
        rec_stack.remove(node)

    for block in diagram.blocks:
        if block.id not in visited:
            dfs(block.id)

    return cycles


def find_disconnected_blocks(diagram: Diagram) -> List[str]:
    """Find disconnected blocks or components.

    A block is considered disconnected if it's not part of the main
    connected component containing I/O blocks.

    Args:
        diagram: Diagram to analyze

    Returns:
        List of warning messages about disconnected blocks
    """
    if len(diagram.blocks) == 0:
        return []

    # Build undirected adjacency list (connections go both ways for connectivity)
    adj: Dict[str, Set[str]] = {block.id: set() for block in diagram.blocks}

    for conn in diagram.connections:
        adj[conn.source_block_id].add(conn.target_block_id)
        adj[conn.target_block_id].add(conn.source_block_id)

    # Find all connected components using BFS
    visited: Set[str] = set()
    components: List[Set[str]] = []

    def bfs(start: str) -> Set[str]:
        component: Set[str] = set()
        queue: List[str] = [start]
        component.add(start)

        while queue:
            node = queue.pop(0)
            for neighbor in adj[node]:
                if neighbor not in component:
                    component.add(neighbor)
                    queue.append(neighbor)

        return component

    # Find all components
    for block in diagram.blocks:
        if block.id not in visited:
            component = bfs(block.id)
            visited.update(component)
            components.append(component)

    # If only one component, everything is connected
    if len(components) <= 1:
        return []

    # Find the "main" component (largest, or one with I/O blocks)
    io_blocks = {block.id for block in diagram.blocks if block.type == "io_marker"}

    main_component: Set[str] = set()
    for component in components:
        if component & io_blocks:  # Has I/O blocks
            main_component = component
            break

    # If no component has I/O blocks, use the largest
    if not main_component:
        main_component = max(components, key=len)

    # Report disconnected blocks
    warnings: List[str] = []
    for component in components:
        if component != main_component:
            block_ids = ", ".join(sorted(component))
            warnings.append(f"Disconnected blocks found: {block_ids}")

    return warnings


def check_system_completeness(diagram: Diagram) -> List[str]:
    """Check if system has required I/O blocks.

    A complete system should have at least one input and one output marker.

    Args:
        diagram: Diagram to analyze

    Returns:
        List of warning messages about missing I/O blocks
    """
    warnings: List[str] = []

    # Count I/O markers
    has_input = False
    has_output = False

    for block in diagram.blocks:
        if block.type == "io_marker":
            # Check marker_type parameter
            for param in block._parameters:
                if param.name == "marker_type":
                    if param.value == "input":
                        has_input = True
                    elif param.value == "output":
                        has_output = True

    # Generate warnings
    if not has_input and not has_output:
        msg = (
            "System has no input or output markers. "
            "Add at least one input and one output."
        )
        warnings.append(msg)
    elif not has_input:
        warnings.append(
            "System has no input marker. Add an input to make the system complete."
        )
    elif not has_output:
        warnings.append(
            "System has no output marker. Add an output to make the system complete."
        )

    return warnings
