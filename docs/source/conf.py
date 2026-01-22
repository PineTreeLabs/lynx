# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Lynx"
copyright = "2026, Jared Callaham"
author = "Jared Callaham"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_nb",
    "sphinx_design",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Furo theme options
html_theme_options = {
    # Logos
    "light_logo": "logo-light.png",
    "dark_logo": "logo-dark.png",
    "sidebar_hide_name": False,
    # Navigation
    "navigation_with_keys": True,
    "source_repository": "https://github.com/pinetreelabs/lynx",
    "source_branch": "main",
    "source_directory": "docs/source/",
    # Light mode colors (Lynx brand)
    "light_css_variables": {
        "color-brand-primary": "#6366f1",  # Indigo primary
        "color-brand-content": "#3e4d98",  # Darker indigo for content
        "color-admonition-background": "rgba(99, 102, 241, 0.1)",  # Transparent indigo
        "color-background-primary": "#ffffff",
        "color-background-secondary": "#f9fafb",  # Light gray
        "color-foreground-primary": "#1f2937",  # Dark gray text
        "color-foreground-secondary": "#4b5563",  # Medium gray text
        "color-link": "#6366f1",  # Indigo links
        "color-link-hover": "#818cf8",  # Lighter indigo on hover
        "color-sidebar-background": "#fafbfc",
        "color-sidebar-background-border": "#e5e7eb",
    },
    # Dark mode colors (Lynx brand adapted for dark backgrounds)
    "dark_css_variables": {
        "color-brand-primary": "#8297f8",  # Lighter indigo for dark mode
        "color-brand-content": "#a5b4fc",  # Even lighter for content
        # Transparent lighter indigo
        "color-admonition-background": "rgba(130, 151, 248, 0.1)",
        "color-background-primary": "#1f2937",  # Dark charcoal
        "color-background-secondary": "#111827",  # Darker charcoal
        "color-foreground-primary": "#f9fafb",  # Light gray text
        "color-foreground-secondary": "#d1d5db",  # Medium light gray
        "color-link": "#8297f8",  # Lighter indigo links
        "color-link-hover": "#a5b4fc",  # Even lighter on hover
        "color-sidebar-background": "#1a1f2e",
        "color-sidebar-background-border": "#374151",
    },
    # Footer
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/pinetreelabs/lynx",
            "html": """
                <svg stroke="currentColor" fill="currentColor"
                     stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd"
                          d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29
                             6.53 5.47 7.59.4.07.55-.17.55-.38
                             0-.19-.01-.82-.01-1.49-2.01.37-2.53
                             -.49-2.69-.94-.09-.23-.48-.94-.82
                             -1.13-.28-.15-.68-.52-.01-.53.63
                             -.01 1.08.58 1.23.82.72 1.21 1.87
                             .87 2.33.66.07-.52.28-.87.51
                             -1.07-1.78-.2-3.64-.89-3.64
                             -3.95 0-.87.31-1.59.82-2.15
                             -.08-.2-.36-1.02.08-2.12 0 0 .67
                             -.21 2.2.82.64-.18 1.32-.27 2
                             -.27.68 0 1.36.09 2 .27 1.53
                             -1.04 2.2-.82 2.2-.82.44 1.1.16
                             1.92.08 2.12.51.56.82 1.27.82
                             2.15 0 3.07-1.87 3.75-3.65
                             3.95.29.25.54.73.54 1.48 0
                             1.07-.01 1.93-.01 2.2 0
                             .21.15.46.55.38A8.013 8.013 0
                             0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

html_favicon = "_static/favicon.svg"

# -- Extension configuration -------------------------------------------------

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "inherited-members": False,
    "show-inheritance": True,
}
autodoc_class_signature = "separated"

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = False

# Napoleon settings (Google/NumPy docstring support)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# Intersphinx mappings
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "control": ("https://python-control.readthedocs.io/en/latest/", None),
}

# Suppress known warnings
suppress_warnings = [
    "autodoc",  # Suppress autodoc warnings including duplicate __init__
]

# MyST-NB settings
nb_execution_mode = "cache"
nb_execution_raise_on_error = True
nb_execution_timeout = 60
nb_execution_cache_path = "_build/.jupyter_cache"

# MyST parser settings
myst_enable_extensions = [
    "amsmath",  # Advanced math support
    "attrs_inline",  # Inline HTML attributes
    "attrs_block",  # Block HTML attributes
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",  # ~~strikethrough~~ support
    "substitution",
    "tasklist",
]
