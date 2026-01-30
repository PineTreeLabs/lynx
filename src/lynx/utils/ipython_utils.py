# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import control
from IPython.display import Markdown, display

__all__ = ["display_sys"]


# Hack for LaTeX rendering in VS Code Jupyter notebooks
# Required for control>=0.10.2
def display_sys(sys: control.InputOutputSystem):  # type: ignore
    display(Markdown(sys._repr_markdown_()))
