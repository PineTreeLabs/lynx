# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Lynx - Block Diagram Widget for Control Systems

Interactive Jupyter widget for creating and editing control system block diagrams.

Main exports:
    Diagram: Block diagram container
    LynxWidget: anywidget for Jupyter display
    edit: Launch widget to edit a diagram
    Block types: GainBlock, InputMarker, OutputMarker
"""

__version__ = "0.1.0"

from lynx.blocks import Block, GainBlock, InputMarker, OutputMarker
from lynx.diagram import Diagram
from lynx.render import render
from lynx.utils.theme_config import set_default_theme
from lynx.widget import LynxWidget


def edit(diagram: Diagram, height: int = 400) -> LynxWidget:
    """Launch interactive widget to edit a diagram.

    This is the recommended way to edit diagrams. The widget displays the diagram
    and any changes made in the UI are automatically saved to the diagram object.

    Args:
        diagram: Diagram instance to edit
        height: Widget height in pixels (default: 400)

    Returns:
        LynxWidget instance (automatically displayed in Jupyter)

    Examples:
        >>> import lynx
        >>> diagram = lynx.Diagram()
        >>> lynx.edit(diagram)  # Launch editor
        >>> # Make changes in UI...
        >>> lynx.edit(diagram)  # Re-launch with previous state

        >>> # Custom height
        >>> lynx.edit(diagram, height=450)
    """
    from ipywidgets import Layout

    # Set layout during widget creation to avoid race condition
    widget = LynxWidget(
        diagram=diagram, layout=Layout(height=f"{height}px", width="100%")
    )
    return widget


__all__ = [
    "__version__",
    "Diagram",
    "LynxWidget",
    "edit",
    "render",
    "set_default_theme",
    "Block",
    "GainBlock",
    "InputMarker",
    "OutputMarker",
]
