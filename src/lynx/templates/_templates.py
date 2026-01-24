# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Diagram template loader using importlib.resources for pip-installable packages.

This module loads JSON diagram templates from the templates/ directory using
importlib.resources.files(), which works correctly with all installation methods:
- Regular pip install
- Editable install (pip install -e .)
- Zip imports
- Wheel distributions
"""

from importlib.resources import files

__all__ = ["DIAGRAM_TEMPLATES"]


def _load_templates() -> dict[str, str]:
    """Load all JSON templates from the templates directory.

    Returns:
        Dictionary mapping template names to JSON strings
    """
    templates = {}

    # Get reference to this package's directory
    template_dir = files("lynx.templates")

    # Template file mapping (filename -> dict key)
    template_files = {
        "open_loop_tf.json": "open_loop_tf",
        "open_loop_ss.json": "open_loop_ss",
        "feedback_tf.json": "feedback_tf",
        "feedback_ss.json": "feedback_ss",
        "feedforward_tf.json": "feedforward_tf",
        "feedforward_ss.json": "feedforward_ss",
        "filtered_tf.json": "filtered",
        "cascaded.json": "cascaded",
    }

    for filename, key in template_files.items():
        template_file = template_dir / filename
        if template_file.is_file():
            # Read as text (JSON string)
            templates[key] = template_file.read_text(encoding="utf-8")

    return templates


# Load templates at module import time
DIAGRAM_TEMPLATES = _load_templates()
