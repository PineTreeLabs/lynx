# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration tests for label uniqueness validation behavior.

Tests the intended behavior:
1. Duplicate block labels → ValidationResult with errors (is_valid=False)
2. Duplicate connection labels → ValidationResult with errors (is_valid=False)
3. get_ss/get_tf raise ValidationError when diagram has duplicate labels
4. get_ss/get_tf log warnings when ValidationResult has warnings (but is_valid=True)
"""

import pytest

from lynx.conversion.interconnect import validate_for_export
from lynx.diagram import Diagram, ValidationError


class TestLabelUniquenessValidation:
    """Test that duplicate labels result in validation errors."""

    def test_duplicate_block_labels_validation_error(self):
        """Duplicate block labels should result in ValidationResult with errors."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "gain",
            "g2",
            K=3.0,
            label="controller",  # Duplicate!
            position={"x": 200, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        # Connect properly
        diagram.add_connection("c1", "input1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "g2", "in")
        diagram.add_connection("c3", "g2", "out", "output1", "in")

        # Validate
        result = validate_for_export(diagram)

        # Should have errors (not warnings)
        assert not result.is_valid, (
            "Diagram with duplicate block labels should be invalid"
        )
        assert len(result.errors) > 0, "Should have at least one error"
        assert any(
            "duplicate" in err.lower()
            and "block" in err.lower()
            and "controller" in err.lower()
            for err in result.errors
        ), (
            f"Should have error about duplicate block label 'controller', "
            f"got: {result.errors}"
        )

    def test_duplicate_connection_labels_validation_error(self):
        """Duplicate connection labels should result in ValidationResult with errors."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block("gain", "g2", K=3.0, position={"x": 200, "y": 0})
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        # Connect with duplicate labels
        diagram.add_connection("c1", "input1", "out", "g1", "in", label="signal")
        diagram.add_connection(
            "c2", "g1", "out", "g2", "in", label="signal"
        )  # Duplicate!
        diagram.add_connection("c3", "g2", "out", "output1", "in")

        # Validate
        result = validate_for_export(diagram)

        # Should have errors (not warnings)
        assert not result.is_valid, (
            "Diagram with duplicate connection labels should be invalid"
        )
        assert len(result.errors) > 0, "Should have at least one error"
        assert any(
            "duplicate" in err.lower()
            and "connection" in err.lower()
            and "signal" in err.lower()
            for err in result.errors
        ), (
            f"Should have error about duplicate connection label 'signal', "
            f"got: {result.errors}"
        )

    def test_unique_labels_validation_passes(self):
        """Diagrams with unique labels should pass validation."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "gain", "g2", K=3.0, label="plant", position={"x": 200, "y": 0}
        )
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        # Connect with unique labels
        diagram.add_connection("c1", "input1", "out", "g1", "in", label="ref")
        diagram.add_connection("c2", "g1", "out", "g2", "in", label="control")
        diagram.add_connection("c3", "g2", "out", "output1", "in", label="output")

        # Validate
        result = validate_for_export(diagram)

        # Should be valid with no errors
        assert result.is_valid, (
            f"Diagram with unique labels should be valid, got errors: {result.errors}"
        )
        # Check for duplicate label errors specifically
        assert not any("duplicate" in err.lower() for err in result.errors), (
            f"Should have no duplicate label errors, got: {result.errors}"
        )


class TestGetSSGetTFValidationBehavior:
    """Test that get_ss/get_tf handle validation results correctly."""

    def test_get_ss_raises_on_duplicate_block_labels(self):
        """get_ss should raise ValidationError when diagram has
        duplicate block labels."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "gain",
            "g2",
            K=3.0,
            label="controller",  # Duplicate!
            position={"x": 200, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        diagram.add_connection("c1", "input1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "g2", "in")
        diagram.add_connection("c3", "g2", "out", "output1", "in")

        # get_ss should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            diagram.get_ss("r", "y")

        # Error message should mention duplicate labels
        assert "duplicate" in str(exc_info.value).lower(), (
            f"Error should mention duplicate labels, got: {exc_info.value}"
        )

    def test_get_tf_raises_on_duplicate_connection_labels(self):
        """get_tf should raise ValidationError when diagram has
        duplicate connection labels."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block("gain", "g1", K=5.0, position={"x": 100, "y": 0})
        diagram.add_block("gain", "g2", K=3.0, position={"x": 200, "y": 0})
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        diagram.add_connection("c1", "input1", "out", "g1", "in", label="signal")
        diagram.add_connection(
            "c2", "g1", "out", "g2", "in", label="signal"
        )  # Duplicate!
        diagram.add_connection("c3", "g2", "out", "output1", "in")

        # get_tf should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            diagram.get_tf("r", "y")

        # Error message should mention duplicate labels
        assert "duplicate" in str(exc_info.value).lower(), (
            f"Error should mention duplicate labels, got: {exc_info.value}"
        )

    def test_get_ss_succeeds_with_unique_labels(self):
        """get_ss should succeed when all labels are unique."""
        diagram = Diagram()
        diagram.add_block(
            "io_marker",
            "input1",
            marker_type="input",
            label="r",
            position={"x": 0, "y": 0},
        )
        diagram.add_block(
            "gain", "g1", K=5.0, label="controller", position={"x": 100, "y": 0}
        )
        diagram.add_block(
            "transfer_function",
            "tf1",
            numerator=[2.0],
            denominator=[1.0, 3.0],
            label="plant",
            position={"x": 200, "y": 0},
        )
        diagram.add_block(
            "io_marker",
            "output1",
            marker_type="output",
            label="y",
            position={"x": 300, "y": 0},
        )

        diagram.add_connection("c1", "input1", "out", "g1", "in")
        diagram.add_connection("c2", "g1", "out", "tf1", "in")
        diagram.add_connection("c3", "tf1", "out", "output1", "in")

        # Should succeed without raising
        sys = diagram.get_ss("r", "y")
        assert sys is not None, "get_ss should return a system"
        assert sys.ninputs == 1, "Should have 1 input"
        assert sys.noutputs == 1, "Should have 1 output"
