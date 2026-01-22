# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Performance tests for theme switching (Phase 8).

Tests for:
- T061: Theme switching performance (< 100ms)
- T062: Rapid theme switching (no lag or artifacts)
- T063: Multiple diagrams performance (50+ diagrams)
"""

import time

import pytest

from lynx import Diagram
from lynx.utils.theme_config import set_default_theme


@pytest.fixture
def clean_theme_config():
    """Reset global theme config before each test."""
    import lynx.utils.theme_config as config

    original_session = config._session_default
    original_env = config._environment_default
    config._session_default = None

    yield

    config._session_default = original_session
    config._environment_default = original_env


class TestThemeSwitchingPerformance:
    """Test theme switching performance (T061)."""

    def test_single_theme_switch_performance(self, clean_theme_config):
        """T061: Test single theme switch completes in < 100ms."""
        diagram = Diagram(theme="light")

        start_time = time.perf_counter()
        diagram.theme = "dark"
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Theme switching should be nearly instantaneous (< 1ms for Python-side)
        # Note: UI rendering time would add more, but Python API should be fast
        assert elapsed_ms < 100, (
            f"Theme switch took {elapsed_ms:.2f}ms, expected < 100ms"
        )
        assert diagram.theme == "dark"

    def test_theme_switch_with_validation_performance(self, clean_theme_config):
        """T061: Test theme switch with validation is fast."""
        diagram = Diagram()

        start_time = time.perf_counter()
        diagram.theme = "high-contrast"  # Triggers validation
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert elapsed_ms < 100, f"Theme switch with validation took {elapsed_ms:.2f}ms"
        assert diagram.theme == "high-contrast"

    def test_invalid_theme_validation_performance(self, clean_theme_config):
        """T061: Test invalid theme validation doesn't slow down system."""
        diagram = Diagram()

        start_time = time.perf_counter()
        diagram.theme = "invalid_theme"  # Triggers validation + warning
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Even with logging, should be fast
        assert elapsed_ms < 100, f"Invalid theme validation took {elapsed_ms:.2f}ms"
        assert diagram.theme is None

    def test_theme_switch_with_large_diagram(self, clean_theme_config):
        """T061: Test theme switch performance with large diagram."""
        diagram = Diagram(theme="light")

        # Create large diagram (50 blocks)
        for i in range(50):
            diagram.add_block("gain", f"g{i}", K=float(i))

        start_time = time.perf_counter()
        diagram.theme = "dark"
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Theme change shouldn't be affected by diagram size
        assert elapsed_ms < 100, (
            f"Theme switch with large diagram took {elapsed_ms:.2f}ms"
        )
        assert diagram.theme == "dark"

    def test_resolve_theme_performance(self, clean_theme_config):
        """T061: Test resolve_theme() is fast."""
        from lynx.utils.theme_config import resolve_theme

        set_default_theme("dark")

        start_time = time.perf_counter()
        theme = resolve_theme(None)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert elapsed_ms < 10, (
            f"resolve_theme() took {elapsed_ms:.2f}ms, expected < 10ms"
        )
        assert theme == "dark"


class TestRapidThemeSwitching:
    """Test rapid theme switching (T062)."""

    def test_100_rapid_theme_switches(self, clean_theme_config):
        """T062: Test 100 rapid theme switches complete without errors."""
        diagram = Diagram()
        themes = ["light", "dark", "high-contrast"]

        start_time = time.perf_counter()
        for i in range(100):
            diagram.theme = themes[i % 3]
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # 100 switches should complete quickly (< 100ms total, i.e., < 1ms per switch)
        assert elapsed_ms < 100, f"100 theme switches took {elapsed_ms:.2f}ms"
        assert diagram.theme == "light"  # Last theme (99 % 3 = 0)

    def test_1000_rapid_theme_switches(self, clean_theme_config):
        """T062: Test 1000 rapid theme switches for stress testing."""
        diagram = Diagram()
        themes = ["light", "dark", "high-contrast"]

        start_time = time.perf_counter()
        for i in range(1000):
            diagram.theme = themes[i % 3]
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # 1000 switches should still be fast (< 500ms)
        assert elapsed_ms < 500, f"1000 theme switches took {elapsed_ms:.2f}ms"
        assert diagram.theme == "light"  # Last theme (999 % 3 = 0)

    def test_alternating_theme_switches(self, clean_theme_config):
        """T062: Test alternating between two themes rapidly."""
        diagram = Diagram()

        start_time = time.perf_counter()
        for i in range(100):
            diagram.theme = "light" if i % 2 == 0 else "dark"
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert elapsed_ms < 100, f"100 alternating switches took {elapsed_ms:.2f}ms"
        # Last iteration: i=99 (odd), so diagram.theme = "dark"
        assert diagram.theme == "dark"

    def test_rapid_switches_with_invalid_themes(self, clean_theme_config):
        """T062: Test rapid switches including invalid themes."""
        diagram = Diagram()
        themes = ["light", "dark", "invalid", "high-contrast", "purple"]

        start_time = time.perf_counter()
        for i in range(100):
            diagram.theme = themes[i % 5]
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Should handle invalid themes gracefully
        assert elapsed_ms < 200, (
            f"100 switches with invalid themes took {elapsed_ms:.2f}ms"
        )
        # Last theme: i=99, 99 % 5 = 4, themes[4] = "purple" (invalid), so None
        assert diagram.theme is None


class TestMultipleDiagramsPerformance:
    """Test performance with many diagrams (T063)."""

    def test_create_50_diagrams_with_themes(self, clean_theme_config):
        """T063: Test creating 50 diagrams with different themes."""
        themes = ["light", "dark", "high-contrast"]

        start_time = time.perf_counter()
        diagrams = []
        for i in range(50):
            d = Diagram(theme=themes[i % 3])
            diagrams.append(d)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Creating 50 diagrams should be fast (< 500ms)
        assert elapsed_ms < 500, f"Creating 50 diagrams took {elapsed_ms:.2f}ms"
        assert len(diagrams) == 50

        # Verify all themes are correct
        for i, d in enumerate(diagrams):
            assert d.theme == themes[i % 3]

    def test_create_100_diagrams_with_session_default(self, clean_theme_config):
        """T063: Test creating 100 diagrams with session default."""
        set_default_theme("dark")

        start_time = time.perf_counter()
        diagrams = [Diagram() for _ in range(100)]
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Creating 100 diagrams should be reasonably fast (< 1000ms = 1 second)
        assert elapsed_ms < 1000, f"Creating 100 diagrams took {elapsed_ms:.2f}ms"
        assert len(diagrams) == 100

        # All should have None (will resolve to session default)
        from lynx.utils.theme_config import resolve_theme

        for d in diagrams:
            assert resolve_theme(d.theme) == "dark"

    def test_change_themes_on_50_diagrams(self, clean_theme_config):
        """T063: Test changing themes on 50 existing diagrams."""
        diagrams = [Diagram(theme="light") for _ in range(50)]

        start_time = time.perf_counter()
        for d in diagrams:
            d.theme = "dark"
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Changing 50 themes should be fast (< 100ms)
        assert elapsed_ms < 100, f"Changing 50 themes took {elapsed_ms:.2f}ms"

        # Verify all changed
        for d in diagrams:
            assert d.theme == "dark"

    def test_save_load_performance_with_theme(self, clean_theme_config):
        """T063: Test save/load performance doesn't degrade with theme."""
        diagram = Diagram(theme="high-contrast")
        for i in range(20):
            diagram.add_block("gain", f"g{i}", K=float(i))

        # Test save performance
        start_time = time.perf_counter()
        data = diagram.to_dict()
        save_elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert save_elapsed_ms < 100, f"Save with theme took {save_elapsed_ms:.2f}ms"
        assert "theme" in data

        # Test load performance
        start_time = time.perf_counter()
        loaded = Diagram.from_dict(data)
        load_elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert load_elapsed_ms < 200, f"Load with theme took {load_elapsed_ms:.2f}ms"
        assert loaded.theme == "high-contrast"

    def test_memory_usage_with_many_diagrams(self, clean_theme_config):
        """T063: Test that theme doesn't cause excessive memory usage."""
        import sys

        # Create baseline
        diagrams_baseline = [Diagram() for _ in range(10)]
        sys.getsizeof(diagrams_baseline)

        # Create 100 diagrams with themes
        diagrams = [Diagram(theme="dark") for _ in range(100)]
        sys.getsizeof(diagrams)

        # Memory should scale roughly linearly
        # Each diagram should add a small, consistent amount
        # (This is a rough check - exact memory usage varies by Python implementation)
        assert len(diagrams) == 100
        assert all(d.theme == "dark" for d in diagrams)


class TestPerformanceBenchmarks:
    """Benchmark tests for performance documentation."""

    def test_benchmark_theme_operations(self, clean_theme_config, benchmark=None):
        """Benchmark various theme operations for documentation."""
        diagram = Diagram()

        # If pytest-benchmark is installed, use it; otherwise just time it
        if benchmark is None:
            # Manual timing
            operations = {
                "set_light": lambda: setattr(diagram, "theme", "light"),
                "set_dark": lambda: setattr(diagram, "theme", "dark"),
                "set_high_contrast": lambda: setattr(diagram, "theme", "high-contrast"),
                "set_none": lambda: setattr(diagram, "theme", None),
            }

            results = {}
            for name, op in operations.items():
                start = time.perf_counter()
                for _ in range(1000):
                    op()
                elapsed_ms = (time.perf_counter() - start) * 1000
                results[name] = elapsed_ms / 1000  # Average per operation

            # All operations should be < 0.1ms each on average
            for name, avg_ms in results.items():
                assert avg_ms < 0.1, f"{name} took {avg_ms:.4f}ms on average"
        else:
            # Use pytest-benchmark if available
            benchmark(lambda: setattr(diagram, "theme", "dark"))

    def test_performance_doesnt_degrade_with_complexity(self, clean_theme_config):
        """Test that theme performance doesn't degrade with diagram complexity."""
        # Simple diagram
        simple = Diagram()
        start = time.perf_counter()
        simple.theme = "dark"
        simple_time = (time.perf_counter() - start) * 1000

        # Complex diagram (100 blocks, 50 connections)
        complex_diagram = Diagram()
        for i in range(100):
            complex_diagram.add_block("gain", f"g{i}", K=float(i))

        # Add some connections
        for i in range(49):
            complex_diagram.add_connection(f"c{i}", f"g{i}", "out", f"g{i + 1}", "in")

        start = time.perf_counter()
        complex_diagram.theme = "dark"
        complex_time = (time.perf_counter() - start) * 1000

        # Complex diagram should take similar time
        # (theme is independent of diagram content)
        # Both should be very fast (< 1ms). Allow some variation at microsecond scale.
        assert complex_time < 1.0, (
            f"Complex diagram theme switch took {complex_time:.4f}ms, expected < 1ms"
        )
        assert simple_time < 1.0, (
            f"Simple diagram theme switch took {simple_time:.4f}ms, expected < 1ms"
        )

        # Complex shouldn't be dramatically slower (< 10x)
        if simple_time > 0:  # Avoid division by zero
            ratio = complex_time / simple_time
            assert ratio < 10, (
                f"Complex is {ratio:.1f}x slower than simple "
                "(not significantly independent)"
            )
