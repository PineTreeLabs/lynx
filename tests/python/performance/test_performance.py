# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Performance tests for Lynx widget.

Verifies that validation and operations meet performance targets.
"""

import time

from lynx.diagram import Diagram
from lynx.validation import validate_diagram


def test_validation_performance_50_blocks():
    """Test that validation completes in <100ms for 50+ blocks.

    Creates a chain of 52 blocks: Input → 50 Gains → Output
    This tests validation performance with a realistic control system size.
    """
    diagram = Diagram()

    # Add input marker
    input_block = diagram.add_block("io_marker", "input1", marker_type="input")
    prev_block_id = input_block.id

    # Add 50 gain blocks in series
    for i in range(50):
        block_id = f"gain{i + 1}"
        diagram.add_block("gain", block_id, K=1.0)

        # Connect previous block to current gain
        conn_id = f"c{i + 1}"
        diagram.add_connection(conn_id, prev_block_id, "out", block_id, "in")
        prev_block_id = block_id

    # Add output marker
    diagram.add_block("io_marker", "output1", marker_type="output")
    diagram.add_connection("c51", prev_block_id, "out", "output1", "in")

    # Verify diagram structure
    assert len(diagram.blocks) == 52, f"Expected 52 blocks, got {len(diagram.blocks)}"
    assert len(diagram.connections) == 51, (
        f"Expected 51 connections, got {len(diagram.connections)}"
    )

    # Measure validation time
    start_time = time.perf_counter()
    result = validate_diagram(diagram)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    # Verify validation passes
    assert result.is_valid, f"Validation failed: {result.errors}"
    assert len(result.warnings) == 0, f"Unexpected warnings: {result.warnings}"

    # Verify performance target: <100ms
    print(f"\n✓ Validation of 52 blocks completed in {elapsed_ms:.2f}ms")
    assert elapsed_ms < 100, f"Validation took {elapsed_ms:.2f}ms (target: <100ms)"


def test_validation_performance_100_blocks():
    """Test validation scales well to 100+ blocks.

    Stress test with 102 blocks (Input → 100 Gains → Output).
    Target: <200ms for 100+ blocks.
    """
    diagram = Diagram()

    # Add input
    input_block = diagram.add_block("io_marker", "input1", marker_type="input")
    prev_block_id = input_block.id

    # Add 100 gain blocks
    for i in range(100):
        block_id = f"gain{i + 1}"
        diagram.add_block("gain", block_id, K=0.99)
        diagram.add_connection(f"c{i + 1}", prev_block_id, "out", block_id, "in")
        prev_block_id = block_id

    # Add output
    diagram.add_block("io_marker", "output1", marker_type="output")
    diagram.add_connection("c101", prev_block_id, "out", "output1", "in")

    # Verify structure
    assert len(diagram.blocks) == 102
    assert len(diagram.connections) == 101

    # Measure validation time
    start_time = time.perf_counter()
    result = validate_diagram(diagram)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    # Verify validation passes
    assert result.is_valid

    # Performance target: <200ms for 100 blocks
    print(f"\n✓ Validation of 102 blocks completed in {elapsed_ms:.2f}ms")
    assert elapsed_ms < 200, (
        f"Validation took {elapsed_ms:.2f}ms for 100 blocks (target: <200ms)"
    )


def test_add_block_performance():
    """Test that adding blocks is fast (<1ms per block)."""
    diagram = Diagram()

    # Measure time to add 50 blocks
    start_time = time.perf_counter()
    for i in range(50):
        diagram.add_block("gain", f"gain{i + 1}", K=1.0)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000
    per_block_ms = elapsed_ms / 50

    assert len(diagram.blocks) == 50

    print(f"\n✓ Added 50 blocks in {elapsed_ms:.2f}ms ({per_block_ms:.3f}ms per block)")
    assert elapsed_ms < 50, (
        f"Adding 50 blocks took {elapsed_ms:.2f}ms (should be <50ms)"
    )


def test_connection_performance():
    """Test that adding connections is fast."""
    diagram = Diagram()

    # Create 50 blocks first
    for i in range(50):
        diagram.add_block("gain", f"gain{i + 1}", K=1.0)

    # Measure time to connect them in series
    start_time = time.perf_counter()
    for i in range(49):
        source_id = f"gain{i + 1}"
        target_id = f"gain{i + 2}"
        conn_id = f"c{i + 1}"
        diagram.add_connection(conn_id, source_id, "out", target_id, "in")
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000
    per_connection_ms = elapsed_ms / 49

    assert len(diagram.connections) == 49

    print(
        f"\n✓ Added 49 connections in {elapsed_ms:.2f}ms "
        f"({per_connection_ms:.3f}ms per connection)"
    )
    assert elapsed_ms < 50, (
        f"Adding connections took {elapsed_ms:.2f}ms (should be <50ms)"
    )


def test_serialization_performance():
    """Test that save/load operations are fast (<1 second)."""
    import os
    import tempfile

    diagram = Diagram()

    # Create moderately complex diagram (30 blocks)
    input_block = diagram.add_block("io_marker", "input1", marker_type="input")
    prev_id = input_block.id

    for i in range(28):
        block_id = f"gain{i + 1}"
        diagram.add_block("gain", block_id, K=0.95)
        diagram.add_connection(f"c{i + 1}", prev_id, "out", block_id, "in")
        prev_id = block_id

    diagram.add_block("io_marker", "output1", marker_type="output")
    diagram.add_connection("c29", prev_id, "out", "output1", "in")

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        # Test save performance
        start_time = time.perf_counter()
        diagram.save(temp_path)
        save_time = (time.perf_counter() - start_time) * 1000

        # Test load performance
        start_time = time.perf_counter()
        loaded = Diagram.load(temp_path)
        load_time = (time.perf_counter() - start_time) * 1000

        # Verify correctness
        assert len(loaded.blocks) == 30
        assert len(loaded.connections) == 29

        # Performance targets: <1000ms each
        print(
            f"\n✓ Save: {save_time:.2f}ms, Load: {load_time:.2f}ms (30-block diagram)"
        )
        assert save_time < 1000, f"Save took {save_time:.2f}ms (target: <1000ms)"
        assert load_time < 1000, f"Load took {load_time:.2f}ms (target: <1000ms)"

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_undo_redo_performance():
    """Test that undo/redo operations are fast."""
    diagram = Diagram()

    # Perform 20 add operations
    for i in range(20):
        diagram.add_block("gain", f"gain{i + 1}", K=1.0)

    assert len(diagram.blocks) == 20

    # Test undo performance (20 undos)
    start_time = time.perf_counter()
    for _ in range(20):
        diagram.undo()
    undo_time = (time.perf_counter() - start_time) * 1000

    assert len(diagram.blocks) == 0

    # Test redo performance (20 redos)
    start_time = time.perf_counter()
    for _ in range(20):
        diagram.redo()
    redo_time = (time.perf_counter() - start_time) * 1000

    assert len(diagram.blocks) == 20

    # Performance targets: <100ms for 20 operations
    print(f"\n✓ Undo: {undo_time:.2f}ms, Redo: {redo_time:.2f}ms (20 operations each)")
    assert undo_time < 100, f"20 undos took {undo_time:.2f}ms (target: <100ms)"
    assert redo_time < 100, f"20 redos took {redo_time:.2f}ms (target: <100ms)"


def test_complex_diagram_validation():
    """Test validation on a complex realistic diagram.

    Creates a PID-style controller with multiple paths to test
    performance on more complex graph structures.
    """
    diagram = Diagram()

    # Input and error sum
    diagram.add_block("io_marker", "input", marker_type="input")
    diagram.add_block("sum", "error_sum", signs=["+", "-", "|"])
    diagram.add_connection("c1", "input", "out", "error_sum", "in1")

    # Three parallel PID paths
    diagram.add_block("gain", "P", K=2.0)  # Proportional
    diagram.add_block(
        "transfer_function", "I", numerator=[0.5], denominator=[1, 0]
    )  # Integral
    diagram.add_block(
        "transfer_function", "D", numerator=[0.1, 0], denominator=[0.01, 1]
    )  # Derivative

    # Connect error to PID components
    diagram.add_connection("c2", "error_sum", "out", "P", "in")
    diagram.add_connection("c3", "error_sum", "out", "I", "in")
    diagram.add_connection("c4", "error_sum", "out", "D", "in")

    # PID sum
    diagram.add_block("sum", "pid_sum", signs=["+", "+", "+"])
    diagram.add_connection("c5", "P", "out", "pid_sum", "in1")
    diagram.add_connection("c6", "I", "out", "pid_sum", "in2")
    diagram.add_connection("c7", "D", "out", "pid_sum", "in3")

    # Plant
    diagram.add_block(
        "transfer_function", "plant", numerator=[1], denominator=[1, 2, 1]
    )
    diagram.add_connection("c8", "pid_sum", "out", "plant", "in")

    # Output and feedback
    diagram.add_block("io_marker", "output", marker_type="output")
    diagram.add_connection("c9", "plant", "out", "output", "in")
    diagram.add_block("gain", "feedback", K=1.0)
    diagram.add_connection("c10", "plant", "out", "feedback", "in")
    diagram.add_connection("c11", "feedback", "out", "error_sum", "in2")

    # 9 blocks total
    assert len(diagram.blocks) == 9
    assert len(diagram.connections) == 11

    # Measure validation
    start_time = time.perf_counter()
    result = validate_diagram(diagram)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Should pass (has transfer functions in feedback)
    assert result.is_valid

    print(f"\n✓ Complex PID diagram validation: {elapsed_ms:.2f}ms")
    assert elapsed_ms < 50, (
        f"Complex validation took {elapsed_ms:.2f}ms (should be <50ms)"
    )
