# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Static diagram rendering - export diagrams as PNG or SVG images.

This module provides the `render()` function for exporting diagrams as static images.

Usage:
    # Display inline in Jupyter
    >>> lynx.render(diagram)

    # Save to file (saves to notebook directory)
    >>> lynx.render(diagram, filename="output.png")

    # SVG format
    >>> lynx.render(diagram, format="svg")

    # Custom dimensions
    >>> lynx.render(diagram, width=800, height=600)
"""

import base64
import threading
import time
from pathlib import Path
from typing import Any, Optional

from lynx.diagram import Diagram
from lynx.widget import LynxWidget


def render(
    diagram: Diagram,
    filename: Optional[str] = None,
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
    transparent: bool = False,
    format: str = "png",
) -> None:
    """Render diagram as a static image.

    If filename is provided, saves the image to disk (like matplotlib savefig).
    If filename is None, displays the image inline in Jupyter.

    Args:
        diagram: The Diagram instance to render
        filename: If provided, saves to this file path.
                  If None, displays image inline in the notebook.
        width: Output width in pixels. If None, auto-calculated from content.
        height: Output height in pixels. If None, auto-calculated from content.
        transparent: If True, background is transparent. Default False (white).
        format: Output format - "png" or "svg". Inferred from filename if provided.

    Raises:
        ValueError: If diagram has no blocks
        ValueError: If format is not "png" or "svg"

    Examples:
        >>> import lynx
        >>> diagram = lynx.Diagram()
        >>> diagram.add_block("gain", id="g1", position={"x": 100, "y": 100}, K=2.5)

        >>> # Display inline
        >>> lynx.render(diagram)

        >>> # Save to file
        >>> lynx.render(diagram, filename="my_diagram.png")

        >>> # SVG with transparency
        >>> lynx.render(diagram, format="svg", transparent=True)
    """
    # Validate diagram is not empty
    if len(diagram.blocks) == 0:
        raise ValueError("Cannot render empty diagram: no blocks to display")

    # Infer format from filename if provided
    if filename:
        ext = Path(filename).suffix.lower()
        if ext == ".png":
            format = "png"
        elif ext == ".svg":
            format = "svg"
        # Otherwise use the format parameter

    # Validate format
    if format not in ("png", "svg"):
        raise ValueError(f"Unsupported format '{format}'. Use 'png' or 'svg'")

    # Create widget in capture mode
    # Use height=0 to make it invisible, but it still renders off-screen
    from IPython.display import display
    from ipywidgets import Layout

    if filename:
        # File save: truly invisible, no output needed
        layout_opts = {"height": "0px", "width": "0px", "overflow": "hidden"}
    else:
        # Inline display: use 1px with opacity 0 to hide the bar
        # JS will set opacity to 1 and resize when image is ready
        layout_opts = {"height": "1px", "width": "1px"}

    widget = LynxWidget(diagram=diagram, layout=Layout(**layout_opts))
    widget._capture_mode = True

    # Store filename for the result observer to use
    widget._pending_filename = filename

    # Set up observer to save file when result arrives (for file saving)
    if filename:

        def on_capture_result(change: Any) -> None:
            result = change["new"]
            if not result or not result.get("success"):
                return

            # Get the pending filename
            pending_filename = getattr(widget, "_pending_filename", None)
            if not pending_filename:
                return

            # Decode base64 data and save to file
            data = result.get("data", "")
            if not data:
                return

            file_format = result.get("format", "png")
            file_path = Path(pending_filename)

            try:
                if file_format == "png":
                    # PNG is binary
                    with open(file_path, "wb") as f:
                        f.write(base64.b64decode(data))
                else:
                    # SVG is text
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(base64.b64decode(data).decode("utf-8"))

                # Clear pending filename
                widget._pending_filename = None
            except Exception as e:
                raise RuntimeError(f"Error saving diagram to file: {e}") from e

        widget.observe(on_capture_result, names=["_capture_result"])

    # Display widget (required for React to render)
    display(widget)

    # Send capture request after a brief delay for React to mount
    timestamp = time.time()

    def send_request() -> None:
        widget._capture_request = {
            "format": format,
            "width": width,
            "height": height,
            "transparent": transparent,
            "timestamp": timestamp,
            # filename=None means display inline, otherwise Python saves to disk
            "filename": None,
            # Tell JS whether to display inline or just send result back
            "displayInline": filename is None,
        }

    # Schedule the request - gives React Flow time to initialize
    timer = threading.Timer(1.0, send_request)
    timer.start()
