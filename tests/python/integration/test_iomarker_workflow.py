# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for IOMarker LaTeX rendering workflow.

Tests the complete end-to-end workflow:
- Create markers with automatic indexing
- Edit custom LaTeX
- Manually change indices with renumbering
- Save and reload diagram
"""

from lynx.diagram import Diagram


def test_full_workflow_create_edit_save_load():
    """T061: Full workflow - create → edit → save → load (TS-006.1).

    Tests complete user workflow with all three user stories:
    1. Create InputMarkers with automatic indexing (US1)
    2. Enable custom LaTeX on marker 0 (US2)
    3. Manually change marker 2 index to 0 (US3)
    4. Save diagram to JSON
    5. Reload diagram from JSON
    6. Verify all state persisted correctly
    """
    # Step 1: Create diagram with 3 InputMarkers
    diagram = Diagram()
    diagram.add_block("io_marker", "in0", marker_type="input")
    diagram.add_block("io_marker", "in1", marker_type="input")
    diagram.add_block("io_marker", "in2", marker_type="input")

    # Verify automatic indexing (US1)
    assert diagram.get_block("in0").get_parameter("index") == 0
    assert diagram.get_block("in1").get_parameter("index") == 1
    assert diagram.get_block("in2").get_parameter("index") == 2

    # Step 2: Enable custom LaTeX on marker 0 (US2)
    diagram.get_block("in0").custom_latex = "r"

    # Verify custom LaTeX set
    assert diagram.get_block("in0").custom_latex == "r"

    # Step 3: Manually change marker 2 index to 0 (US3)
    diagram.update_block_parameter("in2", "index", 0)

    # Verify renumbering occurred (US3)
    assert diagram.get_block("in2").get_parameter("index") == 0  # Changed marker
    assert diagram.get_block("in0").get_parameter("index") == 1  # Shifted up
    assert diagram.get_block("in1").get_parameter("index") == 2  # Shifted up

    # Step 4: Save diagram to JSON
    diagram_json = diagram.to_dict()

    # Step 5: Reload diagram from JSON
    new_diagram = Diagram.from_dict(diagram_json)

    # Step 6: Verify all state persisted correctly
    # Verify indices persisted
    assert new_diagram.get_block("in2").get_parameter("index") == 0
    assert new_diagram.get_block("in0").get_parameter("index") == 1
    assert new_diagram.get_block("in1").get_parameter("index") == 2

    # Verify custom LaTeX persisted
    assert new_diagram.get_block("in0").custom_latex == "r"

    # Verify other markers have no custom LaTeX
    assert new_diagram.get_block("in1").custom_latex is None
    assert new_diagram.get_block("in2").custom_latex is None


def test_mixed_marker_types_workflow():
    """Test workflow with both InputMarkers and OutputMarkers.

    Verifies that:
    - Input and Output indices are independent
    - Renumbering only affects markers of same type
    - Mixed markers save/load correctly
    """
    diagram = Diagram()

    # Create mixed markers
    diagram.add_block("io_marker", "in0", marker_type="input")
    diagram.add_block("io_marker", "out0", marker_type="output")
    diagram.add_block("io_marker", "in1", marker_type="input")
    diagram.add_block("io_marker", "out1", marker_type="output")

    # Verify independent sequences
    assert diagram.get_block("in0").get_parameter("index") == 0
    assert diagram.get_block("in1").get_parameter("index") == 1
    assert diagram.get_block("out0").get_parameter("index") == 0
    assert diagram.get_block("out1").get_parameter("index") == 1

    # Renumber input marker 1 → 0
    diagram.update_block_parameter("in1", "index", 0)

    # Verify only input markers renumbered (outputs unchanged)
    assert diagram.get_block("in1").get_parameter("index") == 0
    assert diagram.get_block("in0").get_parameter("index") == 1
    assert diagram.get_block("out0").get_parameter("index") == 0  # Unchanged
    assert diagram.get_block("out1").get_parameter("index") == 1  # Unchanged

    # Save and reload
    diagram_json = diagram.to_dict()
    new_diagram = Diagram.from_dict(diagram_json)

    # Verify persistence
    assert new_diagram.get_block("in1").get_parameter("index") == 0
    assert new_diagram.get_block("in0").get_parameter("index") == 1
    assert new_diagram.get_block("out0").get_parameter("index") == 0
    assert new_diagram.get_block("out1").get_parameter("index") == 1


def test_delete_add_workflow():
    """Test workflow with marker deletion and addition.

    Verifies that:
    - Deletion triggers cascade renumbering
    - Adding new markers assigns next available index
    - State persists across save/load
    """
    diagram = Diagram()

    # Create 4 markers
    diagram.add_block("io_marker", "in0", marker_type="input")
    diagram.add_block("io_marker", "in1", marker_type="input")
    diagram.add_block("io_marker", "in2", marker_type="input")
    diagram.add_block("io_marker", "in3", marker_type="input")

    # Delete middle marker
    diagram.remove_block("in1")

    # Verify cascade renumbering
    assert diagram.get_block("in0").get_parameter("index") == 0
    assert diagram.get_block("in2").get_parameter("index") == 1  # Was 2
    assert diagram.get_block("in3").get_parameter("index") == 2  # Was 3
    assert diagram.get_block("in1") is None  # Deleted

    # Add new marker
    diagram.add_block("io_marker", "in_new", marker_type="input")

    # Verify new marker gets next index
    assert diagram.get_block("in_new").get_parameter("index") == 3

    # Save and reload
    diagram_json = diagram.to_dict()
    new_diagram = Diagram.from_dict(diagram_json)

    # Verify persistence
    assert new_diagram.get_block("in0").get_parameter("index") == 0
    assert new_diagram.get_block("in2").get_parameter("index") == 1
    assert new_diagram.get_block("in3").get_parameter("index") == 2
    assert new_diagram.get_block("in_new").get_parameter("index") == 3
