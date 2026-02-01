# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for graph pruning algorithms."""

import pytest
from lynx import Diagram
from lynx.conversion.graph_pruning import (
    _build_connection_graph,
    _dfs_forward,
    _dfs_backward,
    _find_reachable_blocks,
)


class TestConnectionGraphBuilding:
    """Tests for connection graph construction."""

    def test_simple_chain(self):
        """Test graph building for A → B → C chain."""
        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "C", "in")

        forward, backward = _build_connection_graph(diagram)

        assert forward["A"] == ["B"]
        assert forward["B"] == ["C"]
        assert forward["C"] == []
        assert backward["A"] == []
        assert backward["B"] == ["A"]
        assert backward["C"] == ["B"]


class TestForwardDFS:
    """Tests for forward depth-first search."""

    def test_simple_chain_forward(self):
        """Test forward DFS on A → B → C."""
        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "C", "in")

        forward, _ = _build_connection_graph(diagram)
        block_a = diagram.get_block("A")
        reachable = _dfs_forward(forward, block_a.id, set())

        assert reachable == {"A", "B", "C"}


class TestBackwardDFS:
    """Tests for backward depth-first search."""

    def test_simple_chain_backward(self):
        """Test backward DFS on A → B → C."""
        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "C", "in")

        _, backward = _build_connection_graph(diagram)
        block_c = diagram.get_block("C")
        reachable = _dfs_backward(backward, block_c.id, set())

        assert reachable == {"A", "B", "C"}


class TestCycleHandling:
    """Tests for cycle detection and handling."""

    def test_forward_dfs_with_cycle(self):
        """Test forward DFS terminates safely with A → B → C → A cycle."""
        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "C", "in")
        diagram.add_connection("c3", "C", "out", "A", "in")

        forward, _ = _build_connection_graph(diagram)
        block_a = diagram.get_block("A")
        reachable = _dfs_forward(forward, block_a.id, set())

        assert reachable == {"A", "B", "C"}  # Should not infinite loop


class TestReachableBlocks:
    """Tests for bidirectional reachability analysis."""

    def test_intersection_simple_chain(self):
        """Test intersection for A → B → C."""
        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "C", "in")

        block_a = diagram.get_block("A")
        block_c = diagram.get_block("C")
        path_blocks = _find_reachable_blocks(diagram, block_a, block_c)

        assert path_blocks == {"A", "B", "C"}


class TestInternalFeedbackDetection:
    """Tests for internal feedback loop preservation (US2)."""

    def test_feedback_block_in_both_reachable_sets(self):
        """Test that feedback blocks are in both forward and backward reachable sets."""
        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        # Create feedback: A → B → C → A
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "C", "in")
        diagram.add_connection("c3", "C", "out", "A", "in")  # Feedback

        block_a = diagram.get_block("A")
        block_c = diagram.get_block("C")

        # Find reachable blocks from A to C
        path_blocks = _find_reachable_blocks(diagram, block_a, block_c)

        # All three blocks should be included (internal loop)
        assert path_blocks == {"A", "B", "C"}


class TestDiagramPruning:
    """Tests for block removal and pruning."""

    def test_prune_diagram_removes_unrelated_blocks(self):
        """Test pruning removes blocks not in path_blocks set."""
        from lynx.conversion.graph_pruning import prune_diagram

        diagram = Diagram()
        diagram.add_block("gain", "A", K=1.0)
        diagram.add_block("gain", "B", K=2.0)
        diagram.add_block("gain", "C", K=3.0)
        diagram.add_block("gain", "D", K=4.0)  # Unrelated
        diagram.add_connection("c1", "A", "out", "B", "in")
        diagram.add_connection("c2", "B", "out", "C", "in")

        # Keep only A, B, C (remove D)
        path_blocks = {"A", "B", "C"}
        pruned = prune_diagram(diagram, path_blocks)

        # Should only have A, B, C
        block_ids = {block.id for block in pruned.blocks}
        assert block_ids == {"A", "B", "C"}
        assert pruned.get_block("D") is None
