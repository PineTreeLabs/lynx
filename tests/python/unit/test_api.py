# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test the public API (lynx.edit and recommended usage patterns)."""

import lynx


def test_edit_function_with_new_diagram():
    """Test lynx.edit() creates widget from diagram."""
    diagram = lynx.Diagram()
    widget = lynx.edit(diagram)

    assert isinstance(widget, lynx.LynxWidget)
    assert widget.diagram is diagram  # Same diagram object
    assert widget.layout.height == "400px"  # Default height
    assert widget.layout.width == "100%"


def test_edit_function_with_custom_height():
    """Test lynx.edit() respects custom height."""
    diagram = lynx.Diagram()
    widget = lynx.edit(diagram, height=450)

    assert widget.layout.height == "450px"
    assert widget.layout.width == "100%"


def test_edit_function_preserves_diagram_state():
    """Test lynx.edit() preserves diagram state across widget launches."""
    # Create diagram and add blocks
    diagram = lynx.Diagram()
    diagram.add_block("gain", "g1", K=2.5)
    diagram.add_block("io_marker", "in1", marker_type="input")

    # Launch widget
    widget1 = lynx.edit(diagram)
    assert len(widget1.diagram.blocks) == 2

    # Close widget and re-launch (simulated by creating new widget)
    widget2 = lynx.edit(diagram)

    # State should be preserved
    assert len(widget2.diagram.blocks) == 2
    assert widget2.diagram is diagram  # Same diagram object
    assert widget2.diagram.blocks[0].id == "g1"


def test_edit_function_diagram_changes_persist():
    """Test changes made via one widget persist to diagram."""
    diagram = lynx.Diagram()
    widget = lynx.edit(diagram)

    # Simulate adding block via widget (directly modifies diagram)
    widget.diagram.add_block("gain", "g2", K=1.0)

    # Changes should persist in diagram
    assert len(diagram.blocks) == 1
    assert diagram.blocks[0].id == "g2"


def test_lynx_widget_with_diagram_parameter():
    """Test LynxWidget accepts diagram parameter (backward compatibility)."""
    diagram = lynx.Diagram()
    diagram.add_block("gain", "g1", K=5.0)

    widget = lynx.LynxWidget(diagram=diagram)

    assert widget.diagram is diagram
    assert len(widget.diagram.blocks) == 1


def test_lynx_widget_without_diagram_parameter():
    """Test LynxWidget creates empty diagram if not provided
    (backward compatibility)."""
    widget = lynx.LynxWidget()

    assert isinstance(widget.diagram, lynx.Diagram)
    assert len(widget.diagram.blocks) == 0


def test_recommended_workflow():
    """Test the recommended workflow: create diagram, edit, save, reload, edit again."""
    # Step 1: Create diagram and edit
    diagram = lynx.Diagram()
    widget1 = lynx.edit(diagram)

    # Step 2: Make changes (simulated)
    widget1.diagram.add_block("gain", "g1", K=2.0)
    widget1.diagram.add_block("sum", "s1", signs=["+", "-", "|"])

    # Step 3: Save
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        diagram.save(temp_path)

        # Step 4: Load in new session
        loaded_diagram = lynx.Diagram.load(temp_path)

        # Step 5: Edit loaded diagram
        widget2 = lynx.edit(loaded_diagram)

        # State should be restored
        assert len(widget2.diagram.blocks) == 2
        assert widget2.diagram.blocks[0].id == "g1"
        assert widget2.diagram.blocks[1].id == "s1"

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
