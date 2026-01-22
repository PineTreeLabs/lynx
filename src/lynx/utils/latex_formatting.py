# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""LaTeX formatting utilities for Lynx blocks.

Provides consistent numerical formatting for LaTeX rendering with configurable
precision and exponential notation thresholds.
"""

import math
from typing import Union

from lynx.config.constants import NUMBER_FORMAT


def format_number(
    value: Union[int, float], sig_figs: int = NUMBER_FORMAT.sig_figs
) -> str:
    """Format number to N significant figures with exponential notation for extremes.

    Args:
        value: Number to format
        sig_figs: Number of significant figures (default from NUMBER_FORMAT)

    Returns:
        Formatted string (e.g., "1.23", "4.56e-3", "1.23e3")

    Exponential notation used based on NUMBER_FORMAT thresholds

    Examples:
        >>> format_number(0.00456)
        '4.56e-03'
        >>> format_number(1234)
        '1.23e+03'
        >>> format_number(123.456)
        '123'
        >>> format_number(0)
        '0'
    """
    if value == 0:
        return "0"

    abs_value = abs(value)

    # Use exponential notation for very small or large numbers
    if (
        abs_value < NUMBER_FORMAT.exp_notation_min
        or abs_value >= NUMBER_FORMAT.exp_notation_max
    ):
        # Format in scientific notation with sig_figs-1 decimal places
        # Use LaTeX format: 1.23 × 10^{3} instead of 1.23e+03
        exp_str = f"{value:.{sig_figs - 1}e}"
        # Parse mantissa and exponent
        mantissa, exponent = exp_str.split("e")
        exp_int = int(exponent)
        return f"{mantissa} \\times 10^{{{exp_int}}}"
    else:
        # For mid-range numbers, round to sig_figs significant figures
        # Use Python's built-in round with significant figures
        # First, get the order of magnitude
        magnitude = math.floor(math.log10(abs_value))

        # Round to the appropriate decimal place
        decimal_places = sig_figs - magnitude - 1

        # Round the value
        if decimal_places >= 0:
            # Positive decimal places (e.g., 1.234 → 1.23)
            formatted = f"{value:.{decimal_places}f}"
            # Strip trailing zeros ONLY if there's a decimal point
            if "." in formatted:
                return formatted.rstrip("0").rstrip(".")
            else:
                return formatted
        else:
            # Negative decimal places (e.g., 123.456 with 2 sig figs → 120)
            rounded_value = round(value, decimal_places)
            # No stripping for integers
            return f"{rounded_value:.0f}"
