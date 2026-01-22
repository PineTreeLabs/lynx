# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Theme configuration and validation utilities for Lynx.

This module provides theme validation, precedence resolution, and default
theme management for the Lynx diagram library.
"""

import logging
import os
from typing import Optional

# Valid theme names
VALID_THEMES = {"light", "dark", "high-contrast", "archimedes-light", "archimedes-dark"}

# Built-in default theme
BUILT_IN_DEFAULT_THEME = "light"

# Module-level session default (mutable via set_default_theme())
_session_default: Optional[str] = None

# Environment variable default (read once at module import)
_environment_default: Optional[str] = None

# Initialize environment default from LYNX_DEFAULT_THEME
_env_theme = os.environ.get("LYNX_DEFAULT_THEME")
if _env_theme is not None:
    if _env_theme in VALID_THEMES:
        _environment_default = _env_theme
    else:
        logging.warning(
            f"Invalid LYNX_DEFAULT_THEME environment variable '{_env_theme}'. "
            f"Must be one of: {', '.join(sorted(VALID_THEMES))}. "
            f"Using built-in default '{BUILT_IN_DEFAULT_THEME}'."
        )


def validate_theme_name(name: Optional[str]) -> Optional[str]:
    """Validate a theme name.

    Args:
        name: Theme name to validate, or None

    Returns:
        The validated theme name if valid, None otherwise

    Notes:
        If the theme name is invalid, a warning is logged and None is returned.
        None input is considered valid (represents "no explicit theme set").
    """
    if name is None:
        return None

    if name in VALID_THEMES:
        return name

    # Invalid theme name - log warning and return None
    logging.warning(
        f"Invalid theme name: '{name}'. "
        f"Must be one of: {', '.join(sorted(VALID_THEMES))}. "
        "Using default theme."
    )
    return None


def resolve_theme(diagram_theme: Optional[str] = None) -> str:
    """Resolve the effective theme using precedence hierarchy.

    Precedence order (highest to lowest):
    1. diagram_theme (instance attribute)
    2. Session default (from set_default_theme())
    3. Environment variable (LYNX_DEFAULT_THEME)
    4. Built-in default ("light")

    Args:
        diagram_theme: Diagram-specific theme (if set)

    Returns:
        Resolved theme name (guaranteed to be valid, never None)
    """
    # 1. Check diagram-level theme (highest priority)
    if diagram_theme is not None:
        validated = validate_theme_name(diagram_theme)
        if validated is not None:
            return validated
        # Invalid diagram theme - fall through to next level

    # 2. Check session-level default
    if _session_default is not None:
        return _session_default  # Already validated in set_default_theme()

    # 3. Check environment variable default
    if _environment_default is not None:
        return _environment_default  # Already validated at module import

    # 4. Use built-in default (always valid)
    return BUILT_IN_DEFAULT_THEME


def set_default_theme(theme_name: str) -> None:
    """Set session-wide default theme.

    This affects all newly created diagrams that don't have an explicit theme.
    Existing diagrams are not affected.

    Args:
        theme_name: Theme name to use as default for new diagrams

    Notes:
        If the theme name is invalid, a warning is logged and the session
        default is not changed.
    """
    global _session_default

    validated = validate_theme_name(theme_name)
    if validated is None:
        # Invalid theme - warning already logged by validate_theme_name()
        return

    _session_default = validated


def get_session_default() -> Optional[str]:
    """Get the current session-level default theme.

    Returns:
        Current session default theme name, or None if not set
    """
    return _session_default


def get_environment_default() -> Optional[str]:
    """Get the environment variable default theme.

    Returns:
        Theme name from LYNX_DEFAULT_THEME env var, or None if not set/invalid
    """
    return _environment_default
