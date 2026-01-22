# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Matplotlib theming utilities for Lynx documentation.

Provides light and dark theme configurations that match Lynx's brand colors
for generating documentation plots.
"""

from typing import Any, Literal

import matplotlib.pyplot as plt
from matplotlib import rcParams

# Lynx brand colors from js/src/styles.css
LYNX_COLORS = {
    "light": {
        "primary": "#6366f1",  # Indigo
        "background": "#ffffff",
        "foreground": "#1f2937",  # Dark gray text
        "grid": "#e5e7eb",  # Light gray
        "secondary": "#818cf8",  # Lighter indigo
        "error": "#dc2626",
        "warning": "#f59e0b",
        "success": "#10b981",
    },
    "dark": {
        "primary": "#8297f8",  # Lighter indigo for dark backgrounds
        "background": "#1f2937",  # Dark charcoal
        "foreground": "#f9fafb",  # Light gray text
        "grid": "#374151",  # Medium gray
        "secondary": "#a5b4fc",  # Even lighter indigo
        "error": "#f87171",
        "warning": "#fbbf24",
        "success": "#34d399",
    },
}


def set_plot_theme(theme: Literal["light", "dark"] = "light") -> None:
    """
    Set matplotlib rcParams to match Lynx theme.

    Parameters
    ----------
    theme : {"light", "dark"}
        Theme to apply. Default is "light".

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from lynx.utils.plot_themes import set_plot_theme
    >>>
    >>> # Use light theme
    >>> set_plot_theme("light")
    >>> plt.plot([1, 2, 3], [1, 4, 9])
    >>> plt.savefig("plot_light.png")
    >>>
    >>> # Use dark theme
    >>> set_plot_theme("dark")
    >>> plt.plot([1, 2, 3], [1, 4, 9])
    >>> plt.savefig("plot_dark.png")
    """
    colors = LYNX_COLORS[theme]

    # Figure and axes styling
    rcParams["figure.facecolor"] = colors["background"]
    rcParams["axes.facecolor"] = colors["background"]
    rcParams["axes.edgecolor"] = colors["foreground"]
    rcParams["axes.labelcolor"] = colors["foreground"]

    # Grid styling
    rcParams["grid.color"] = colors["grid"]
    rcParams["grid.alpha"] = 0.5

    # Ticks and spines
    rcParams["xtick.color"] = colors["foreground"]
    rcParams["ytick.color"] = colors["foreground"]
    rcParams["xtick.labelcolor"] = colors["foreground"]
    rcParams["ytick.labelcolor"] = colors["foreground"]

    # Text
    rcParams["text.color"] = colors["foreground"]

    # Legend
    rcParams["legend.facecolor"] = colors["background"]
    rcParams["legend.edgecolor"] = colors["grid"]
    rcParams["legend.labelcolor"] = colors["foreground"]

    # Default line colors (use Lynx primary)
    rcParams["axes.prop_cycle"] = plt.cycler(
        color=[
            colors["primary"],
            colors["secondary"],
            colors["success"],
            colors["warning"],
            colors["error"],
        ]
    )

    # Font settings (match Lynx fonts)
    rcParams["font.family"] = "sans-serif"
    rcParams["font.sans-serif"] = ["Roboto", "Arial", "sans-serif"]
    rcParams["font.size"] = 10


def save_themed_plot(
    fig: plt.Figure,
    filename_base: str,
    dpi: int = 150,
    bbox_inches: str = "tight",
) -> tuple[str, str]:
    """
    Save a plot in both light and dark themes for MyST documentation.

    This function saves two versions of the same plot with appropriate
    theming for light and dark documentation modes.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to save.
    filename_base : str
        Base filename without extension (e.g., "step_response").
        Will generate "{filename_base}_light.png" and "{filename_base}_dark.png".
    dpi : int, default=150
        Resolution in dots per inch.
    bbox_inches : str, default="tight"
        Bounding box for saved figure.

    Returns
    -------
    tuple[str, str]
        Paths to (light_file, dark_file).

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from lynx.utils.plot_themes import set_plot_theme, save_themed_plot
    >>>
    >>> # Create plot
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> ax.set_xlabel("Time (s)")
    >>> ax.set_ylabel("Output")
    >>> ax.grid(True)
    >>>
    >>> # Save in both themes
    >>> light_path, dark_path = save_themed_plot(fig, "my_plot")
    >>>
    >>> # In MyST markdown:
    >>> # ```{image} my_plot_light.png
    >>> # :class: only-light
    >>> # ```
    >>> #
    >>> # ```{image} my_plot_dark.png
    >>> # :class: only-dark
    >>> # ```
    """
    import io

    from PIL import Image

    light_file = f"{filename_base}_light.png"
    dark_file = f"{filename_base}_dark.png"

    # Save light theme
    set_plot_theme("light")
    fig.canvas.draw()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches=bbox_inches)
    buf.seek(0)
    img = Image.open(buf)
    img.save(light_file, dpi=(dpi, dpi))
    buf.close()

    # Save dark theme
    set_plot_theme("dark")
    fig.canvas.draw()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches=bbox_inches)
    buf.seek(0)
    img = Image.open(buf)
    img.save(dark_file, dpi=(dpi, dpi))
    buf.close()

    return light_file, dark_file


# Convenience context manager
class themed_plot:
    """
    Context manager for creating themed plots.

    Examples
    --------
    >>> from lynx.utils.plot_themes import themed_plot
    >>> import matplotlib.pyplot as plt
    >>>
    >>> with themed_plot("dark"):
    ...     fig, ax = plt.subplots()
    ...     ax.plot([1, 2, 3], [1, 4, 9])
    ...     plt.show()
    """

    def __init__(self, theme: Literal["light", "dark"] = "light") -> None:
        self.theme = theme
        self.old_params: dict[str, Any] = {}

    def __enter__(self) -> "themed_plot":
        # Save current rcParams
        self.old_params = rcParams.copy()
        # Apply theme
        set_plot_theme(self.theme)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        # Restore original rcParams
        rcParams.update(self.old_params)
