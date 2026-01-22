# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Python-control conversion utilities for Lynx diagrams.

Public API:
- get_ss(diagram, from_signal, to_signal) → StateSpace
- get_tf(diagram, from_signal, to_signal) → TransferFunction

Advanced/Internal:
- to_interconnect(diagram) → LinearICSystem
  Available via: from lynx.conversion.interconnect import to_interconnect
  Used internally by get_ss() and get_tf() for subsystem extraction.
  Useful for: performance (build once, index many times), MIMO systems,
  full state-space analysis, and advanced python-control operations.
"""

# Public API - primary user-facing methods for subsystem extraction
from .signal_extraction import get_ss, get_tf

__all__ = ["get_ss", "get_tf"]

# Note: to_interconnect is still available but not part of primary API.
# Import directly from .interconnect if you need it:
#   from lynx.conversion.interconnect import to_interconnect
