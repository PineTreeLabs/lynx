# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for LaTeX formatting utilities."""

from lynx.utils.latex_formatting import format_number


class TestFormatNumber:
    """Test suite for format_number utility."""

    def test_format_number_small_exponential(self):
        """Test exponential notation for small numbers (<0.01) - T008."""
        # Small positive number
        assert format_number(0.00456) == "4.56 \\times 10^{-3}"
        assert format_number(0.00123) == "1.23 \\times 10^{-3}"
        assert format_number(0.001) == "1.00 \\times 10^{-3}"

        # Very small number
        assert format_number(0.000001) == "1.00 \\times 10^{-6}"

        # Negative small number
        assert format_number(-0.00789) == "-7.89 \\times 10^{-3}"

    def test_format_number_large_exponential(self):
        """Test exponential notation for large numbers (>=1000) - T009."""
        # Large positive number
        assert format_number(1234) == "1.23 \\times 10^{3}"
        assert format_number(5678.9) == "5.68 \\times 10^{3}"
        assert format_number(1000) == "1.00 \\times 10^{3}"

        # Very large number
        assert format_number(1000000) == "1.00 \\times 10^{6}"

        # Negative large number
        assert format_number(-12345) == "-1.23 \\times 10^{4}"

    def test_format_number_mid_range(self):
        """Test fixed notation for mid-range numbers (0.01 to 999) - T010."""
        # Mid-range positive numbers
        assert format_number(123.456) == "123"
        assert format_number(12.3456) == "12.3"
        assert format_number(1.23456) == "1.23"
        assert format_number(0.123456) == "0.123"
        assert format_number(0.0123456) == "0.0123"  # >= 0.01, so no exponential

        # Edge cases at boundaries
        assert (
            format_number(0.01) == "0.01"
        )  # At lower boundary (exactly 0.01, still mid-range)
        assert format_number(999) == "999"  # Just below upper boundary
        assert (
            format_number(999.9) == "1000"
        )  # Rounds to 1000, but checked threshold before rounding

        # Negative mid-range
        assert format_number(-45.678) == "-45.7"

    def test_format_number_zero(self):
        """Test zero formatting."""
        assert format_number(0) == "0"
        assert format_number(0.0) == "0"
        assert format_number(-0.0) == "0"

    def test_format_number_custom_sig_figs(self):
        """Test custom significant figures parameter."""
        # 2 sig figs - mid-range (< 1000), rounds to 120
        assert format_number(123.456, sig_figs=2) == "120"

        # 4 sig figs
        assert format_number(12.3456, sig_figs=4) == "12.35"

        # 5 sig figs
        assert format_number(0.123456, sig_figs=5) == "0.12346"
